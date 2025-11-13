"""
Data Drift Detection

Data drift occurs when the statistical properties of input data change over time,
which can degrade model performance.

Types of Drift:
1. Covariate Drift: P(X) changes (input distribution)
2. Concept Drift: P(Y|X) changes (relationship between input and output)
3. Label Drift: P(Y) changes (target distribution)

Detection Methods:
- Kolmogorov-Smirnov test: Distribution comparison
- Population Stability Index (PSI): Feature distribution shift
- Jensen-Shannon Divergence: Distribution similarity

Learning Points:
- Monitor drift continuously in production
- Retrain models when significant drift detected
- Some drift is normal, need thresholds
- Different features may drift at different rates
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from datetime import datetime


class DriftDetector:
    """
    Data drift detection using statistical tests.

    This class provides:
    - Kolmogorov-Smirnov test for continuous features
    - Chi-squared test for categorical features
    - Population Stability Index (PSI)
    - Integration with Evidently AI
    """

    def __init__(self, threshold: float = 0.05):
        """
        Initialize drift detector.

        Args:
            threshold: P-value threshold for statistical tests
                      (lower = more sensitive to drift)
        """
        self.threshold = threshold
        self.reference_data: Optional[pd.DataFrame] = None
        self.drift_history: List[Dict[str, Any]] = []

    def set_reference_data(self, reference_df: pd.DataFrame) -> None:
        """
        Set reference data for drift comparison.

        Reference data should be:
        - Training data or
        - Recent production data when model was performing well

        Args:
            reference_df: Reference DataFrame
        """
        self.reference_data = reference_df.copy()
        print(f"✓ Reference data set: {len(reference_df)} samples, {len(reference_df.columns)} features")

    def detect_numerical_drift(
        self,
        reference: np.ndarray,
        current: np.ndarray,
        feature_name: str
    ) -> Dict[str, Any]:
        """
        Detect drift in numerical feature using KS test.

        Kolmogorov-Smirnov Test:
        - Compares cumulative distributions
        - Non-parametric (no distribution assumption)
        - Returns p-value: low p-value = significant drift

        Args:
            reference: Reference feature values
            current: Current feature values
            feature_name: Name of feature

        Returns:
            Dictionary with drift detection results
        """
        # Kolmogorov-Smirnov test
        statistic, p_value = stats.ks_2samp(reference, current)

        is_drift = p_value < self.threshold

        result = {
            "feature": feature_name,
            "type": "numerical",
            "statistic": statistic,
            "p_value": p_value,
            "drift_detected": is_drift,
            "threshold": self.threshold,
            "method": "kolmogorov_smirnov"
        }

        return result

    def calculate_psi(
        self,
        reference: np.ndarray,
        current: np.ndarray,
        buckets: int = 10
    ) -> float:
        """
        Calculate Population Stability Index (PSI).

        PSI Formula:
        PSI = Σ (current% - reference%) * ln(current% / reference%)

        PSI Interpretation:
        - < 0.1: No significant change
        - 0.1 - 0.25: Moderate change, investigate
        - > 0.25: Significant change, retrain model

        Args:
            reference: Reference feature values
            current: Current feature values
            buckets: Number of buckets for binning

        Returns:
            PSI score
        """
        # Create bins based on reference data
        breakpoints = np.quantile(reference, np.linspace(0, 1, buckets + 1))
        breakpoints = np.unique(breakpoints)  # Remove duplicates

        if len(breakpoints) <= 1:
            return 0.0  # Cannot calculate PSI with single value

        # Calculate distributions
        ref_dist, _ = np.histogram(reference, bins=breakpoints)
        curr_dist, _ = np.histogram(current, bins=breakpoints)

        # Convert to percentages (add small epsilon to avoid division by zero)
        epsilon = 1e-10
        ref_pct = (ref_dist + epsilon) / (len(reference) + epsilon * len(breakpoints))
        curr_pct = (curr_dist + epsilon) / (len(current) + epsilon * len(breakpoints))

        # Calculate PSI
        psi = np.sum((curr_pct - ref_pct) * np.log(curr_pct / ref_pct))

        return psi

    def detect_categorical_drift(
        self,
        reference: np.ndarray,
        current: np.ndarray,
        feature_name: str
    ) -> Dict[str, Any]:
        """
        Detect drift in categorical feature using chi-squared test.

        Chi-Squared Test:
        - Compares category distributions
        - Tests if distributions are independent
        - Returns p-value: low p-value = significant drift

        Args:
            reference: Reference feature values
            current: Current feature values
            feature_name: Name of feature

        Returns:
            Dictionary with drift detection results
        """
        # Get unique categories from both datasets
        categories = np.unique(np.concatenate([reference, current]))

        # Create contingency table
        ref_counts = pd.Series(reference).value_counts()
        curr_counts = pd.Series(current).value_counts()

        # Ensure all categories present in both
        contingency = pd.DataFrame({
            "reference": [ref_counts.get(cat, 0) for cat in categories],
            "current": [curr_counts.get(cat, 0) for cat in categories]
        })

        # Chi-squared test
        statistic, p_value, dof, expected = stats.chi2_contingency(contingency.T)

        is_drift = p_value < self.threshold

        result = {
            "feature": feature_name,
            "type": "categorical",
            "statistic": statistic,
            "p_value": p_value,
            "drift_detected": is_drift,
            "threshold": self.threshold,
            "method": "chi_squared"
        }

        return result

    def detect_drift(
        self,
        current_df: pd.DataFrame,
        numerical_features: List[str],
        categorical_features: List[str] = None
    ) -> Dict[str, Any]:
        """
        Detect drift across all features.

        Args:
            current_df: Current data to check for drift
            numerical_features: List of numerical feature names
            categorical_features: List of categorical feature names

        Returns:
            Dictionary with drift detection results for all features

        Example:
            >>> detector = DriftDetector(threshold=0.05)
            >>> detector.set_reference_data(train_df)
            >>> results = detector.detect_drift(
            ...     production_df,
            ...     numerical_features=['age', 'income'],
            ...     categorical_features=['gender', 'city']
            ... )
            >>> print(f"Drift detected: {results['drift_detected']}")
        """
        if self.reference_data is None:
            raise ValueError("Reference data not set. Call set_reference_data() first.")

        results = {
            "timestamp": datetime.now(),
            "total_features": len(numerical_features) + len(categorical_features or []),
            "features": [],
            "drift_detected": False,
            "drifted_features": []
        }

        # Check numerical features
        for feature in numerical_features:
            if feature not in self.reference_data.columns or feature not in current_df.columns:
                print(f"Warning: Feature {feature} not found in data")
                continue

            drift_result = self.detect_numerical_drift(
                self.reference_data[feature].values,
                current_df[feature].values,
                feature
            )

            # Calculate PSI
            psi = self.calculate_psi(
                self.reference_data[feature].values,
                current_df[feature].values
            )
            drift_result["psi"] = psi

            results["features"].append(drift_result)

            if drift_result["drift_detected"]:
                results["drift_detected"] = True
                results["drifted_features"].append(feature)

        # Check categorical features
        if categorical_features:
            for feature in categorical_features:
                if feature not in self.reference_data.columns or feature not in current_df.columns:
                    continue

                drift_result = self.detect_categorical_drift(
                    self.reference_data[feature].values,
                    current_df[feature].values,
                    feature
                )

                results["features"].append(drift_result)

                if drift_result["drift_detected"]:
                    results["drift_detected"] = True
                    results["drifted_features"].append(feature)

        # Store in history
        self.drift_history.append(results)

        # Print summary
        print("\n" + "=" * 50)
        print("DRIFT DETECTION RESULTS")
        print("=" * 50)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Total features checked: {results['total_features']}")
        print(f"Drift detected: {results['drift_detected']}")
        if results['drifted_features']:
            print(f"Drifted features: {', '.join(results['drifted_features'])}")
        print()

        # Print details for drifted features
        for feature_result in results["features"]:
            if feature_result["drift_detected"]:
                print(f"  {feature_result['feature']}:")
                print(f"    Method: {feature_result['method']}")
                print(f"    P-value: {feature_result['p_value']:.6f}")
                if "psi" in feature_result:
                    print(f"    PSI: {feature_result['psi']:.4f}")

        return results

    def generate_evidently_report(
        self,
        reference_df: pd.DataFrame,
        current_df: pd.DataFrame,
        output_path: str = "drift_report.html"
    ) -> None:
        """
        Generate comprehensive drift report using Evidently.

        Evidently provides:
        - Visual drift reports
        - Statistical tests
        - Distribution comparisons
        - Interactive HTML output

        Args:
            reference_df: Reference dataset
            current_df: Current dataset
            output_path: Path to save HTML report

        Example:
            >>> detector.generate_evidently_report(
            ...     train_df,
            ...     production_df,
            ...     "drift_report.html"
            ... )
        """
        # Create report
        report = Report(metrics=[
            DataDriftPreset(),
            DataQualityPreset(),
        ])

        # Run report
        report.run(reference_data=reference_df, current_data=current_df)

        # Save report
        report.save_html(output_path)
        print(f"✓ Drift report saved: {output_path}")

    def should_retrain(
        self,
        drift_results: Dict[str, Any],
        max_drifted_features: int = 3,
        max_psi: float = 0.25
    ) -> bool:
        """
        Determine if model should be retrained based on drift.

        Retrain Criteria:
        - Too many features have drifted
        - PSI exceeds threshold for critical features
        - Consistent drift over time

        Args:
            drift_results: Results from detect_drift()
            max_drifted_features: Maximum drifted features before retrain
            max_psi: Maximum PSI before retrain

        Returns:
            True if model should be retrained
        """
        # Check number of drifted features
        if len(drift_results["drifted_features"]) >= max_drifted_features:
            print(f"⚠️  Retrain recommended: {len(drift_results['drifted_features'])} features drifted")
            return True

        # Check PSI values
        for feature_result in drift_results["features"]:
            if "psi" in feature_result and feature_result["psi"] > max_psi:
                print(f"⚠️  Retrain recommended: PSI {feature_result['psi']:.4f} > {max_psi} for {feature_result['feature']}")
                return True

        return False
