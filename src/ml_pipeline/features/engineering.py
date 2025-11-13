"""
Feature Engineering

This module provides tools for creating and transforming features to improve
model performance.

Feature Engineering Techniques:
1. Mathematical transformations (log, sqrt, power)
2. Feature interactions (products, ratios)
3. Polynomial features
4. Time-based features
5. Domain-specific features

Learning Points:
- Good features > complex models
- Feature engineering requires domain knowledge
- Always validate new features improve model performance
- Version your features for reproducibility
"""

from typing import List, Dict, Any, Callable, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
import joblib


class FeatureEngineer:
    """
    Feature engineering pipeline for creating and transforming features.

    This class provides:
    - Automated feature creation
    - Feature interaction generation
    - Feature transformation functions
    - Feature versioning and tracking
    """

    def __init__(self):
        """Initialize feature engineer."""
        self.feature_transformations: Dict[str, Callable] = {}
        self.polynomial_features: Optional[PolynomialFeatures] = None
        self.feature_selector: Optional[SelectKBest] = None

    def add_mathematical_features(
        self, df: pd.DataFrame, columns: List[str]
    ) -> pd.DataFrame:
        """
        Add mathematical transformations of existing features.

        Common transformations:
        - Log: Useful for skewed distributions
        - Square root: Reduces impact of outliers
        - Square: Captures non-linear relationships
        - Reciprocal: Useful for rate-like features

        Args:
            df: Input DataFrame
            columns: Columns to transform

        Returns:
            DataFrame with added transformation columns

        Example:
            >>> df = engineer.add_mathematical_features(
            ...     df,
            ...     columns=['income', 'age']
            ... )
            # Adds: income_log, income_sqrt, income_squared
            #       age_log, age_sqrt, age_squared
        """
        df = df.copy()

        for col in columns:
            # Log transformation (add 1 to handle zeros)
            df[f"{col}_log"] = np.log1p(df[col])

            # Square root (only for non-negative values)
            if (df[col] >= 0).all():
                df[f"{col}_sqrt"] = np.sqrt(df[col])

            # Squared
            df[f"{col}_squared"] = df[col] ** 2

            # Reciprocal (avoid division by zero)
            df[f"{col}_reciprocal"] = 1 / (df[col] + 1e-8)

        return df

    def add_interaction_features(
        self, df: pd.DataFrame, column_pairs: List[tuple]
    ) -> pd.DataFrame:
        """
        Create interaction features between column pairs.

        Interaction Features capture relationships between variables:
        - Product: x1 * x2 (multiplicative effect)
        - Sum: x1 + x2 (additive effect)
        - Difference: x1 - x2 (relative difference)
        - Ratio: x1 / x2 (relative magnitude)

        Args:
            df: Input DataFrame
            column_pairs: List of (col1, col2) tuples to interact

        Returns:
            DataFrame with added interaction columns

        Example:
            >>> df = engineer.add_interaction_features(
            ...     df,
            ...     column_pairs=[('age', 'income'), ('hours', 'wage')]
            ... )
            # Adds: age_x_income_product, age_x_income_sum, etc.
        """
        df = df.copy()

        for col1, col2 in column_pairs:
            # Product
            df[f"{col1}_x_{col2}_product"] = df[col1] * df[col2]

            # Sum
            df[f"{col1}_x_{col2}_sum"] = df[col1] + df[col2]

            # Difference
            df[f"{col1}_x_{col2}_diff"] = df[col1] - df[col2]

            # Ratio (avoid division by zero)
            df[f"{col1}_x_{col2}_ratio"] = df[col1] / (df[col2] + 1e-8)

        return df

    def add_polynomial_features(
        self, df: pd.DataFrame, columns: List[str], degree: int = 2
    ) -> pd.DataFrame:
        """
        Add polynomial features up to specified degree.

        Polynomial features capture non-linear relationships:
        - Degree 2: x1, x2, x1^2, x2^2, x1*x2
        - Degree 3: Above + x1^3, x2^3, x1^2*x2, x1*x2^2

        Warning: Polynomial features grow exponentially with degree!
        - n features, degree 2: n*(n+3)/2 features
        - n features, degree 3: n*(n+1)*(n+2)/6 features

        Args:
            df: Input DataFrame
            columns: Columns to create polynomials from
            degree: Polynomial degree (typically 2 or 3)

        Returns:
            DataFrame with polynomial features

        Example:
            >>> df = engineer.add_polynomial_features(
            ...     df,
            ...     columns=['age', 'income'],
            ...     degree=2
            ... )
        """
        df = df.copy()

        # Create polynomial features
        self.polynomial_features = PolynomialFeatures(
            degree=degree, include_bias=False
        )

        # Select only specified columns
        X_poly = self.polynomial_features.fit_transform(df[columns])

        # Get feature names
        feature_names = self.polynomial_features.get_feature_names_out(columns)

        # Add to DataFrame (skip original features as they already exist)
        for i, name in enumerate(feature_names):
            if name not in columns:  # Skip original features
                df[f"poly_{name}"] = X_poly[:, i]

        return df

    def add_statistical_features(
        self, df: pd.DataFrame, columns: List[str], windows: List[int] = [3, 7, 30]
    ) -> pd.DataFrame:
        """
        Add rolling statistical features (useful for time series).

        Statistical Features:
        - Rolling mean: Trend indicator
        - Rolling std: Volatility indicator
        - Rolling min/max: Range indicators

        Args:
            df: Input DataFrame (should be time-ordered)
            columns: Columns to compute statistics on
            windows: Window sizes for rolling statistics

        Returns:
            DataFrame with statistical features

        Example:
            >>> df = engineer.add_statistical_features(
            ...     df,
            ...     columns=['sales'],
            ...     windows=[7, 30]
            ... )
            # Adds: sales_rolling_mean_7, sales_rolling_std_7, etc.
        """
        df = df.copy()

        for col in columns:
            for window in windows:
                # Rolling mean
                df[f"{col}_rolling_mean_{window}"] = (
                    df[col].rolling(window=window).mean()
                )

                # Rolling standard deviation
                df[f"{col}_rolling_std_{window}"] = (
                    df[col].rolling(window=window).std()
                )

                # Rolling min
                df[f"{col}_rolling_min_{window}"] = (
                    df[col].rolling(window=window).min()
                )

                # Rolling max
                df[f"{col}_rolling_max_{window}"] = (
                    df[col].rolling(window=window).max()
                )

        return df

    def select_features(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        k: int = 10,
        method: str = "f_classif",
    ) -> List[str]:
        """
        Select top-k features using statistical tests.

        Feature Selection Methods:
        - f_classif: ANOVA F-value (classification)
        - mutual_info_classif: Mutual information (non-linear)
        - chi2: Chi-squared test (non-negative features only)

        Why Feature Selection?
        - Reduces overfitting
        - Improves interpretability
        - Reduces training time
        - Removes noisy features

        Args:
            X: Feature DataFrame
            y: Target variable
            k: Number of top features to select
            method: Selection method

        Returns:
            List of selected feature names

        Example:
            >>> selected_features = engineer.select_features(
            ...     X_train,
            ...     y_train,
            ...     k=10,
            ...     method='mutual_info_classif'
            ... )
        """
        # Choose scoring function
        if method == "f_classif":
            score_func = f_classif
        elif method == "mutual_info_classif":
            score_func = mutual_info_classif
        else:
            raise ValueError(f"Unknown method: {method}")

        # Select top k features
        self.feature_selector = SelectKBest(score_func=score_func, k=k)
        self.feature_selector.fit(X, y)

        # Get selected feature names
        selected_mask = self.feature_selector.get_support()
        selected_features = X.columns[selected_mask].tolist()

        # Get feature scores
        scores = self.feature_selector.scores_
        feature_scores = pd.DataFrame(
            {"feature": X.columns, "score": scores}
        ).sort_values("score", ascending=False)

        print(f"Top {k} features selected:")
        print(feature_scores.head(k))

        return selected_features

    def create_feature_set(
        self,
        df: pd.DataFrame,
        numerical_columns: List[str],
        categorical_columns: List[str] = None,
        add_interactions: bool = True,
        add_polynomials: bool = False,
        polynomial_degree: int = 2,
    ) -> pd.DataFrame:
        """
        Create a comprehensive feature set with multiple engineering techniques.

        This is a convenience method that applies multiple feature engineering
        techniques in sequence.

        Args:
            df: Input DataFrame
            numerical_columns: Numerical columns to engineer features from
            categorical_columns: Categorical columns (for interactions)
            add_interactions: Whether to add interaction features
            add_polynomials: Whether to add polynomial features
            polynomial_degree: Degree for polynomial features

        Returns:
            DataFrame with engineered features

        Example:
            >>> df_engineered = engineer.create_feature_set(
            ...     df,
            ...     numerical_columns=['age', 'income'],
            ...     add_interactions=True,
            ...     add_polynomials=True
            ... )
        """
        df_features = df.copy()

        # Add mathematical transformations
        print("Adding mathematical features...")
        df_features = self.add_mathematical_features(df_features, numerical_columns)

        # Add interaction features
        if add_interactions and len(numerical_columns) >= 2:
            print("Adding interaction features...")
            # Create pairs of numerical columns
            column_pairs = [
                (numerical_columns[i], numerical_columns[j])
                for i in range(len(numerical_columns))
                for j in range(i + 1, len(numerical_columns))
            ]
            df_features = self.add_interaction_features(df_features, column_pairs[:5])  # Limit to avoid explosion

        # Add polynomial features
        if add_polynomials:
            print(f"Adding polynomial features (degree={polynomial_degree})...")
            df_features = self.add_polynomial_features(
                df_features, numerical_columns, degree=polynomial_degree
            )

        print(f"Feature engineering complete: {len(df.columns)} -> {len(df_features.columns)} features")

        return df_features

    def save(self, filepath: str) -> None:
        """Save feature engineer to disk."""
        joblib.dump(
            {
                "polynomial_features": self.polynomial_features,
                "feature_selector": self.feature_selector,
            },
            filepath,
        )

    @classmethod
    def load(cls, filepath: str) -> "FeatureEngineer":
        """Load feature engineer from disk."""
        data = joblib.load(filepath)
        instance = cls()
        instance.polynomial_features = data["polynomial_features"]
        instance.feature_selector = data["feature_selector"]
        return instance
