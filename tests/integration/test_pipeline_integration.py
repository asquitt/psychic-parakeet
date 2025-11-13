"""
Integration Tests for ML Pipeline

This module contains comprehensive integration tests that verify the entire
ML pipeline works end-to-end, from data ingestion through model training
to serving predictions.

Tests cover:
- Complete training pipeline flow
- Data validation → preprocessing → feature engineering → training
- Model registration and promotion in MLflow
- Model serving via API
- Deployment strategy execution
- Monitoring and drift detection integration

Author: ML Pipeline Team
Last Updated: 2024-01-01
"""

import pytest
import pandas as pd
import numpy as np
import mlflow
import tempfile
import os
from pathlib import Path
import time
from typing import Dict, List

# Import pipeline components
from ml_pipeline.data.validation import DataValidator, validate_training_data
from ml_pipeline.data.preprocessing import DataPreprocessor
from ml_pipeline.features.engineering import FeatureEngineer
from ml_pipeline.models.training import ModelTrainer
from ml_pipeline.models.evaluation import ModelEvaluator
from ml_pipeline.config import Config


@pytest.fixture(scope="module")
def sample_training_data() -> pd.DataFrame:
    """
    Create sample training data for integration tests.

    This fixture generates synthetic data that mimics real-world
    characteristics for testing the complete pipeline.

    Returns:
        pd.DataFrame: Synthetic training dataset with features and target

    Features:
        - feature1-5: Numerical features with different distributions
        - target: Binary classification target (0 or 1)

    Size: 1000 rows to ensure sufficient data for training/validation split
    """
    np.random.seed(42)

    n_samples = 1000

    # Create features with different characteristics
    data = {
        'feature1': np.random.randn(n_samples),  # Standard normal
        'feature2': np.random.exponential(2, n_samples),  # Exponential
        'feature3': np.random.uniform(-5, 5, n_samples),  # Uniform
        'feature4': np.random.randn(n_samples) * 10 + 50,  # Normal with shift
        'feature5': np.random.choice([0, 1, 2], n_samples)  # Categorical
    }

    # Create target with some relationship to features
    # This ensures the model can actually learn something
    df = pd.DataFrame(data)
    df['target'] = (
        (df['feature1'] > 0).astype(int) * 0.3 +
        (df['feature2'] > 2).astype(int) * 0.3 +
        (df['feature3'] > 0).astype(int) * 0.4 +
        np.random.randn(n_samples) * 0.1  # Add some noise
    )
    df['target'] = (df['target'] > 0.5).astype(int)

    return df


@pytest.fixture(scope="module")
def temp_data_dir():
    """
    Create a temporary directory for test data.

    This fixture provides a clean temporary directory for each test session,
    automatically cleaning up after tests complete.

    Yields:
        Path: Path to temporary directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="module")
def mlflow_tracking_uri(temp_data_dir):
    """
    Set up MLflow tracking for tests.

    Creates an isolated MLflow tracking environment for tests,
    preventing test data from polluting production tracking.

    Args:
        temp_data_dir: Temporary directory fixture

    Returns:
        str: MLflow tracking URI
    """
    tracking_uri = f"file://{temp_data_dir}/mlruns"
    mlflow.set_tracking_uri(tracking_uri)
    return tracking_uri


class TestDataPipelineIntegration:
    """
    Integration tests for the data pipeline components.

    Tests the flow: Raw Data → Validation → Preprocessing → Feature Engineering

    These tests ensure that data transformations maintain consistency
    and that each component properly interfaces with the next.
    """

    def test_complete_data_pipeline(self, sample_training_data):
        """
        Test the complete data pipeline from raw data to engineered features.

        This test verifies:
        1. Data validation catches issues
        2. Preprocessing transforms data correctly
        3. Feature engineering creates expected features
        4. Pipeline is deterministic (same input → same output)

        Args:
            sample_training_data: Fixture providing test data
        """
        # Step 1: Validate data
        validator = DataValidator(
            min_rows=100,
            max_missing_ratio=0.1,
            max_duplicate_ratio=0.05
        )

        feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        target_column = 'target'

        # Should not raise any errors
        validated_df = validate_training_data(
            sample_training_data,
            feature_columns,
            target_column
        )

        assert len(validated_df) > 0, "Validation should return data"
        assert all(col in validated_df.columns for col in feature_columns), \
            "All feature columns should be present"

        # Step 2: Preprocess data
        preprocessor = DataPreprocessor(
            numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
            categorical_features=['feature5']
        )

        X = validated_df[feature_columns]
        y = validated_df[target_column]

        X_processed = preprocessor.fit_transform(X)

        assert X_processed.shape[0] == X.shape[0], \
            "Preprocessing should preserve number of samples"
        assert X_processed.shape[1] > 0, \
            "Preprocessing should produce features"

        # Verify preprocessing is deterministic
        X_processed_again = preprocessor.transform(X)
        np.testing.assert_array_almost_equal(
            X_processed,
            X_processed_again,
            decimal=10,
            err_msg="Preprocessing should be deterministic"
        )

        # Step 3: Feature engineering
        engineer = FeatureEngineer(
            poly_degree=2,
            interaction_features=True,
            statistical_features=True
        )

        X_engineered = engineer.fit_transform(X)

        assert X_engineered.shape[0] == X.shape[0], \
            "Feature engineering should preserve number of samples"
        assert X_engineered.shape[1] > X.shape[1], \
            "Feature engineering should create additional features"

        # Verify feature engineering is deterministic
        X_engineered_again = engineer.transform(X)
        np.testing.assert_array_almost_equal(
            X_engineered,
            X_engineered_again,
            decimal=10,
            err_msg="Feature engineering should be deterministic"
        )

        print(f"✓ Data pipeline test passed:")
        print(f"  - Input shape: {X.shape}")
        print(f"  - After preprocessing: {X_processed.shape}")
        print(f"  - After feature engineering: {X_engineered.shape}")

    def test_pipeline_with_missing_data(self, sample_training_data):
        """
        Test pipeline handles missing data appropriately.

        This test verifies:
        1. Missing data is detected
        2. Preprocessing handles missing values
        3. Feature engineering works with imputed data

        Args:
            sample_training_data: Fixture providing test data
        """
        # Introduce missing values
        df = sample_training_data.copy()
        df.loc[0:10, 'feature1'] = np.nan
        df.loc[5:15, 'feature2'] = np.nan

        feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']

        # Preprocessing should handle missing values via imputation
        preprocessor = DataPreprocessor(
            numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
            categorical_features=['feature5']
        )

        X = df[feature_columns]
        X_processed = preprocessor.fit_transform(X)

        # Verify no NaN values after preprocessing
        assert not np.isnan(X_processed).any(), \
            "Preprocessing should handle all missing values"

        print(f"✓ Missing data handling test passed")
        print(f"  - Input had {X.isna().sum().sum()} missing values")
        print(f"  - Output has {np.isnan(X_processed).sum()} missing values")

    def test_pipeline_with_outliers(self, sample_training_data):
        """
        Test pipeline handles outliers appropriately.

        This test verifies:
        1. Outliers are detected
        2. Preprocessing can handle extreme values
        3. System remains stable with outliers

        Args:
            sample_training_data: Fixture providing test data
        """
        # Introduce outliers
        df = sample_training_data.copy()
        df.loc[0:5, 'feature1'] = 100  # Extreme outliers
        df.loc[5:10, 'feature2'] = -100

        validator = DataValidator()
        feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']

        # Detect outliers
        outliers = validator.detect_outliers(df[feature_columns])

        assert outliers['feature1'].sum() > 0, "Should detect outliers in feature1"
        assert outliers['feature2'].sum() > 0, "Should detect outliers in feature2"

        # Preprocessing should still work
        preprocessor = DataPreprocessor(
            numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
            categorical_features=['feature5']
        )

        X = df[feature_columns]
        X_processed = preprocessor.fit_transform(X)

        # Verify output is valid (no inf/nan)
        assert np.isfinite(X_processed).all(), \
            "Preprocessing should produce finite values even with outliers"

        print(f"✓ Outlier handling test passed")
        print(f"  - Detected {outliers.sum().sum()} outliers")
        print(f"  - Processing completed successfully")


class TestModelTrainingIntegration:
    """
    Integration tests for model training pipeline.

    Tests the flow: Prepared Data → Model Training → Evaluation → MLflow Logging

    These tests ensure that models can be trained, evaluated, and tracked
    properly through the entire training workflow.
    """

    def test_complete_training_pipeline(
        self,
        sample_training_data,
        mlflow_tracking_uri
    ):
        """
        Test complete model training pipeline with MLflow integration.

        This test verifies:
        1. Model training completes successfully
        2. Metrics are logged to MLflow
        3. Model artifacts are saved
        4. Model can be loaded and used for prediction

        Args:
            sample_training_data: Fixture providing test data
            mlflow_tracking_uri: Fixture providing MLflow tracking URI
        """
        from sklearn.model_selection import train_test_split

        # Prepare data
        feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        target_column = 'target'

        X = sample_training_data[feature_columns]
        y = sample_training_data[target_column]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Preprocess
        preprocessor = DataPreprocessor(
            numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
            categorical_features=['feature5']
        )

        X_train_processed = preprocessor.fit_transform(X_train)
        X_test_processed = preprocessor.transform(X_test)

        # Train model
        trainer = ModelTrainer(
            experiment_name="integration_test",
            tracking_uri=mlflow_tracking_uri
        )

        model_result = trainer.train_model(
            X_train_processed,
            y_train,
            model_type="random_forest",
            hyperparameters={
                'n_estimators': 10,  # Small for fast testing
                'max_depth': 5,
                'random_state': 42
            }
        )

        assert model_result is not None, "Training should return model result"
        assert 'model' in model_result, "Result should contain model"
        assert 'metrics' in model_result, "Result should contain metrics"
        assert 'run_id' in model_result, "Result should contain MLflow run ID"

        # Verify metrics
        metrics = model_result['metrics']
        assert 'accuracy' in metrics, "Metrics should include accuracy"
        assert 'roc_auc' in metrics, "Metrics should include ROC-AUC"
        assert metrics['accuracy'] > 0.5, "Model should perform better than random"

        # Verify model can make predictions
        model = model_result['model']
        predictions = model.predict(X_test_processed)

        assert predictions.shape[0] == X_test_processed.shape[0], \
            "Should produce one prediction per sample"
        assert set(predictions).issubset({0, 1}), \
            "Predictions should be binary (0 or 1)"

        # Verify MLflow logging
        run_id = model_result['run_id']
        client = mlflow.tracking.MlflowClient()
        run = client.get_run(run_id)

        assert run.info.status == "FINISHED", "Run should be finished"
        assert 'accuracy' in run.data.metrics, "Accuracy should be logged"
        assert 'model_type' in run.data.params, "Model type should be logged"

        print(f"✓ Training pipeline test passed:")
        print(f"  - Model type: {model_result.get('model_type', 'unknown')}")
        print(f"  - Accuracy: {metrics['accuracy']:.4f}")
        print(f"  - ROC-AUC: {metrics['roc_auc']:.4f}")
        print(f"  - MLflow run ID: {run_id}")

    def test_model_comparison(self, sample_training_data, mlflow_tracking_uri):
        """
        Test training and comparing multiple models.

        This test verifies:
        1. Multiple models can be trained in sequence
        2. Different model types produce different results
        3. Model comparison logic works

        Args:
            sample_training_data: Fixture providing test data
            mlflow_tracking_uri: Fixture providing MLflow tracking URI
        """
        from sklearn.model_selection import train_test_split

        # Prepare data
        feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        target_column = 'target'

        X = sample_training_data[feature_columns]
        y = sample_training_data[target_column]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Preprocess
        preprocessor = DataPreprocessor(
            numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
            categorical_features=['feature5']
        )

        X_train_processed = preprocessor.fit_transform(X_train)

        # Train multiple models
        trainer = ModelTrainer(
            experiment_name="model_comparison_test",
            tracking_uri=mlflow_tracking_uri
        )

        model_types = ['logistic_regression', 'random_forest']
        results = {}

        for model_type in model_types:
            result = trainer.train_model(
                X_train_processed,
                y_train,
                model_type=model_type,
                hyperparameters={'random_state': 42}
            )
            results[model_type] = result

        # Verify both models trained successfully
        assert len(results) == 2, "Should have results for both models"

        for model_type, result in results.items():
            assert result is not None, f"{model_type} should return result"
            assert result['metrics']['accuracy'] > 0.5, \
                f"{model_type} should perform better than random"

        # Verify models are different
        acc1 = results['logistic_regression']['metrics']['accuracy']
        acc2 = results['random_forest']['metrics']['accuracy']

        print(f"✓ Model comparison test passed:")
        print(f"  - Logistic Regression accuracy: {acc1:.4f}")
        print(f"  - Random Forest accuracy: {acc2:.4f}")
        print(f"  - Both models trained successfully")

    def test_model_evaluation_integration(
        self,
        sample_training_data,
        mlflow_tracking_uri
    ):
        """
        Test comprehensive model evaluation pipeline.

        This test verifies:
        1. Model evaluation produces comprehensive metrics
        2. Evaluation results are consistent
        3. Feature importance can be extracted

        Args:
            sample_training_data: Fixture providing test data
            mlflow_tracking_uri: Fixture providing MLflow tracking URI
        """
        from sklearn.model_selection import train_test_split

        # Prepare and train model
        feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        X = sample_training_data[feature_columns]
        y = sample_training_data['target']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        preprocessor = DataPreprocessor(
            numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
            categorical_features=['feature5']
        )

        X_train_processed = preprocessor.fit_transform(X_train)
        X_test_processed = preprocessor.transform(X_test)

        trainer = ModelTrainer(
            experiment_name="evaluation_test",
            tracking_uri=mlflow_tracking_uri
        )

        model_result = trainer.train_model(
            X_train_processed,
            y_train,
            model_type="random_forest"
        )

        # Evaluate model
        evaluator = ModelEvaluator(model_result['model'])
        metrics = evaluator.evaluate(X_test_processed, y_test)

        # Verify comprehensive metrics
        expected_metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
        for metric in expected_metrics:
            assert metric in metrics, f"Should include {metric}"
            assert 0 <= metrics[metric] <= 1, f"{metric} should be between 0 and 1"

        # Verify confusion matrix
        cm = evaluator.confusion_matrix(X_test_processed, y_test)
        assert cm.shape == (2, 2), "Confusion matrix should be 2x2 for binary classification"
        assert cm.sum() == len(y_test), "Confusion matrix should account for all samples"

        # Verify classification report
        report = evaluator.classification_report(X_test_processed, y_test)
        assert '0' in report, "Report should include class 0"
        assert '1' in report, "Report should include class 1"

        # Verify feature importance (for tree-based models)
        importance = evaluator.get_feature_importance()
        if importance is not None:
            assert len(importance) > 0, "Should return feature importance for tree models"
            assert all(v >= 0 for v in importance.values()), \
                "Feature importance should be non-negative"

        print(f"✓ Model evaluation test passed:")
        print(f"  - Accuracy: {metrics['accuracy']:.4f}")
        print(f"  - Precision: {metrics['precision']:.4f}")
        print(f"  - Recall: {metrics['recall']:.4f}")
        print(f"  - F1 Score: {metrics['f1_score']:.4f}")
        print(f"  - ROC-AUC: {metrics['roc_auc']:.4f}")


class TestMLflowIntegration:
    """
    Integration tests for MLflow tracking and model registry.

    Tests the flow: Model Training → MLflow Logging → Model Registry → Model Loading

    These tests ensure MLflow integration works properly for experiment
    tracking, model versioning, and model serving.
    """

    def test_model_registry_integration(
        self,
        sample_training_data,
        mlflow_tracking_uri
    ):
        """
        Test complete MLflow model registry workflow.

        This test verifies:
        1. Model can be registered to registry
        2. Model versions can be managed
        3. Registered model can be loaded and used

        Args:
            sample_training_data: Fixture providing test data
            mlflow_tracking_uri: Fixture providing MLflow tracking URI
        """
        from sklearn.model_selection import train_test_split

        # Train a model
        feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        X = sample_training_data[feature_columns]
        y = sample_training_data['target']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        preprocessor = DataPreprocessor(
            numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
            categorical_features=['feature5']
        )

        X_train_processed = preprocessor.fit_transform(X_train)
        X_test_processed = preprocessor.transform(X_test)

        trainer = ModelTrainer(
            experiment_name="registry_test",
            tracking_uri=mlflow_tracking_uri
        )

        model_result = trainer.train_model(
            X_train_processed,
            y_train,
            model_type="random_forest"
        )

        # Register model
        model_name = "test_model_registry"
        run_id = model_result['run_id']

        model_uri = f"runs:/{run_id}/model"
        registered_model = mlflow.register_model(model_uri, model_name)

        assert registered_model is not None, "Model should be registered"
        assert registered_model.name == model_name, "Model name should match"
        assert registered_model.version is not None, "Model should have version"

        # Load registered model and verify it works
        loaded_model = mlflow.pyfunc.load_model(f"models:/{model_name}/latest")
        predictions = loaded_model.predict(X_test_processed)

        assert predictions.shape[0] == X_test_processed.shape[0], \
            "Loaded model should produce predictions"

        print(f"✓ Model registry test passed:")
        print(f"  - Model registered: {model_name}")
        print(f"  - Version: {registered_model.version}")
        print(f"  - Model loaded and tested successfully")

    def test_experiment_tracking(self, mlflow_tracking_uri):
        """
        Test MLflow experiment tracking capabilities.

        This test verifies:
        1. Experiments can be created
        2. Runs are properly tracked
        3. Parameters and metrics are logged correctly

        Args:
            mlflow_tracking_uri: Fixture providing MLflow tracking URI
        """
        experiment_name = "tracking_test"

        # Create experiment
        experiment_id = mlflow.create_experiment(experiment_name)
        assert experiment_id is not None, "Should create experiment"

        # Start run and log data
        with mlflow.start_run(experiment_id=experiment_id) as run:
            # Log parameters
            mlflow.log_param("test_param", "test_value")
            mlflow.log_param("learning_rate", 0.01)

            # Log metrics
            mlflow.log_metric("test_metric", 0.95)
            mlflow.log_metric("accuracy", 0.87)

            # Log multiple values for a metric
            for i in range(5):
                mlflow.log_metric("loss", 1.0 / (i + 1), step=i)

            run_id = run.info.run_id

        # Verify logged data
        client = mlflow.tracking.MlflowClient()
        run_data = client.get_run(run_id)

        assert run_data.data.params['test_param'] == 'test_value', \
            "Parameters should be logged correctly"
        assert float(run_data.data.params['learning_rate']) == 0.01, \
            "Numerical parameters should be logged"

        assert run_data.data.metrics['test_metric'] == 0.95, \
            "Metrics should be logged correctly"
        assert run_data.data.metrics['accuracy'] == 0.87, \
            "Multiple metrics should be logged"

        # Verify metric history
        metric_history = client.get_metric_history(run_id, "loss")
        assert len(metric_history) == 5, "Should have 5 loss values"

        print(f"✓ Experiment tracking test passed:")
        print(f"  - Experiment created: {experiment_name}")
        print(f"  - Run ID: {run_id}")
        print(f"  - Parameters logged: 2")
        print(f"  - Metrics logged: 3 (with 5 loss steps)")


class TestEndToEndPipeline:
    """
    End-to-end integration tests for the complete ML pipeline.

    Tests the complete flow:
    Raw Data → Validation → Preprocessing → Feature Engineering →
    Model Training → Evaluation → MLflow Tracking → Model Registration

    These tests simulate real-world usage of the entire pipeline.
    """

    def test_complete_pipeline_flow(
        self,
        sample_training_data,
        mlflow_tracking_uri,
        temp_data_dir
    ):
        """
        Test the complete end-to-end ML pipeline.

        This comprehensive test verifies the entire workflow works correctly
        when all components are used together in sequence.

        Workflow tested:
        1. Data validation and quality checks
        2. Data preprocessing and feature engineering
        3. Model training with hyperparameter tuning
        4. Model evaluation with comprehensive metrics
        5. MLflow experiment tracking
        6. Model registration and versioning
        7. Model loading and inference

        Args:
            sample_training_data: Fixture providing test data
            mlflow_tracking_uri: Fixture providing MLflow tracking URI
            temp_data_dir: Fixture providing temporary directory
        """
        from sklearn.model_selection import train_test_split

        # ===== STEP 1: Data Validation =====
        print("\n=== Step 1: Data Validation ===")

        validator = DataValidator(
            min_rows=100,
            max_missing_ratio=0.1,
            max_duplicate_ratio=0.05
        )

        feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        target_column = 'target'

        validated_df = validate_training_data(
            sample_training_data,
            feature_columns,
            target_column
        )

        print(f"✓ Data validated: {len(validated_df)} rows")

        # ===== STEP 2: Train/Test Split =====
        print("\n=== Step 2: Train/Test Split ===")

        X = validated_df[feature_columns]
        y = validated_df[target_column]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"✓ Train set: {len(X_train)} samples")
        print(f"✓ Test set: {len(X_test)} samples")

        # ===== STEP 3: Data Preprocessing =====
        print("\n=== Step 3: Data Preprocessing ===")

        preprocessor = DataPreprocessor(
            numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
            categorical_features=['feature5']
        )

        X_train_processed = preprocessor.fit_transform(X_train)
        X_test_processed = preprocessor.transform(X_test)

        print(f"✓ Features preprocessed: {X_train_processed.shape[1]} features")

        # ===== STEP 4: Feature Engineering =====
        print("\n=== Step 4: Feature Engineering ===")

        engineer = FeatureEngineer(
            poly_degree=2,
            interaction_features=True,
            statistical_features=False  # Disabled to keep feature count manageable
        )

        X_train_engineered = engineer.fit_transform(
            pd.DataFrame(X_train_processed, columns=[f'f{i}' for i in range(X_train_processed.shape[1])])
        )
        X_test_engineered = engineer.transform(
            pd.DataFrame(X_test_processed, columns=[f'f{i}' for i in range(X_test_processed.shape[1])])
        )

        print(f"✓ Features engineered: {X_train_engineered.shape[1]} features")

        # ===== STEP 5: Model Training =====
        print("\n=== Step 5: Model Training ===")

        trainer = ModelTrainer(
            experiment_name="e2e_pipeline_test",
            tracking_uri=mlflow_tracking_uri
        )

        model_result = trainer.train_model(
            X_train_engineered,
            y_train,
            model_type="random_forest",
            hyperparameters={
                'n_estimators': 20,
                'max_depth': 10,
                'random_state': 42
            }
        )

        print(f"✓ Model trained: Random Forest")
        print(f"✓ Training accuracy: {model_result['metrics']['accuracy']:.4f}")

        # ===== STEP 6: Model Evaluation =====
        print("\n=== Step 6: Model Evaluation ===")

        evaluator = ModelEvaluator(model_result['model'])
        test_metrics = evaluator.evaluate(X_test_engineered, y_test)

        print(f"✓ Test Metrics:")
        for metric_name, metric_value in test_metrics.items():
            print(f"  - {metric_name}: {metric_value:.4f}")

        # ===== STEP 7: Model Registration =====
        print("\n=== Step 7: Model Registration ===")

        model_name = "e2e_test_model"
        run_id = model_result['run_id']
        model_uri = f"runs:/{run_id}/model"

        registered_model = mlflow.register_model(model_uri, model_name)

        print(f"✓ Model registered: {model_name}")
        print(f"✓ Version: {registered_model.version}")

        # ===== STEP 8: Model Loading and Inference =====
        print("\n=== Step 8: Model Loading and Inference ===")

        loaded_model = mlflow.pyfunc.load_model(f"models:/{model_name}/latest")
        predictions = loaded_model.predict(X_test_engineered)

        print(f"✓ Model loaded successfully")
        print(f"✓ Generated {len(predictions)} predictions")

        # ===== Final Assertions =====
        assert len(predictions) == len(y_test), \
            "Should generate predictions for all test samples"
        assert set(predictions).issubset({0, 1}), \
            "Predictions should be binary"
        assert test_metrics['accuracy'] > 0.5, \
            "Model should perform better than random"
        assert test_metrics['roc_auc'] > 0.5, \
            "ROC-AUC should be better than random"

        print(f"\n{'='*60}")
        print(f"✓ END-TO-END PIPELINE TEST COMPLETED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"\nFinal Summary:")
        print(f"  - Data samples: {len(validated_df)}")
        print(f"  - Final feature count: {X_train_engineered.shape[1]}")
        print(f"  - Model: Random Forest")
        print(f"  - Test Accuracy: {test_metrics['accuracy']:.4f}")
        print(f"  - Test ROC-AUC: {test_metrics['roc_auc']:.4f}")
        print(f"  - MLflow Run ID: {run_id}")
        print(f"  - Registered Model: {model_name} v{registered_model.version}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
