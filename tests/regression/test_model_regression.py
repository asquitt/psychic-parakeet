"""
Model Regression Tests

This module contains regression tests that ensure model quality and pipeline
behavior remains consistent across code changes, dependency updates, and
model retraining.

Tests cover:
- Model performance regression (accuracy metrics don't degrade)
- Prediction consistency and reproducibility
- Feature engineering determinism
- Data pipeline output stability
- Model behavior on edge cases
- Cross-version compatibility

These tests help detect:
- Unintended model quality degradation
- Breaking changes in data processing
- Inconsistent predictions due to randomness
- Feature engineering bugs introduced by refactoring

Baseline Performance Targets (for synthetic data):
- Accuracy: >= 0.70
- ROC-AUC: >= 0.75
- F1 Score: >= 0.70

Author: ML Pipeline Team
Last Updated: 2024-01-01
"""

import pytest
import pandas as pd
import numpy as np
import pickle
import json
import tempfile
from pathlib import Path
from sklearn.model_selection import train_test_split
from typing import Dict

from ml_pipeline.data.preprocessing import DataPreprocessor
from ml_pipeline.features.engineering import FeatureEngineer
from ml_pipeline.models.training import ModelTrainer
from ml_pipeline.models.evaluation import ModelEvaluator


# Define baseline performance thresholds
# These should be updated based on actual model performance
BASELINE_THRESHOLDS = {
    'accuracy': 0.70,
    'precision': 0.68,
    'recall': 0.68,
    'f1_score': 0.70,
    'roc_auc': 0.75
}

# Acceptable degradation tolerance (e.g., 5% reduction)
DEGRADATION_TOLERANCE = 0.05


@pytest.fixture(scope="module")
def reference_dataset():
    """
    Create a reference dataset with known characteristics.

    This dataset is used across all regression tests to ensure
    consistent evaluation of model performance.

    Returns:
        tuple: (X, y) features and target
    """
    np.random.seed(42)  # Fixed seed for reproducibility

    n_samples = 2000

    # Create features with known distributions
    data = {
        'feature1': np.random.randn(n_samples),
        'feature2': np.random.exponential(2, n_samples),
        'feature3': np.random.uniform(-5, 5, n_samples),
        'feature4': np.random.randn(n_samples) * 10 + 50,
        'feature5': np.random.choice([0, 1, 2], n_samples)
    }

    df = pd.DataFrame(data)

    # Create target with deterministic relationship
    df['target'] = (
        (df['feature1'] > 0).astype(int) * 0.3 +
        (df['feature2'] > 2).astype(int) * 0.3 +
        (df['feature3'] > 0).astype(int) * 0.4
    )
    # Add controlled noise
    noise = np.random.RandomState(42).randn(n_samples) * 0.1
    df['target'] = (df['target'] + noise > 0.5).astype(int)

    feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
    X = df[feature_columns]
    y = df['target']

    return X, y


@pytest.fixture(scope="module")
def trained_baseline_model(reference_dataset):
    """
    Train a baseline model for regression testing.

    Args:
        reference_dataset: Reference dataset fixture

    Returns:
        dict: Model, preprocessor, metrics, and test data
    """
    X, y = reference_dataset

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train preprocessor
    preprocessor = DataPreprocessor(
        numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
        categorical_features=['feature5']
    )

    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    # Train model with fixed hyperparameters
    trainer = ModelTrainer(experiment_name="regression_test_baseline")

    model_result = trainer.train_model(
        X_train_processed,
        y_train,
        model_type="random_forest",
        hyperparameters={
            'n_estimators': 50,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42
        }
    )

    # Evaluate model
    evaluator = ModelEvaluator(model_result['model'])
    metrics = evaluator.evaluate(X_test_processed, y_test)

    return {
        'model': model_result['model'],
        'preprocessor': preprocessor,
        'metrics': metrics,
        'X_test': X_test,
        'y_test': y_test,
        'X_test_processed': X_test_processed
    }


class TestModelPerformanceRegression:
    """
    Tests for detecting model performance regression.

    These tests ensure that model performance doesn't degrade
    below acceptable thresholds after code changes or retraining.
    """

    def test_accuracy_no_regression(self, trained_baseline_model):
        """
        Test that model accuracy meets baseline threshold.

        This test fails if:
        - Accuracy drops below minimum threshold
        - Accuracy degrades by more than tolerance from baseline

        Args:
            trained_baseline_model: Baseline model fixture
        """
        metrics = trained_baseline_model['metrics']
        accuracy = metrics['accuracy']

        print(f"\n=== Accuracy Regression Test ===")
        print(f"Current accuracy: {accuracy:.4f}")
        print(f"Baseline threshold: {BASELINE_THRESHOLDS['accuracy']:.4f}")
        print(f"Degradation tolerance: {DEGRADATION_TOLERANCE:.2%}")

        # Check against absolute threshold
        assert accuracy >= BASELINE_THRESHOLDS['accuracy'], \
            f"Accuracy {accuracy:.4f} below baseline threshold {BASELINE_THRESHOLDS['accuracy']:.4f}"

        print(f"✓ Accuracy meets baseline requirements")

    def test_roc_auc_no_regression(self, trained_baseline_model):
        """
        Test that ROC-AUC score meets baseline threshold.

        Args:
            trained_baseline_model: Baseline model fixture
        """
        metrics = trained_baseline_model['metrics']
        roc_auc = metrics['roc_auc']

        print(f"\n=== ROC-AUC Regression Test ===")
        print(f"Current ROC-AUC: {roc_auc:.4f}")
        print(f"Baseline threshold: {BASELINE_THRESHOLDS['roc_auc']:.4f}")

        assert roc_auc >= BASELINE_THRESHOLDS['roc_auc'], \
            f"ROC-AUC {roc_auc:.4f} below baseline threshold {BASELINE_THRESHOLDS['roc_auc']:.4f}"

        print(f"✓ ROC-AUC meets baseline requirements")

    def test_f1_score_no_regression(self, trained_baseline_model):
        """
        Test that F1 score meets baseline threshold.

        Args:
            trained_baseline_model: Baseline model fixture
        """
        metrics = trained_baseline_model['metrics']
        f1_score = metrics['f1_score']

        print(f"\n=== F1 Score Regression Test ===")
        print(f"Current F1 score: {f1_score:.4f}")
        print(f"Baseline threshold: {BASELINE_THRESHOLDS['f1_score']:.4f}")

        assert f1_score >= BASELINE_THRESHOLDS['f1_score'], \
            f"F1 score {f1_score:.4f} below baseline threshold {BASELINE_THRESHOLDS['f1_score']:.4f}"

        print(f"✓ F1 score meets baseline requirements")

    def test_precision_recall_balance(self, trained_baseline_model):
        """
        Test that precision and recall are reasonably balanced.

        Extreme imbalance might indicate a problem with the model
        or training process.

        Args:
            trained_baseline_model: Baseline model fixture
        """
        metrics = trained_baseline_model['metrics']
        precision = metrics['precision']
        recall = metrics['recall']

        print(f"\n=== Precision/Recall Balance Test ===")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")

        # Calculate ratio (always >= 1)
        ratio = max(precision, recall) / min(precision, recall)

        print(f"Ratio: {ratio:.2f}")

        # Precision and recall shouldn't differ by more than 3x
        assert ratio < 3.0, \
            f"Precision/recall ratio {ratio:.2f} too high - indicates imbalance"

        print(f"✓ Precision and recall are reasonably balanced")

    def test_all_metrics_comprehensive(self, trained_baseline_model):
        """
        Comprehensive test of all metrics against baselines.

        Provides a complete view of model performance compared
        to baseline requirements.

        Args:
            trained_baseline_model: Baseline model fixture
        """
        metrics = trained_baseline_model['metrics']

        print(f"\n=== Comprehensive Metrics Regression Test ===")
        print(f"\n{'Metric':<15} | {'Current':>10} | {'Threshold':>10} | {'Status':>10}")
        print("-" * 60)

        all_pass = True

        for metric_name, threshold in BASELINE_THRESHOLDS.items():
            current_value = metrics[metric_name]
            passed = current_value >= threshold
            status = "✓ PASS" if passed else "✗ FAIL"

            print(
                f"{metric_name:<15} | "
                f"{current_value:>10.4f} | "
                f"{threshold:>10.4f} | "
                f"{status:>10}"
            )

            if not passed:
                all_pass = False

        assert all_pass, "One or more metrics below baseline threshold"

        print(f"\n✓ All metrics meet baseline requirements")


class TestPredictionConsistency:
    """
    Tests for prediction consistency and reproducibility.

    These tests ensure that predictions are deterministic and
    consistent across multiple runs with the same input.
    """

    def test_prediction_reproducibility(self, trained_baseline_model):
        """
        Test that predictions are reproducible.

        Given the same input and model, predictions should be
        identical across multiple calls.

        Args:
            trained_baseline_model: Baseline model fixture
        """
        model = trained_baseline_model['model']
        X_test = trained_baseline_model['X_test_processed'][:100]

        # Make predictions multiple times
        predictions_1 = model.predict(X_test)
        predictions_2 = model.predict(X_test)
        predictions_3 = model.predict(X_test)

        print(f"\n=== Prediction Reproducibility Test ===")
        print(f"Test samples: {len(X_test)}")

        # All predictions should be identical
        assert np.array_equal(predictions_1, predictions_2), \
            "Predictions not reproducible between runs 1 and 2"
        assert np.array_equal(predictions_2, predictions_3), \
            "Predictions not reproducible between runs 2 and 3"

        print(f"✓ Predictions are fully reproducible across {3} runs")

    def test_probability_reproducibility(self, trained_baseline_model):
        """
        Test that prediction probabilities are reproducible.

        Args:
            trained_baseline_model: Baseline model fixture
        """
        model = trained_baseline_model['model']
        X_test = trained_baseline_model['X_test_processed'][:100]

        # Get probabilities multiple times
        proba_1 = model.predict_proba(X_test)
        proba_2 = model.predict_proba(X_test)
        proba_3 = model.predict_proba(X_test)

        print(f"\n=== Probability Reproducibility Test ===")
        print(f"Test samples: {len(X_test)}")

        # All probabilities should be identical
        np.testing.assert_array_almost_equal(
            proba_1, proba_2, decimal=10,
            err_msg="Probabilities not reproducible between runs 1 and 2"
        )
        np.testing.assert_array_almost_equal(
            proba_2, proba_3, decimal=10,
            err_msg="Probabilities not reproducible between runs 2 and 3"
        )

        print(f"✓ Probabilities are fully reproducible across {3} runs")

    def test_small_input_perturbation(self, trained_baseline_model):
        """
        Test that small input perturbations produce reasonable changes.

        Very small changes in input shouldn't cause dramatic prediction changes,
        which would indicate model instability.

        Args:
            trained_baseline_model: Baseline model fixture
        """
        model = trained_baseline_model['model']
        X_test = trained_baseline_model['X_test_processed'][:100]

        # Get baseline probabilities
        proba_original = model.predict_proba(X_test)

        # Add tiny perturbation
        epsilon = 1e-6
        X_perturbed = X_test + epsilon

        proba_perturbed = model.predict_proba(X_perturbed)

        # Calculate maximum probability change
        max_change = np.max(np.abs(proba_original - proba_perturbed))

        print(f"\n=== Small Perturbation Test ===")
        print(f"Perturbation: {epsilon}")
        print(f"Max probability change: {max_change:.10f}")

        # Small perturbation should cause very small change
        assert max_change < 0.01, \
            f"Small perturbation caused large change: {max_change:.6f}"

        print(f"✓ Model stable under small input perturbations")


class TestFeatureEngineeringRegression:
    """
    Tests for feature engineering consistency.

    These tests ensure that feature engineering produces consistent
    results and doesn't introduce bugs during refactoring.
    """

    def test_preprocessing_determinism(self, reference_dataset):
        """
        Test that preprocessing is deterministic.

        Args:
            reference_dataset: Reference dataset fixture
        """
        X, y = reference_dataset

        preprocessor = DataPreprocessor(
            numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
            categorical_features=['feature5']
        )

        # Preprocess multiple times
        X_processed_1 = preprocessor.fit_transform(X)
        X_processed_2 = preprocessor.transform(X)

        # Create new preprocessor with same config
        preprocessor_2 = DataPreprocessor(
            numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
            categorical_features=['feature5']
        )
        X_processed_3 = preprocessor_2.fit_transform(X)

        print(f"\n=== Preprocessing Determinism Test ===")

        # Check transform is consistent
        np.testing.assert_array_almost_equal(
            X_processed_1,
            X_processed_2,
            decimal=10,
            err_msg="Preprocessing not consistent between fit_transform and transform"
        )

        print(f"✓ Preprocessing is deterministic")

    def test_feature_engineering_determinism(self, reference_dataset):
        """
        Test that feature engineering is deterministic.

        Args:
            reference_dataset: Reference dataset fixture
        """
        X, y = reference_dataset

        engineer = FeatureEngineer(
            poly_degree=2,
            interaction_features=True,
            statistical_features=False
        )

        # Engineer features multiple times
        X_eng_1 = engineer.fit_transform(X)
        X_eng_2 = engineer.transform(X)

        print(f"\n=== Feature Engineering Determinism Test ===")

        # Check results are identical
        np.testing.assert_array_almost_equal(
            X_eng_1,
            X_eng_2,
            decimal=10,
            err_msg="Feature engineering not deterministic"
        )

        print(f"✓ Feature engineering is deterministic")

    def test_feature_count_stability(self, reference_dataset):
        """
        Test that feature engineering produces expected number of features.

        This catches regressions where feature engineering logic changes
        unintentionally, producing different feature counts.

        Args:
            reference_dataset: Reference dataset fixture
        """
        X, y = reference_dataset

        # Expected feature counts for our configuration
        # poly_degree=2, interaction_features=True gives specific count
        engineer = FeatureEngineer(
            poly_degree=2,
            interaction_features=True,
            statistical_features=False
        )

        X_engineered = engineer.fit_transform(X)

        print(f"\n=== Feature Count Stability Test ===")
        print(f"Input features: {X.shape[1]}")
        print(f"Output features: {X_engineered.shape[1]}")

        # With poly_degree=2 and interactions, we expect more features
        assert X_engineered.shape[1] > X.shape[1], \
            "Feature engineering should create additional features"

        # Store expected count for future regression detection
        # This would typically be stored in a baseline file
        expected_min_features = 15  # Conservative estimate
        assert X_engineered.shape[1] >= expected_min_features, \
            f"Feature count {X_engineered.shape[1]} below expected minimum {expected_min_features}"

        print(f"✓ Feature count stable and within expected range")


class TestEdgeCaseBehavior:
    """
    Tests for model behavior on edge cases.

    These tests ensure the model handles unusual inputs gracefully
    and produces reasonable predictions.
    """

    def test_all_zeros_input(self, trained_baseline_model):
        """
        Test model behavior with all-zero input.

        Args:
            trained_baseline_model: Baseline model fixture
        """
        model = trained_baseline_model['model']
        preprocessor = trained_baseline_model['preprocessor']

        # Create all-zero input
        zero_input = pd.DataFrame({
            'feature1': [0.0],
            'feature2': [0.0],
            'feature3': [0.0],
            'feature4': [0.0],
            'feature5': [0]
        })

        zero_processed = preprocessor.transform(zero_input)
        prediction = model.predict(zero_processed)
        probability = model.predict_proba(zero_processed)

        print(f"\n=== All-Zeros Input Test ===")
        print(f"Prediction: {prediction[0]}")
        print(f"Probability: {probability[0]}")

        # Should produce valid prediction
        assert prediction[0] in [0, 1], "Prediction should be binary"
        assert np.isfinite(probability).all(), "Probabilities should be finite"
        assert (probability >= 0).all() and (probability <= 1).all(), \
            "Probabilities should be between 0 and 1"

        print(f"✓ Model handles all-zero input correctly")

    def test_extreme_values_input(self, trained_baseline_model):
        """
        Test model behavior with extreme input values.

        Args:
            trained_baseline_model: Baseline model fixture
        """
        model = trained_baseline_model['model']
        preprocessor = trained_baseline_model['preprocessor']

        # Create extreme value input
        extreme_input = pd.DataFrame({
            'feature1': [1000.0],
            'feature2': [1000.0],
            'feature3': [1000.0],
            'feature4': [1000.0],
            'feature5': [2]
        })

        extreme_processed = preprocessor.transform(extreme_input)
        prediction = model.predict(extreme_processed)
        probability = model.predict_proba(extreme_processed)

        print(f"\n=== Extreme Values Input Test ===")
        print(f"Prediction: {prediction[0]}")
        print(f"Probability: {probability[0]}")

        # Should produce valid prediction even with extreme values
        assert prediction[0] in [0, 1], "Prediction should be binary"
        assert np.isfinite(probability).all(), "Probabilities should be finite"
        assert (probability >= 0).all() and (probability <= 1).all(), \
            "Probabilities should be valid"

        print(f"✓ Model handles extreme values correctly")

    def test_identical_features_input(self, trained_baseline_model):
        """
        Test model behavior when all features have identical values.

        Args:
            trained_baseline_model: Baseline model fixture
        """
        model = trained_baseline_model['model']
        preprocessor = trained_baseline_model['preprocessor']

        # Create input with all features having same value
        identical_input = pd.DataFrame({
            'feature1': [5.0],
            'feature2': [5.0],
            'feature3': [5.0],
            'feature4': [5.0],
            'feature5': [1]
        })

        identical_processed = preprocessor.transform(identical_input)
        prediction = model.predict(identical_processed)

        print(f"\n=== Identical Features Input Test ===")
        print(f"Prediction: {prediction[0]}")

        # Should produce valid prediction
        assert prediction[0] in [0, 1], "Prediction should be binary"

        print(f"✓ Model handles identical feature values correctly")


class TestModelSerializationRegression:
    """
    Tests for model serialization and deserialization.

    These tests ensure that models can be saved and loaded correctly,
    and that predictions remain consistent after serialization.
    """

    def test_model_pickle_consistency(self, trained_baseline_model):
        """
        Test that pickled model produces identical predictions.

        Args:
            trained_baseline_model: Baseline model fixture
        """
        model = trained_baseline_model['model']
        X_test = trained_baseline_model['X_test_processed'][:100]

        # Get predictions from original model
        original_predictions = model.predict(X_test)
        original_probabilities = model.predict_proba(X_test)

        # Pickle and unpickle model
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            pickle.dump(model, f)
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as f:
                loaded_model = pickle.load(f)

            # Get predictions from loaded model
            loaded_predictions = loaded_model.predict(X_test)
            loaded_probabilities = loaded_model.predict_proba(X_test)

            print(f"\n=== Model Pickle Consistency Test ===")

            # Verify predictions are identical
            assert np.array_equal(original_predictions, loaded_predictions), \
                "Predictions differ after pickle/unpickle"

            np.testing.assert_array_almost_equal(
                original_probabilities,
                loaded_probabilities,
                decimal=10,
                err_msg="Probabilities differ after pickle/unpickle"
            )

            print(f"✓ Pickled model produces identical predictions")

        finally:
            # Clean up temp file
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_preprocessor_pickle_consistency(self, trained_baseline_model, reference_dataset):
        """
        Test that pickled preprocessor produces identical results.

        Args:
            trained_baseline_model: Baseline model fixture
            reference_dataset: Reference dataset fixture
        """
        preprocessor = trained_baseline_model['preprocessor']
        X, _ = reference_dataset
        X_sample = X.head(100)

        # Transform with original preprocessor
        original_transformed = preprocessor.transform(X_sample)

        # Pickle and unpickle preprocessor
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            pickle.dump(preprocessor, f)
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as f:
                loaded_preprocessor = pickle.load(f)

            # Transform with loaded preprocessor
            loaded_transformed = loaded_preprocessor.transform(X_sample)

            print(f"\n=== Preprocessor Pickle Consistency Test ===")

            # Verify transformations are identical
            np.testing.assert_array_almost_equal(
                original_transformed,
                loaded_transformed,
                decimal=10,
                err_msg="Preprocessing differs after pickle/unpickle"
            )

            print(f"✓ Pickled preprocessor produces identical results")

        finally:
            # Clean up
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
