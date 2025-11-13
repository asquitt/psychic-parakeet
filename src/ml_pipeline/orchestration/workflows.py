"""
Prefect Workflow Orchestration

Prefect is a modern workflow orchestration framework that provides:
- DAG (Directed Acyclic Graph) execution
- Task dependencies and retries
- Scheduling and cron jobs
- Monitoring and observability
- Workflow versioning

Learning Points:
- Workflows = sequence of tasks with dependencies
- Tasks = atomic units of work
- Flows = collections of tasks
- Prefect handles retry logic, logging, monitoring
- Use for complex multi-step ML pipelines

Why Prefect over Airflow?
- More Pythonic API
- Better testing support
- Lighter weight
- Modern architecture
- Cost-efficient for smaller teams
"""

from typing import Dict, Any, Optional, List
from datetime import timedelta
import pandas as pd
import mlflow
from prefect import flow, task
from prefect.tasks import task_input_hash

from ml_pipeline.data.validation import DataValidator, validate_training_data
from ml_pipeline.data.preprocessing import DataPreprocessor, prepare_train_test_split
from ml_pipeline.features.engineering import FeatureEngineer
from ml_pipeline.models.training import ModelTrainer
from ml_pipeline.models.evaluation import ModelEvaluator
from ml_pipeline.monitoring.drift_detection import DriftDetector
from ml_pipeline.config import config


# ============================================================================
# TRAINING PIPELINE
# ============================================================================

@task(
    name="load_data",
    description="Load training data from source",
    retries=3,
    retry_delay_seconds=10,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1),
)
def load_data_task(data_path: str) -> pd.DataFrame:
    """
    Load data from file.

    Task Configuration:
    - Retries: 3 attempts with 10s delay
    - Caching: Results cached for 1 hour
    - Cache key: Based on input path

    Args:
        data_path: Path to data file

    Returns:
        Loaded DataFrame
    """
    print(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


@task(
    name="validate_data",
    description="Validate data quality and schema"
)
def validate_data_task(
    df: pd.DataFrame,
    feature_columns: List[str],
    target_column: str
) -> pd.DataFrame:
    """
    Validate and clean data.

    Args:
        df: Raw DataFrame
        feature_columns: Feature column names
        target_column: Target column name

    Returns:
        Validated DataFrame
    """
    print("Validating data...")
    clean_df = validate_training_data(df, feature_columns, target_column)
    print(f"✓ Data validated: {len(clean_df)} rows retained")
    return clean_df


@task(name="engineer_features")
def engineer_features_task(
    df: pd.DataFrame,
    numerical_columns: List[str],
    categorical_columns: List[str] = None
) -> pd.DataFrame:
    """
    Engineer features from raw data.

    Args:
        df: Input DataFrame
        numerical_columns: Numerical feature columns
        categorical_columns: Categorical feature columns

    Returns:
        DataFrame with engineered features
    """
    print("Engineering features...")
    engineer = FeatureEngineer()

    df_features = engineer.create_feature_set(
        df,
        numerical_columns=numerical_columns,
        categorical_columns=categorical_columns or [],
        add_interactions=True,
        add_polynomials=False,  # Disable to control feature explosion
    )

    print(f"✓ Features engineered: {len(df_features.columns)} total features")
    return df_features


@task(name="split_data")
def split_data_task(
    df: pd.DataFrame,
    feature_columns: List[str],
    target_column: str,
    test_size: float = 0.2
) -> Dict[str, Any]:
    """
    Split data into train and test sets.

    Args:
        df: DataFrame
        feature_columns: Feature columns
        target_column: Target column
        test_size: Test set proportion

    Returns:
        Dictionary with train/test splits
    """
    print(f"Splitting data ({test_size:.0%} test)...")

    X_train, X_test, y_train, y_test = prepare_train_test_split(
        df,
        feature_columns,
        target_column,
        test_size=test_size,
        stratify=True
    )

    print(f"✓ Train: {len(X_train)} samples, Test: {len(X_test)} samples")

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test
    }


@task(name="preprocess_data")
def preprocess_data_task(
    data_splits: Dict[str, Any],
    numerical_features: List[str],
    categorical_features: List[str] = None
) -> Dict[str, Any]:
    """
    Preprocess training and test data.

    Args:
        data_splits: Dictionary with train/test splits
        numerical_features: Numerical feature names
        categorical_features: Categorical feature names

    Returns:
        Dictionary with preprocessed data and preprocessor
    """
    print("Preprocessing data...")

    # Create and fit preprocessor
    preprocessor = DataPreprocessor(
        numerical_features=numerical_features,
        categorical_features=categorical_features or [],
        scaling_method="standard"
    )

    # Fit on training data only
    X_train_scaled = preprocessor.fit_transform(data_splits["X_train"])
    X_test_scaled = preprocessor.transform(data_splits["X_test"])

    # Save preprocessor
    preprocessor.save("models/preprocessor.joblib")
    print("✓ Preprocessor saved")

    return {
        "X_train": X_train_scaled,
        "X_test": X_test_scaled,
        "y_train": data_splits["y_train"],
        "y_test": data_splits["y_test"],
        "preprocessor": preprocessor
    }


@task(name="train_model")
def train_model_task(
    processed_data: Dict[str, Any],
    model_type: str = "xgboost",
    tune_hyperparameters: bool = True
) -> Dict[str, Any]:
    """
    Train ML model.

    Args:
        processed_data: Preprocessed data
        model_type: Type of model to train
        tune_hyperparameters: Whether to tune hyperparameters

    Returns:
        Dictionary with trained model and run_id
    """
    print(f"Training {model_type} model...")

    trainer = ModelTrainer(
        experiment_name="ml_pipeline_training",
        mlflow_tracking_uri=config.mlflow.mlflow_tracking_uri
    )

    X_train = processed_data["X_train"]
    y_train = processed_data["y_train"]

    if tune_hyperparameters:
        print("Tuning hyperparameters...")
        model, best_params = trainer.tune_hyperparameters(
            X_train,
            y_train,
            model_type=model_type,
            search_type="random",
            n_iter=10  # Reduced for speed
        )
        run_id = None  # Tuning creates its own run
    else:
        model, run_id = trainer.train_model(
            X_train,
            y_train,
            model_type=model_type
        )

    print("✓ Model training complete")

    return {
        "model": model,
        "run_id": run_id,
        "model_type": model_type
    }


@task(name="evaluate_model")
def evaluate_model_task(
    model_result: Dict[str, Any],
    processed_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluate trained model.

    Args:
        model_result: Result from training
        processed_data: Preprocessed data

    Returns:
        Evaluation results
    """
    print("Evaluating model...")

    evaluator = ModelEvaluator()

    evaluation_results = evaluator.evaluate_and_log(
        model_result["model"],
        processed_data["X_test"],
        processed_data["y_test"],
        run_id=model_result.get("run_id")
    )

    print("✓ Model evaluation complete")

    return evaluation_results


@task(name="register_model")
def register_model_task(
    model_result: Dict[str, Any],
    evaluation_results: Dict[str, Any],
    model_name: str = "production_model",
    min_accuracy: float = 0.7
) -> Optional[str]:
    """
    Register model if it meets quality criteria.

    Args:
        model_result: Training results
        evaluation_results: Evaluation results
        model_name: Name for registered model
        min_accuracy: Minimum accuracy for registration

    Returns:
        Model version if registered, None otherwise
    """
    metrics = evaluation_results["metrics"]
    accuracy = metrics.get("accuracy", 0)

    print(f"Checking model quality (accuracy: {accuracy:.4f})...")

    if accuracy < min_accuracy:
        print(f"✗ Model quality insufficient (< {min_accuracy:.4f}), not registering")
        return None

    if not model_result.get("run_id"):
        print("✗ No run_id available, cannot register model")
        return None

    print(f"✓ Model quality acceptable, registering...")

    trainer = ModelTrainer(
        experiment_name="ml_pipeline_training",
        mlflow_tracking_uri=config.mlflow.mlflow_tracking_uri
    )

    version = trainer.register_model(
        run_id=model_result["run_id"],
        model_name=model_name,
        stage="Staging"
    )

    print(f"✓ Model registered: {model_name} v{version}")

    return version


@flow(
    name="training_pipeline",
    description="End-to-end ML model training pipeline"
)
def training_pipeline(
    data_path: str,
    feature_columns: List[str],
    target_column: str,
    numerical_features: List[str],
    categorical_features: List[str] = None,
    model_type: str = "xgboost",
    tune_hyperparameters: bool = True
) -> Dict[str, Any]:
    """
    Complete training pipeline flow.

    This workflow orchestrates the entire training process:
    1. Load data
    2. Validate data quality
    3. Engineer features
    4. Split into train/test
    5. Preprocess data
    6. Train model
    7. Evaluate model
    8. Register model if quality is good

    Args:
        data_path: Path to training data
        feature_columns: Feature column names
        target_column: Target column name
        numerical_features: Numerical feature names
        categorical_features: Categorical feature names
        model_type: Type of model to train
        tune_hyperparameters: Whether to tune hyperparameters

    Returns:
        Dictionary with pipeline results

    Example:
        >>> from ml_pipeline.orchestration.workflows import training_pipeline
        >>> results = training_pipeline(
        ...     data_path="data/train.csv",
        ...     feature_columns=["age", "income"],
        ...     target_column="purchased",
        ...     numerical_features=["age", "income"],
        ...     model_type="xgboost"
        ... )
    """
    print("=" * 70)
    print("STARTING TRAINING PIPELINE")
    print("=" * 70)

    # Load and validate data
    df = load_data_task(data_path)
    df_validated = validate_data_task(df, feature_columns, target_column)

    # Engineer features
    df_features = engineer_features_task(
        df_validated,
        numerical_features,
        categorical_features
    )

    # Get updated feature columns after engineering
    all_features = [col for col in df_features.columns if col != target_column]

    # Split data
    data_splits = split_data_task(
        df_features,
        all_features,
        target_column
    )

    # Preprocess
    processed_data = preprocess_data_task(
        data_splits,
        numerical_features=all_features  # Use all features after engineering
    )

    # Train model
    model_result = train_model_task(
        processed_data,
        model_type,
        tune_hyperparameters
    )

    # Evaluate model
    evaluation_results = evaluate_model_task(
        model_result,
        processed_data
    )

    # Register model
    model_version = register_model_task(
        model_result,
        evaluation_results
    )

    print("=" * 70)
    print("TRAINING PIPELINE COMPLETE")
    print("=" * 70)

    return {
        "model_version": model_version,
        "metrics": evaluation_results["metrics"],
        "model_type": model_type
    }


# ============================================================================
# MONITORING PIPELINE
# ============================================================================

@task(name="detect_drift")
def detect_drift_task(
    reference_data_path: str,
    current_data_path: str,
    numerical_features: List[str],
    categorical_features: List[str] = None
) -> Dict[str, Any]:
    """
    Detect data drift.

    Args:
        reference_data_path: Path to reference data
        current_data_path: Path to current data
        numerical_features: Numerical features to check
        categorical_features: Categorical features to check

    Returns:
        Drift detection results
    """
    print("Detecting data drift...")

    # Load data
    reference_df = pd.read_csv(reference_data_path)
    current_df = pd.read_csv(current_data_path)

    # Initialize detector
    detector = DriftDetector(threshold=0.05)
    detector.set_reference_data(reference_df)

    # Detect drift
    results = detector.detect_drift(
        current_df,
        numerical_features,
        categorical_features
    )

    # Check if retraining needed
    should_retrain = detector.should_retrain(results)

    return {
        "drift_detected": results["drift_detected"],
        "drifted_features": results["drifted_features"],
        "should_retrain": should_retrain,
        "details": results
    }


@flow(
    name="monitoring_pipeline",
    description="Monitor production model performance and drift"
)
def monitoring_pipeline(
    reference_data_path: str,
    current_data_path: str,
    numerical_features: List[str],
    categorical_features: List[str] = None
) -> Dict[str, Any]:
    """
    Monitoring pipeline flow.

    Args:
        reference_data_path: Path to reference data
        current_data_path: Path to current production data
        numerical_features: Numerical features
        categorical_features: Categorical features

    Returns:
        Monitoring results

    Example:
        >>> from ml_pipeline.orchestration.workflows import monitoring_pipeline
        >>> results = monitoring_pipeline(
        ...     reference_data_path="data/train.csv",
        ...     current_data_path="data/production.csv",
        ...     numerical_features=["age", "income"]
        ... )
    """
    print("=" * 70)
    print("STARTING MONITORING PIPELINE")
    print("=" * 70)

    # Detect drift
    drift_results = detect_drift_task(
        reference_data_path,
        current_data_path,
        numerical_features,
        categorical_features
    )

    print("=" * 70)
    print("MONITORING PIPELINE COMPLETE")
    print("=" * 70)

    if drift_results["should_retrain"]:
        print("⚠️  ALERT: Model retraining recommended!")

    return drift_results


if __name__ == "__main__":
    # Example usage
    print("Prefect workflows loaded. Use prefect CLI to run:")
    print("  prefect deployment build")
    print("  prefect deployment apply")
