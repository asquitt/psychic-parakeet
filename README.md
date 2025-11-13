# 🚀 Production-Ready ML Pipeline with MLOps

A comprehensive, end-to-end machine learning pipeline demonstrating industry best practices for MLOps, including experiment tracking, model registry, sophisticated deployment strategies, and comprehensive monitoring.

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Components](#components)
- [Usage Guide](#usage-guide)
- [Deployment Strategies](#deployment-strategies)
- [Monitoring & Alerting](#monitoring--alerting)
- [Learning Resources](#learning-resources)
- [Contributing](#contributing)

## 🎯 Overview

This project implements a production-grade ML pipeline that showcases the complete MLOps lifecycle:

```
Data → Validation → Feature Engineering → Training → Evaluation → Deployment → Monitoring
```

**Built for learning and production use**, this pipeline includes extensive documentation, comments, and examples to help you understand each component and decision.

## ✨ Key Features

### 🔄 Workflow Orchestration
- **Prefect** for managing complex DAG workflows
- Automated training, evaluation, and deployment pipelines
- Scheduled retraining and monitoring jobs
- Error handling and retry logic

### 📊 Experiment Tracking & Model Registry
- **MLflow** for experiment tracking, model versioning, and registry
- Automatic logging of parameters, metrics, and artifacts
- Model comparison and selection
- Staged model promotion (Staging → Production)

### 🚢 Deployment Strategies
- **Canary Deployments**: Gradual rollout with automatic rollback
- **Blue/Green Deployments**: Zero-downtime updates
- **Shadow Deployments**: A/B testing with live traffic
- Performance-based automatic rollback

### 📈 Monitoring & Alerting
- **Data Drift Detection**: Kolmogorov-Smirnov test, PSI calculation
- **Performance Monitoring**: Latency, throughput, error rates
- **Model Degradation Detection**: Track prediction quality
- **Prometheus + Grafana**: Metrics collection and visualization

### 🔧 Production-Ready API
- **FastAPI** REST API for model serving
- Request validation with Pydantic
- Health checks and readiness probes
- Prometheus metrics integration
- Batch prediction support

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       ML Pipeline Architecture               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Data       │───▶│   Feature    │───▶│   Model      │ │
│  │   Pipeline   │    │  Engineering │    │   Training   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                    │                     │        │
│         ▼                    ▼                     ▼        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Prefect Orchestration                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         MLflow (Tracking + Model Registry)           │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                ┌───────────┴───────────┐                   │
│                ▼                       ▼                    │
│  ┌──────────────────────┐   ┌──────────────────────┐      │
│  │   Deployment         │   │   Monitoring         │      │
│  │   Strategies         │   │   & Alerting         │      │
│  │  - Canary            │   │  - Drift Detection   │      │
│  │  - Blue/Green        │   │  - Performance       │      │
│  │  - Shadow            │   │  - Health Checks     │      │
│  └──────────────────────┘   └──────────────────────┘      │
│                │                       │                    │
│                ▼                       ▼                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastAPI Model Serving                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Prometheus ──▶ Grafana Dashboards            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- 8GB+ RAM recommended

### 1. Clone and Install

```bash
# Clone repository
git clone <repository-url>
cd psychic-parakeet

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### 2. Start Infrastructure

```bash
# Start all services (MLflow, Prefect, PostgreSQL, Prometheus, Grafana)
make docker-up

# Or manually:
docker-compose up -d
```

**Services will be available at:**
- MLflow UI: http://localhost:5000
- Prefect UI: http://localhost:4200
- Model API: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### 3. Generate Sample Data

```bash
# Generate sample dataset for testing
python scripts/generate_sample_data.py
```

### 4. Run Training Pipeline

```bash
# Run complete training pipeline
python scripts/run_training.py

# Or use make command:
make train
```

### 5. Start Model Serving

```bash
# Start FastAPI server
make serve

# Or manually:
uvicorn ml_pipeline.serving.api:app --reload
```

### 6. Make Predictions

```bash
# Test prediction endpoint
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "feature1": 1.0,
      "feature2": 2.5,
      "feature3": 0.8
    }
  }'
```

## 📁 Project Structure

```
ml-pipeline/
├── src/ml_pipeline/           # Main package
│   ├── data/                  # Data validation & preprocessing
│   │   ├── validation.py      # Data quality checks
│   │   └── preprocessing.py   # Data transformation
│   ├── features/              # Feature engineering
│   │   └── engineering.py     # Feature creation & selection
│   ├── models/                # Model training & evaluation
│   │   ├── training.py        # Training with MLflow
│   │   └── evaluation.py      # Model evaluation metrics
│   ├── serving/               # Model serving
│   │   └── api.py            # FastAPI REST API
│   ├── deployment/            # Deployment strategies
│   │   └── strategies.py      # Canary, Blue/Green, Shadow
│   ├── monitoring/            # Monitoring & alerting
│   │   ├── drift_detection.py # Data drift detection
│   │   └── performance.py     # Performance monitoring
│   ├── orchestration/         # Workflow orchestration
│   │   └── workflows.py       # Prefect flows
│   └── config.py             # Configuration management
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── notebooks/                 # Jupyter notebooks
├── data/                      # Data storage
│   ├── raw/                   # Raw data
│   ├── processed/             # Processed data
│   └── interim/               # Intermediate data
├── models/                    # Saved models
├── config/                    # Configuration files
│   ├── prometheus.yml         # Prometheus config
│   └── grafana/              # Grafana dashboards
├── scripts/                   # Utility scripts
├── docs/                      # Documentation
├── .github/workflows/         # CI/CD pipelines
├── docker-compose.yml         # Docker services
├── Dockerfile.api            # API container
├── Dockerfile.worker         # Worker container
├── requirements.txt          # Python dependencies
├── Makefile                  # Common commands
└── README.md                 # This file
```

## 🔧 Components

### 1. Data Validation & Preprocessing

**Location:** `src/ml_pipeline/data/`

- **Validation:** Schema checks, missing values, outliers, duplicates
- **Preprocessing:** Scaling, encoding, imputation
- **Features:** Reusable sklearn pipelines, saved for production

```python
from ml_pipeline.data.validation import DataValidator, validate_training_data
from ml_pipeline.data.preprocessing import DataPreprocessor

# Validate data
validator = DataValidator()
clean_df = validate_training_data(df, feature_columns, target_column)

# Create preprocessing pipeline
preprocessor = DataPreprocessor(
    numerical_features=['age', 'income'],
    categorical_features=['gender', 'city'],
    scaling_method='standard'
)
X_scaled = preprocessor.fit_transform(X_train)
```

### 2. Feature Engineering

**Location:** `src/ml_pipeline/features/`

- Mathematical transformations (log, sqrt, polynomial)
- Feature interactions and ratios
- Feature selection with statistical tests
- Rolling statistics for time series

```python
from ml_pipeline.features.engineering import FeatureEngineer

engineer = FeatureEngineer()
df_features = engineer.create_feature_set(
    df,
    numerical_columns=['age', 'income'],
    add_interactions=True,
    add_polynomials=True
)
```

### 3. Model Training & Tracking

**Location:** `src/ml_pipeline/models/`

- Multiple algorithms (XGBoost, Random Forest, Gradient Boosting, etc.)
- Hyperparameter tuning (Grid Search, Random Search)
- Automatic MLflow logging
- Model registry integration

```python
from ml_pipeline.models.training import ModelTrainer

trainer = ModelTrainer(experiment_name="my_experiment")

# Train with hyperparameter tuning
best_model, best_params = trainer.tune_hyperparameters(
    X_train, y_train,
    model_type="xgboost",
    search_type="random"
)

# Register model
trainer.register_model(run_id, "production_model", stage="Production")
```

### 4. Model Evaluation

**Location:** `src/ml_pipeline/models/evaluation.py`

- Comprehensive metrics (accuracy, precision, recall, F1, ROC-AUC)
- Confusion matrix and classification report
- Feature importance analysis
- Model comparison framework

```python
from ml_pipeline.models.evaluation import ModelEvaluator

evaluator = ModelEvaluator()
results = evaluator.evaluate_and_log(
    model, X_test, y_test,
    feature_names=feature_names,
    run_id=run_id
)
```

### 5. Workflow Orchestration

**Location:** `src/ml_pipeline/orchestration/`

- Complete training pipeline as Prefect flow
- Task dependencies and retries
- Monitoring pipeline
- Scheduled workflows

```python
from ml_pipeline.orchestration.workflows import training_pipeline

results = training_pipeline(
    data_path="data/train.csv",
    feature_columns=['age', 'income'],
    target_column='purchased',
    numerical_features=['age', 'income'],
    model_type="xgboost"
)
```

## 🚀 Deployment Strategies

### Canary Deployment

Gradually roll out new model version to minimize risk:

```python
from ml_pipeline.deployment.strategies import CanaryDeployment

canary = CanaryDeployment(
    initial_traffic_percentage=10,
    increment_percentage=10,
    rollback_threshold=0.05
)

canary.start_deployment()

# Route requests
version = canary.route_request()  # Returns CURRENT or CANARY

# Monitor and increment
if canary.should_increment_traffic():
    canary.increment_traffic()

# Auto-rollback on degradation
if canary.should_rollback():
    canary.rollback()
```

### Blue/Green Deployment

Zero-downtime deployment with instant rollback:

```python
from ml_pipeline.deployment.strategies import BlueGreenDeployment

deployment = BlueGreenDeployment()

# Deploy to green
deployment.deploy_to_green("v2.0")

# Test green environment...

# Switch traffic
deployment.switch_to_green()

# Rollback if needed
deployment.rollback_to_blue()
```

### Shadow Deployment

Test new model with production traffic without impacting users:

```python
from ml_pipeline.deployment.strategies import ShadowDeployment

shadow = ShadowDeployment()
shadow.start_shadow_deployment("v1.0", "v2.0")

# Makes predictions from both models
current_pred, shadow_pred = shadow.predict(features, model_v1, model_v2)

# Analyze performance
analysis = shadow.analyze_shadow_performance()
```

## 📊 Monitoring & Alerting

### Data Drift Detection

**Location:** `src/ml_pipeline/monitoring/drift_detection.py`

Detect when input data distribution changes:

```python
from ml_pipeline.monitoring.drift_detection import DriftDetector

detector = DriftDetector(threshold=0.05)
detector.set_reference_data(train_df)

# Check for drift
results = detector.detect_drift(
    production_df,
    numerical_features=['age', 'income'],
    categorical_features=['gender']
)

if results['drift_detected']:
    print(f"Drift detected in: {results['drifted_features']}")

# Determine if retraining needed
if detector.should_retrain(results):
    print("⚠️  Model retraining recommended")
```

**Drift Detection Methods:**
- Kolmogorov-Smirnov test for numerical features
- Chi-squared test for categorical features
- Population Stability Index (PSI)
- Evidently AI integration for comprehensive reports

### Performance Monitoring

**Location:** `src/ml_pipeline/monitoring/performance.py`

Track production model performance:

```python
from ml_pipeline.monitoring.performance import PerformanceMonitor

monitor = PerformanceMonitor(
    latency_threshold_ms=100,
    error_rate_threshold=0.01
)

# Record prediction
monitor.record_prediction(
    latency_ms=45.2,
    prediction=1,
    error=False
)

# Get metrics
metrics = monitor.get_current_metrics()
print(f"P95 latency: {metrics['p95_latency_ms']}ms")
print(f"Error rate: {metrics['error_rate']:.2%}")

# Check SLA violations
violations = monitor.check_sla_violations()
if violations['has_violations']:
    print("⚠️  SLA violations detected!")
```

**Monitored Metrics:**
- Latency (avg, p50, p95, p99)
- Throughput (requests per second)
- Error rate
- Prediction distribution
- Confidence scores
- Model accuracy (when ground truth available)

### Prometheus Metrics

All metrics are automatically exported to Prometheus:

```python
# Automatic metrics from FastAPI
- predictions_total
- prediction_latency_seconds
- prediction_throughput_rps
- model_loaded
```

Access metrics at: http://localhost:9090

### Grafana Dashboards

Pre-configured dashboards for visualization:
- Model performance metrics
- Data drift indicators
- System health
- API latency and throughput

Access Grafana at: http://localhost:3000 (admin/admin)

## 📚 Learning Resources

### Understanding Each Component

1. **Data Validation** (`data/validation.py`)
   - Why: Prevents "garbage in, garbage out"
   - Techniques: Schema validation, outlier detection, quality checks
   - When: Before training and in production

2. **Feature Engineering** (`features/engineering.py`)
   - Why: Good features > complex models
   - Techniques: Transformations, interactions, selection
   - Impact: Can improve accuracy by 10-30%

3. **Experiment Tracking** (`models/training.py`)
   - Why: Track what works and reproducibility
   - Tool: MLflow
   - Benefits: Compare experiments, version models, reproduce results

4. **Deployment Strategies** (`deployment/strategies.py`)
   - Why: Minimize risk of bad deployments
   - Strategies: Canary, Blue/Green, Shadow
   - Goal: Zero downtime, quick rollback

5. **Monitoring** (`monitoring/`)
   - Why: Models degrade over time
   - What to monitor: Drift, performance, latency
   - Action: Alert and retrain when needed

### Key Concepts

**MLOps vs DevOps:**
- MLOps adds: Data versioning, experiment tracking, model registry, drift detection
- Similar: CI/CD, monitoring, containerization

**Production ML Challenges:**
1. Data drift: Input distribution changes
2. Concept drift: Relationship between features and target changes
3. Model staleness: Model becomes outdated
4. Monitoring: Need real-time performance tracking
5. Reproducibility: Must be able to recreate models

**Cost Efficiency Tips:**
1. Use caching in Prefect tasks (already configured)
2. Batch predictions instead of one-by-one
3. Use smaller models when appropriate
4. Monitor resource usage with Prometheus
5. Auto-scale based on traffic

## 🔄 Complete Workflow Example

Here's a complete workflow from data to production:

```bash
# 1. Start infrastructure
make docker-up

# 2. Generate sample data
python scripts/generate_sample_data.py

# 3. Run training pipeline (includes validation, engineering, training, evaluation)
python scripts/run_training.py

# 4. Check MLflow for experiment results
# Visit http://localhost:5000

# 5. Start model serving
make serve

# 6. Make predictions
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"feature1": 1.0, "feature2": 2.5}}'

# 7. Monitor metrics
# Visit http://localhost:9090 (Prometheus)
# Visit http://localhost:3000 (Grafana)

# 8. Run monitoring pipeline (check for drift)
python scripts/run_monitoring.py

# 9. If drift detected, retrain
python scripts/run_training.py
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test
pytest tests/unit/test_validation.py -v
```

## 🛠️ Development

```bash
# Format code
make format

# Check formatting
make format-check

# Run linters
make lint

# Clean up
make clean
```

## 📖 API Documentation

Once the API is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐳 Docker Commands

```bash
# Build images
make docker-build

# Start services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down

# Clean up everything
make docker-clean
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MLflow** for experiment tracking
- **Prefect** for workflow orchestration
- **FastAPI** for high-performance API
- **Evidently AI** for drift detection
- **Prometheus & Grafana** for monitoring

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ for learning and production ML systems**
