"""
Unit Tests for Data Processing Components

These tests validate data validation, preprocessing, and transformation
logic using mocks and fixtures to avoid external dependencies.

Tests are designed to be:
- Fast (< 1s each)
- Isolated (no external dependencies)
- Deterministic (consistent results)
- Well-documented (clear purpose)
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock


class TestDataValidation:
    """Test suite for data validation logic."""

    def test_dataframe_shape_validation(self, sample_data_small):
        """Test that dataframe shape is validated correctly."""
        df = sample_data_small

        # Should have expected number of rows and columns
        assert len(df) == 100, "Should have 100 rows"
        assert len(df.columns) == 6, "Should have 6 columns"

    def test_required_columns_present(self, sample_data_small):
        """Test that required columns are present in dataframe."""
        df = sample_data_small

        required_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5', 'target']

        for col in required_columns:
            assert col in df.columns, f"Column {col} should be present"

    def test_no_missing_values_in_target(self, sample_data_small):
        """Test that target column has no missing values."""
        df = sample_data_small

        assert not df['target'].isna().any(), "Target should have no missing values"

    def test_data_types_correct(self, sample_data_small):
        """Test that data types are correct."""
        df = sample_data_small

        # Numerical features should be float
        assert df['feature1'].dtype in [np.float64, np.float32]
        assert df['feature2'].dtype in [np.float64, np.float32]

        # Target should be integer
        assert df['target'].dtype in [np.int64, np.int32, np.int8]

    def test_target_values_binary(self, sample_data_small):
        """Test that target contains only binary values."""
        df = sample_data_small

        unique_values = df['target'].unique()
        assert set(unique_values).issubset({0, 1}), "Target should be binary (0 or 1)"

    def test_no_duplicate_rows(self, sample_data_small):
        """Test that there are no duplicate rows."""
        df = sample_data_small

        duplicates = df.duplicated().sum()
        # Some duplicates are acceptable in random data
        assert duplicates < len(df) * 0.1, "Less than 10% duplicates acceptable"

    def test_feature_ranges_reasonable(self, sample_data_small):
        """Test that feature values are within reasonable ranges."""
        df = sample_data_small

        # Check for extreme outliers (beyond 10 standard deviations)
        for col in ['feature1', 'feature2', 'feature3', 'feature4']:
            mean = df[col].mean()
            std = df[col].std()

            # Values should be within reasonable range
            extreme_values = df[(df[col] > mean + 10*std) | (df[col] < mean - 10*std)]
            assert len(extreme_values) < 5, f"Too many extreme values in {col}"


class TestDataPreprocessing:
    """Test suite for data preprocessing logic."""

    def test_preprocessing_preserves_sample_count(self, sample_data_small, mock_preprocessor):
        """Test that preprocessing doesn't change number of samples."""
        df = sample_data_small

        feature_cols = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        X = df[feature_cols]

        X_processed = mock_preprocessor.fit_transform(X)

        assert len(X_processed) == len(X), "Sample count should be preserved"

    def test_preprocessing_is_deterministic(self, sample_data_small):
        """Test that preprocessing produces consistent results."""
        df = sample_data_small.copy()

        feature_cols = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        X = df[feature_cols]

        # Process twice with same data
        from sklearn.preprocessing import StandardScaler
        scaler1 = StandardScaler()
        result1 = scaler1.fit_transform(X[['feature1', 'feature2']])

        scaler2 = StandardScaler()
        result2 = scaler2.fit_transform(X[['feature1', 'feature2']])

        # Results should be identical
        np.testing.assert_array_almost_equal(result1, result2, decimal=10)

    def test_scaling_produces_zero_mean(self, sample_data_small):
        """Test that standard scaling produces zero mean."""
        df = sample_data_small

        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()

        X_scaled = scaler.fit_transform(df[['feature1', 'feature2']])

        # Mean should be close to zero
        assert np.abs(X_scaled.mean()) < 1e-10, "Scaled data should have zero mean"

    def test_scaling_produces_unit_variance(self, sample_data_small):
        """Test that standard scaling produces unit variance."""
        df = sample_data_small

        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()

        X_scaled = scaler.fit_transform(df[['feature1', 'feature2']])

        # Variance should be close to 1
        assert np.abs(X_scaled.std() - 1.0) < 0.1, "Scaled data should have unit variance"

    def test_preprocessing_handles_single_sample(self, mock_preprocessor):
        """Test that preprocessing works with single sample."""
        single_sample = pd.DataFrame({
            'feature1': [0.5],
            'feature2': [1.2],
            'feature3': [-0.3],
            'feature4': [55.0],
            'feature5': [1]
        })

        result = mock_preprocessor.transform(single_sample)

        assert result.shape[0] == 1, "Should process single sample"


class TestFeatureEngineering:
    """Test suite for feature engineering logic."""

    def test_polynomial_features_increase_count(self, sample_data_small):
        """Test that polynomial features increase feature count."""
        from sklearn.preprocessing import PolynomialFeatures

        X = sample_data_small[['feature1', 'feature2']].values

        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)

        assert X_poly.shape[1] > X.shape[1], "Polynomial features should increase feature count"

    def test_feature_interactions_created(self, sample_data_small):
        """Test that feature interactions are created."""
        from sklearn.preprocessing import PolynomialFeatures

        X = sample_data_small[['feature1', 'feature2']].values

        poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
        X_poly = poly.fit_transform(X)

        # Should have original features + interaction
        expected_features = 2 + 1  # f1, f2, f1*f2
        assert X_poly.shape[1] == expected_features

    def test_feature_names_preserved(self):
        """Test that feature names can be tracked."""
        from sklearn.preprocessing import PolynomialFeatures

        poly = PolynomialFeatures(degree=2)
        X = np.array([[1, 2], [3, 4]])

        poly.fit(X)
        feature_names = poly.get_feature_names_out(['f1', 'f2'])

        assert len(feature_names) == 6  # 1, f1, f2, f1^2, f1*f2, f2^2

    def test_feature_engineering_deterministic(self, sample_data_small):
        """Test that feature engineering is deterministic."""
        from sklearn.preprocessing import PolynomialFeatures

        X = sample_data_small[['feature1', 'feature2']].values

        poly1 = PolynomialFeatures(degree=2)
        result1 = poly1.fit_transform(X)

        poly2 = PolynomialFeatures(degree=2)
        result2 = poly2.fit_transform(X)

        np.testing.assert_array_almost_equal(result1, result2, decimal=10)


class TestDataSplitting:
    """Test suite for train/test splitting logic."""

    def test_stratified_split_preserves_class_balance(self, sample_data_small):
        """Test that stratified split preserves target distribution."""
        from sklearn.model_selection import train_test_split

        df = sample_data_small
        X = df[['feature1', 'feature2']]
        y = df['target']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Check class distributions are similar
        train_ratio = y_train.mean()
        test_ratio = y_test.mean()
        overall_ratio = y.mean()

        assert abs(train_ratio - overall_ratio) < 0.1, "Train set should preserve class balance"
        assert abs(test_ratio - overall_ratio) < 0.1, "Test set should preserve class balance"

    def test_split_sizes_correct(self, sample_data_small):
        """Test that split produces correct sizes."""
        from sklearn.model_selection import train_test_split

        df = sample_data_small
        X = df[['feature1', 'feature2']]
        y = df['target']

        test_size = 0.2
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        expected_test_size = int(len(X) * test_size)
        assert abs(len(X_test) - expected_test_size) <= 1, "Test set size should be close to expected"

    def test_split_is_reproducible(self, sample_data_small):
        """Test that split with same seed is reproducible."""
        from sklearn.model_selection import train_test_split

        df = sample_data_small
        X = df[['feature1', 'feature2']]
        y = df['target']

        # Split twice with same seed
        X_train1, X_test1, y_train1, y_test1 = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        X_train2, X_test2, y_train2, y_test2 = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Should be identical
        pd.testing.assert_frame_equal(X_train1, X_train2)
        pd.testing.assert_series_equal(y_train1, y_train2)


class TestDataTransformations:
    """Test suite for data transformation utilities."""

    def test_log_transform_handles_positive_values(self):
        """Test log transformation with positive values."""
        X = np.array([[1, 2], [3, 4], [5, 6]])

        X_log = np.log1p(X)  # log(1 + x)

        assert np.isfinite(X_log).all(), "Log transform should produce finite values"
        assert (X_log >= 0).all(), "Log transform of positive values should be positive"

    def test_clip_handles_outliers(self, sample_data_small):
        """Test clipping handles outliers correctly."""
        df = sample_data_small.copy()

        # Add extreme outliers
        df.loc[0, 'feature1'] = 1000
        df.loc[1, 'feature1'] = -1000

        # Clip to reasonable range
        df['feature1'] = df['feature1'].clip(-10, 10)

        assert df['feature1'].max() <= 10, "Max should be clipped"
        assert df['feature1'].min() >= -10, "Min should be clipped"

    def test_fillna_handles_missing_values(self):
        """Test that missing value imputation works."""
        df = pd.DataFrame({
            'feature1': [1, 2, np.nan, 4, 5],
            'feature2': [np.nan, 2, 3, 4, 5]
        })

        # Fill with mean
        df_filled = df.fillna(df.mean())

        assert not df_filled.isna().any().any(), "Should have no missing values after fillna"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
