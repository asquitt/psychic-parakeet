# Quick Start Guide

Get up and running with the ML Pipeline in 10 minutes!

## Prerequisites

Before you begin, ensure you have:
- Python 3.9 or higher
- Docker and Docker Compose
- 8GB+ RAM
- Git

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd psychic-parakeet
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### 4. Start Infrastructure Services

```bash
# Start all services (PostgreSQL, MLflow, Prefect, Prometheus, Grafana)
docker-compose up -d

# Wait about 30 seconds for services to initialize
```

Verify services are running:
- MLflow: http://localhost:5000
- Prefect: http://localhost:4200
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### 5. Generate Sample Data

```bash
python scripts/generate_sample_data.py
```

This creates:
- `data/raw/train.csv` - Training data (1000 samples)
- `data/raw/test.csv` - Test data (200 samples)
- `data/raw/production.csv` - Production data with drift (500 samples)

### 6. Run Training Pipeline

```bash
python scripts/run_training.py
```

This will:
1. ✅ Load and validate data
2. ✅ Engineer features
3. ✅ Split into train/test
4. ✅ Preprocess data
5. ✅ Train XGBoost model with hyperparameter tuning
6. ✅ Evaluate model
7. ✅ Register model in MLflow

Expected output:
```
Training accuracy: 0.85+
Test accuracy: 0.80+
Model registered in MLflow
```

### 7. View Experiment Results

Open MLflow UI: http://localhost:5000

You'll see:
- All training runs
- Metrics comparison
- Model artifacts
- Registered models

### 8. Start Model Serving API

```bash
# In a new terminal (keep virtual environment activated)
python -m uvicorn ml_pipeline.serving.api:app --reload --host 0.0.0.0 --port 8000
```

Or use the Make command:
```bash
make serve
```

### 9. Test API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Make a Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "feature_1": 1.5,
      "feature_2": -0.5,
      "feature_3": 0.8,
      "feature_4": 1.2,
      "feature_5": -0.3
    }
  }'
```

#### Or use the test script
```bash
python scripts/test_api.py
```

### 10. View API Documentation

Open Swagger UI: http://localhost:8000/docs

Here you can:
- See all endpoints
- Try requests interactively
- View request/response schemas

### 11. Run Monitoring Pipeline

```bash
python scripts/run_monitoring.py
```

This will:
1. ✅ Load reference data (training)
2. ✅ Load current data (production)
3. ✅ Detect data drift
4. ✅ Calculate drift metrics
5. ✅ Recommend retraining if needed

Expected output:
```
Drift detected: True
Drifted features: feature_1, feature_2
Retraining recommended: True
```

### 12. View Monitoring Dashboards

#### Prometheus (Metrics)
http://localhost:9090

Query examples:
- `prediction_latency_seconds` - Latency metrics
- `predictions_total` - Total predictions count
- `prediction_throughput_rps` - Requests per second

#### Grafana (Visualization)
http://localhost:3000 (admin/admin)

Pre-configured dashboards for:
- Model performance
- API latency
- Throughput
- Error rates

## What You've Accomplished

In just 10 minutes, you've:

✅ Set up a complete ML infrastructure
✅ Generated sample data
✅ Trained and evaluated a model
✅ Tracked experiments in MLflow
✅ Deployed a production API
✅ Made predictions via REST API
✅ Monitored for data drift
✅ Set up metrics collection

## Next Steps

### Explore the Codebase

1. **Data Pipeline** (`src/ml_pipeline/data/`)
   - See how data validation works
   - Understand preprocessing pipelines

2. **Feature Engineering** (`src/ml_pipeline/features/`)
   - Learn feature creation techniques
   - Understand feature selection

3. **Model Training** (`src/ml_pipeline/models/`)
   - Explore hyperparameter tuning
   - See MLflow integration

4. **Deployment Strategies** (`src/ml_pipeline/deployment/`)
   - Try canary deployments
   - Test blue/green switches

5. **Monitoring** (`src/ml_pipeline/monitoring/`)
   - Understand drift detection
   - Set up alerts

### Try Advanced Features

#### 1. Canary Deployment

```python
from ml_pipeline.deployment.strategies import CanaryDeployment

canary = CanaryDeployment(initial_traffic_percentage=10)
canary.start_deployment()

# Gradually increase traffic
while canary.current_traffic_percentage < 100:
    if canary.should_increment_traffic():
        canary.increment_traffic()
    if canary.should_rollback():
        canary.rollback()
        break
```

#### 2. Blue/Green Deployment

```python
from ml_pipeline.deployment.strategies import BlueGreenDeployment

deployment = BlueGreenDeployment()
deployment.deploy_to_green("v2.0")
deployment.switch_to_green()
```

#### 3. Custom Training Pipeline

```python
from ml_pipeline.orchestration.workflows import training_pipeline

results = training_pipeline(
    data_path="your_data.csv",
    feature_columns=['col1', 'col2'],
    target_column='target',
    numerical_features=['col1', 'col2'],
    model_type="random_forest",  # Try different models!
    tune_hyperparameters=True
)
```

### Customize Configuration

Edit `.env` file or create `.env.local`:

```bash
# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000

# Model Serving
MODEL_SERVICE_PORT=8000

# Deployment
DEPLOYMENT_STRATEGY=canary
CANARY_TRAFFIC_PERCENTAGE=10

# Monitoring
DRIFT_THRESHOLD=0.1
LATENCY_THRESHOLD_MS=100
```

### Add Your Own Data

Replace sample data with your own:

1. Format your data as CSV with features and target
2. Update feature column names in scripts
3. Run training pipeline:

```python
python scripts/run_training.py --data-path your_data.csv
```

## Common Commands

```bash
# Infrastructure
make docker-up          # Start all services
make docker-down        # Stop all services
make docker-logs        # View logs
make docker-clean       # Clean up everything

# Development
make install            # Install dependencies
make test              # Run tests
make lint              # Run linters
make format            # Format code

# ML Operations
make train             # Run training pipeline
make serve             # Start API server
make monitor           # Run monitoring pipeline

# Generate documentation
make docs

# Clean up temporary files
make clean
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker ps

# Check ports are available
lsof -i :5000  # MLflow
lsof -i :4200  # Prefect
lsof -i :8000  # API

# Restart services
docker-compose down
docker-compose up -d
```

### Import Errors

```bash
# Reinstall package
pip install -e .

# Check virtual environment is activated
which python  # Should point to venv
```

### API Not Loading Model

```bash
# Check MLflow is running
curl http://localhost:5000/health

# Check model is registered
# Visit http://localhost:5000 and check Models tab

# Check logs
docker-compose logs model-api
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres

# Check connection
docker-compose exec postgres psql -U mlpipeline -l
```

## Getting Help

- **Documentation:** See `docs/` directory
- **Examples:** Check `notebooks/` directory
- **API Docs:** http://localhost:8000/docs
- **Issues:** Open an issue on GitHub

## What's Next?

Now that you have the basics running, you can:

1. **Learn the Architecture** - Read `docs/ARCHITECTURE.md`
2. **Explore Components** - Each module has detailed comments
3. **Try Examples** - Jupyter notebooks in `notebooks/`
4. **Customize** - Adapt to your use case
5. **Deploy** - Take to production!

## Production Deployment

Ready for production? Check out:
- `docs/DEPLOYMENT.md` - Production deployment guide
- Kubernetes manifests (coming soon)
- CI/CD setup in `.github/workflows/`

---

**Congratulations! You're now running a production-grade ML pipeline! 🚀**

Questions? Open an issue or check the documentation!
