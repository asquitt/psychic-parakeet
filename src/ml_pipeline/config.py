"""
Configuration Management

This module handles all configuration settings for the ML pipeline using
Pydantic for validation and environment variable support.

Key Concepts:
- Pydantic Settings: Type-safe configuration with validation
- Environment Variables: 12-factor app methodology for config
- Separation of Concerns: Different configs for different components
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """PostgreSQL database configuration.

    Used for:
    - MLflow backend store (experiment metadata)
    - Prefect backend (workflow metadata)
    - Application data storage
    """

    postgres_user: str = Field(default="mlpipeline", description="Database user")
    postgres_password: str = Field(default="changeme123", description="Database password")
    postgres_db: str = Field(default="mlpipeline", description="Database name")
    postgres_host: str = Field(default="localhost", description="Database host")
    postgres_port: int = Field(default=5432, description="Database port")

    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def async_connection_string(self) -> str:
        """Generate async SQLAlchemy connection string for Prefect."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/prefect"
        )

    class Config:
        env_file = ".env"


class MLflowConfig(BaseSettings):
    """MLflow experiment tracking and model registry configuration.

    MLflow Components:
    - Tracking Server: Logs parameters, metrics, artifacts
    - Backend Store: Stores experiment metadata (PostgreSQL)
    - Artifact Store: Stores models and artifacts (local/S3)
    - Model Registry: Manages model versions and staging
    """

    mlflow_tracking_uri: str = Field(
        default="http://localhost:5000",
        description="MLflow tracking server URI"
    )
    mlflow_backend_store_uri: str = Field(
        default="sqlite:///mlflow.db",
        description="Backend store for experiment metadata"
    )
    mlflow_artifact_root: str = Field(
        default="./mlartifacts",
        description="Root directory for artifacts"
    )

    class Config:
        env_file = ".env"


class PrefectConfig(BaseSettings):
    """Prefect workflow orchestration configuration.

    Prefect manages:
    - DAG execution and scheduling
    - Task dependencies and retries
    - Workflow versioning
    - Execution monitoring
    """

    prefect_api_url: str = Field(
        default="http://localhost:4200/api",
        description="Prefect API server URL"
    )
    prefect_api_database_connection_url: Optional[str] = Field(
        default=None,
        description="Prefect database connection URL"
    )

    class Config:
        env_file = ".env"


class ModelServingConfig(BaseSettings):
    """Model serving API configuration.

    FastAPI service for model inference with:
    - REST API endpoints
    - Request validation
    - Performance monitoring
    - Health checks
    """

    model_service_host: str = Field(default="0.0.0.0", description="API host")
    model_service_port: int = Field(default=8000, description="API port")
    model_registry_uri: str = Field(
        default="http://localhost:5000",
        description="MLflow registry URI"
    )
    model_name: str = Field(default="production_model", description="Model name")
    model_stage: str = Field(default="Production", description="Model stage")

    class Config:
        env_file = ".env"


class DeploymentConfig(BaseSettings):
    """Deployment strategy configuration.

    Deployment Strategies:
    - Canary: Gradually route traffic to new version
    - Blue/Green: Switch traffic between two environments
    - Rolling: Incrementally replace instances
    """

    deployment_strategy: str = Field(
        default="canary",
        description="Deployment strategy: canary, blue_green, rolling"
    )
    canary_traffic_percentage: int = Field(
        default=10,
        description="Initial traffic % for canary deployments"
    )
    rollback_threshold: float = Field(
        default=0.05,
        description="Performance degradation threshold for rollback"
    )

    class Config:
        env_file = ".env"


class MonitoringConfig(BaseSettings):
    """Monitoring and alerting configuration.

    Monitoring Components:
    - Data Drift Detection: Detect distribution changes
    - Performance Monitoring: Track latency and throughput
    - Model Degradation: Monitor prediction quality
    - Alerting: Notify on threshold breaches
    """

    # Data Drift
    drift_detection_enabled: bool = Field(default=True)
    drift_check_interval_hours: int = Field(default=24)
    drift_threshold: float = Field(default=0.1, description="KS test threshold")

    # Performance
    latency_threshold_ms: int = Field(default=100, description="Max latency in ms")
    throughput_min_rps: int = Field(default=10, description="Min requests per second")
    performance_check_interval_minutes: int = Field(default=5)

    # Prometheus
    prometheus_port: int = Field(default=9090)
    grafana_port: int = Field(default=3000)

    class Config:
        env_file = ".env"


class Config(BaseSettings):
    """Main configuration class combining all sub-configurations."""

    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    mlflow: MLflowConfig = Field(default_factory=MLflowConfig)
    prefect: PrefectConfig = Field(default_factory=PrefectConfig)
    serving: ModelServingConfig = Field(default_factory=ModelServingConfig)
    deployment: DeploymentConfig = Field(default_factory=DeploymentConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    class Config:
        env_file = ".env"


# Singleton configuration instance
config = Config()
