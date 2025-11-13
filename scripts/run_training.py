"""
Run Training Pipeline

This script runs the complete training pipeline including:
- Data loading and validation
- Feature engineering
- Model training with hyperparameter tuning
- Model evaluation
- Model registration

Usage:
    python scripts/run_training.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ml_pipeline.orchestration.workflows import training_pipeline


def main():
    """Run training pipeline with sample data."""
    print("=" * 70)
    print("RUNNING TRAINING PIPELINE")
    print("=" * 70)

    # Configuration
    config = {
        "data_path": "data/raw/train.csv",
        "feature_columns": [
            "feature_1", "feature_2", "feature_3", "feature_4", "feature_5",
            "category_a", "category_b"
        ],
        "target_column": "target",
        "numerical_features": [
            "feature_1", "feature_2", "feature_3", "feature_4", "feature_5"
        ],
        "categorical_features": ["category_a", "category_b"],
        "model_type": "xgboost",
        "tune_hyperparameters": True
    }

    print("\nConfiguration:")
    for key, value in config.items():
        print(f"  {key}: {value}")

    # Check if data exists
    data_path = Path(config["data_path"])
    if not data_path.exists():
        print(f"\n❌ Error: Data file not found: {data_path}")
        print("Please run: python scripts/generate_sample_data.py")
        sys.exit(1)

    print("\nStarting training pipeline...")

    try:
        # Run pipeline
        results = training_pipeline(
            data_path=config["data_path"],
            feature_columns=config["feature_columns"],
            target_column=config["target_column"],
            numerical_features=config["numerical_features"],
            categorical_features=config["categorical_features"],
            model_type=config["model_type"],
            tune_hyperparameters=config["tune_hyperparameters"]
        )

        print("\n" + "=" * 70)
        print("TRAINING PIPELINE COMPLETE!")
        print("=" * 70)
        print(f"\nModel Version: {results['model_version']}")
        print(f"Model Type: {results['model_type']}")
        print("\nMetrics:")
        for metric, value in results['metrics'].items():
            print(f"  {metric}: {value:.4f}")

        print("\n📊 View results in MLflow: http://localhost:5000")
        print("🚀 Start serving: make serve")

    except Exception as e:
        print(f"\n❌ Error running training pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
