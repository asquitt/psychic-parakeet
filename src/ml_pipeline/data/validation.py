"""
Data Validation

This module provides data validation using multiple approaches:
1. Pydantic: Schema validation and type checking
2. Custom validators: Business logic validation
3. Statistical checks: Outlier detection, distribution checks

Learning Points:
- Data validation prevents garbage in/garbage out
- Early validation catches issues before expensive training
- Schema evolution requires versioned validators
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field, validator
from evidently.test_suite import TestSuite
from evidently.tests import (
    TestNumberOfColumnsWithMissingValues,
    TestNumberOfRowsWithMissingValues,
    TestNumberOfConstantColumns,
    TestNumberOfDuplicatedRows,
)


class DataSchema(BaseModel):
    """
    Pydantic schema for input data validation.

    This schema ensures each data point has:
    - Required fields present
    - Correct data types
    - Values within expected ranges
    """

    id: Optional[str] = Field(None, description="Unique identifier")
    timestamp: Optional[datetime] = Field(None, description="Record timestamp")
    features: Dict[str, float] = Field(..., description="Feature dictionary")
    target: Optional[float] = Field(None, description="Target variable")

    @validator("features")
    def validate_features(cls, v):
        """Ensure all feature values are valid numbers."""
        for key, value in v.items():
            if not isinstance(value, (int, float)) or np.isnan(value):
                raise ValueError(f"Feature {key} has invalid value: {value}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sample_001",
                "timestamp": "2024-01-01T00:00:00",
                "features": {"feature1": 1.0, "feature2": 2.5},
                "target": 1.0,
            }
        }


class DataValidator:
    """
    Comprehensive data validator using multiple validation strategies.

    Validation Levels:
    1. Schema Validation: Type and structure checks
    2. Statistical Validation: Distribution and outlier checks
    3. Business Logic Validation: Domain-specific rules
    """

    def __init__(
        self,
        min_rows: int = 100,
        max_missing_ratio: float = 0.1,
        max_constant_columns: int = 0,
        max_duplicate_ratio: float = 0.05,
    ):
        """
        Initialize validator with quality thresholds.

        Args:
            min_rows: Minimum number of rows required
            max_missing_ratio: Maximum ratio of missing values allowed
            max_constant_columns: Maximum number of constant columns allowed
            max_duplicate_ratio: Maximum ratio of duplicate rows allowed
        """
        self.min_rows = min_rows
        self.max_missing_ratio = max_missing_ratio
        self.max_constant_columns = max_constant_columns
        self.max_duplicate_ratio = max_duplicate_ratio

    def validate_schema(self, df: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        Validate DataFrame schema.

        Args:
            df: Input DataFrame
            required_columns: List of required column names

        Returns:
            bool: True if schema is valid

        Raises:
            ValueError: If schema validation fails
        """
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        return True

    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data quality using statistical checks.

        This method checks for:
        - Sufficient data volume
        - Missing values within acceptable limits
        - No constant columns (zero variance)
        - Low duplicate rate

        Args:
            df: Input DataFrame

        Returns:
            Dict containing validation results and metrics

        Raises:
            ValueError: If data quality checks fail
        """
        results = {
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "missing_ratio": df.isnull().sum().sum() / (len(df) * len(df.columns)),
            "duplicate_ratio": df.duplicated().sum() / len(df),
            "constant_columns": [],
        }

        # Check minimum rows
        if results["num_rows"] < self.min_rows:
            raise ValueError(
                f"Insufficient data: {results['num_rows']} rows "
                f"(minimum: {self.min_rows})"
            )

        # Check missing values
        if results["missing_ratio"] > self.max_missing_ratio:
            raise ValueError(
                f"Too many missing values: {results['missing_ratio']:.2%} "
                f"(maximum: {self.max_missing_ratio:.2%})"
            )

        # Check for constant columns
        for col in df.columns:
            if df[col].nunique() == 1:
                results["constant_columns"].append(col)

        if len(results["constant_columns"]) > self.max_constant_columns:
            raise ValueError(
                f"Too many constant columns: {results['constant_columns']}"
            )

        # Check duplicates
        if results["duplicate_ratio"] > self.max_duplicate_ratio:
            raise ValueError(
                f"Too many duplicates: {results['duplicate_ratio']:.2%} "
                f"(maximum: {self.max_duplicate_ratio:.2%})"
            )

        return results

    def detect_outliers(
        self, df: pd.DataFrame, method: str = "iqr", threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        Detect outliers using statistical methods.

        Methods:
        - IQR (Interquartile Range): Q1 - 1.5*IQR, Q3 + 1.5*IQR
        - Z-score: |z| > threshold
        - Isolation Forest: Anomaly detection algorithm

        Args:
            df: Input DataFrame
            method: Outlier detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection

        Returns:
            DataFrame with boolean mask of outliers
        """
        outliers = pd.DataFrame(False, index=df.index, columns=df.columns)

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outliers[col] = (df[col] < lower_bound) | (df[col] > upper_bound)

            elif method == "zscore":
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outliers[col] = z_scores > threshold

        return outliers

    def run_evidently_tests(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run Evidently data quality tests.

        Evidently provides automated data quality checks:
        - Missing values analysis
        - Constant columns detection
        - Duplicate rows detection
        - Distribution checks

        Args:
            df: Input DataFrame

        Returns:
            Dict containing test results
        """
        # Create test suite
        tests = TestSuite(
            tests=[
                TestNumberOfColumnsWithMissingValues(),
                TestNumberOfRowsWithMissingValues(),
                TestNumberOfConstantColumns(),
                TestNumberOfDuplicatedRows(),
            ]
        )

        # Run tests
        tests.run(reference_data=None, current_data=df)

        # Extract results
        results = {
            "passed": tests.as_dict()["summary"]["all_passed"],
            "tests": tests.as_dict()["tests"],
        }

        return results


def validate_training_data(
    df: pd.DataFrame, feature_columns: List[str], target_column: str
) -> pd.DataFrame:
    """
    Validate and clean training data.

    This is a convenience function that runs all validation checks
    and returns cleaned data ready for training.

    Args:
        df: Raw DataFrame
        feature_columns: List of feature column names
        target_column: Target column name

    Returns:
        Validated and cleaned DataFrame

    Example:
        >>> df = pd.read_csv('data.csv')
        >>> clean_df = validate_training_data(
        ...     df,
        ...     feature_columns=['age', 'income'],
        ...     target_column='purchased'
        ... )
    """
    validator = DataValidator()

    # Schema validation
    required_columns = feature_columns + [target_column]
    validator.validate_schema(df, required_columns)

    # Data quality validation
    quality_results = validator.validate_data_quality(df)
    print(f"Data quality check passed: {quality_results}")

    # Remove rows with missing values
    df_clean = df.dropna(subset=required_columns)

    # Remove duplicates
    df_clean = df_clean.drop_duplicates()

    # Detect and flag outliers (but don't remove them yet)
    outliers = validator.detect_outliers(df_clean[feature_columns])
    print(f"Outliers detected: {outliers.sum().sum()} values")

    return df_clean
