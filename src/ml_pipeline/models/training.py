"""
Model Training with MLflow Integration

This module provides model training with:
- Multiple ML algorithms (sklearn, XGBoost)
- Hyperparameter tuning with cross-validation
- Experiment tracking with MLflow
- Model versioning and registry

Learning Points:
- MLflow tracks everything: parameters, metrics, models, artifacts
- Experiment organization: group related runs
- Model registry: production-ready model management
- Hyperparameter tuning: find optimal model configuration

MLflow Key Concepts:
- Experiment: Container for related runs (e.g., "customer_churn")
- Run: Single model training execution with tracked metrics
- Artifact: Files logged with run (models, plots, data)
- Model Registry: Central model store with staging and production
"""

from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from xgboost import XGBClassifier
import mlflow
import mlflow.sklearn
import mlflow.xgboost
from mlflow.models.signature import infer_signature


class ModelTrainer:
    """
    Model training with MLflow tracking and hyperparameter tuning.

    This class provides:
    - Multiple algorithm support
    - Automated hyperparameter tuning
    - Experiment tracking
    - Model versioning
    - Cross-validation
    """

    def __init__(
        self,
        experiment_name: str,
        mlflow_tracking_uri: str = "http://localhost:5000",
    ):
        """
        Initialize model trainer with MLflow configuration.

        Args:
            experiment_name: Name of MLflow experiment
            mlflow_tracking_uri: MLflow tracking server URI
        """
        self.experiment_name = experiment_name
        mlflow.set_tracking_uri(mlflow_tracking_uri)

        # Create or get experiment
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            self.experiment_id = mlflow.create_experiment(experiment_name)
        else:
            self.experiment_id = experiment.experiment_id

        mlflow.set_experiment(experiment_name)

        # Available models
        self.model_registry = {
            "logistic_regression": LogisticRegression,
            "random_forest": RandomForestClassifier,
            "gradient_boosting": GradientBoostingClassifier,
            "xgboost": XGBClassifier,
            "svm": SVC,
        }

    def get_default_hyperparameters(self, model_type: str) -> Dict[str, Any]:
        """
        Get default hyperparameter search space for each model type.

        Hyperparameter Tuning Strategy:
        - Logistic Regression: Regularization strength, penalty type
        - Random Forest: Trees, depth, min samples
        - Gradient Boosting: Learning rate, trees, depth
        - XGBoost: Similar to GB + advanced features
        - SVM: Kernel, C, gamma

        Args:
            model_type: Type of model

        Returns:
            Dictionary of hyperparameter ranges
        """
        hyperparameters = {
            "logistic_regression": {
                "C": [0.01, 0.1, 1.0, 10.0, 100.0],
                "penalty": ["l1", "l2"],
                "solver": ["liblinear", "saga"],
                "max_iter": [1000],
            },
            "random_forest": {
                "n_estimators": [50, 100, 200],
                "max_depth": [5, 10, 15, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2"],
            },
            "gradient_boosting": {
                "n_estimators": [50, 100, 200],
                "learning_rate": [0.01, 0.1, 0.2],
                "max_depth": [3, 5, 7],
                "min_samples_split": [2, 5, 10],
                "subsample": [0.8, 0.9, 1.0],
            },
            "xgboost": {
                "n_estimators": [50, 100, 200],
                "learning_rate": [0.01, 0.1, 0.2],
                "max_depth": [3, 5, 7],
                "min_child_weight": [1, 3, 5],
                "subsample": [0.8, 0.9, 1.0],
                "colsample_bytree": [0.8, 0.9, 1.0],
            },
            "svm": {
                "C": [0.1, 1.0, 10.0],
                "kernel": ["rbf", "linear"],
                "gamma": ["scale", "auto"],
            },
        }

        return hyperparameters.get(model_type, {})

    def train_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        model_type: str = "random_forest",
        hyperparameters: Optional[Dict[str, Any]] = None,
        run_name: Optional[str] = None,
    ) -> Tuple[Any, str]:
        """
        Train a single model with specified hyperparameters.

        This method:
        1. Creates MLflow run
        2. Logs parameters
        3. Trains model
        4. Logs metrics
        5. Saves model to registry

        Args:
            X_train: Training features
            y_train: Training targets
            model_type: Type of model to train
            hyperparameters: Model hyperparameters (if None, uses defaults)
            run_name: Name for this training run

        Returns:
            Tuple of (trained_model, run_id)

        Example:
            >>> trainer = ModelTrainer("customer_churn")
            >>> model, run_id = trainer.train_model(
            ...     X_train, y_train,
            ...     model_type="xgboost",
            ...     hyperparameters={"n_estimators": 100, "max_depth": 5}
            ... )
        """
        if model_type not in self.model_registry:
            raise ValueError(f"Unknown model type: {model_type}")

        # Use defaults if no hyperparameters provided
        if hyperparameters is None:
            hyperparameters = {}

        # Start MLflow run
        with mlflow.start_run(run_name=run_name) as run:
            # Log parameters
            mlflow.log_param("model_type", model_type)
            for param, value in hyperparameters.items():
                mlflow.log_param(param, value)

            # Create and train model
            model_class = self.model_registry[model_type]
            model = model_class(**hyperparameters)
            model.fit(X_train, y_train)

            # Calculate training metrics
            train_score = model.score(X_train, y_train)
            mlflow.log_metric("train_accuracy", train_score)

            # Cross-validation score
            cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            mlflow.log_metric("cv_mean_accuracy", cv_scores.mean())
            mlflow.log_metric("cv_std_accuracy", cv_scores.std())

            # Infer model signature (input/output schema)
            signature = infer_signature(X_train, model.predict(X_train))

            # Log model
            if model_type == "xgboost":
                mlflow.xgboost.log_model(model, "model", signature=signature)
            else:
                mlflow.sklearn.log_model(model, "model", signature=signature)

            print(f"✓ Model trained: {model_type}")
            print(f"  Train accuracy: {train_score:.4f}")
            print(f"  CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
            print(f"  Run ID: {run.info.run_id}")

            return model, run.info.run_id

    def tune_hyperparameters(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        model_type: str = "random_forest",
        param_grid: Optional[Dict[str, List]] = None,
        search_type: str = "grid",
        cv: int = 5,
        n_iter: int = 20,
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Tune model hyperparameters using grid or random search.

        Hyperparameter Tuning Methods:
        - Grid Search: Exhaustive search over parameter grid
          - Pros: Finds best combination
          - Cons: Expensive for large grids
        - Random Search: Random sampling from parameter space
          - Pros: More efficient, explores broader space
          - Cons: May miss optimal combination

        Args:
            X_train: Training features
            y_train: Training targets
            model_type: Type of model
            param_grid: Hyperparameter grid (if None, uses defaults)
            search_type: 'grid' or 'random'
            cv: Number of cross-validation folds
            n_iter: Number of iterations for random search

        Returns:
            Tuple of (best_model, best_parameters)

        Example:
            >>> best_model, best_params = trainer.tune_hyperparameters(
            ...     X_train, y_train,
            ...     model_type="xgboost",
            ...     search_type="random",
            ...     n_iter=20
            ... )
        """
        if model_type not in self.model_registry:
            raise ValueError(f"Unknown model type: {model_type}")

        # Use default grid if not provided
        if param_grid is None:
            param_grid = self.get_default_hyperparameters(model_type)

        # Create base model
        model_class = self.model_registry[model_type]
        base_model = model_class()

        # Start MLflow run for hyperparameter tuning
        with mlflow.start_run(run_name=f"{model_type}_tuning") as parent_run:
            mlflow.log_param("model_type", model_type)
            mlflow.log_param("search_type", search_type)
            mlflow.log_param("cv_folds", cv)

            # Perform search
            if search_type == "grid":
                print(f"Starting grid search with {len(param_grid)} parameters...")
                search = GridSearchCV(
                    base_model,
                    param_grid,
                    cv=cv,
                    scoring="accuracy",
                    n_jobs=-1,
                    verbose=1,
                )
            else:  # random
                print(f"Starting random search with {n_iter} iterations...")
                search = RandomizedSearchCV(
                    base_model,
                    param_grid,
                    n_iter=n_iter,
                    cv=cv,
                    scoring="accuracy",
                    n_jobs=-1,
                    verbose=1,
                    random_state=42,
                )

            search.fit(X_train, y_train)

            # Log best parameters and score
            mlflow.log_params(search.best_params_)
            mlflow.log_metric("best_cv_score", search.best_score_)

            # Log all CV results
            results_df = pd.DataFrame(search.cv_results_)
            results_df.to_csv("cv_results.csv", index=False)
            mlflow.log_artifact("cv_results.csv")

            print(f"\n✓ Hyperparameter tuning complete")
            print(f"  Best CV score: {search.best_score_:.4f}")
            print(f"  Best parameters: {search.best_params_}")

            return search.best_estimator_, search.best_params_

    def compare_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        model_types: List[str] = None,
    ) -> pd.DataFrame:
        """
        Train and compare multiple models.

        This method:
        1. Trains multiple model types
        2. Evaluates each on test data
        3. Compares performance metrics
        4. Logs everything to MLflow

        Args:
            X_train: Training features
            y_train: Training targets
            X_test: Test features
            y_test: Test targets
            model_types: List of model types to compare

        Returns:
            DataFrame with model comparison results

        Example:
            >>> comparison = trainer.compare_models(
            ...     X_train, y_train, X_test, y_test,
            ...     model_types=["logistic_regression", "random_forest", "xgboost"]
            ... )
            >>> print(comparison.sort_values("test_accuracy", ascending=False))
        """
        if model_types is None:
            model_types = ["logistic_regression", "random_forest", "xgboost"]

        results = []

        for model_type in model_types:
            print(f"\nTraining {model_type}...")

            # Train model
            model, run_id = self.train_model(
                X_train,
                y_train,
                model_type=model_type,
                run_name=f"{model_type}_comparison",
            )

            # Evaluate on test set
            test_score = model.score(X_test, y_test)

            # Log test metrics to the same run
            with mlflow.start_run(run_id=run_id):
                mlflow.log_metric("test_accuracy", test_score)

            results.append(
                {
                    "model_type": model_type,
                    "run_id": run_id,
                    "train_accuracy": model.score(X_train, y_train),
                    "test_accuracy": test_score,
                }
            )

        results_df = pd.DataFrame(results)
        print("\n" + "=" * 50)
        print("MODEL COMPARISON RESULTS")
        print("=" * 50)
        print(results_df.to_string(index=False))

        return results_df

    def register_model(
        self,
        run_id: str,
        model_name: str,
        stage: str = "Staging",
    ) -> str:
        """
        Register model in MLflow Model Registry.

        Model Registry Stages:
        - None: Newly registered
        - Staging: Under testing
        - Production: Deployed to production
        - Archived: Deprecated

        Args:
            run_id: MLflow run ID
            model_name: Name to register model as
            stage: Initial stage for model

        Returns:
            Model version

        Example:
            >>> version = trainer.register_model(
            ...     run_id="abc123",
            ...     model_name="customer_churn_model",
            ...     stage="Staging"
            ... )
        """
        # Get model URI from run
        model_uri = f"runs:/{run_id}/model"

        # Register model
        model_details = mlflow.register_model(model_uri, model_name)

        # Transition to specified stage
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=model_name,
            version=model_details.version,
            stage=stage,
        )

        print(f"✓ Model registered: {model_name} version {model_details.version}")
        print(f"  Stage: {stage}")

        return model_details.version
