"""
Performance Monitoring

Monitor model performance metrics in production:
- Latency tracking
- Throughput measurement
- Error rate monitoring
- Resource utilization
- Model quality metrics

Learning Points:
- Production metrics differ from training metrics
- Latency SLAs are critical for user experience
- Monitor both technical and business metrics
- Set up alerts for degradation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
import time
import numpy as np
from prometheus_client import Histogram, Counter, Gauge, Summary


class PerformanceMonitor:
    """
    Real-time performance monitoring for ML models.

    Tracks:
    - Prediction latency (response time)
    - Throughput (requests per second)
    - Error rate
    - Model performance metrics
    - Resource usage
    """

    def __init__(
        self,
        window_size: int = 1000,
        latency_threshold_ms: float = 100,
        error_rate_threshold: float = 0.01,
    ):
        """
        Initialize performance monitor.

        Args:
            window_size: Size of sliding window for metrics
            latency_threshold_ms: Latency threshold in milliseconds
            error_rate_threshold: Error rate threshold (0.01 = 1%)
        """
        self.window_size = window_size
        self.latency_threshold_ms = latency_threshold_ms
        self.error_rate_threshold = error_rate_threshold

        # Sliding windows for metrics
        self.latencies = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
        self.errors = deque(maxlen=window_size)
        self.predictions = deque(maxlen=window_size)

        # Prometheus metrics
        self.latency_histogram = Histogram(
            'prediction_latency_seconds',
            'Prediction latency in seconds',
            buckets=[.001, .005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0]
        )

        self.error_counter = Counter(
            'prediction_errors_total',
            'Total number of prediction errors'
        )

        self.throughput_gauge = Gauge(
            'prediction_throughput_rps',
            'Current prediction throughput (requests per second)'
        )

    def record_prediction(
        self,
        latency_ms: float,
        prediction: Any,
        error: bool = False
    ) -> None:
        """
        Record a prediction and its metrics.

        Args:
            latency_ms: Prediction latency in milliseconds
            prediction: Model prediction value
            error: Whether prediction resulted in error
        """
        timestamp = datetime.now()

        # Record in sliding windows
        self.latencies.append(latency_ms)
        self.timestamps.append(timestamp)
        self.errors.append(1 if error else 0)
        self.predictions.append(prediction)

        # Update Prometheus metrics
        self.latency_histogram.observe(latency_ms / 1000)  # Convert to seconds
        if error:
            self.error_counter.inc()

        # Update throughput
        self._update_throughput()

    def _update_throughput(self) -> None:
        """Calculate and update current throughput."""
        if len(self.timestamps) < 2:
            return

        # Calculate requests in last second
        now = datetime.now()
        one_second_ago = now - timedelta(seconds=1)

        recent_requests = sum(
            1 for ts in self.timestamps
            if ts >= one_second_ago
        )

        self.throughput_gauge.set(recent_requests)

    def get_current_metrics(self) -> Dict[str, float]:
        """
        Get current performance metrics.

        Returns:
            Dictionary with current metrics

        Metrics:
        - avg_latency_ms: Average latency in milliseconds
        - p50_latency_ms: Median latency
        - p95_latency_ms: 95th percentile latency (SLA metric)
        - p99_latency_ms: 99th percentile latency
        - error_rate: Percentage of requests with errors
        - throughput_rps: Requests per second
        """
        if not self.latencies:
            return {}

        latencies_array = np.array(self.latencies)

        metrics = {
            "avg_latency_ms": np.mean(latencies_array),
            "p50_latency_ms": np.percentile(latencies_array, 50),
            "p95_latency_ms": np.percentile(latencies_array, 95),
            "p99_latency_ms": np.percentile(latencies_array, 99),
            "max_latency_ms": np.max(latencies_array),
            "min_latency_ms": np.min(latencies_array),
            "error_rate": np.mean(self.errors),
            "total_requests": len(self.latencies),
        }

        # Calculate throughput
        if len(self.timestamps) >= 2:
            time_span = (self.timestamps[-1] - self.timestamps[0]).total_seconds()
            if time_span > 0:
                metrics["throughput_rps"] = len(self.timestamps) / time_span

        return metrics

    def check_sla_violations(self) -> Dict[str, Any]:
        """
        Check for SLA violations.

        SLA (Service Level Agreement) Metrics:
        - P95 latency: 95% of requests must be < threshold
        - Error rate: Must be < threshold
        - Throughput: Must be > minimum

        Returns:
            Dictionary with violation status and details
        """
        metrics = self.get_current_metrics()

        violations = {
            "has_violations": False,
            "violations": []
        }

        # Check latency SLA
        if metrics.get("p95_latency_ms", 0) > self.latency_threshold_ms:
            violations["has_violations"] = True
            violations["violations"].append({
                "type": "latency",
                "message": f"P95 latency {metrics['p95_latency_ms']:.2f}ms exceeds threshold {self.latency_threshold_ms}ms"
            })

        # Check error rate SLA
        if metrics.get("error_rate", 0) > self.error_rate_threshold:
            violations["has_violations"] = True
            violations["violations"].append({
                "type": "error_rate",
                "message": f"Error rate {metrics['error_rate']:.2%} exceeds threshold {self.error_rate_threshold:.2%}"
            })

        return violations

    def get_performance_summary(self) -> str:
        """
        Get human-readable performance summary.

        Returns:
            Formatted performance summary string
        """
        metrics = self.get_current_metrics()

        if not metrics:
            return "No metrics available"

        summary = []
        summary.append("=" * 50)
        summary.append("PERFORMANCE METRICS")
        summary.append("=" * 50)
        summary.append(f"Total Requests: {metrics['total_requests']}")
        summary.append(f"")
        summary.append(f"Latency:")
        summary.append(f"  Average:  {metrics['avg_latency_ms']:.2f}ms")
        summary.append(f"  P50:      {metrics['p50_latency_ms']:.2f}ms")
        summary.append(f"  P95:      {metrics['p95_latency_ms']:.2f}ms")
        summary.append(f"  P99:      {metrics['p99_latency_ms']:.2f}ms")
        summary.append(f"")
        summary.append(f"Error Rate: {metrics['error_rate']:.2%}")

        if "throughput_rps" in metrics:
            summary.append(f"Throughput: {metrics['throughput_rps']:.2f} req/s")

        # Check for violations
        violations = self.check_sla_violations()
        if violations["has_violations"]:
            summary.append(f"")
            summary.append("⚠️  SLA VIOLATIONS:")
            for violation in violations["violations"]:
                summary.append(f"  - {violation['message']}")

        return "\n".join(summary)


class ModelQualityMonitor:
    """
    Monitor model quality metrics in production.

    Tracks:
    - Prediction distribution
    - Confidence scores
    - Model quality (when ground truth available)
    """

    def __init__(self, window_size: int = 1000):
        """
        Initialize model quality monitor.

        Args:
            window_size: Size of sliding window for metrics
        """
        self.window_size = window_size

        # Sliding windows
        self.predictions = deque(maxlen=window_size)
        self.confidences = deque(maxlen=window_size)
        self.ground_truths = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)

    def record_prediction(
        self,
        prediction: float,
        confidence: Optional[float] = None,
        ground_truth: Optional[float] = None
    ) -> None:
        """
        Record a prediction and optional ground truth.

        Args:
            prediction: Model prediction
            confidence: Prediction confidence/probability
            ground_truth: Actual value (if available)
        """
        self.predictions.append(prediction)
        self.confidences.append(confidence)
        self.ground_truths.append(ground_truth)
        self.timestamps.append(datetime.now())

    def get_prediction_distribution(self) -> Dict[str, Any]:
        """
        Analyze prediction distribution.

        Returns:
            Dictionary with distribution statistics
        """
        if not self.predictions:
            return {}

        predictions_array = np.array([p for p in self.predictions if p is not None])

        return {
            "mean": np.mean(predictions_array),
            "std": np.std(predictions_array),
            "min": np.min(predictions_array),
            "max": np.max(predictions_array),
            "median": np.median(predictions_array),
        }

    def get_confidence_distribution(self) -> Dict[str, Any]:
        """
        Analyze confidence score distribution.

        Low confidence predictions may indicate:
        - Model uncertainty
        - Out-of-distribution data
        - Need for human review

        Returns:
            Dictionary with confidence statistics
        """
        confidences = [c for c in self.confidences if c is not None]

        if not confidences:
            return {}

        confidences_array = np.array(confidences)

        return {
            "mean_confidence": np.mean(confidences_array),
            "std_confidence": np.std(confidences_array),
            "low_confidence_rate": np.mean(confidences_array < 0.7),  # < 70% confidence
            "high_confidence_rate": np.mean(confidences_array > 0.9),  # > 90% confidence
        }

    def calculate_accuracy(self) -> Optional[float]:
        """
        Calculate accuracy from ground truth labels.

        This requires ground truth to be available, which may be:
        - Delayed (feedback loop)
        - Partial (only for some predictions)
        - Never available (no feedback)

        Returns:
            Accuracy if ground truth available, None otherwise
        """
        # Filter pairs where ground truth is available
        pairs = [
            (p, gt) for p, gt in zip(self.predictions, self.ground_truths)
            if gt is not None and p is not None
        ]

        if not pairs:
            return None

        predictions, ground_truths = zip(*pairs)
        predictions = np.array(predictions)
        ground_truths = np.array(ground_truths)

        # Calculate accuracy (assuming binary classification)
        accuracy = np.mean(predictions == ground_truths)

        return accuracy

    def detect_performance_degradation(
        self,
        baseline_accuracy: float,
        threshold: float = 0.05
    ) -> bool:
        """
        Detect if model performance has degraded.

        Args:
            baseline_accuracy: Expected baseline accuracy
            threshold: Degradation threshold (0.05 = 5%)

        Returns:
            True if degradation detected
        """
        current_accuracy = self.calculate_accuracy()

        if current_accuracy is None:
            return False  # Cannot determine without ground truth

        degradation = baseline_accuracy - current_accuracy

        if degradation > threshold:
            print(f"⚠️  Performance degradation detected:")
            print(f"   Baseline: {baseline_accuracy:.2%}")
            print(f"   Current:  {current_accuracy:.2%}")
            print(f"   Drop:     {degradation:.2%}")
            return True

        return False
