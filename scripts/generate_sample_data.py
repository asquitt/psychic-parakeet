"""
Generate Sample Data for ML Pipeline

This script generates a synthetic dataset for testing the ML pipeline.
The dataset simulates a binary classification problem.

Usage:
    python scripts/generate_sample_data.py
"""

import numpy as np
import pandas as pd
from pathlib import Path


def generate_classification_data(
    n_samples: int = 1000,
    n_features: int = 5,
    n_informative: int = 3,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic classification dataset.

    Args:
        n_samples: Number of samples to generate
        n_features: Number of features
        n_informative: Number of informative features
        random_state: Random seed for reproducibility

    Returns:
        DataFrame with features and target
    """
    np.random.seed(random_state)

    # Generate informative features
    X_informative = np.random.randn(n_samples, n_informative)

    # Generate noise features
    X_noise = np.random.randn(n_samples, n_features - n_informative)

    # Combine features
    X = np.hstack([X_informative, X_noise])

    # Generate target based on linear combination of informative features
    weights = np.random.randn(n_informative)
    linear_combination = X_informative @ weights

    # Add some non-linearity
    target_proba = 1 / (1 + np.exp(-linear_combination))

    # Generate binary target
    y = (target_proba > 0.5).astype(int)

    # Create DataFrame
    feature_names = [f"feature_{i+1}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y

    # Add some categorical features
    df['category_a'] = np.random.choice(['A', 'B', 'C'], size=n_samples)
    df['category_b'] = np.random.choice(['X', 'Y'], size=n_samples)

    # Add timestamp
    df['timestamp'] = pd.date_range(start='2024-01-01', periods=n_samples, freq='H')

    return df


def main():
    """Generate and save sample datasets."""
    print("Generating sample datasets...")

    # Create data directories
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    (data_dir / "raw").mkdir(exist_ok=True)
    (data_dir / "processed").mkdir(exist_ok=True)

    # Generate training data (1000 samples)
    print("Generating training data...")
    train_df = generate_classification_data(
        n_samples=1000,
        n_features=5,
        n_informative=3,
        random_state=42
    )
    train_path = data_dir / "raw" / "train.csv"
    train_df.to_csv(train_path, index=False)
    print(f"✓ Training data saved: {train_path}")
    print(f"  Shape: {train_df.shape}")
    print(f"  Target distribution: {train_df['target'].value_counts().to_dict()}")

    # Generate test data (200 samples)
    print("\nGenerating test data...")
    test_df = generate_classification_data(
        n_samples=200,
        n_features=5,
        n_informative=3,
        random_state=123
    )
    test_path = data_dir / "raw" / "test.csv"
    test_df.to_csv(test_path, index=False)
    print(f"✓ Test data saved: {test_path}")
    print(f"  Shape: {test_df.shape}")

    # Generate production data (with slight drift)
    print("\nGenerating production data (with drift)...")
    np.random.seed(456)
    prod_df = generate_classification_data(
        n_samples=500,
        n_features=5,
        n_informative=3,
        random_state=456
    )
    # Add drift by shifting distribution
    for col in ['feature_1', 'feature_2']:
        prod_df[col] = prod_df[col] + 0.5  # Shift mean

    prod_path = data_dir / "raw" / "production.csv"
    prod_df.to_csv(prod_path, index=False)
    print(f"✓ Production data saved: {prod_path}")
    print(f"  Shape: {prod_df.shape}")
    print(f"  Note: Contains intentional drift for monitoring demonstration")

    print("\n" + "=" * 60)
    print("Sample data generation complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run training pipeline: python scripts/run_training.py")
    print("2. Run monitoring pipeline: python scripts/run_monitoring.py")


if __name__ == "__main__":
    main()
