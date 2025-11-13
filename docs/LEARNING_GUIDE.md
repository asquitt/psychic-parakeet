# Learning Guide: Understanding MLOps

This guide helps you learn MLOps concepts through this codebase. Each section includes theory, code examples, and exercises.

## Table of Contents

1. [Introduction to MLOps](#introduction-to-mlops)
2. [Data Pipeline](#data-pipeline)
3. [Feature Engineering](#feature-engineering)
4. [Experiment Tracking](#experiment-tracking)
5. [Model Registry](#model-registry)
6. [Deployment Strategies](#deployment-strategies)
7. [Monitoring](#monitoring)
8. [Orchestration](#orchestration)

## Introduction to MLOps

### What is MLOps?

MLOps (Machine Learning Operations) is a set of practices that combines ML, DevOps, and Data Engineering to:
- Deploy ML models reliably and efficiently
- Monitor model performance in production
- Maintain and update models over time

### Traditional ML vs MLOps

**Traditional ML Workflow:**
```
Data → Notebook → Model → PowerPoint
```

**MLOps Workflow:**
```
Data → Pipeline → Training → Registry → Deployment → Monitoring → Retraining
```

### Why MLOps Matters

1. **Reproducibility:** Can you recreate that model you trained 6 months ago?
2. **Automation:** Deploy new models without manual steps
3. **Monitoring:** Know when models degrade
4. **Collaboration:** Multiple people can work on same pipeline
5. **Reliability:** Production systems need high availability

## Data Pipeline

### Theory

**Key Concepts:**
- **Data Validation:** Ensure data meets expectations before training
- **Data Quality:** Missing values, duplicates, outliers
- **Schema Validation:** Type checking, required fields
- **Preprocessing:** Scaling, encoding, transformations

**Why Validation Matters:**
- Garbage in = Garbage out
- Catch data issues early (cheaper to fix)
- Prevent production failures
- Document data expectations

### Code Example

**File:** `src/ml_pipeline/data/validation.py`

```python
from ml_pipeline.data.validation import DataValidator

# Create validator
validator = DataValidator(
    min_rows=100,              # Minimum data requirements
    max_missing_ratio=0.1,     # Max 10% missing values
    max_duplicate_ratio=0.05   # Max 5% duplicates
)

# Validate data
results = validator.validate_data_quality(df)

# Check for outliers
outliers = validator.detect_outliers(df, method='iqr')
```

### Exercise 1: Data Validation

1. Load the sample data:
   ```python
   import pandas as pd
   df = pd.read_csv('data/raw/train.csv')
   ```

2. Check data quality:
   - How many missing values?
   - Any duplicate rows?
   - Distribution of target variable?

3. Detect outliers in numerical features

4. Create a custom validation rule

### Best Practices

✅ **DO:**
- Validate early in pipeline
- Log validation results
- Set appropriate thresholds
- Document validation rules

❌ **DON'T:**
- Skip validation ("looks good")
- Use arbitrary thresholds
- Ignore validation failures
- Validate only once

## Feature Engineering

### Theory

**Why Feature Engineering?**
- Better features > Better algorithms
- Domain knowledge captured in features
- Can improve accuracy by 10-30%

**Common Techniques:**
1. **Mathematical:** log, sqrt, polynomial
2. **Interactions:** products, ratios between features
3. **Aggregations:** rolling mean, std, min, max
4. **Encoding:** one-hot, label, target encoding

### Code Example

**File:** `src/ml_pipeline/features/engineering.py`

```python
from ml_pipeline.features.engineering import FeatureEngineer

engineer = FeatureEngineer()

# Add mathematical transformations
df = engineer.add_mathematical_features(
    df,
    columns=['age', 'income']
)
# Creates: age_log, age_sqrt, age_squared, income_log, etc.

# Add interactions
df = engineer.add_interaction_features(
    df,
    column_pairs=[('age', 'income')]
)
# Creates: age_x_income_product, age_x_income_ratio, etc.
```

### Exercise 2: Feature Engineering

1. Create features from sample data:
   ```python
   from ml_pipeline.features.engineering import FeatureEngineer

   engineer = FeatureEngineer()
   df_features = engineer.create_feature_set(
       df,
       numerical_columns=['feature_1', 'feature_2'],
       add_interactions=True
   )
   ```

2. Analyze feature importance:
   ```python
   from sklearn.ensemble import RandomForestClassifier

   model = RandomForestClassifier()
   model.fit(X, y)

   importances = pd.DataFrame({
       'feature': feature_names,
       'importance': model.feature_importances_
   }).sort_values('importance', ascending=False)
   ```

3. Select top features:
   ```python
   selected_features = engineer.select_features(
       X, y, k=10, method='mutual_info_classif'
   )
   ```

### Best Practices

✅ **DO:**
- Start simple, add complexity if needed
- Validate new features improve model
- Version your features
- Document feature creation logic

❌ **DON'T:**
- Create too many features (curse of dimensionality)
- Use target information in features (data leakage)
- Ignore domain knowledge
- Forget to apply same features at inference

## Experiment Tracking

### Theory

**What is Experiment Tracking?**
- Log parameters, metrics, and artifacts from ML experiments
- Compare different models and configurations
- Reproduce experiments

**Why MLflow?**
- Open source, no vendor lock-in
- Tracks everything: params, metrics, models, artifacts
- Model registry included
- Works with any ML library

**Key Concepts:**
- **Experiment:** Group of related runs (e.g., "customer_churn")
- **Run:** Single training execution
- **Parameters:** Model hyperparameters
- **Metrics:** Performance metrics (accuracy, loss, etc.)
- **Artifacts:** Files (models, plots, data)

### Code Example

**File:** `src/ml_pipeline/models/training.py`

```python
from ml_pipeline.models.training import ModelTrainer
import mlflow

# Create trainer
trainer = ModelTrainer(experiment_name="my_experiment")

# Train model (automatically logs everything)
model, run_id = trainer.train_model(
    X_train, y_train,
    model_type="xgboost",
    hyperparameters={"n_estimators": 100, "max_depth": 5}
)

# MLflow automatically logs:
# - Parameters: n_estimators, max_depth, model_type
# - Metrics: train_accuracy, cv_mean_accuracy, cv_std_accuracy
# - Artifacts: Model, plots
```

### Exercise 3: Experiment Tracking

1. Train multiple models:
   ```python
   for model_type in ['logistic_regression', 'random_forest', 'xgboost']:
       model, run_id = trainer.train_model(
           X_train, y_train,
           model_type=model_type
       )
   ```

2. View in MLflow UI (http://localhost:5000)

3. Compare models:
   - Which has best accuracy?
   - Which is fastest?
   - Which has smallest size?

4. Retrieve best model:
   ```python
   # Load model from run
   model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")
   ```

### Best Practices

✅ **DO:**
- Log everything (it's cheap)
- Use meaningful experiment names
- Add tags for categorization
- Include notes about interesting findings

❌ **DON'T:**
- Forget to log important parameters
- Overwrite previous experiments
- Use default experiment name
- Skip logging failed runs (learn from failures!)

## Model Registry

### Theory

**What is Model Registry?**
- Central repository for ML models
- Version control for models
- Staging and promotion workflow

**Model Lifecycle:**
```
Trained → None → Staging → Production → Archived
```

**Stages:**
- **None:** Just registered, not ready
- **Staging:** Under testing
- **Production:** Deployed and serving traffic
- **Archived:** Deprecated, kept for history

### Code Example

```python
# Register model
version = trainer.register_model(
    run_id=run_id,
    model_name="customer_churn_model",
    stage="Staging"
)

# Transition to production
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(
    name="customer_churn_model",
    version=version,
    stage="Production"
)

# Load production model
model = mlflow.pyfunc.load_model(
    f"models:/customer_churn_model/Production"
)
```

### Exercise 4: Model Registry

1. Register your best model
2. Transition through stages: Staging → Production
3. Load and compare different versions
4. Archive old version

### Best Practices

✅ **DO:**
- Use descriptive model names
- Test in Staging before Production
- Keep Production stable
- Document model changes

❌ **DON'T:**
- Deploy directly to Production
- Delete models (archive instead)
- Skip testing
- Lose track of which model is live

## Deployment Strategies

### Theory

**Why Different Strategies?**
- Minimize deployment risk
- Enable gradual rollout
- Quick rollback if issues
- Test with real traffic

**Strategies:**

1. **Canary Deployment**
   - Gradually increase traffic to new version
   - Monitor performance
   - Auto-rollback if degradation

2. **Blue/Green Deployment**
   - Two identical environments
   - Instant traffic switch
   - Easy rollback

3. **Shadow Deployment**
   - New version receives copy of traffic
   - Predictions not returned to users
   - Safe comparison

### Code Examples

**Canary:**
```python
from ml_pipeline.deployment.strategies import CanaryDeployment

canary = CanaryDeployment(
    initial_traffic_percentage=10,
    increment_percentage=10,
    rollback_threshold=0.05
)

canary.start_deployment()

# Route request
version = canary.route_request()  # Returns CURRENT or CANARY
```

**Blue/Green:**
```python
from ml_pipeline.deployment.strategies import BlueGreenDeployment

bg = BlueGreenDeployment()
bg.deploy_to_green("v2.0")
bg.switch_to_green()  # Instant switch
```

### Exercise 5: Deployment

1. Implement canary deployment simulation
2. Monitor metrics during rollout
3. Trigger rollback on degradation
4. Compare blue/green vs canary

### Best Practices

✅ **DO:**
- Start with small traffic percentage
- Monitor closely during rollout
- Have rollback plan
- Automate deployment

❌ **DON'T:**
- Deploy all at once
- Ignore monitoring
- Skip testing
- Deploy on Friday (if possible!)

## Monitoring

### Theory

**What to Monitor:**
1. **Data Drift:** Input distribution changes
2. **Concept Drift:** Relationship between X and Y changes
3. **Performance:** Latency, throughput, errors
4. **Model Quality:** Accuracy degradation

**Why Monitor?**
- Models degrade over time
- Data changes
- Early problem detection
- Informed retraining decisions

### Code Examples

**Drift Detection:**
```python
from ml_pipeline.monitoring.drift_detection import DriftDetector

detector = DriftDetector(threshold=0.05)
detector.set_reference_data(train_df)

results = detector.detect_drift(
    production_df,
    numerical_features=['age', 'income']
)

if results['should_retrain']:
    print("Retraining recommended!")
```

**Performance Monitoring:**
```python
from ml_pipeline.monitoring.performance import PerformanceMonitor

monitor = PerformanceMonitor()

monitor.record_prediction(
    latency_ms=45.2,
    prediction=1,
    error=False
)

metrics = monitor.get_current_metrics()
print(f"P95 latency: {metrics['p95_latency_ms']}ms")
```

### Exercise 6: Monitoring

1. Detect drift in production data
2. Set up performance monitoring
3. Define SLA thresholds
4. Create alert rules

### Best Practices

✅ **DO:**
- Monitor continuously
- Set realistic thresholds
- Alert on actionable issues
- Track metrics over time

❌ **DON'T:**
- Monitor only during deployment
- Set too sensitive alerts (alert fatigue)
- Ignore drift warnings
- Wait for users to report issues

## Orchestration

### Theory

**What is Orchestration?**
- Automate multi-step ML workflows
- Handle dependencies between steps
- Retry failed tasks
- Schedule regular runs

**Why Prefect?**
- Pythonic (no DAG DSL)
- Easy local testing
- Modern architecture
- Lightweight

**Key Concepts:**
- **Flow:** Workflow (collection of tasks)
- **Task:** Unit of work
- **Dependencies:** Task execution order
- **Retries:** Automatic retry on failure
- **Caching:** Reuse results

### Code Example

**File:** `src/ml_pipeline/orchestration/workflows.py`

```python
from prefect import flow, task

@task(retries=3, retry_delay_seconds=10)
def load_data(path):
    return pd.read_csv(path)

@task
def train_model(data):
    # Training logic
    return model

@flow
def training_pipeline(data_path):
    data = load_data(data_path)
    model = train_model(data)
    return model
```

### Exercise 7: Orchestration

1. Run training pipeline
2. Simulate failure and watch retry
3. Check task caching
4. Schedule periodic runs

### Best Practices

✅ **DO:**
- Use tasks for reusable units
- Add retries for flaky operations
- Cache expensive computations
- Log task execution

❌ **DON'T:**
- Put everything in one task
- Ignore failures
- Skip error handling
- Make tasks dependent on external state

## Putting It All Together

### Complete Workflow

```python
# 1. Generate data
python scripts/generate_sample_data.py

# 2. Train model (includes validation, features, tracking)
python scripts/run_training.py

# 3. Check MLflow
# Visit http://localhost:5000

# 4. Start serving
make serve

# 5. Make predictions
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {...}}'

# 6. Monitor
python scripts/run_monitoring.py

# 7. If drift detected, retrain
python scripts/run_training.py
```

### Project Challenge

Build your own ML pipeline:

1. Choose a dataset (Kaggle, UCI ML Repository)
2. Implement data validation
3. Engineer features
4. Train multiple models with MLflow
5. Select best model
6. Deploy with API
7. Monitor for drift
8. Set up automated retraining

## Further Learning

### Resources

**Books:**
- "Designing Machine Learning Systems" by Chip Huyen
- "Machine Learning Design Patterns" by Lakshmanan et al.
- "Reliable Machine Learning" by Breck et al.

**Online:**
- MLflow Documentation
- Prefect Documentation
- FastAPI Tutorial
- Prometheus & Grafana Guides

**Practice:**
- Kaggle Competitions
- Open source ML projects
- Deploy your own models

### Next Steps

1. **Understand Each Component:** Read code with comments
2. **Experiment:** Change parameters, try different approaches
3. **Build:** Create your own pipeline for a real problem
4. **Deploy:** Take a model to production
5. **Share:** Contribute improvements back

## Questions & Answers

### Q: When should I retrain my model?

A: Retrain when:
- Data drift exceeds threshold
- Performance degrades significantly
- New data available that wasn't in training
- Business logic changes
- Scheduled interval (e.g., monthly)

### Q: How do I choose deployment strategy?

A: Consider:
- **Canary:** High-risk changes, gradual validation needed
- **Blue/Green:** Need instant rollback, have resources for 2 environments
- **Shadow:** Want extensive testing, can handle duplicate traffic

### Q: What metrics should I monitor?

A: Monitor:
- **System:** Latency, throughput, error rate
- **Data:** Distribution drift, missing values
- **Model:** Accuracy, confidence scores, prediction distribution
- **Business:** ROI, user satisfaction, cost

### Q: How often should I check for drift?

A: Depends on:
- How fast your data changes
- Business criticality
- Resource constraints
- Common: Daily to weekly checks

---

**Happy Learning! 🚀**

Remember: The best way to learn is by doing. Experiment with this codebase, break things, fix them, and build something awesome!
