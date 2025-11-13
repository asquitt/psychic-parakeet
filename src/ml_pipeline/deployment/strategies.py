"""
Deployment Strategies Implementation

This module provides production-grade deployment strategies for ML models:

1. Canary Deployment:
   - Gradually increase traffic to new version
   - Monitor performance metrics
   - Auto-rollback on degradation

2. Blue/Green Deployment:
   - Two identical environments (blue = current, green = new)
   - Instant traffic switch
   - Easy rollback

3. Shadow Deployment:
   - New version receives copy of traffic
   - Predictions logged but not returned
   - Compare performance without user impact

Learning Points:
- Zero-downtime deployments are crucial for production
- Monitor performance during rollout
- Have rollback strategy ready
- Test with real traffic patterns
"""

from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
import time
import random
from dataclasses import dataclass
import mlflow


class DeploymentStrategy(Enum):
    """Deployment strategy types."""
    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    SHADOW = "shadow"


class ModelVersion(Enum):
    """Model version identifiers."""
    BLUE = "blue"
    GREEN = "green"
    CURRENT = "current"
    CANARY = "canary"


@dataclass
class DeploymentMetrics:
    """Metrics for deployment monitoring."""
    latency_ms: float
    error_rate: float
    throughput_rps: float
    accuracy: Optional[float] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class CanaryDeployment:
    """
    Canary deployment strategy.

    How it works:
    1. Deploy new version alongside current version
    2. Route small % of traffic to new version (e.g., 10%)
    3. Monitor performance metrics
    4. Gradually increase traffic if metrics are good
    5. Rollback if performance degrades

    Benefits:
    - Reduces risk of bad deployments
    - Early detection of issues
    - Gradual validation with real traffic

    Use when:
    - Deploying significant model changes
    - High-traffic production systems
    - Need to validate performance with real data
    """

    def __init__(
        self,
        initial_traffic_percentage: int = 10,
        increment_percentage: int = 10,
        increment_interval_minutes: int = 30,
        rollback_threshold: float = 0.05,
    ):
        """
        Initialize canary deployment.

        Args:
            initial_traffic_percentage: Initial % of traffic to canary
            increment_percentage: How much to increase traffic each step
            increment_interval_minutes: Minutes between traffic increases
            rollback_threshold: Performance degradation threshold for rollback
        """
        self.current_traffic_percentage = 0
        self.initial_traffic_percentage = initial_traffic_percentage
        self.increment_percentage = increment_percentage
        self.increment_interval_minutes = increment_interval_minutes
        self.rollback_threshold = rollback_threshold

        self.current_version_metrics: List[DeploymentMetrics] = []
        self.canary_version_metrics: List[DeploymentMetrics] = []
        self.deployment_start_time: Optional[datetime] = None
        self.is_active = False

    def start_deployment(self) -> None:
        """Start canary deployment."""
        self.current_traffic_percentage = self.initial_traffic_percentage
        self.deployment_start_time = datetime.now()
        self.is_active = True
        print(f"🚀 Canary deployment started: {self.initial_traffic_percentage}% traffic to canary")

    def route_request(self) -> ModelVersion:
        """
        Route request to either current or canary version.

        Returns:
            ModelVersion indicating which version to use
        """
        if not self.is_active:
            return ModelVersion.CURRENT

        # Randomly route based on traffic percentage
        if random.randint(1, 100) <= self.current_traffic_percentage:
            return ModelVersion.CANARY
        return ModelVersion.CURRENT

    def record_metrics(self, version: ModelVersion, metrics: DeploymentMetrics) -> None:
        """Record metrics for a model version."""
        if version == ModelVersion.CANARY:
            self.canary_version_metrics.append(metrics)
        else:
            self.current_version_metrics.append(metrics)

    def should_increment_traffic(self) -> bool:
        """Check if traffic should be increased."""
        if not self.is_active:
            return False

        if self.current_traffic_percentage >= 100:
            return False

        # Check if enough time has passed
        time_since_start = (datetime.now() - self.deployment_start_time).total_seconds()
        if time_since_start < self.increment_interval_minutes * 60:
            return False

        # Check if canary performance is acceptable
        if self.should_rollback():
            return False

        return True

    def increment_traffic(self) -> None:
        """Increase traffic to canary version."""
        new_percentage = min(
            100,
            self.current_traffic_percentage + self.increment_percentage
        )
        print(f"📈 Increasing canary traffic: {self.current_traffic_percentage}% → {new_percentage}%")
        self.current_traffic_percentage = new_percentage

        if self.current_traffic_percentage >= 100:
            self.complete_deployment()

    def should_rollback(self) -> bool:
        """
        Check if deployment should be rolled back.

        Rollback Criteria:
        - Error rate increased significantly
        - Latency degraded beyond threshold
        - Accuracy dropped (if available)

        Returns:
            True if rollback is needed
        """
        if not self.canary_version_metrics or not self.current_version_metrics:
            return False

        # Calculate average metrics
        canary_latency = sum(m.latency_ms for m in self.canary_version_metrics[-10:]) / min(10, len(self.canary_version_metrics))
        current_latency = sum(m.latency_ms for m in self.current_version_metrics[-10:]) / min(10, len(self.current_version_metrics))

        canary_error_rate = sum(m.error_rate for m in self.canary_version_metrics[-10:]) / min(10, len(self.canary_version_metrics))
        current_error_rate = sum(m.error_rate for m in self.current_version_metrics[-10:]) / min(10, len(self.current_version_metrics))

        # Check for degradation
        latency_degradation = (canary_latency - current_latency) / current_latency if current_latency > 0 else 0
        error_rate_degradation = canary_error_rate - current_error_rate

        if latency_degradation > self.rollback_threshold:
            print(f"⚠️  Latency degradation detected: {latency_degradation:.2%}")
            return True

        if error_rate_degradation > self.rollback_threshold:
            print(f"⚠️  Error rate increase detected: {error_rate_degradation:.2%}")
            return True

        return False

    def rollback(self) -> None:
        """Rollback to previous version."""
        print("🔄 Rolling back to previous version")
        self.current_traffic_percentage = 0
        self.is_active = False

    def complete_deployment(self) -> None:
        """Complete canary deployment."""
        print("✅ Canary deployment complete: 100% traffic on new version")
        self.is_active = False


class BlueGreenDeployment:
    """
    Blue/Green deployment strategy.

    How it works:
    1. Blue environment = current production
    2. Green environment = new version
    3. Deploy to green while blue serves traffic
    4. Test green environment
    5. Switch traffic from blue to green instantly
    6. Keep blue as backup for quick rollback

    Benefits:
    - Zero downtime
    - Instant rollback
    - Full testing before switch
    - Clean separation of versions

    Use when:
    - Zero downtime is critical
    - Need instant rollback capability
    - Have infrastructure for two full environments
    """

    def __init__(self):
        """Initialize blue/green deployment."""
        self.active_environment = ModelVersion.BLUE
        self.blue_version: Optional[str] = None
        self.green_version: Optional[str] = None

    def deploy_to_green(self, model_version: str) -> None:
        """
        Deploy new version to green environment.

        Args:
            model_version: Version to deploy
        """
        print(f"🟢 Deploying version {model_version} to GREEN environment")
        self.green_version = model_version
        print("✓ GREEN environment ready (not receiving traffic)")

    def switch_to_green(self) -> None:
        """Switch traffic from blue to green."""
        print(f"🔄 Switching traffic: BLUE → GREEN")
        self.active_environment = ModelVersion.GREEN
        print("✅ Traffic now on GREEN environment")

    def rollback_to_blue(self) -> None:
        """Rollback traffic to blue environment."""
        print("🔄 Rolling back traffic: GREEN → BLUE")
        self.active_environment = ModelVersion.BLUE
        print("✅ Traffic rolled back to BLUE environment")

    def promote_green_to_blue(self) -> None:
        """
        Promote green to blue after successful deployment.

        This frees up green for the next deployment.
        """
        print("🔄 Promoting GREEN to BLUE")
        self.blue_version = self.green_version
        self.green_version = None
        self.active_environment = ModelVersion.BLUE
        print("✅ GREEN promoted to BLUE, ready for next deployment")

    def get_active_version(self) -> str:
        """Get currently active model version."""
        if self.active_environment == ModelVersion.BLUE:
            return self.blue_version
        return self.green_version


class ShadowDeployment:
    """
    Shadow deployment strategy.

    How it works:
    1. Deploy new version alongside current version
    2. Send copy of all traffic to both versions
    3. Return predictions from current version only
    4. Log predictions from new version
    5. Compare performance offline
    6. Promote when confident

    Benefits:
    - Zero user impact
    - Test with 100% real traffic
    - Collect metrics before committing
    - Safe performance comparison

    Use when:
    - Need extensive validation
    - Want to A/B test models
    - Risk-averse deployment needed
    - Comparing model architectures
    """

    def __init__(self):
        """Initialize shadow deployment."""
        self.current_version: Optional[str] = None
        self.shadow_version: Optional[str] = None
        self.shadow_predictions: List[Dict[str, Any]] = []
        self.is_active = False

    def start_shadow_deployment(
        self,
        current_version: str,
        shadow_version: str
    ) -> None:
        """
        Start shadow deployment.

        Args:
            current_version: Current production version
            shadow_version: New version to shadow test
        """
        self.current_version = current_version
        self.shadow_version = shadow_version
        self.is_active = True
        print(f"👥 Shadow deployment started:")
        print(f"   Current: {current_version} (serving)")
        print(f"   Shadow: {shadow_version} (logging only)")

    def predict(
        self,
        features: Dict[str, float],
        current_model: Any,
        shadow_model: Any
    ) -> tuple:
        """
        Make predictions from both models.

        Args:
            features: Input features
            current_model: Current production model
            shadow_model: Shadow model being tested

        Returns:
            Tuple of (current_prediction, shadow_prediction)
        """
        # Current prediction (returned to user)
        current_prediction = current_model.predict([features])[0]

        # Shadow prediction (logged only)
        shadow_prediction = None
        if self.is_active and shadow_model:
            try:
                shadow_prediction = shadow_model.predict([features])[0]
                self.shadow_predictions.append({
                    "features": features,
                    "current_prediction": current_prediction,
                    "shadow_prediction": shadow_prediction,
                    "timestamp": datetime.now()
                })
            except Exception as e:
                print(f"Shadow prediction failed: {e}")

        return current_prediction, shadow_prediction

    def analyze_shadow_performance(self) -> Dict[str, Any]:
        """
        Analyze shadow deployment performance.

        Returns:
            Dictionary with comparison metrics
        """
        if not self.shadow_predictions:
            return {"error": "No shadow predictions recorded"}

        # Calculate agreement rate
        agreements = sum(
            1 for p in self.shadow_predictions
            if p["current_prediction"] == p["shadow_prediction"]
        )
        agreement_rate = agreements / len(self.shadow_predictions)

        analysis = {
            "total_predictions": len(self.shadow_predictions),
            "agreement_rate": agreement_rate,
            "disagreement_rate": 1 - agreement_rate,
            "current_version": self.current_version,
            "shadow_version": self.shadow_version
        }

        print("\n" + "=" * 50)
        print("SHADOW DEPLOYMENT ANALYSIS")
        print("=" * 50)
        print(f"Total predictions: {analysis['total_predictions']}")
        print(f"Agreement rate: {analysis['agreement_rate']:.2%}")
        print(f"Disagreement rate: {analysis['disagreement_rate']:.2%}")

        return analysis

    def promote_shadow_to_production(self) -> None:
        """Promote shadow version to production."""
        print(f"✅ Promoting shadow version {self.shadow_version} to production")
        self.current_version = self.shadow_version
        self.shadow_version = None
        self.is_active = False
        self.shadow_predictions = []


class DeploymentManager:
    """
    Manages different deployment strategies.

    This provides a unified interface for all deployment strategies.
    """

    def __init__(self, strategy: DeploymentStrategy):
        """
        Initialize deployment manager.

        Args:
            strategy: Deployment strategy to use
        """
        self.strategy = strategy

        if strategy == DeploymentStrategy.CANARY:
            self.deployer = CanaryDeployment()
        elif strategy == DeploymentStrategy.BLUE_GREEN:
            self.deployer = BlueGreenDeployment()
        elif strategy == DeploymentStrategy.SHADOW:
            self.deployer = ShadowDeployment()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def deploy(self, **kwargs) -> None:
        """Execute deployment based on strategy."""
        if self.strategy == DeploymentStrategy.CANARY:
            self.deployer.start_deployment()
        elif self.strategy == DeploymentStrategy.BLUE_GREEN:
            self.deployer.deploy_to_green(kwargs.get("model_version"))
        elif self.strategy == DeploymentStrategy.SHADOW:
            self.deployer.start_shadow_deployment(
                kwargs.get("current_version"),
                kwargs.get("shadow_version")
            )
