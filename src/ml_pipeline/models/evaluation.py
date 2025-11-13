"""
Model Evaluation and Comparison

This module provides comprehensive model evaluation including:
- Performance metrics (accuracy, precision, recall, F1, ROC-AUC)
- Confusion matrix and classification report
- Feature importance analysis
- Model comparison and selection
- Performance visualization

Learning Points:
- Choose metrics based on problem type and business goals
- Confusion matrix shows type I and type II errors
- ROC curve and AUC for classification threshold selection
- Feature importance for model interpretability
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve,
)
import mlflow


class ModelEvaluator:
    """
    Comprehensive model evaluation with MLflow logging.

    This class provides:
    - Multiple evaluation metrics
    - Confusion matrix analysis
    - ROC curve calculation
    - Feature importance extraction
    - Performance comparison
    """

    def __init__(self):
        """Initialize model evaluator."""
        pass

    def evaluate_classification(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
        average: str = "binary",
    ) -> Dict[str, float]:
        """
        Evaluate classification model performance.

        Metrics Explained:
        - Accuracy: (TP + TN) / Total - Overall correctness
        - Precision: TP / (TP + FP) - Of predicted positives, how many are correct?
        - Recall: TP / (TP + FN) - Of actual positives, how many did we find?
        - F1: 2 * (Precision * Recall) / (Precision + Recall) - Harmonic mean
        - ROC-AUC: Area under ROC curve - Discrimination ability

        When to use which metric?
        - Accuracy: Balanced classes, equal cost of errors
        - Precision: When false positives are costly (e.g., spam detection)
        - Recall: When false negatives are costly (e.g., disease diagnosis)
        - F1: Balance between precision and recall
        - ROC-AUC: When you need to tune classification threshold

        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities (for ROC-AUC)
            average: Averaging method for multiclass ('binary', 'micro', 'macro')

        Returns:
            Dictionary of metrics

        Example:
            >>> metrics = evaluator.evaluate_classification(
            ...     y_test, y_pred, y_proba
            ... )
            >>> print(f"Accuracy: {metrics['accuracy']:.4f}")
        """
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average=average, zero_division=0),
            "recall": recall_score(y_true, y_pred, average=average, zero_division=0),
            "f1": f1_score(y_true, y_pred, average=average, zero_division=0),
        }

        # Add ROC-AUC if probabilities provided
        if y_proba is not None:
            try:
                # For binary classification
                if len(y_proba.shape) == 1 or y_proba.shape[1] == 1:
                    metrics["roc_auc"] = roc_auc_score(y_true, y_proba)
                # For multiclass with probabilities
                elif y_proba.shape[1] > 2:
                    metrics["roc_auc"] = roc_auc_score(
                        y_true, y_proba, average=average, multi_class="ovr"
                    )
                # For binary with 2D probabilities
                else:
                    metrics["roc_auc"] = roc_auc_score(y_true, y_proba[:, 1])
            except Exception as e:
                print(f"Warning: Could not calculate ROC-AUC: {e}")

        return metrics

    def get_confusion_matrix(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> np.ndarray:
        """
        Calculate confusion matrix.

        Confusion Matrix Layout:
                     Predicted
                    Neg    Pos
        Actual Neg  TN     FP
               Pos  FN     TP

        Where:
        - TN: True Negatives (correctly predicted negative)
        - FP: False Positives (Type I error - predicted positive, actually negative)
        - FN: False Negatives (Type II error - predicted negative, actually positive)
        - TP: True Positives (correctly predicted positive)

        Args:
            y_true: True labels
            y_pred: Predicted labels

        Returns:
            Confusion matrix as numpy array
        """
        return confusion_matrix(y_true, y_pred)

    def get_classification_report(
        self, y_true: np.ndarray, y_pred: np.ndarray, target_names: Optional[List[str]] = None
    ) -> str:
        """
        Generate detailed classification report.

        The report includes:
        - Precision, recall, F1-score for each class
        - Support (number of samples) for each class
        - Macro and weighted averages

        Args:
            y_true: True labels
            y_pred: Predicted labels
            target_names: Names of target classes

        Returns:
            Classification report as string
        """
        return classification_report(y_true, y_pred, target_names=target_names)

    def calculate_roc_curve(
        self, y_true: np.ndarray, y_proba: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate ROC curve data.

        ROC (Receiver Operating Characteristic) Curve:
        - X-axis: False Positive Rate (FPR)
        - Y-axis: True Positive Rate (TPR/Recall)
        - Plots performance at different classification thresholds
        - AUC: Area under curve (1.0 = perfect, 0.5 = random)

        Use ROC curve to:
        - Choose optimal classification threshold
        - Compare model performance visually
        - Understand precision-recall tradeoff

        Args:
            y_true: True labels
            y_proba: Predicted probabilities

        Returns:
            Tuple of (fpr, tpr, thresholds)
        """
        fpr, tpr, thresholds = roc_curve(y_true, y_proba)
        return fpr, tpr, thresholds

    def get_feature_importance(
        self, model: Any, feature_names: List[str], top_n: int = 20
    ) -> pd.DataFrame:
        """
        Extract feature importance from model.

        Feature Importance Interpretation:
        - Tree-based models: Gini importance or split count
        - Linear models: Absolute coefficient values
        - Higher importance = more influential in predictions

        Use feature importance for:
        - Model interpretability
        - Feature selection
        - Domain insights
        - Debugging (unexpected important features may indicate data leakage)

        Args:
            model: Trained model with feature_importances_ or coef_
            feature_names: Names of features
            top_n: Number of top features to return

        Returns:
            DataFrame with features and importance scores

        Example:
            >>> importance_df = evaluator.get_feature_importance(
            ...     model, feature_names, top_n=10
            ... )
            >>> print(importance_df)
        """
        # Extract importance based on model type
        if hasattr(model, "feature_importances_"):
            # Tree-based models (RF, GBM, XGBoost)
            importance = model.feature_importances_
        elif hasattr(model, "coef_"):
            # Linear models
            importance = np.abs(model.coef_[0] if len(model.coef_.shape) > 1 else model.coef_)
        else:
            raise ValueError("Model does not have feature_importances_ or coef_")

        # Create DataFrame
        importance_df = pd.DataFrame(
            {"feature": feature_names, "importance": importance}
        ).sort_values("importance", ascending=False)

        return importance_df.head(top_n)

    def evaluate_and_log(
        self,
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray,
        feature_names: Optional[List[str]] = None,
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation with MLflow logging.

        This method:
        1. Makes predictions
        2. Calculates all metrics
        3. Logs metrics to MLflow
        4. Logs confusion matrix
        5. Logs feature importance

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            feature_names: Feature names for importance
            run_id: MLflow run ID (if None, creates new run)

        Returns:
            Dictionary with all evaluation results

        Example:
            >>> results = evaluator.evaluate_and_log(
            ...     model, X_test, y_test,
            ...     feature_names=feature_columns,
            ...     run_id=run_id
            ... )
        """
        # Make predictions
        y_pred = model.predict(X_test)

        # Get probabilities if available
        y_proba = None
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test)
            if len(y_proba.shape) > 1 and y_proba.shape[1] == 2:
                y_proba = y_proba[:, 1]  # Use positive class probability

        # Calculate metrics
        metrics = self.evaluate_classification(y_test, y_pred, y_proba)

        # Get confusion matrix
        cm = self.get_confusion_matrix(y_test, y_pred)

        # Get classification report
        report = self.get_classification_report(y_test, y_pred)

        # Get feature importance if possible
        feature_importance = None
        if feature_names is not None:
            try:
                feature_importance = self.get_feature_importance(model, feature_names)
            except ValueError:
                pass

        # Log to MLflow
        if run_id:
            with mlflow.start_run(run_id=run_id):
                # Log metrics
                for metric_name, metric_value in metrics.items():
                    mlflow.log_metric(f"test_{metric_name}", metric_value)

                # Log confusion matrix
                cm_df = pd.DataFrame(cm)
                cm_df.to_csv("confusion_matrix.csv", index=False)
                mlflow.log_artifact("confusion_matrix.csv")

                # Log classification report
                with open("classification_report.txt", "w") as f:
                    f.write(report)
                mlflow.log_artifact("classification_report.txt")

                # Log feature importance
                if feature_importance is not None:
                    feature_importance.to_csv("feature_importance.csv", index=False)
                    mlflow.log_artifact("feature_importance.csv")

        # Print results
        print("\n" + "=" * 50)
        print("MODEL EVALUATION RESULTS")
        print("=" * 50)
        for metric_name, metric_value in metrics.items():
            print(f"{metric_name:15s}: {metric_value:.4f}")
        print("\nConfusion Matrix:")
        print(cm)
        print("\nClassification Report:")
        print(report)
        if feature_importance is not None:
            print("\nTop Feature Importances:")
            print(feature_importance.to_string(index=False))

        return {
            "metrics": metrics,
            "confusion_matrix": cm,
            "classification_report": report,
            "feature_importance": feature_importance,
        }

    def compare_model_performance(
        self, results_list: List[Dict[str, Any]], metric: str = "f1"
    ) -> pd.DataFrame:
        """
        Compare performance of multiple models.

        Args:
            results_list: List of evaluation results from evaluate_and_log
            metric: Metric to use for comparison

        Returns:
            DataFrame with model comparison
        """
        comparison_data = []

        for i, results in enumerate(results_list):
            metrics = results["metrics"]
            comparison_data.append(
                {"model_id": i, **metrics}
            )

        comparison_df = pd.DataFrame(comparison_data).sort_values(
            metric, ascending=False
        )

        return comparison_df
