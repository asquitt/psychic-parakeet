"""
Unit Tests for Data Validation

This module tests the data validation functionality to ensure
data quality checks work correctly.
"""

import pytest
import pandas as pd
import numpy as np
from ml_pipeline.data.validation import DataValidator, validate_training_data


class TestDataValidator:
    """Test suite for DataValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = DataValidator(
            min_rows=10,
            max_missing_ratio=0.1,
            max_duplicate_ratio=0.05
        )

    def test_validator_initialization(self):
        """Test validator initializes with correct parameters."""
        assert self.validator.min_rows == 10
        assert self.validator.max_missing_ratio == 0.1
        assert self.validator.max_duplicate_ratio == 0.05

    def test_validate_schema_success(self):
        """Test schema validation passes with all required columns."""
        df = pd.DataFrame({
            'feature1': [1, 2, 3],
            'feature2': [4, 5, 6],
            'target': [0, 1, 0]
        })

        required_columns = ['feature1', 'feature2', 'target']
        result = self.validator.validate_schema(df, required_columns)

        assert result is True

    def test_validate_schema_missing_columns(self):
        """Test schema validation fails with missing columns."""
        df = pd.DataFrame({
            'feature1': [1, 2, 3],
            'target': [0, 1, 0]
        })

        required_columns = ['feature1', 'feature2', 'target']

        with pytest.raises(ValueError, match="Missing required columns"):
            self.validator.validate_schema(df, required_columns)

    def test_validate_data_quality_success(self):
        """Test data quality validation passes with good data."""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': np.random.choice([0, 1], 100)
        })

        results = self.validator.validate_data_quality(df)

        assert results['num_rows'] == 100
        assert results['missing_ratio'] < 0.1
        assert results['duplicate_ratio'] < 0.05

    def test_validate_data_quality_insufficient_rows(self):
        """Test validation fails with insufficient rows."""
        df = pd.DataFrame({
            'feature1': [1, 2, 3],
            'target': [0, 1, 0]
        })

        with pytest.raises(ValueError, match="Insufficient data"):
            self.validator.validate_data_quality(df)

    def test_validate_data_quality_too_many_missing(self):
        """Test validation fails with too many missing values."""
        df = pd.DataFrame({
            'feature1': [1, 2, np.nan] * 10,
            'feature2': [np.nan, 5, 6] * 10,
            'target': [0, 1, 0] * 10
        })

        with pytest.raises(ValueError, match="Too many missing values"):
            self.validator.validate_data_quality(df)

    def test_detect_outliers_iqr(self):
        """Test IQR outlier detection."""
        # Create data with clear outliers
        data = np.concatenate([
            np.random.randn(100),  # Normal data
            [10, 11, -10, -11]     # Outliers
        ])

        df = pd.DataFrame({
            'feature1': data,
            'feature2': np.random.randn(104)
        })

        outliers = self.validator.detect_outliers(df, method='iqr')

        # Should detect some outliers in feature1
        assert outliers['feature1'].sum() > 0

    def test_validate_training_data(self):
        """Test complete training data validation pipeline."""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': np.random.choice([0, 1], 100)
        })

        feature_columns = ['feature1', 'feature2']
        target_column = 'target'

        clean_df = validate_training_data(df, feature_columns, target_column)

        # Should return a DataFrame
        assert isinstance(clean_df, pd.DataFrame)

        # Should have all rows (no missing or duplicates in this case)
        assert len(clean_df) <= len(df)

        # Should have all required columns
        assert all(col in clean_df.columns for col in feature_columns + [target_column])


class TestDataSchema:
    """Test suite for Pydantic data schema."""

    def test_valid_data_schema(self):
        """Test schema accepts valid data."""
        from ml_pipeline.data.validation import DataSchema

        data = {
            "features": {"feature1": 1.0, "feature2": 2.5},
            "target": 1.0
        }

        schema = DataSchema(**data)
        assert schema.features == {"feature1": 1.0, "feature2": 2.5}
        assert schema.target == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
