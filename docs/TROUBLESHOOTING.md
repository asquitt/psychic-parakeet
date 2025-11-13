# Troubleshooting Guide

This comprehensive guide helps diagnose and resolve common issues in the ML pipeline.

## Table of Contents

1. [General Debugging Strategy](#general-debugging-strategy)
2. [Infrastructure Issues](#infrastructure-issues)
3. [Data Pipeline Issues](#data-pipeline-issues)
4. [Training Issues](#training-issues)
5. [Deployment Issues](#deployment-issues)
6. [API Issues](#api-issues)
7. [Performance Issues](#performance-issues)
8. [Monitoring Issues](#monitoring-issues)
9. [Common Error Messages](#common-error-messages)
10. [Diagnostic Tools](#diagnostic-tools)

---

## 1. General Debugging Strategy

###  Systematic Troubleshooting Process

```markdown
Step 1: REPRODUCE
- Can you consistently reproduce the issue?
- What are the exact steps to trigger it?
- Does it happen in all environments?

Step 2: ISOLATE
- When did the issue start?
- What changed recently (code, data, config, infrastructure)?
- Does it affect all users or just some?
- Is it specific to certain inputs?

Step 3: GATHER
- Collect logs (application, system, database)
- Check metrics (CPU, memory, latency, errors)
- Capture example inputs/outputs
- Note timestamps

Step 4: HYPOTHESIZE
- What are possible causes?
- Which is most likely?
- How can you test each hypothesis?

Step 5: TEST
- Test one hypothesis at a time
- Change only one variable
- Verify fix resolves issue
- Ensure no new issues introduced

Step 6: DOCUMENT
- Document root cause
- Document solution
- Update runbooks
- Share with team
```

### Quick Diagnostic Commands

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f model-api
docker-compose logs -f mlflow
docker-compose logs -f prefect-server

# Check resource usage
docker stats

# Test API health
curl http://localhost:8000/health

# Check database connection
docker-compose exec postgres psql -U mlpipeline -c "SELECT version();"

# Check MLflow
curl http://localhost:5000/health

# Check Prefect
curl http://localhost:4200/api/health
```

---

## 2. Infrastructure Issues

### Issue: Services Won't Start

**Symptoms:**
- `docker-compose up` fails
- Containers exit immediately
- Port binding errors

**Diagnosis:**

```bash
# Check Docker daemon
docker info

# Check port availability
lsof -i :5000  # MLflow
lsof -i :4200  # Prefect
lsof -i :8000  # API
lsof -i :5432  # PostgreSQL

# Check Docker logs
docker-compose logs [service-name]

# Check resource constraints
docker system df
df -h
free -h
```

**Solutions:**

```bash
# Port already in use
# Solution 1: Kill process using port
kill -9 $(lsof -t -i:8000)

# Solution 2: Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use different host port

# Out of disk space
# Clean up Docker resources
docker system prune -a
docker volume prune

# Permission issues
sudo chown -R $USER:$USER .

# Restart Docker daemon
sudo systemctl restart docker
```

### Issue: Database Connection Fails

**Symptoms:**
- "Connection refused" errors
- MLflow/Prefect can't connect to PostgreSQL
- Timeout errors

**Diagnosis:**

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U mlpipeline -c "SELECT 1;"

# Check connection string
echo $POSTGRES_HOST
echo $POSTGRES_PORT
```

**Solutions:**

```bash
# PostgreSQL not ready
# Add healthcheck wait
docker-compose up -d postgres
sleep 30  # Wait for PostgreSQL to be ready
docker-compose up -d

# Wrong credentials
# Check .env file
cat .env | grep POSTGRES

# Network issues
# Recreate networks
docker-compose down
docker network prune
docker-compose up -d

# Database doesn't exist
docker-compose exec postgres psql -U mlpipeline -c "CREATE DATABASE mlflow;"
docker-compose exec postgres psql -U mlpipeline -c "CREATE DATABASE prefect;"
```

### Issue: Container Keeps Restarting

**Symptoms:**
- Container status shows "Restarting"
- Service unavailable

**Diagnosis:**

```bash
# Check container logs
docker-compose logs --tail=100 [service-name]

# Check exit code
docker-compose ps

# Inspect container
docker inspect [container-id]

# Check resource limits
docker stats [container-name]
```

**Solutions:**

```bash
# Out of memory
# Increase memory limit in docker-compose.yml
services:
  model-api:
    mem_limit: 2g
    memswap_limit: 2g

# Application error on startup
# Check application logs
# Fix code/configuration issue

# Health check failing
# Adjust health check parameters
healthcheck:
  interval: 60s  # Less frequent
  timeout: 10s   # More time
  retries: 5     # More retries
```

---

## 3. Data Pipeline Issues

### Issue: Data Validation Fails

**Symptoms:**
- "Schema validation failed"
- "Too many missing values"
- Training pipeline fails at validation step

**Diagnosis:**

```python
# Load and inspect data
import pandas as pd

df = pd.read_csv('data/raw/train.csv')

# Check shape
print(f"Shape: {df.shape}")

# Check missing values
print(df.isnull().sum())

# Check dtypes
print(df.dtypes)

# Check for duplicates
print(f"Duplicates: {df.duplicated().sum()}")

# Check statistics
print(df.describe())

# Check specific columns
print(df['target'].value_counts())
```

**Solutions:**

```python
# Missing values above threshold
# Option 1: Impute missing values
from sklearn.impute import SimpleImputer

imputer = SimpleImputer(strategy='mean')
df[numerical_cols] = imputer.fit_transform(df[numerical_cols])

# Option 2: Drop rows with missing values
df = df.dropna(subset=critical_columns)

# Option 3: Adjust threshold
validator = DataValidator(
    max_missing_ratio=0.15  # Allow 15% missing
)

# Schema mismatch
# Check expected vs actual columns
expected_columns = ['feature1', 'feature2', 'target']
actual_columns = df.columns.tolist()
missing = set(expected_columns) - set(actual_columns)
extra = set(actual_columns) - set(expected_columns)

print(f"Missing columns: {missing}")
print(f"Extra columns: {extra}")

# Duplicates
# Remove duplicates
df = df.drop_duplicates(subset=['id'], keep='first')
```

### Issue: Feature Engineering Fails

**Symptoms:**
- "ValueError: could not convert string to float"
- "ZeroDivisionError"
- NaN or Inf values in features

**Diagnosis:**

```python
# Check for non-numeric values
df.select_dtypes(include=['object']).head()

# Check for zero values (before division)
print((df == 0).sum())

# Check for Inf/NaN
print(np.isinf(df.select_dtypes(include=[np.number])).sum())
print(np.isnan(df.select_dtypes(include=[np.number])).sum())

# Identify problematic features
for col in df.columns:
    if df[col].isnull().any():
        print(f"{col}: {df[col].isnull().sum()} NaN values")
    if np.isinf(df[col]).any():
        print(f"{col}: {np.isinf(df[col]).sum()} Inf values")
```

**Solutions:**

```python
# Handle division by zero
df['ratio'] = df['numerator'] / (df['denominator'] + 1e-10)  # Add small epsilon

# Handle log of zero/negative
df['log_feature'] = np.log1p(df['feature'].clip(lower=0))  # log(1 + x), clip negative

# Replace Inf with NaN, then handle
df = df.replace([np.inf, -np.inf], np.nan)
df = df.fillna(0)  # or other strategy

# Convert string columns
df['numeric_col'] = pd.to_numeric(df['string_col'], errors='coerce')

# Handle categorical variables
df = pd.get_dummies(df, columns=['categorical_col'])
```

### Issue: Data Drift Not Detecting Changes

**Symptoms:**
- Drift detector always returns "no drift"
- Known distribution changes not detected

**Diagnosis:**

```python
from ml_pipeline.monitoring.drift_detection import DriftDetector

detector = DriftDetector(threshold=0.05)
detector.set_reference_data(train_df)

# Check reference data was set
print(f"Reference data shape: {detector.reference_data.shape}")

# Manually check distributions
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

for i, col in enumerate(['feature1', 'feature2']):
    ax = axes[i // 2, i % 2]
    train_df[col].hist(ax=ax, alpha=0.5, label='Reference', bins=50)
    production_df[col].hist(ax=ax, alpha=0.5, label='Current', bins=50)
    ax.legend()
    ax.set_title(col)

plt.tight_layout()
plt.savefig('distribution_comparison.png')

# Check K-S test manually
from scipy import stats
for col in numerical_columns:
    statistic, p_value = stats.ks_2samp(
        train_df[col],
        production_df[col]
    )
    print(f"{col}: p-value = {p_value}")
```

**Solutions:**

```python
# Threshold too strict
detector = DriftDetector(threshold=0.10)  # Less sensitive

# Not enough samples
# Ensure enough data for statistical power
assert len(production_df) > 100, "Need more samples"

# Features not comparable (different scales)
# Normalize before comparison
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
train_normalized = scaler.fit_transform(train_df[numerical_columns])
prod_normalized = scaler.transform(production_df[numerical_columns])

# Use normalized data for drift detection

# Wrong reference data
# Ensure using correct reference dataset
detector.set_reference_data(correct_train_df)
```

---

## 4. Training Issues

### Issue: Training Takes Too Long

**Symptoms:**
- Training doesn't complete
- Hyperparameter tuning times out
- Resource usage high

**Diagnosis:**

```python
# Profile training code
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Training code here
model.fit(X_train, y_train)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 time consumers

# Check data size
print(f"Training samples: {len(X_train)}")
print(f"Features: {X_train.shape[1]}")
print(f"Memory usage: {X_train.nbytes / 1024**2:.2f} MB")

# Monitor resource usage
import psutil
print(f"CPU usage: {psutil.cpu_percent()}%")
print(f"Memory usage: {psutil.virtual_memory().percent}%")
```

**Solutions:**

```python
# Too much data
# Solution 1: Sample data
X_train_sample = X_train.sample(frac=0.5, random_state=42)
y_train_sample = y_train.loc[X_train_sample.index]

# Solution 2: Use incremental learning
from sklearn.linear_model import SGDClassifier

model = SGDClassifier()
for chunk in pd.read_csv('data.csv', chunksize=10000):
    model.partial_fit(chunk[features], chunk['target'])

# Too many features
# Solution: Feature selection
from sklearn.feature_selection import SelectKBest

selector = SelectKBest(k=50)
X_train_reduced = selector.fit_transform(X_train, y_train)

# Too complex model
# Solution: Simplify model
model = XGBClassifier(
    n_estimators=50,  # Reduce from 1000
    max_depth=3,      # Reduce from 10
    n_jobs=-1         # Use all CPUs
)

# Inefficient hyperparameter search
# Solution: Random search instead of grid search
from sklearn.model_selection import RandomizedSearchCV

search = RandomizedSearchCV(
    model,
    param_distributions=param_grid,
    n_iter=20,  # Instead of exhaustive grid
    cv=3,       # Reduce CV folds
    n_jobs=-1
)

# Use early stopping
model = XGBClassifier(
    early_stopping_rounds=10,
    eval_metric='logloss'
)
model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)]
)
```

### Issue: Model Not Training (Loss Not Decreasing)

**Symptoms:**
- Loss stays constant or increases
- Accuracy doesn't improve
- Model predicts same class for all samples

**Diagnosis:**

```python
# Check data
print(f"Unique targets: {y_train.nunique()}")
print(f"Target distribution:\n{y_train.value_counts()}")

# Check for data leakage
# Features shouldn't correlate perfectly with target
for col in X_train.columns:
    corr = X_train[col].corr(y_train)
    if abs(corr) > 0.99:
        print(f"Warning: {col} has correlation {corr} with target!")

# Check feature scaling
print(X_train.describe())

# Check for NaN/Inf
print(f"NaN in features: {X_train.isnull().sum().sum()}")
print(f"Inf in features: {np.isinf(X_train).sum().sum()}")

# Check class imbalance
print(f"Class 0: {(y_train == 0).sum()}")
print(f"Class 1: {(y_train == 1).sum()}")
```

**Solutions:**

```python
# Class imbalance
# Solution 1: Use class weights
from sklearn.utils.class_weight import compute_class_weight

class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)

model = XGBClassifier(scale_pos_weight=class_weights[1]/class_weights[0])

# Solution 2: Oversample minority class
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# Features not scaled
# Solution: Scale features
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Learning rate too high/low
# Solution: Tune learning rate
for lr in [0.001, 0.01, 0.1, 0.3]:
    model = XGBClassifier(learning_rate=lr)
    model.fit(X_train, y_train)
    score = model.score(X_val, y_val)
    print(f"LR {lr}: {score:.4f}")

# Model too simple for problem
# Solution: Increase model complexity
model = XGBClassifier(
    n_estimators=200,  # More trees
    max_depth=7,       # Deeper trees
    learning_rate=0.05
)
```

### Issue: Model Overfitting

**Symptoms:**
- High training accuracy, low test accuracy
- Large gap between train/val scores
- Model performs poorly on new data

**Diagnosis:**

```python
# Compare train vs test scores
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)

print(f"Train accuracy: {train_score:.4f}")
print(f"Test accuracy: {test_score:.4f}")
print(f"Gap: {train_score - test_score:.4f}")

# Check learning curves
from sklearn.model_selection import learning_curve

train_sizes, train_scores, val_scores = learning_curve(
    model, X_train, y_train,
    train_sizes=np.linspace(0.1, 1.0, 10),
    cv=5
)

# Plot learning curves
import matplotlib.pyplot as plt

plt.plot(train_sizes, train_scores.mean(axis=1), label='Train')
plt.plot(train_sizes, val_scores.mean(axis=1), label='Validation')
plt.xlabel('Training Size')
plt.ylabel('Score')
plt.legend()
plt.savefig('learning_curves.png')
```

**Solutions:**

```python
# Regularization
# L2 regularization
model = LogisticRegression(C=0.1)  # Smaller C = more regularization

# L1 regularization (feature selection)
model = LogisticRegression(penalty='l1', C=0.1, solver='liblinear')

# For tree models: limit complexity
model = XGBClassifier(
    max_depth=3,              # Reduce from 6
    min_child_weight=5,       # Increase from 1
    gamma=0.1,                # Minimum loss reduction
    subsample=0.8,            # Sample 80% of data
    colsample_bytree=0.8,     # Sample 80% of features
    reg_alpha=0.1,            # L1 regularization
    reg_lambda=1.0            # L2 regularization
)

# More training data
# Collect more data
# Or use data augmentation

# Reduce features
# Use feature selection
from sklearn.feature_selection import RFE

selector = RFE(model, n_features_to_select=20)
X_train_selected = selector.fit_transform(X_train, y_train)

# Ensemble methods
from sklearn.ensemble import BaggingClassifier

ensemble = BaggingClassifier(
    base_estimator=model,
    n_estimators=10,
    max_samples=0.8,
    max_features=0.8
)

# Cross-validation
# Use CV during training
from sklearn.model_selection import cross_val_score

cv_scores = cross_val_score(model, X_train, y_train, cv=5)
print(f"CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
```

---

## 5. Deployment Issues

### Issue: Model Fails to Load

**Symptoms:**
- "FileNotFoundError: model not found"
- "Model failed to load"
- API returns 500 errors on startup

**Diagnosis:**

```bash
# Check model file exists
ls -lh models/

# Check MLflow for registered models
docker-compose exec mlflow mlflow models list

# Check model registry
curl http://localhost:5000/api/2.0/mlflow/registered-models/list

# Check API logs
docker-compose logs model-api | grep -i "error\|exception"

# Try loading model manually
python -c "import mlflow; model = mlflow.pyfunc.load_model('models:/production_model/Production'); print('Success')"
```

**Solutions:**

```python
# Model not registered
# Register model first
from ml_pipeline.models.training import ModelTrainer

trainer = ModelTrainer("my_experiment")
version = trainer.register_model(
    run_id="your-run-id",
    model_name="production_model",
    stage="Production"
)

# Wrong model stage
# Check which stage model is in
from mlflow.tracking import MlflowClient

client = MlflowClient()
versions = client.get_latest_versions("production_model")
for v in versions:
    print(f"Version {v.version}: {v.current_stage}")

# Transition to correct stage
client.transition_model_version_stage(
    name="production_model",
    version="1",
    stage="Production"
)

# MLflow server not accessible
# Check MLflow is running
curl http://localhost:5000/health

# Check connection from API container
docker-compose exec model-api curl http://mlflow:5000/health

# Fix: Update MLFLOW_TRACKING_URI in .env

# Incompatible model version
# Model trained with different library version
# Solution: Retrain model with current environment
# Or use same library versions
```

### Issue: Canary Deployment Not Routing Traffic

**Symptoms:**
- All traffic going to old version
- Canary metrics not updating

**Diagnosis:**

```python
from ml_pipeline.deployment.strategies import CanaryDeployment

canary = CanaryDeployment()

# Check deployment status
print(f"Active: {canary.is_active}")
print(f"Traffic %: {canary.current_traffic_percentage}")

# Test routing manually
for i in range(100):
    version = canary.route_request()
    print(version, end=' ')
```

**Solutions:**

```python
# Deployment not started
canary.start_deployment()

# Traffic percentage at 0
# Manually set traffic
canary.current_traffic_percentage = 10

# Not incrementing
# Check increment conditions
if canary.should_increment_traffic():
    canary.increment_traffic()
else:
    print("Conditions not met for increment:")
    print(f"  Time since start: {canary.time_since_start}")
    print(f"  Performance acceptable: {not canary.should_rollback()}")

# Rollback triggered incorrectly
# Adjust thresholds
canary = CanaryDeployment(
    rollback_threshold=0.10  # 10% degradation allowed
)
```

### Issue: Auto-Rollback Not Working

**Symptoms:**
- Performance degraded but no rollback
- Rollback doesn't revert traffic

**Diagnosis:**

```python
# Check if rollback condition met
should_rollback = canary.should_rollback()
print(f"Should rollback: {should_rollback}")

# Check metrics
canary_metrics = canary.get_canary_metrics()
current_metrics = canary.get_current_metrics()

print(f"Canary error rate: {canary_metrics['error_rate']}")
print(f"Current error rate: {current_metrics['error_rate']}")

# Check threshold
print(f"Rollback threshold: {canary.rollback_threshold}")
```

**Solutions:**

```python
# Not collecting metrics
# Ensure metrics being recorded
canary.record_metrics(
    version=ModelVersion.CANARY,
    metrics=DeploymentMetrics(
        latency_ms=latency,
        error_rate=errors/total,
        throughput_rps=rps
    )
)

# Threshold too lenient
canary.rollback_threshold = 0.03  # 3% degradation triggers rollback

# Manual rollback
canary.rollback()
```

---

## 6. API Issues

### Issue: API Returns 500 Errors

**Symptoms:**
- Internal server error
- API crashes on certain requests

**Diagnosis:**

```bash
# Check API logs
docker-compose logs model-api --tail=100

# Test API manually
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"feature1": 1.0}}'

# Check API is running
curl http://localhost:8000/health

# Check Python errors
docker-compose exec model-api python -c "from ml_pipeline.serving.api import app; print('OK')"
```

**Solutions:**

```python
# Missing dependencies
# Install in container
docker-compose exec model-api pip install missing-package

# Or rebuild
docker-compose build model-api
docker-compose up -d model-api

# Model loading error
# Check model exists and is accessible
# See "Model Fails to Load" section above

# Invalid request format
# Validate request schema matches expected
# Check PredictionRequest model in api.py

# Unhandled exception
# Add better error handling in API
@app.post("/predict")
async def predict(request: PredictionRequest):
    try:
        # Prediction code
        return prediction
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

### Issue: API Slow/High Latency

**Symptoms:**
- Requests take >1 second
- Timeouts
- Poor user experience

**Diagnosis:**

```python
# Profile API endpoint
import time

@app.post("/predict")
async def predict(request: PredictionRequest):
    start = time.time()

    # Time each step
    t1 = time.time()
    features = load_features(request)
    print(f"Load features: {(time.time() - t1)*1000:.2f}ms")

    t2 = time.time()
    processed = preprocess(features)
    print(f"Preprocess: {(time.time() - t2)*1000:.2f}ms")

    t3 = time.time()
    prediction = model.predict(processed)
    print(f"Prediction: {(time.time() - t3)*1000:.2f}ms")

    print(f"Total: {(time.time() - start)*1000:.2f}ms")

    return prediction

# Check resource usage
docker stats model-api

# Check database connection pooling
# Check network latency
```

**Solutions:**

```python
# Model inference slow
# Solution 1: Model optimization (quantization, pruning)
# Solution 2: Cache predictions
from functools import lru_cache

@lru_cache(maxsize=1000)
def predict_cached(features_hash):
    return model.predict(features)

# Feature loading slow
# Solution: Cache features
import redis

redis_client = redis.Redis(host='redis')

def get_features(user_id):
    cached = redis_client.get(f"features:{user_id}")
    if cached:
        return json.loads(cached)

    features = fetch_from_db(user_id)
    redis_client.setex(f"features:{user_id}", 3600, json.dumps(features))
    return features

# Database queries slow
# Solution: Connection pooling, indexing
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    db_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)

# Synchronous code blocking
# Solution: Use async/await
@app.post("/predict")
async def predict(request: PredictionRequest):
    # Use async operations
    features = await fetch_features_async(request.user_id)
    prediction = await model.predict_async(features)
    return prediction
```

### Issue: API High Memory Usage

**Symptoms:**
- Container OOM killed
- Memory usage growing
- Service crashes

**Diagnosis:**

```bash
# Monitor memory
docker stats model-api

# Check memory leaks
# Install memory_profiler
pip install memory_profiler

# Profile endpoint
from memory_profiler import profile

@profile
@app.post("/predict")
async def predict(request):
    # endpoint code
    pass

# Check model size
import sys
print(f"Model size: {sys.getsizeof(model) / 1024**2:.2f} MB")
```

**Solutions:**

```python
# Model too large
# Solution: Model compression
# Quantize model to INT8
import onnxruntime as ort

# Convert to ONNX
onnx_model = convert_to_onnx(model)

# Quantize
quantized_model = quantize_dynamic(onnx_model)

# Memory leak
# Solution: Explicitly delete large objects
prediction = model.predict(features)
del features  # Free memory
import gc
gc.collect()

# Too many model copies
# Solution: Singleton pattern
class ModelSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = load_model()
        return cls._instance

# Unbounded cache
# Solution: Limit cache size
from functools import lru_cache

@lru_cache(maxsize=1000)  # Limit cache size
def predict_cached(features_hash):
    return model.predict(features)

# Batch size too large
# Solution: Reduce batch size
predictions = []
for batch in chunks(requests, size=32):  # Smaller batches
    preds = model.predict(batch)
    predictions.extend(preds)
```

---

## 7. Performance Issues

### Issue: Drift Detection Too Slow

**Symptoms:**
- Drift check takes >10 minutes
- Times out
- Blocks other operations

**Diagnosis:**

```python
import time

detector = DriftDetector()

start = time.time()
results = detector.detect_drift(production_df, numerical_features)
elapsed = time.time() - start

print(f"Drift detection took {elapsed:.2f} seconds")
print(f"Samples: {len(production_df)}")
print(f"Features: {len(numerical_features)}")
```

**Solutions:**

```python
# Too many samples
# Solution 1: Sample data
production_sample = production_df.sample(n=10000, random_state=42)
results = detector.detect_drift(production_sample, numerical_features)

# Solution 2: Use faster tests
# KS test is O(n log n), can be slow for large datasets
# Use simpler metrics for large data
def fast_drift_check(ref, curr):
    # Compare simple statistics
    ref_mean, ref_std = ref.mean(), ref.std()
    curr_mean, curr_std = curr.mean(), curr.std()

    mean_change = abs(curr_mean - ref_mean) / ref_std
    std_change = abs(curr_std - ref_std) / ref_std

    return mean_change > 0.5 or std_change > 0.5

# Too many features
# Solution: Check most important features only
important_features = ['feature1', 'feature2', 'feature3']
results = detector.detect_drift(production_df, important_features)

# Run drift detection async
import asyncio

async def check_drift_async():
    # Run in thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        detector.detect_drift,
        production_df,
        numerical_features
    )
    return result
```

### Issue: Training Pipeline Fails in Prefect

**Symptoms:**
- Prefect flow shows failed
- Tasks timeout
- Dependencies not installed

**Diagnosis:**

```bash
# Check Prefect flow runs
curl http://localhost:4200/api/flow_runs

# Check task logs in Prefect UI
# http://localhost:4200

# Check Prefect worker logs
docker-compose logs prefect-worker

# Test task locally
python -c "
from ml_pipeline.orchestration.workflows import load_data_task
result = load_data_task('data/raw/train.csv')
print('Success')
"
```

**Solutions:**

```python
# Task timeout
# Increase timeout in task decorator
@task(
    timeout_seconds=3600,  # 1 hour
    retries=3
)
def train_model_task(...):
    pass

# Dependencies not installed
# Ensure requirements installed in Prefect worker
# Add to Dockerfile.worker

# Task caching issues
# Clear cache
@task(
    cache_key_fn=None,  # Disable caching
)

# Or update cache key function
@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1)
)

# Memory issues in tasks
# Solution: Use smaller batch sizes
# Or increase worker resources in docker-compose.yml
services:
  prefect-worker:
    mem_limit: 4g

# Task fails silently
# Add better logging
@task
def my_task():
    try:
        # Task code
        logger.info("Task completed successfully")
    except Exception as e:
        logger.error(f"Task failed: {e}", exc_info=True)
        raise
```

---

## 8. Monitoring Issues

### Issue: Prometheus Not Collecting Metrics

**Symptoms:**
- Empty Prometheus dashboards
- No metrics data
- "No data" in Grafana

**Diagnosis:**

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Prometheus config
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml

# Test metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus logs
docker-compose logs prometheus
```

**Solutions:**

```yaml
# Prometheus not scraping
# Fix scrape config in prometheus.yml
scrape_configs:
  - job_name: 'model-api'
    static_configs:
      - targets: ['model-api:8000']  # Use service name, not localhost

# Restart Prometheus
docker-compose restart prometheus

# Metrics not exposed
# Ensure Prometheus instrumentator added to FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

# Wrong metrics path
# Update prometheus.yml
scrape_configs:
  - job_name: 'model-api'
    metrics_path: '/metrics'  # Ensure correct path
    static_configs:
      - targets: ['model-api:8000']

# Network issues
# Ensure services on same network
docker-compose exec prometheus ping model-api
```

### Issue: Grafana Can't Connect to Prometheus

**Symptoms:**
- Grafana datasource shows "Error"
- No data in Grafana dashboards

**Diagnosis:**

```bash
# Check Grafana datasources
curl -u admin:admin http://localhost:3000/api/datasources

# Test connection from Grafana to Prometheus
docker-compose exec grafana curl http://prometheus:9090/api/v1/query?query=up

# Check Grafana logs
docker-compose logs grafana
```

**Solutions:**

```yaml
# Fix datasource URL
# In config/grafana/datasources/prometheus.yml
datasources:
  - name: Prometheus
    url: http://prometheus:9090  # Use service name

# Restart Grafana
docker-compose restart grafana

# Manually add datasource in UI
# http://localhost:3000/datasources
# URL: http://prometheus:9090
# Access: Server (default)

# Network issues
# Ensure on same network
networks:
  ml-pipeline:
    driver: bridge

services:
  grafana:
    networks:
      - ml-pipeline
  prometheus:
    networks:
      - ml-pipeline
```

---

## 9. Common Error Messages

### "ImportError: No module named 'ml_pipeline'"

```bash
# Solution: Install package
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/project/src"
```

### "KeyError: 'feature_name'"

```python
# Solution: Check feature names match
print("Expected features:", model.feature_names_)
print("Actual features:", X.columns.tolist())

# Add missing features
for feature in model.feature_names_:
    if feature not in X.columns:
        X[feature] = 0  # Or appropriate default
```

### "mlflow.exceptions.MlflowException: Run ID not found"

```bash
# Solution: Check run exists
mlflow runs list --experiment-name my_experiment

# Or use correct tracking URI
export MLFLOW_TRACKING_URI=http://localhost:5000
```

### "psycopg2.OperationalError: could not connect to server"

```bash
# Solution: Wait for PostgreSQL to be ready
./scripts/wait-for-it.sh postgres:5432 -- echo "PostgreSQL is up"

# Or add depends_on with healthcheck
services:
  mlflow:
    depends_on:
      postgres:
        condition: service_healthy
```

---

## 10. Diagnostic Tools

### System Diagnostic Script

```bash
#!/bin/bash
# scripts/diagnose.sh

echo "=== System Diagnostics ==="

echo "\n1. Docker Status:"
docker info | grep -E 'Running|CPUs|Total Memory'

echo "\n2. Container Status:"
docker-compose ps

echo "\n3. Service Health:"
curl -s http://localhost:5000/health | jq . || echo "MLflow: DOWN"
curl -s http://localhost:4200/api/health | jq . || echo "Prefect: DOWN"
curl -s http://localhost:8000/health | jq . || echo "API: DOWN"

echo "\n4. Database Connection:"
docker-compose exec -T postgres pg_isready -U mlpipeline

echo "\n5. Disk Usage:"
df -h | grep -E 'Filesystem|/$'

echo "\n6. Memory Usage:"
free -h

echo "\n7. Recent Errors (last 10):"
docker-compose logs --tail=100 | grep -i error | tail -10

echo "\n8. Port Usage:"
lsof -i :5000,4200,8000,5432,9090,3000 | grep LISTEN

echo "\n=== Diagnostics Complete ==="
```

### Performance Profiling Script

```python
# scripts/profile_api.py
import requests
import time
import statistics

def profile_api(endpoint, n_requests=100):
    """Profile API endpoint performance."""
    latencies = []

    for i in range(n_requests):
        start = time.time()
        response = requests.post(
            endpoint,
            json={"features": {"feature1": 1.0, "feature2": 2.0}}
        )
        latency = (time.time() - start) * 1000
        latencies.append(latency)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")

    print(f"Requests: {n_requests}")
    print(f"Mean latency: {statistics.mean(latencies):.2f}ms")
    print(f"Median latency: {statistics.median(latencies):.2f}ms")
    print(f"P95 latency: {sorted(latencies)[int(0.95*len(latencies))]:.2f}ms")
    print(f"P99 latency: {sorted(latencies)[int(0.99*len(latencies))]:.2f}ms")
    print(f"Max latency: {max(latencies):.2f}ms")

if __name__ == "__main__":
    profile_api("http://localhost:8000/predict")
```

### Log Analysis Script

```bash
#!/bin/bash
# scripts/analyze_logs.sh

echo "=== Log Analysis ==="

echo "\n1. Error Summary:"
docker-compose logs | grep -i error | cut -d'|' -f2 | sort | uniq -c | sort -rn | head -10

echo "\n2. Warning Summary:"
docker-compose logs | grep -i warning | cut -d'|' -f2 | sort | uniq -c | sort -rn | head -10

echo "\n3. Recent Critical Events:"
docker-compose logs --since 1h | grep -E 'critical|fatal|emergency'

echo "\n4. Request Volume:"
docker-compose logs model-api | grep "POST /predict" | wc -l

echo "\n5. Failed Predictions:"
docker-compose logs model-api | grep "prediction failed" | wc -l
```

---

## Quick Reference

### Essential Commands

```bash
# Restart everything
docker-compose down && docker-compose up -d

# View logs
docker-compose logs -f [service]

# Execute command in container
docker-compose exec [service] [command]

# Check resource usage
docker stats

# Clean up Docker
docker system prune -a

# Test API
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"features": {}}'

# View MLflow experiments
mlflow experiments list

# Check Prefect flows
prefect flow run list
```

### Getting Help

1. Check logs first
2. Review this troubleshooting guide
3. Search GitHub issues
4. Ask in team Slack
5. Create detailed bug report

**Remember:** Most issues can be resolved by:
- Restarting services
- Checking logs
- Verifying configuration
- Ensuring dependencies installed

---

**Need more help?** Open an issue with:
- Error message
- Steps to reproduce
- Environment details
- Relevant logs
