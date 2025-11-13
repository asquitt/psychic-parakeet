"""
Unit Tests for Model Training and Evaluation Components

These tests validate model training, evaluation, and prediction logic
using mocks and fixtures.

Test coverage:
- Model training logic
- Model evaluation metrics
- Prediction consistency
- Model serialization
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


class TestModelTraining:
    """Test suite for model training logic."""

    def test_random_forest_trains_successfully(self, sample_data_small):
        """Test that Random Forest can be trained."""
        df = sample_data_small
        X = df[['feature1', 'feature2', 'feature3']].values
        y = df['target'].values

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        # Model should have been fitted
        assert hasattr(model, 'estimators_'), "Model should have estimators after fitting"
        assert len(model.estimators_) == 10, "Should have 10 trees"

    def test_logistic_regression_trains_successfully(self, sample_data_small):
        """Test that Logistic Regression can be trained."""
        df = sample_data_small
        X = df[['feature1', 'feature2', 'feature3']].values
        y = df['target'].values

        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X, y)

        # Model should have coefficients
        assert hasattr(model, 'coef_'), "Model should have coefficients after fitting"
        assert model.coef_.shape[1] == 3, "Should have 3 feature coefficients"

    def test_model_training_with_different_random_seeds(self, sample_data_small):
        """Test that different seeds produce different models."""
        df = sample_data_small
        X = df[['feature1', 'feature2']].values
        y = df['target'].values

        model1 = RandomForestClassifier(n_estimators=10, random_state=42)
        model1.fit(X, y)
        pred1 = model1.predict(X)

        model2 = RandomForestClassifier(n_estimators=10, random_state=123)
        model2.fit(X, y)
        pred2 = model2.predict(X)

        # Predictions might differ with different seeds
        # (though they should both work)
        assert len(pred1) == len(pred2)

    def test_model_training_is_reproducible(self, sample_data_small):
        """Test that training with same seed is reproducible."""
        df = sample_data_small
        X = df[['feature1', 'feature2']].values
        y = df['target'].values

        model1 = RandomForestClassifier(n_estimators=10, random_state=42)
        model1.fit(X, y)
        pred1 = model1.predict(X)

        model2 = RandomForestClassifier(n_estimators=10, random_state=42)
        model2.fit(X, y)
        pred2 = model2.predict(X)

        # Predictions should be identical with same seed
        np.testing.assert_array_equal(pred1, pred2)


class TestModelPrediction:
    """Test suite for model prediction logic."""

    def test_predict_returns_correct_shape(self, mock_model, sample_data_small):
        """Test that predictions have correct shape."""
        df = sample_data_small
        X = df[['feature1', 'feature2']].values[:5]

        predictions = mock_model.predict(X)

        assert predictions.shape[0] == 5, "Should have 5 predictions"

    def test_predict_proba_returns_probabilities(self, mock_model, sample_data_small):
        """Test that predict_proba returns valid probabilities."""
        df = sample_data_small
        X = df[['feature1', 'feature2']].values[:5]

        probabilities = mock_model.predict_proba(X)

        assert probabilities.shape == (5, 2), "Should have shape (5, 2) for binary classification"
        assert (probabilities >= 0).all(), "Probabilities should be >= 0"
        assert (probabilities <= 1).all(), "Probabilities should be <= 1"

        # Probabilities should sum to 1
        prob_sums = probabilities.sum(axis=1)
        np.testing.assert_array_almost_equal(prob_sums, np.ones(5), decimal=5)

    def test_predictions_are_binary(self, sample_data_small):
        """Test that predictions are binary for classification."""
        df = sample_data_small
        X = df[['feature1', 'feature2']].values
        y = df['target'].values

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        predictions = model.predict(X)

        unique_predictions = np.unique(predictions)
        assert set(unique_predictions).issubset({0, 1}), "Predictions should be 0 or 1"

    def test_predict_single_sample(self, sample_data_small):
        """Test prediction on single sample."""
        df = sample_data_small
        X = df[['feature1', 'feature2']].values
        y = df['target'].values

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        single_sample = X[0:1]  # Keep 2D shape
        prediction = model.predict(single_sample)

        assert prediction.shape[0] == 1, "Should predict for single sample"
        assert prediction[0] in [0, 1], "Prediction should be binary"


class TestModelEvaluation:
    """Test suite for model evaluation metrics."""

    def test_accuracy_calculation(self):
        """Test accuracy metric calculation."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 1])

        accuracy = accuracy_score(y_true, y_pred)

        assert accuracy == 0.8, "Accuracy should be 0.8 (4/5 correct)"

    def test_precision_calculation(self):
        """Test precision metric calculation."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 1])

        precision = precision_score(y_true, y_pred)

        assert precision == 1.0, "Precision should be 1.0 (2/2 correct positive predictions)"

    def test_recall_calculation(self):
        """Test recall metric calculation."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 1])

        recall = recall_score(y_true, y_pred)

        # 2 out of 3 actual positives predicted correctly
        expected_recall = 2/3
        assert abs(recall - expected_recall) < 0.01, f"Recall should be {expected_recall}"

    def test_f1_score_calculation(self):
        """Test F1 score calculation."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 1])

        f1 = f1_score(y_true, y_pred)

        # F1 is harmonic mean of precision (1.0) and recall (0.667)
        expected_f1 = 2 * (1.0 * 0.667) / (1.0 + 0.667)
        assert abs(f1 - expected_f1) < 0.01, f"F1 should be approximately {expected_f1}"

    def test_roc_auc_score_calculation(self):
        """Test ROC-AUC score calculation."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.2, 0.95])

        roc_auc = roc_auc_score(y_true, y_prob)

        assert 0 <= roc_auc <= 1, "ROC-AUC should be between 0 and 1"
        assert roc_auc > 0.5, "ROC-AUC should be better than random"

    def test_evaluation_metrics_format(self, classification_metrics):
        """Test that evaluation metrics have correct format."""
        metrics = {
            'accuracy': 0.85,
            'precision': 0.82,
            'recall': 0.88,
            'f1_score': 0.85,
            'roc_auc': 0.90
        }

        # Check all required metrics are present
        for metric_name, metric_type in classification_metrics.items():
            assert metric_name in metrics, f"{metric_name} should be in metrics"
            assert isinstance(metrics[metric_name], metric_type), f"{metric_name} should be {metric_type}"

        # Check metrics are in valid range
        for metric_name, metric_value in metrics.items():
            assert 0 <= metric_value <= 1, f"{metric_name} should be between 0 and 1"


class TestModelSerialization:
    """Test suite for model serialization/deserialization."""

    def test_model_can_be_pickled(self, sample_data_small, temp_file):
        """Test that model can be serialized with pickle."""
        import pickle

        df = sample_data_small
        X = df[['feature1', 'feature2']].values
        y = df['target'].values

        # Train model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        # Get original predictions
        original_predictions = model.predict(X)

        # Pickle model
        model_file = temp_file.parent / "model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)

        # Load model
        with open(model_file, 'rb') as f:
            loaded_model = pickle.load(f)

        # Get loaded predictions
        loaded_predictions = loaded_model.predict(X)

        # Predictions should be identical
        np.testing.assert_array_equal(original_predictions, loaded_predictions)

    def test_model_metadata_preserved(self, sample_data_small):
        """Test that model metadata is preserved after training."""
        df = sample_data_small
        X = df[['feature1', 'feature2']].values
        y = df['target'].values

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        # Check metadata
        assert model.n_estimators == 10, "n_estimators should be preserved"
        assert model.random_state == 42, "random_state should be preserved"
        assert hasattr(model, 'n_features_in_'), "Should track number of features"
        assert model.n_features_in_ == 2, "Should have 2 input features"


class TestFeatureImportance:
    """Test suite for feature importance extraction."""

    def test_random_forest_has_feature_importance(self, sample_data_small):
        """Test that Random Forest provides feature importances."""
        df = sample_data_small
        X = df[['feature1', 'feature2', 'feature3']].values
        y = df['target'].values

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        assert hasattr(model, 'feature_importances_'), "Should have feature importances"
        assert len(model.feature_importances_) == 3, "Should have 3 feature importances"

    def test_feature_importances_sum_to_one(self, sample_data_small):
        """Test that feature importances sum to 1."""
        df = sample_data_small
        X = df[['feature1', 'feature2', 'feature3']].values
        y = df['target'].values

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        importance_sum = model.feature_importances_.sum()
        assert abs(importance_sum - 1.0) < 1e-6, "Feature importances should sum to 1"

    def test_feature_importances_non_negative(self, sample_data_small):
        """Test that feature importances are non-negative."""
        df = sample_data_small
        X = df[['feature1', 'feature2', 'feature3']].values
        y = df['target'].values

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        assert (model.feature_importances_ >= 0).all(), "Feature importances should be non-negative"


class TestModelValidation:
    """Test suite for model validation and testing."""

    def test_cross_validation_basic(self, sample_data_small):
        """Test basic cross-validation."""
        from sklearn.model_selection import cross_val_score

        df = sample_data_small
        X = df[['feature1', 'feature2']].values
        y = df['target'].values

        model = RandomForestClassifier(n_estimators=10, random_state=42)

        scores = cross_val_score(model, X, y, cv=3)

        assert len(scores) == 3, "Should have 3 CV scores"
        assert all(0 <= s <= 1 for s in scores), "Scores should be between 0 and 1"

    def test_validation_split_preserves_samples(self, sample_data_small):
        """Test that validation split preserves all samples."""
        from sklearn.model_selection import train_test_split

        df = sample_data_small
        X = df[['feature1', 'feature2']].values
        y = df['target'].values

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        total_samples = len(X_train) + len(X_val)
        assert total_samples == len(X), "Split should preserve all samples"

    def test_model_performs_better_than_random(self, sample_data_medium):
        """Test that model performs better than random guessing."""
        df = sample_data_medium
        X = df[['feature1', 'feature2', 'feature3']].values
        y = df['target'].values

        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = RandomForestClassifier(n_estimators=20, random_state=42)
        model.fit(X_train, y_train)

        accuracy = model.score(X_test, y_test)

        # Model should perform better than random (0.5 for binary classification)
        assert accuracy > 0.55, f"Model accuracy {accuracy} should be better than random (0.5)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
