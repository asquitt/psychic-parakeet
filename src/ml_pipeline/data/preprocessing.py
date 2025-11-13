"""
Data Preprocessing

This module handles data transformation and preprocessing:
- Handling missing values
- Encoding categorical variables
- Scaling numerical features
- Train/test splitting with proper validation

Learning Points:
- Preprocessing must be consistent between training and inference
- Use sklearn pipelines for reproducibility
- Fit on training data only, transform on all data
- Save preprocessing artifacts for production use
"""

from typing import List, Tuple, Optional, Dict, Any
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import joblib


class DataPreprocessor:
    """
    Data preprocessing pipeline using sklearn transformers.

    This class creates reusable preprocessing pipelines that can be:
    - Fit on training data
    - Saved to disk
    - Loaded and applied to new data in production

    Key Concepts:
    - ColumnTransformer: Apply different preprocessing to different columns
    - Pipeline: Chain multiple preprocessing steps
    - Fit/Transform: Learn parameters from training, apply to all data
    """

    def __init__(
        self,
        numerical_features: List[str],
        categorical_features: List[str],
        scaling_method: str = "standard",
        handle_missing: str = "mean",
    ):
        """
        Initialize preprocessing pipeline.

        Args:
            numerical_features: List of numerical column names
            categorical_features: List of categorical column names
            scaling_method: 'standard', 'robust', or 'minmax'
            handle_missing: How to handle missing values: 'mean', 'median', 'most_frequent'
        """
        self.numerical_features = numerical_features
        self.categorical_features = categorical_features
        self.scaling_method = scaling_method
        self.handle_missing = handle_missing
        self.preprocessor: Optional[ColumnTransformer] = None
        self._is_fitted = False

    def build_pipeline(self) -> ColumnTransformer:
        """
        Build the preprocessing pipeline.

        Pipeline Structure:
        1. Numerical Features:
           - Impute missing values
           - Scale values (standardization/normalization)

        2. Categorical Features:
           - Impute missing values with most frequent
           - One-hot encode

        Returns:
            ColumnTransformer with separate pipelines for different feature types
        """
        # Numerical pipeline
        numerical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy=self.handle_missing)),
                ("scaler", self._get_scaler()),
            ]
        )

        # Categorical pipeline
        categorical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                (
                    "onehot",
                    OneHotEncoder(
                        drop="if_binary",  # Drop one category for binary features
                        sparse_output=False,  # Return dense array
                        handle_unknown="ignore",  # Ignore unknown categories at inference
                    ),
                ),
            ]
        )

        # Combine pipelines
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numerical_pipeline, self.numerical_features),
                ("cat", categorical_pipeline, self.categorical_features),
            ],
            remainder="drop",  # Drop columns not specified
        )

        return preprocessor

    def _get_scaler(self):
        """
        Get the appropriate scaler based on scaling_method.

        Scaler Comparison:
        - StandardScaler: Mean=0, Std=1 (assumes normal distribution)
        - RobustScaler: Uses median and IQR (robust to outliers)
        - MinMaxScaler: Scales to [0, 1] range

        Returns:
            Scaler instance
        """
        if self.scaling_method == "standard":
            return StandardScaler()
        elif self.scaling_method == "robust":
            return RobustScaler()
        elif self.scaling_method == "minmax":
            return MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling method: {self.scaling_method}")

    def fit(self, X: pd.DataFrame) -> "DataPreprocessor":
        """
        Fit the preprocessing pipeline on training data.

        Important: Only call this on training data!
        The pipeline learns statistics (mean, std, categories) from this data.

        Args:
            X: Training data DataFrame

        Returns:
            self (for method chaining)
        """
        self.preprocessor = self.build_pipeline()
        self.preprocessor.fit(X)
        self._is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transform data using fitted preprocessing pipeline.

        Args:
            X: Data to transform

        Returns:
            Transformed numpy array

        Raises:
            ValueError: If pipeline hasn't been fitted
        """
        if not self._is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")

        return self.preprocessor.transform(X)

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Fit and transform in one step (for training data only).

        Args:
            X: Training data DataFrame

        Returns:
            Transformed numpy array
        """
        return self.fit(X).transform(X)

    def get_feature_names(self) -> List[str]:
        """
        Get feature names after transformation.

        This is useful for interpretability and debugging.

        Returns:
            List of feature names after one-hot encoding
        """
        if not self._is_fitted:
            raise ValueError("Preprocessor must be fitted first")

        feature_names = []

        # Get numerical feature names
        feature_names.extend(self.numerical_features)

        # Get categorical feature names (after one-hot encoding)
        if self.categorical_features:
            cat_pipeline = self.preprocessor.named_transformers_["cat"]
            encoder = cat_pipeline.named_steps["onehot"]
            cat_names = encoder.get_feature_names_out(self.categorical_features)
            feature_names.extend(cat_names)

        return feature_names

    def save(self, filepath: str) -> None:
        """
        Save fitted preprocessor to disk.

        This is crucial for production deployment - we need to apply
        the exact same preprocessing to new data.

        Args:
            filepath: Path to save the preprocessor
        """
        if not self._is_fitted:
            raise ValueError("Cannot save unfitted preprocessor")

        joblib.dump(
            {
                "preprocessor": self.preprocessor,
                "numerical_features": self.numerical_features,
                "categorical_features": self.categorical_features,
                "scaling_method": self.scaling_method,
                "handle_missing": self.handle_missing,
            },
            filepath,
        )

    @classmethod
    def load(cls, filepath: str) -> "DataPreprocessor":
        """
        Load a saved preprocessor from disk.

        Args:
            filepath: Path to saved preprocessor

        Returns:
            Loaded DataPreprocessor instance
        """
        data = joblib.load(filepath)

        instance = cls(
            numerical_features=data["numerical_features"],
            categorical_features=data["categorical_features"],
            scaling_method=data["scaling_method"],
            handle_missing=data["handle_missing"],
        )
        instance.preprocessor = data["preprocessor"]
        instance._is_fitted = True

        return instance


def prepare_train_test_split(
    df: pd.DataFrame,
    feature_columns: List[str],
    target_column: str,
    test_size: float = 0.2,
    random_state: int = 42,
    stratify: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split data into training and testing sets.

    Best Practices:
    - Use stratified split for classification to maintain class balance
    - Set random_state for reproducibility
    - Typical split: 80% train, 20% test
    - For time series, use time-based split instead

    Args:
        df: Full dataset
        feature_columns: Feature column names
        target_column: Target column name
        test_size: Proportion of data for testing (0.0-1.0)
        random_state: Random seed for reproducibility
        stratify: Whether to stratify split (for classification)

    Returns:
        Tuple of (X_train, X_test, y_train, y_test)

    Example:
        >>> X_train, X_test, y_train, y_test = prepare_train_test_split(
        ...     df=data,
        ...     feature_columns=['age', 'income'],
        ...     target_column='purchased',
        ...     test_size=0.2,
        ...     stratify=True
        ... )
    """
    X = df[feature_columns]
    y = df[target_column]

    stratify_array = y if stratify else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify_array
    )

    return X_train, X_test, y_train, y_test


def create_preprocessing_pipeline(
    X_train: pd.DataFrame,
    numerical_features: List[str],
    categorical_features: List[str],
    scaling_method: str = "standard",
) -> DataPreprocessor:
    """
    Create and fit a preprocessing pipeline.

    This is a convenience function that creates a preprocessor,
    fits it on training data, and returns it ready to use.

    Args:
        X_train: Training features
        numerical_features: List of numerical column names
        categorical_features: List of categorical column names
        scaling_method: Scaling method to use

    Returns:
        Fitted DataPreprocessor

    Example:
        >>> preprocessor = create_preprocessing_pipeline(
        ...     X_train,
        ...     numerical_features=['age', 'income'],
        ...     categorical_features=['gender', 'city'],
        ...     scaling_method='standard'
        ... )
        >>> X_train_scaled = preprocessor.transform(X_train)
        >>> X_test_scaled = preprocessor.transform(X_test)
    """
    preprocessor = DataPreprocessor(
        numerical_features=numerical_features,
        categorical_features=categorical_features,
        scaling_method=scaling_method,
    )

    preprocessor.fit(X_train)

    return preprocessor
