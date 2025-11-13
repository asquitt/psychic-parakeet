"""
Run Monitoring Pipeline

This script runs the monitoring pipeline to detect data drift and
determine if model retraining is needed.

Usage:
    python scripts/run_monitoring.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ml_pipeline.orchestration.workflows import monitoring_pipeline


def main():
    """Run monitoring pipeline."""
    print("=" * 70)
    print("RUNNING MONITORING PIPELINE")
    print("=" * 70)

    # Configuration
    config = {
        "reference_data_path": "data/raw/train.csv",
        "current_data_path": "data/raw/production.csv",
        "numerical_features": [
            "feature_1", "feature_2", "feature_3", "feature_4", "feature_5"
        ],
        "categorical_features": ["category_a", "category_b"]
    }

    print("\nConfiguration:")
    for key, value in config.items():
        print(f"  {key}: {value}")

    # Check if data exists
    ref_path = Path(config["reference_data_path"])
    curr_path = Path(config["current_data_path"])

    if not ref_path.exists() or not curr_path.exists():
        print(f"\n❌ Error: Data files not found")
        print("Please run: python scripts/generate_sample_data.py")
        sys.exit(1)

    print("\nStarting monitoring pipeline...")

    try:
        # Run pipeline
        results = monitoring_pipeline(
            reference_data_path=config["reference_data_path"],
            current_data_path=config["current_data_path"],
            numerical_features=config["numerical_features"],
            categorical_features=config["categorical_features"]
        )

        print("\n" + "=" * 70)
        print("MONITORING PIPELINE COMPLETE!")
        print("=" * 70)

        print(f"\nDrift Detected: {results['drift_detected']}")

        if results['drift_detected']:
            print(f"Drifted Features: {', '.join(results['drifted_features'])}")

        print(f"Retraining Recommended: {results['should_retrain']}")

        if results['should_retrain']:
            print("\n⚠️  ACTION REQUIRED: Model retraining is recommended!")
            print("Run: python scripts/run_training.py")
        else:
            print("\n✅ Model is performing well, no action needed")

    except Exception as e:
        print(f"\n❌ Error running monitoring pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
