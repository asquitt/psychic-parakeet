"""
FastAPI Model Serving

This module provides a production-ready REST API for model inference with:
- Request validation using Pydantic
- Model versioning and registry integration
- Performance monitoring with Prometheus
- Health checks and readiness probes
- Async request handling

Learning Points:
- FastAPI: Modern, fast (high-performance) web framework
- Pydantic: Data validation and serialization
- Async endpoints: Better resource utilization
- Prometheus metrics: Essential for production monitoring
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import numpy as np
import mlflow
import mlflow.pyfunc
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator

from ml_pipeline.config import config


class PredictionRequest(BaseModel):
    """
    Request schema for model predictions.

    Pydantic models provide:
    - Automatic validation
    - JSON serialization/deserialization
    - API documentation
    - Type hints
    """

    features: Dict[str, float] = Field(
        ...,
        description="Feature dictionary with feature names as keys",
        example={"feature1": 1.0, "feature2": 2.5, "feature3": 0.8}
    )
    model_version: Optional[str] = Field(
        None,
        description="Specific model version (optional)"
    )

    @validator("features")
    def validate_features(cls, v):
        """Validate that all features are numeric."""
        for key, value in v.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f"Feature {key} must be numeric")
        return v


class PredictionResponse(BaseModel):
    """Response schema for model predictions."""

    prediction: float = Field(..., description="Model prediction")
    probability: Optional[float] = Field(None, description="Prediction probability")
    model_version: str = Field(..., description="Model version used")
    latency_ms: float = Field(..., description="Prediction latency in milliseconds")
    timestamp: datetime = Field(..., description="Prediction timestamp")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_name: str = Field(..., description="Loaded model name")
    model_version: str = Field(..., description="Loaded model version")
    uptime_seconds: float = Field(..., description="Service uptime")


class ModelServer:
    """
    Model serving with MLflow registry integration.

    This class handles:
    - Loading models from MLflow registry
    - Making predictions
    - Caching models for performance
    - Version management
    """

    def __init__(
        self,
        model_name: str,
        model_stage: str = "Production",
        registry_uri: str = None,
    ):
        """
        Initialize model server.

        Args:
            model_name: Name of model in MLflow registry
            model_stage: Model stage to load (Production, Staging, None)
            registry_uri: MLflow registry URI
        """
        self.model_name = model_name
        self.model_stage = model_stage
        self.registry_uri = registry_uri or config.serving.model_registry_uri

        mlflow.set_tracking_uri(self.registry_uri)

        self.model = None
        self.model_version = None
        self.load_model()

    def load_model(self) -> None:
        """
        Load model from MLflow registry.

        Model Loading Strategy:
        - Use model stage (Production, Staging)
        - Load from MLflow's model registry
        - Cache model in memory for fast inference
        """
        try:
            # Load model from registry
            model_uri = f"models:/{self.model_name}/{self.model_stage}"
            self.model = mlflow.pyfunc.load_model(model_uri)

            # Get model version
            client = mlflow.tracking.MlflowClient()
            model_versions = client.get_latest_versions(
                self.model_name, stages=[self.model_stage]
            )
            if model_versions:
                self.model_version = model_versions[0].version

            print(f"✓ Model loaded: {self.model_name} v{self.model_version} ({self.model_stage})")

        except Exception as e:
            print(f"✗ Failed to load model: {e}")
            raise

    def predict(self, features: Dict[str, float]) -> tuple:
        """
        Make prediction using loaded model.

        Args:
            features: Feature dictionary

        Returns:
            Tuple of (prediction, probability)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        # Convert features to DataFrame (MLflow format)
        import pandas as pd
        features_df = pd.DataFrame([features])

        start_time = time.time()

        # Make prediction
        prediction = self.model.predict(features_df)[0]

        # Get probability if available
        probability = None
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(features_df)[0]
            probability = float(proba[1] if len(proba) > 1 else proba[0])

        latency_ms = (time.time() - start_time) * 1000

        return prediction, probability, latency_ms


# Create FastAPI app
app = FastAPI(
    title="ML Model Serving API",
    description="Production-ready ML model serving with monitoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Prometheus metrics
prediction_counter = Counter(
    "predictions_total",
    "Total number of predictions",
    ["model_name", "model_version"]
)
prediction_latency = Histogram(
    "prediction_latency_seconds",
    "Prediction latency in seconds",
    ["model_name", "model_version"]
)
model_load_status = Gauge(
    "model_loaded",
    "Whether model is successfully loaded"
)

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Instrument FastAPI app
Instrumentator().instrument(app).expose(app)

# Global model server instance
model_server: Optional[ModelServer] = None
start_time = time.time()


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup."""
    global model_server
    try:
        model_server = ModelServer(
            model_name=config.serving.model_name,
            model_stage=config.serving.model_stage,
            registry_uri=config.serving.model_registry_uri,
        )
        model_load_status.set(1)
    except Exception as e:
        print(f"Failed to load model on startup: {e}")
        model_load_status.set(0)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "ML Model Serving API",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint.

    Used by:
    - Kubernetes liveness probes
    - Load balancers
    - Monitoring systems
    """
    uptime = time.time() - start_time

    return HealthResponse(
        status="healthy" if model_server and model_server.model else "unhealthy",
        model_loaded=model_server is not None and model_server.model is not None,
        model_name=model_server.model_name if model_server else "none",
        model_version=model_server.model_version if model_server else "none",
        uptime_seconds=uptime
    )


@app.get("/ready")
async def readiness():
    """
    Readiness check endpoint.

    Returns 200 if service is ready to accept requests.
    Used by Kubernetes readiness probes.
    """
    if model_server is None or model_server.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make prediction endpoint.

    This is the main inference endpoint that:
    1. Validates input
    2. Makes prediction
    3. Records metrics
    4. Returns result

    Example:
        POST /predict
        {
            "features": {
                "feature1": 1.0,
                "feature2": 2.5,
                "feature3": 0.8
            }
        }

    Returns:
        {
            "prediction": 1.0,
            "probability": 0.85,
            "model_version": "3",
            "latency_ms": 12.5,
            "timestamp": "2024-01-01T00:00:00"
        }
    """
    if model_server is None or model_server.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Make prediction
        prediction, probability, latency_ms = model_server.predict(request.features)

        # Record metrics
        prediction_counter.labels(
            model_name=model_server.model_name,
            model_version=model_server.model_version
        ).inc()

        prediction_latency.labels(
            model_name=model_server.model_name,
            model_version=model_server.model_version
        ).observe(latency_ms / 1000)

        return PredictionResponse(
            prediction=float(prediction),
            probability=probability,
            model_version=model_server.model_version,
            latency_ms=latency_ms,
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=List[PredictionResponse])
async def predict_batch(requests: List[PredictionRequest]):
    """
    Batch prediction endpoint.

    More efficient for multiple predictions:
    - Reduces network overhead
    - Batch processing optimizations
    - Better throughput

    Example:
        POST /predict/batch
        [
            {"features": {"feature1": 1.0, "feature2": 2.5}},
            {"features": {"feature1": 2.0, "feature2": 3.5}}
        ]
    """
    if model_server is None or model_server.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    responses = []
    for req in requests:
        try:
            prediction, probability, latency_ms = model_server.predict(req.features)

            # Record metrics
            prediction_counter.labels(
                model_name=model_server.model_name,
                model_version=model_server.model_version
            ).inc()

            responses.append(
                PredictionResponse(
                    prediction=float(prediction),
                    probability=probability,
                    model_version=model_server.model_version,
                    latency_ms=latency_ms,
                    timestamp=datetime.now()
                )
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Batch prediction failed at index {len(responses)}: {str(e)}"
            )

    return responses


@app.post("/model/reload")
async def reload_model():
    """
    Reload model from registry.

    Use this endpoint to:
    - Load new model version
    - Recover from model loading errors
    - Update to latest production model
    """
    global model_server
    try:
        if model_server:
            model_server.load_model()
            model_load_status.set(1)
            return {
                "status": "success",
                "message": f"Model reloaded: {model_server.model_name} v{model_server.model_version}"
            }
        else:
            raise HTTPException(status_code=500, detail="Model server not initialized")
    except Exception as e:
        model_load_status.set(0)
        raise HTTPException(status_code=500, detail=f"Model reload failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=config.serving.model_service_host,
        port=config.serving.model_service_port,
        log_level="info"
    )
