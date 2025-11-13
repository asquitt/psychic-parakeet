# Production ML Best Practices Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Pre-Production Checklist](#pre-production-checklist)
3. [Model Development Best Practices](#model-development-best-practices)
4. [Data Management](#data-management)
5. [Model Training](#model-training)
6. [Model Evaluation](#model-evaluation)
7. [Deployment Best Practices](#deployment-best-practices)
8. [Monitoring & Observability](#monitoring--observability)
9. [Incident Response](#incident-response)
10. [Performance Optimization](#performance-optimization)
11. [Security](#security)
12. [Team Collaboration](#team-collaboration)
13. [Cost Management](#cost-management)
14. [Common Pitfalls](#common-pitfalls)

---

## 1. Introduction

This guide compiles battle-tested best practices for production ML systems based on:
- Industry standards from Google, Netflix, Uber, Airbnb
- Academic research (MLOps papers)
- Lessons learned from production failures
- Field experience from ML practitioners

### The Production ML Maturity Model

```
Level 0: Manual Process
└─ Notebooks, manual deployment, no monitoring

Level 1: ML Pipeline Automation
├─ Automated training
├─ Model versioning
└─ Basic monitoring

Level 2: CI/CD for ML
├─ Automated testing
├─ Automated deployment
├─ Data validation
└─ Feature engineering automation

Level 3: Continuous Training & Monitoring
├─ Automated retraining
├─ Drift detection
├─ A/B testing
└─ Production monitoring

Level 4: Full MLOps
├─ Feature stores
├─ Model governance
├─ Advanced monitoring
└─ Multi-model orchestration
```

**Our Current System: Level 2-3** (Strong CI/CD, good monitoring, basic continuous training)

---

## 2. Pre-Production Checklist

### 2.1 Business Requirements

```markdown
✅ Problem Definition
- [ ] Clear success metrics defined
- [ ] Baseline performance established
- [ ] Minimum acceptable performance threshold set
- [ ] Business impact quantified
- [ ] Stakeholders aligned

✅ Product Requirements
- [ ] Latency requirements (p50, p95, p99)
- [ ] Throughput requirements (RPS)
- [ ] Availability requirements (99%, 99.9%, 99.99%)
- [ ] Accuracy requirements
- [ ] Freshness requirements (how often to retrain)
```

### 2.2 Technical Requirements

```markdown
✅ Data Requirements
- [ ] Data volume sufficient (1000x features minimum)
- [ ] Data quality acceptable (< 5% missing)
- [ ] Data labeling process defined
- [ ] Data collection automated
- [ ] Data storage strategy defined

✅ Model Requirements
- [ ] Model complexity appropriate for problem
- [ ] Model size fits memory constraints
- [ ] Inference time meets latency requirements
- [ ] Model interpretability requirements met
- [ ] Model bias evaluated and acceptable

✅ Infrastructure Requirements
- [ ] Compute resources provisioned
- [ ] Storage capacity planned
- [ ] Network bandwidth sufficient
- [ ] Backup and disaster recovery planned
- [ ] Scaling strategy defined
```

### 2.3 Operational Requirements

```markdown
✅ Monitoring Setup
- [ ] Model performance metrics defined
- [ ] System performance metrics tracked
- [ ] Data quality monitoring in place
- [ ] Drift detection configured
- [ ] Alerting rules defined
- [ ] On-call rotation established

✅ Documentation
- [ ] Model card created
- [ ] API documentation complete
- [ ] Runbook for incidents
- [ ] Architecture diagram
- [ ] Deployment guide

✅ Testing
- [ ] Unit tests (> 80% coverage)
- [ ] Integration tests
- [ ] Performance tests
- [ ] Load tests
- [ ] Shadow testing completed
```

### 2.4 Compliance & Legal

```markdown
✅ Regulatory Compliance
- [ ] GDPR compliance (if EU data)
- [ ] CCPA compliance (if CA data)
- [ ] HIPAA compliance (if healthcare)
- [ ] Data retention policies
- [ ] Privacy impact assessment

✅ Ethical Considerations
- [ ] Bias testing completed
- [ ] Fairness metrics evaluated
- [ ] Explainability requirements met
- [ ] Right to explanation supported
- [ ] Ethical review completed
```

---

## 3. Model Development Best Practices

### 3.1 Experiment Tracking

**Problem:** "I can't reproduce that great model from 3 months ago"

**Solution:**

```python
# ALWAYS log everything with MLflow
with mlflow.start_run(run_name="experiment_v42"):
    # Log code version
    mlflow.log_param("git_commit", get_git_commit())

    # Log data version
    mlflow.log_param("data_version", "20240115")

    # Log hyperparameters
    mlflow.log_params({
        "learning_rate": 0.01,
        "n_estimators": 100,
        "max_depth": 5
    })

    # Log metrics
    mlflow.log_metrics({
        "train_accuracy": 0.95,
        "val_accuracy": 0.89,
        "test_accuracy": 0.87
    })

    # Log artifacts
    mlflow.log_artifact("feature_importance.png")

    # Log model with signature
    signature = infer_signature(X_train, model.predict(X_train))
    mlflow.sklearn.log_model(model, "model", signature=signature)
```

**Best Practices:**

✅ **DO:**
- Log every experiment, even failures
- Use descriptive run names
- Track data versions
- Log Git commit hashes
- Save model signatures
- Document unusual findings

❌ **DON'T:**
- Overwrite previous experiments
- Use default experiment names
- Forget to log failures
- Skip logging hyperparameters

### 3.2 Code Quality

**Standards:**

```python
# Use type hints
def train_model(
    X: np.ndarray,
    y: np.ndarray,
    model_type: str = "xgboost"
) -> Tuple[Any, str]:
    """
    Train a machine learning model.

    Args:
        X: Training features of shape (n_samples, n_features)
        y: Training targets of shape (n_samples,)
        model_type: Type of model to train

    Returns:
        Tuple of (trained_model, run_id)

    Raises:
        ValueError: If model_type is unknown
    """
    pass

# Use dataclasses for configuration
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Model training configuration."""
    learning_rate: float = 0.01
    n_estimators: int = 100
    max_depth: int = 5
    random_state: int = 42

# Use enums for constants
from enum import Enum

class ModelStage(Enum):
    """MLflow model registry stages."""
    NONE = "None"
    STAGING = "Staging"
    PRODUCTION = "Production"
    ARCHIVED = "Archived"
```

**Code Review Checklist:**

```markdown
✅ Functionality
- [ ] Code works as expected
- [ ] Edge cases handled
- [ ] Error handling present
- [ ] Input validation

✅ Readability
- [ ] Clear variable names
- [ ] Functions < 50 lines
- [ ] Docstrings present
- [ ] Type hints used

✅ Testing
- [ ] Unit tests present
- [ ] Test coverage > 80%
- [ ] Integration tests
- [ ] Edge cases tested

✅ Performance
- [ ] No obvious inefficiencies
- [ ] Proper data structures used
- [ ] Memory leaks checked
- [ ] Benchmarks if performance-critical

✅ Security
- [ ] No hardcoded secrets
- [ ] Input sanitization
- [ ] SQL injection prevention
- [ ] XSS prevention
```

---

## 4. Data Management

### 4.1 Data Quality Monitoring

**The 5 Pillars of Data Quality:**

1. **Completeness**: No missing values (or acceptable %)
2. **Consistency**: Data follows schema
3. **Accuracy**: Data represents reality
4. **Timeliness**: Data is fresh
5. **Validity**: Data in correct format/range

**Implementation:**

```python
class DataQualityMonitor:
    """
    Comprehensive data quality monitoring.

    Checks:
    - Schema validation
    - Missing values
    - Outliers
    - Distribution changes
    - Referential integrity
    """

    def validate_batch(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run all quality checks."""
        results = {}

        # 1. Completeness
        results['completeness'] = self.check_completeness(df)

        # 2. Consistency
        results['consistency'] = self.check_consistency(df)

        # 3. Accuracy (statistical checks)
        results['accuracy'] = self.check_accuracy(df)

        # 4. Timeliness
        results['timeliness'] = self.check_timeliness(df)

        # 5. Validity
        results['validity'] = self.check_validity(df)

        return results

    def check_completeness(self, df):
        """Check for missing values."""
        missing_pct = df.isnull().sum() / len(df)
        threshold = 0.05  # 5% missing acceptable

        violations = missing_pct[missing_pct > threshold]
        return {
            'passed': len(violations) == 0,
            'violations': violations.to_dict()
        }
```

**Best Practices:**

✅ **DO:**
- Monitor data quality continuously
- Set up alerts for quality degradation
- Track data quality metrics over time
- Document acceptable quality levels
- Automate quality reports

❌ **DON'T:**
- Assume data quality is constant
- Ignore small quality issues
- Skip validation for "trusted" sources
- Hard-code quality thresholds

### 4.2 Data Versioning

**Why Version Data?**
- Reproducibility: Recreate exact model
- Debugging: Identify problematic data
- Rollback: Revert to known-good data
- Compliance: Audit trail

**Implementation with DVC:**

```bash
# Initialize DVC
dvc init

# Track data file
dvc add data/train.csv

# Commit tracking file
git add data/train.csv.dvc .gitignore
git commit -m "Track training data v1.0"

# Tag data version
git tag -a "data-v1.0" -m "Initial training data"

# Push data to remote storage
dvc push

# Later: Retrieve specific data version
git checkout data-v1.0
dvc pull
```

**Best Practices:**

✅ **DO:**
- Version all training data
- Use semantic versioning (v1.0, v1.1, v2.0)
- Tag major data releases
- Document data changes
- Store data in versioned storage (S3 versioning)

❌ **DON'T:**
- Version data in Git (use DVC/LFS)
- Skip versioning "because it's too big"
- Forget to version test data
- Delete old versions too quickly

### 4.3 Feature Store Best Practices

**When to Use Feature Store:**

✅ **YES, if:**
- Multiple models use same features
- Training/serving skew is a problem
- Features are expensive to compute
- Need point-in-time correctness
- Team needs feature discovery

❌ **NO, if:**
- Single model, simple features
- Features are cheap to compute
- Small team, simple use case
- Prototyping/experimenting

**Feature Store Architecture:**

```python
# Feature definition
@feature_set(
    name="user_features",
    entities=["user_id"],
    online=True,  # Enable online serving
    offline=True   # Enable offline training
)
def user_features():
    return """
    SELECT
        user_id,
        age,
        country,
        signup_date,
        total_purchases,
        avg_purchase_value
    FROM users
    """

# Online features (prediction time)
features = feature_store.get_online_features(
    feature_refs=["user_features:age", "user_features:country"],
    entity_rows=[{"user_id": 123}]
)

# Offline features (training time)
training_data = feature_store.get_historical_features(
    feature_refs=["user_features:*"],
    entity_df=labels_df  # Joins at correct timestamp
)
```

---

## 5. Model Training

### 5.1 Training Data Best Practices

**Data Splitting Strategy:**

```python
# Time-series data: ALWAYS use time-based split
def time_based_split(df, test_size=0.2):
    """
    Time-based train/test split.

    Critical for time-series to prevent data leakage!
    """
    split_date = df['date'].quantile(1 - test_size)
    train = df[df['date'] < split_date]
    test = df[df['date'] >= split_date]
    return train, test

# Non-time-series: Stratified split
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,  # Maintain class balance
    random_state=42
)

# Hold-out validation set for hyperparameter tuning
X_train, X_val, y_train, y_val = train_test_split(
    X_train, y_train,
    test_size=0.2,
    stratify=y_train,
    random_state=42
)
```

**Common Data Leakage Scenarios:**

```python
# ❌ WRONG: Fit on all data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # LEAKAGE!
X_train, X_test = train_test_split(X_scaled)

# ✅ CORRECT: Fit only on training data
X_train, X_test = train_test_split(X)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # Only transform

# ❌ WRONG: Feature selection on all data
selected_features = select_features(X, y)  # LEAKAGE!
X_selected = X[selected_features]

# ✅ CORRECT: Feature selection on training only
selected_features = select_features(X_train, y_train)
X_train_selected = X_train[selected_features]
X_test_selected = X_test[selected_features]
```

### 5.2 Hyperparameter Tuning

**Tuning Budget Allocation:**

```python
# Start with rough search, then refine

# Stage 1: Random search (broad exploration)
# Budget: 50-100 iterations
random_search = RandomizedSearchCV(
    estimator=model,
    param_distributions={
        'learning_rate': [0.001, 0.01, 0.1, 0.2],
        'n_estimators': [50, 100, 200, 500],
        'max_depth': [3, 5, 7, 10]
    },
    n_iter=100,
    cv=5,
    random_state=42
)

# Stage 2: Grid search (fine-tuning)
# Budget: 20-30 iterations around best
best_lr = random_search.best_params_['learning_rate']
grid_search = GridSearchCV(
    estimator=model,
    param_grid={
        'learning_rate': [best_lr * 0.5, best_lr, best_lr * 1.5],
        'n_estimators': [90, 100, 110],
        'max_depth': [4, 5, 6]
    },
    cv=5
)

# Stage 3: Bayesian optimization (if needed)
# Budget: 50-100 iterations
from skopt import BayesSearchCV

bayes_search = BayesSearchCV(
    estimator=model,
    search_spaces={
        'learning_rate': (0.001, 0.3, 'log-uniform'),
        'n_estimators': (50, 500),
        'max_depth': (3, 15)
    },
    n_iter=50,
    cv=5
)
```

**Early Stopping:**

```python
# Use early stopping to save time
model = XGBClassifier(
    n_estimators=1000,
    early_stopping_rounds=50,  # Stop if no improvement for 50 rounds
    eval_metric='logloss'
)

model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=False
)

print(f"Best iteration: {model.best_iteration}")
print(f"Best score: {model.best_score}")
```

### 5.3 Cross-Validation Strategy

**Choose Right CV Strategy:**

```python
# 1. Standard K-Fold (default)
from sklearn.model_selection import KFold

kfold = KFold(n_splits=5, shuffle=True, random_state=42)

# 2. Stratified K-Fold (for imbalanced classes)
from sklearn.model_selection import StratifiedKFold

stratified = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# 3. Time Series Split (for temporal data)
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)

# 4. Group K-Fold (when samples are grouped)
from sklearn.model_selection import GroupKFold

# Example: Multiple samples per user
group_kfold = GroupKFold(n_splits=5)
cv_scores = cross_val_score(
    model, X, y,
    groups=user_ids,  # Ensure same user in same fold
    cv=group_kfold
)
```

**Best Practices:**

✅ **DO:**
- Use 5-10 folds typically
- Use stratified CV for classification
- Use time-based CV for time series
- Use group CV when samples are related
- Report mean and std of CV scores

❌ **DON'T:**
- Use too few folds (< 3)
- Use too many folds (> 10 usually wasteful)
- Forget to shuffle (except time series)
- Ignore data leakage in CV

---

## 6. Model Evaluation

### 6.1 Metrics Selection

**Classification Metrics Guide:**

| Metric | When to Use | Formula | Range |
|--------|-------------|---------|-------|
| **Accuracy** | Balanced classes | (TP + TN) / Total | 0-1 |
| **Precision** | False positives costly | TP / (TP + FP) | 0-1 |
| **Recall** | False negatives costly | TP / (TP + FN) | 0-1 |
| **F1 Score** | Balance precision/recall | 2 * P * R / (P + R) | 0-1 |
| **ROC-AUC** | Class probability quality | Area under ROC curve | 0-1 |
| **PR-AUC** | Imbalanced classes | Area under PR curve | 0-1 |

**Example Decision Matrix:**

```python
# Medical diagnosis: False negatives very costly
# Priority: HIGH RECALL (don't miss diseased patients)
# Metric: Recall > 0.95, then optimize precision

# Spam detection: False positives annoying
# Priority: HIGH PRECISION (don't mark real emails as spam)
# Metric: Precision > 0.95, then optimize recall

# Fraud detection: Both costly, but FP more common
# Priority: BALANCED F1-SCORE
# Metric: F1 > 0.85

# Credit scoring: Need probability calibration
# Priority: ROC-AUC for ranking
# Metric: ROC-AUC > 0.75
```

### 6.2 Model Comparison

**Fair Comparison Requirements:**

```python
class ModelComparer:
    """
    Fair model comparison framework.

    Requirements:
    - Same train/test split
    - Same preprocessing
    - Same CV folds
    - Same metrics
    - Statistical significance testing
    """

    def compare_models(self, models, X, y, cv=5):
        """Compare multiple models fairly."""
        results = []

        # Use same CV folds for all models
        cv_folds = list(KFold(n_splits=cv, shuffle=True, random_state=42).split(X))

        for name, model in models.items():
            scores = []

            for train_idx, test_idx in cv_folds:
                X_train, X_test = X[train_idx], X[test_idx]
                y_train, y_test = y[train_idx], y[test_idx]

                model.fit(X_train, y_train)
                score = model.score(X_test, y_test)
                scores.append(score)

            results.append({
                'model': name,
                'mean_score': np.mean(scores),
                'std_score': np.std(scores),
                'scores': scores
            })

        # Statistical significance test
        self.test_significance(results)

        return pd.DataFrame(results)

    def test_significance(self, results):
        """Test if differences are statistically significant."""
        from scipy.stats import ttest_rel

        # Paired t-test between each pair
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                statistic, pvalue = ttest_rel(
                    results[i]['scores'],
                    results[j]['scores']
                )

                print(f"{results[i]['model']} vs {results[j]['model']}")
                print(f"  t-statistic: {statistic:.4f}")
                print(f"  p-value: {pvalue:.4f}")
                print(f"  Significant: {pvalue < 0.05}\n")
```

### 6.3 Error Analysis

**Systematic Error Analysis:**

```python
def analyze_errors(y_true, y_pred, X, feature_names):
    """
    Comprehensive error analysis.

    Steps:
    1. Identify error types
    2. Find error patterns
    3. Quantify error impact
    4. Suggest improvements
    """

    # 1. Error distribution
    errors = y_true != y_pred
    error_rate = errors.mean()

    print(f"Overall error rate: {error_rate:.2%}")

    # 2. Error by feature ranges
    for feature in feature_names:
        # Bin feature into quartiles
        quartiles = pd.qcut(X[feature], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])

        # Error rate by quartile
        error_by_quartile = pd.DataFrame({
            'quartile': quartiles,
            'error': errors
        }).groupby('quartile')['error'].mean()

        print(f"\n{feature} error rate by quartile:")
        print(error_by_quartile)

    # 3. Confusion patterns (for classification)
    from sklearn.metrics import confusion_matrix

    cm = confusion_matrix(y_true, y_pred)
    print("\nConfusion Matrix:")
    print(cm)

    # 4. Most confident wrong predictions
    if hasattr(model, 'predict_proba'):
        probas = model.predict_proba(X)
        max_probas = probas.max(axis=1)

        # High confidence errors
        confident_errors = (errors) & (max_probas > 0.9)
        print(f"\nHigh-confidence errors: {confident_errors.sum()}")

        # Analyze these cases
        if confident_errors.sum() > 0:
            print("Investigate these cases for systematic issues!")
```

---

## 7. Deployment Best Practices

### 7.1 Deployment Strategy Selection

**Decision Matrix:**

| Strategy | Use When | Pros | Cons |
|----------|----------|------|------|
| **Canary** | Risk mitigation needed | Gradual validation, auto-rollback | Complex setup, slower rollout |
| **Blue/Green** | Zero-downtime required | Instant switch, easy rollback | 2x resources, all-or-nothing |
| **Shadow** | Need extensive testing | No user impact, real traffic | Duplicate compute, delayed results |
| **Rolling** | Large service fleet | Resource efficient | Slow rollback, mixed versions |

**Selection Guide:**

```python
def select_deployment_strategy(requirements):
    """Recommend deployment strategy based on requirements."""

    # High risk, critical service
    if requirements['criticality'] == 'high':
        if requirements['can_duplicate_traffic']:
            return 'shadow'  # Safest: Test with real traffic, no impact
        else:
            return 'canary'  # Safe: Gradual rollout with monitoring

    # Zero-downtime requirement
    elif requirements['zero_downtime']:
        if requirements['can_double_resources']:
            return 'blue_green'  # Instant switch, easy rollback
        else:
            return 'rolling'  # Gradual replacement

    # Standard deployment
    else:
        return 'canary'  # Good balance of safety and efficiency
```

### 7.2 Pre-Deployment Validation

**Validation Checklist:**

```python
class PreDeploymentValidator:
    """
    Comprehensive pre-deployment validation.

    Gates:
    1. Model performance
    2. API compatibility
    3. Resource requirements
    4. Integration tests
    5. Load tests
    """

    def validate_model(self, model, test_data):
        """Gate 1: Model performance acceptable."""
        metrics = evaluate_model(model, test_data)

        assert metrics['accuracy'] >= 0.85, "Accuracy too low"
        assert metrics['precision'] >= 0.80, "Precision too low"
        assert metrics['recall'] >= 0.80, "Recall too low"

        print("✅ Model performance acceptable")

    def validate_api_compatibility(self, new_api, old_api):
        """Gate 2: API backward compatible."""
        # Check request/response schemas match
        assert new_api.request_schema == old_api.request_schema, \
            "Request schema changed!"

        # Response can have new fields, but not remove old ones
        new_fields = set(new_api.response_schema.keys())
        old_fields = set(old_api.response_schema.keys())

        assert old_fields.issubset(new_fields), \
            "Response schema removed fields!"

        print("✅ API compatibility validated")

    def validate_resources(self, model):
        """Gate 3: Resource requirements acceptable."""
        # Memory footprint
        model_size = get_model_size(model)
        assert model_size < 1000, "Model too large (>1GB)"

        # Inference time
        latency = measure_latency(model)
        assert latency < 100, "Latency too high (>100ms)"

        print("✅ Resource requirements acceptable")

    def run_integration_tests(self):
        """Gate 4: Integration tests pass."""
        # Test full pipeline
        result = pytest.main([
            'tests/integration/',
            '-v',
            '--tb=short'
        ])

        assert result == 0, "Integration tests failed!"
        print("✅ Integration tests passed")

    def run_load_tests(self, endpoint):
        """Gate 5: Load tests pass."""
        # Use locust or similar
        results = run_locust_test(
            endpoint=endpoint,
            users=100,
            spawn_rate=10,
            duration='5m'
        )

        assert results['p95_latency'] < 200, "P95 latency too high"
        assert results['error_rate'] < 0.01, "Error rate too high"

        print("✅ Load tests passed")
```

### 7.3 Rollback Criteria

**Automatic Rollback Triggers:**

```python
class RollbackManager:
    """
    Automated rollback decision making.

    Triggers:
    - Error rate spike
    - Latency degradation
    - Accuracy drop (if labels available)
    - Data drift
    - Resource exhaustion
    """

    def __init__(self, thresholds):
        self.thresholds = thresholds
        self.baseline_metrics = None

    def should_rollback(self, current_metrics):
        """Determine if rollback needed."""
        triggers = []

        # Error rate spike
        if current_metrics['error_rate'] > self.thresholds['max_error_rate']:
            triggers.append(f"Error rate: {current_metrics['error_rate']:.2%}")

        # Latency degradation
        latency_increase = (
            current_metrics['p95_latency'] - self.baseline_metrics['p95_latency']
        ) / self.baseline_metrics['p95_latency']

        if latency_increase > self.thresholds['max_latency_increase']:
            triggers.append(f"Latency increase: {latency_increase:.2%}")

        # Accuracy drop (if available)
        if 'accuracy' in current_metrics:
            accuracy_drop = self.baseline_metrics['accuracy'] - current_metrics['accuracy']
            if accuracy_drop > self.thresholds['max_accuracy_drop']:
                triggers.append(f"Accuracy drop: {accuracy_drop:.2%}")

        # Resource exhaustion
        if current_metrics['memory_usage'] > self.thresholds['max_memory']:
            triggers.append(f"Memory: {current_metrics['memory_usage']:.1f}GB")

        if triggers:
            print("🚨 ROLLBACK TRIGGERED:")
            for trigger in triggers:
                print(f"  - {trigger}")
            return True

        return False

    def execute_rollback(self):
        """Execute rollback procedure."""
        print("🔄 Executing rollback...")

        # 1. Route traffic to old version
        # 2. Stop new version
        # 3. Notify team
        # 4. Create incident
        # 5. Preserve logs for debugging
```

---

## 8. Monitoring & Observability

### 8.1 The Four Golden Signals

**Google's SRE Golden Signals for ML:**

```python
class GoldenSignalsMonitor:
    """
    Monitor the four golden signals:
    1. Latency: How long requests take
    2. Traffic: How many requests
    3. Errors: Rate of failed requests
    4. Saturation: Resource utilization
    """

    def monitor_latency(self):
        """
        Track latency distribution.

        SLI: P95 latency < 100ms
        SLO: 99.9% of requests meet SLI
        """
        p50 = self.get_percentile(0.50)
        p95 = self.get_percentile(0.95)
        p99 = self.get_percentile(0.99)

        # Alert if P95 exceeds threshold
        if p95 > 100:
            self.alert("High latency", severity="warning")

    def monitor_traffic(self):
        """
        Track request volume.

        Watch for:
        - Unexpected drops (service down?)
        - Unexpected spikes (attack? viral event?)
        """
        current_rps = self.get_current_rps()
        baseline_rps = self.get_baseline_rps()

        # Alert on anomalies
        if current_rps < baseline_rps * 0.5:
            self.alert("Traffic drop", severity="critical")
        elif current_rps > baseline_rps * 2:
            self.alert("Traffic spike", severity="warning")

    def monitor_errors(self):
        """
        Track error rates.

        SLI: Error rate < 0.1%
        SLO: 99.9% of time error rate meets SLI
        """
        error_rate = self.get_error_rate()

        if error_rate > 0.001:  # 0.1%
            self.alert("High error rate", severity="critical")

    def monitor_saturation(self):
        """
        Track resource utilization.

        Resources:
        - CPU
        - Memory
        - Disk I/O
        - Network
        """
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()

        if cpu_usage > 0.8:
            self.alert("High CPU", severity="warning")
        if memory_usage > 0.9:
            self.alert("High memory", severity="critical")
```

### 8.2 ML-Specific Monitoring

**What Makes ML Monitoring Different:**

```python
class MLMonitor:
    """
    ML-specific monitoring beyond traditional metrics.

    ML Metrics:
    1. Prediction distribution
    2. Feature distribution
    3. Model confidence
    4. Data drift
    5. Model performance (when labels available)
    """

    def monitor_prediction_distribution(self):
        """
        Track prediction distribution over time.

        Red flags:
        - Sudden shift in predictions
        - All predictions same class
        - Predictions outside expected range
        """
        current_dist = self.get_prediction_distribution()
        baseline_dist = self.baseline_prediction_distribution

        # Compare distributions
        ks_stat, p_value = stats.ks_2samp(current_dist, baseline_dist)

        if p_value < 0.05:
            self.alert("Prediction distribution shifted", severity="warning")

    def monitor_feature_distribution(self):
        """
        Track input feature distributions.

        This catches:
        - Data pipeline issues
        - Upstream system changes
        - Seasonal effects
        """
        for feature in self.features:
            drift_detected = self.detect_drift(feature)
            if drift_detected:
                self.alert(f"Drift in {feature}", severity="warning")

    def monitor_model_confidence(self):
        """
        Track model confidence over time.

        Low confidence indicators:
        - Out-of-distribution inputs
        - Model uncertainty
        - Need for human review
        """
        avg_confidence = self.get_average_confidence()

        if avg_confidence < 0.7:
            self.alert("Low model confidence", severity="info")

        # Track confidence distribution
        low_confidence_rate = self.get_low_confidence_rate(threshold=0.5)

        if low_confidence_rate > 0.2:  # 20% low confidence
            self.alert("Many low-confidence predictions", severity="warning")

    def monitor_model_performance(self):
        """
        Track actual model performance (when labels arrive).

        Note: Labels often delayed (hours/days/weeks)
        """
        if self.labels_available():
            current_accuracy = self.calculate_accuracy()
            baseline_accuracy = self.baseline_accuracy

            if current_accuracy < baseline_accuracy - 0.05:
                self.alert("Model performance degraded", severity="critical")
                self.trigger_retraining()
```

### 8.3 Alert Fatigue Prevention

**Smart Alerting Strategy:**

```python
class SmartAlerting:
    """
    Prevent alert fatigue with intelligent alerting.

    Techniques:
    1. Alert aggregation
    2. Anomaly detection (not just thresholds)
    3. Alert suppression
    4. Escalation policies
    5. Automatic remediation
    """

    def should_alert(self, metric, value):
        """Decide if alert needed."""

        # 1. Check if already alerting on this
        if self.is_currently_alerting(metric):
            return False  # Don't duplicate

        # 2. Use anomaly detection, not just thresholds
        is_anomaly = self.detect_anomaly(metric, value)

        if not is_anomaly:
            return False

        # 3. Check alert frequency
        recent_alerts = self.get_recent_alerts(metric, hours=1)

        if len(recent_alerts) > 3:
            return False  # Too frequent, suppress

        # 4. Check business hours (for non-critical)
        if not self.is_critical(metric) and not self.is_business_hours():
            return False  # Wait for business hours

        return True

    def detect_anomaly(self, metric, value):
        """ML-based anomaly detection."""
        # Use historical data to detect anomalies
        # More sophisticated than fixed thresholds

        historical_values = self.get_historical_values(metric, days=30)

        # Calculate Z-score
        mean = np.mean(historical_values)
        std = np.std(historical_values)
        z_score = (value - mean) / std

        # Anomaly if > 3 standard deviations
        return abs(z_score) > 3
```

---

## 9. Incident Response

### 9.1 Incident Response Playbook

**When Production ML Model Fails:**

```markdown
## Phase 1: Detection & Triage (0-15 minutes)

✅ Detection
- [ ] Alert received
- [ ] Incident severity assessed (P0/P1/P2/P3)
- [ ] On-call engineer notified

✅ Initial Assessment
- [ ] Verify it's a real issue (not false positive)
- [ ] Determine scope (% of traffic affected)
- [ ] Identify symptoms (errors, latency, accuracy)

## Phase 2: Mitigation (15-60 minutes)

✅ Immediate Actions
- [ ] Roll back to previous version if available
- [ ] Route traffic to backup model
- [ ] Enable feature flags to disable problematic features
- [ ] Scale up resources if capacity issue

✅ Communication
- [ ] Create incident channel (#incident-YYYYMMDD-001)
- [ ] Notify stakeholders
- [ ] Update status page
- [ ] Start incident timeline

## Phase 3: Investigation (Parallel with mitigation)

✅ Data Collection
- [ ] Gather logs from last hour
- [ ] Export metrics dashboard
- [ ] Capture example failing requests
- [ ] Check recent deployments/changes

✅ Hypothesis Testing
- [ ] Test most likely causes
- [ ] Reproduce issue in staging
- [ ] Identify root cause

## Phase 4: Resolution (1-4 hours)

✅ Fix Implementation
- [ ] Develop fix
- [ ] Test fix thoroughly
- [ ] Deploy fix with monitoring
- [ ] Verify fix resolves issue

✅ Monitoring
- [ ] Watch metrics closely (2-4 hours)
- [ ] Verify no regression
- [ ] Confirm customer impact resolved

## Phase 5: Post-Mortem (Within 48 hours)

✅ Documentation
- [ ] Write incident report
- [ ] Timeline of events
- [ ] Root cause analysis
- [ ] Action items

✅ Prevention
- [ ] Identify preventative measures
- [ ] Update monitoring/alerting
- [ ] Update runbooks
- [ ] Share learnings with team
```

### 9.2 Common ML Incidents & Solutions

**Incident Type 1: Model Accuracy Degradation**

```python
# Symptoms:
- Model accuracy drops suddenly
- More customer complaints
- Confidence scores lower

# Investigation Steps:
1. Check for data drift
   - Compare current vs training data distributions

2. Check for label delay
   - Are we evaluating on stale labels?

3. Check for upstream changes
   - Did data pipeline change?
   - Did feature definitions change?

4. Check model staleness
   - When was model last trained?

# Resolution:
- If drift: Trigger retraining
- If upstream: Fix data pipeline
- If stale: Emergency retrain on recent data
```

**Incident Type 2: High Latency**

```python
# Symptoms:
- P95 latency > 200ms (was 50ms)
- Timeouts increasing
- User complaints

# Investigation Steps:
1. Check resource utilization
   - CPU/Memory maxed out?

2. Check model complexity
   - Did model get larger?
   - More features?

3. Check dependencies
   - Database slow?
   - Feature store timeout?

4. Check traffic patterns
   - Traffic spike?
   - Unusual request patterns?

# Resolution:
- Scale up resources
- Optimize model (quantization, pruning)
- Cache common predictions
- Add load shedding
```

**Incident Type 3: Prediction Errors**

```python
# Symptoms:
- 500 errors from prediction API
- Model returns NaN
- Feature extraction fails

# Investigation Steps:
1. Check input validation
   - Malformed requests?
   - Missing required fields?

2. Check model loading
   - Model file corrupted?
   - Version mismatch?

3. Check dependencies
   - Missing features?
   - External service down?

# Resolution:
- Add better input validation
- Add fallback to previous model
- Implement graceful degradation
```

---

## 10. Performance Optimization

### 10.1 Latency Optimization Checklist

**Target Latency Breakdown:**

```
Total Latency Budget: 100ms

├─ Network (20ms)
│  ├─ Client → Load Balancer (5ms)
│  ├─ Load Balancer → API (5ms)
│  └─ API → Client (10ms)
│
├─ Feature Loading (30ms)
│  ├─ Cache hit: 1ms
│  ├─ Cache miss: 30ms
│  └─ Feature computation: 50ms
│
├─ Model Inference (40ms)
│  ├─ Preprocessing: 5ms
│  ├─ Model forward pass: 30ms
│  └─ Postprocessing: 5ms
│
└─ Overhead (10ms)
   ├─ Request parsing: 2ms
   ├─ Validation: 2ms
   ├─ Logging: 2ms
   └─ Response formatting: 4ms
```

**Optimization Techniques:**

```python
# 1. Model Optimization
- Quantization: FP32 → INT8 (4x smaller, 2-4x faster)
- Pruning: Remove 50% weights (2x smaller, 1.5x faster)
- Knowledge Distillation: Teacher → Student (10x smaller)
- ONNX Runtime: 2-3x faster inference

# 2. Feature Optimization
- Cache hot features (Redis): 1ms vs 30ms
- Precompute features: Compute offline
- Feature selection: Fewer features = faster
- Approximate features: Trade accuracy for speed

# 3. Infrastructure Optimization
- Use GPU for batch inference
- Enable async requests
- Connection pooling
- Compression (gzip)

# 4. Code Optimization
- Profile code (cProfile)
- Optimize hot paths
- Use vectorization (NumPy)
- Avoid Python loops
```

### 10.2 Cost Optimization

**Cost Breakdown Typical ML Service:**

```
Monthly Cost: $10,000

├─ Compute (60% = $6,000)
│  ├─ API Servers: $3,000
│  ├─ Training: $2,000
│  └─ Feature computation: $1,000
│
├─ Storage (20% = $2,000)
│  ├─ Model artifacts: $500
│  ├─ Training data: $1,000
│  └─ Logs: $500
│
├─ Database (15% = $1,500)
│  ├─ PostgreSQL: $800
│  ├─ Redis: $500
│  └─ Backups: $200
│
└─ Network (5% = $500)
   └─ Data transfer: $500
```

**Cost Optimization Strategies:**

```python
# 1. Compute Optimization
✅ Use spot instances for training (70% cheaper)
✅ Auto-scale API servers based on traffic
✅ Cache predictions (reduce compute)
✅ Use smaller models when possible
✅ Batch predictions (higher throughput)

# 2. Storage Optimization
✅ Compress model artifacts
✅ Delete old model versions (keep last 3)
✅ Use object storage lifecycle (S3 Glacier)
✅ Compress logs
✅ Sample verbose logs (not all requests)

# 3. Database Optimization
✅ Right-size database instances
✅ Use read replicas for read-heavy workloads
✅ Archive old data
✅ Optimize queries
✅ Use connection pooling

# 4. Network Optimization
✅ Use CDN for static assets
✅ Compress API responses
✅ Reduce payload size
✅ Use regional endpoints
```

---

## 11. Security

### 11.1 Security Checklist

```markdown
✅ Authentication & Authorization
- [ ] API requires authentication
- [ ] Use OAuth2/JWT tokens
- [ ] Implement RBAC (Role-Based Access Control)
- [ ] Rotate keys regularly
- [ ] Audit access logs

✅ Data Security
- [ ] Encrypt data in transit (TLS)
- [ ] Encrypt data at rest
- [ ] Mask PII in logs
- [ ] Implement data retention policies
- [ ] Handle deletion requests (GDPR)

✅ Model Security
- [ ] Validate all inputs
- [ ] Sanitize outputs
- [ ] Rate limiting
- [ ] Protect against adversarial attacks
- [ ] Model watermarking (optional)

✅ Infrastructure Security
- [ ] Use private networks
- [ ] Implement firewalls
- [ ] Security scanning (Trivy, Snyk)
- [ ] Patch dependencies regularly
- [ ] Secrets management (Vault, AWS Secrets)

✅ Monitoring & Audit
- [ ] Log all access
- [ ] Anomaly detection
- [ ] Security alerts
- [ ] Regular security audits
- [ ] Penetration testing
```

### 11.2 Common Security Vulnerabilities

**SQL Injection in Feature Queries:**

```python
# ❌ VULNERABLE
def get_user_features(user_id):
    query = f"SELECT * FROM features WHERE user_id = {user_id}"
    return db.execute(query)

# ✅ SAFE: Use parameterized queries
def get_user_features(user_id):
    query = "SELECT * FROM features WHERE user_id = %s"
    return db.execute(query, (user_id,))
```

**Model Extraction Attacks:**

```python
# Attacker tries to steal model by querying it many times

class ModelExtractionDefense:
    """Defend against model extraction attacks."""

    def __init__(self, max_requests_per_user=1000):
        self.max_requests = max_requests_per_user
        self.request_counts = {}

    def check_rate_limit(self, user_id):
        """Limit requests per user."""
        count = self.request_counts.get(user_id, 0)

        if count > self.max_requests:
            raise ValueError("Rate limit exceeded")

        self.request_counts[user_id] = count + 1

    def add_noise_to_predictions(self, predictions):
        """Add small noise to prevent exact extraction."""
        noise = np.random.normal(0, 0.01, size=predictions.shape)
        return predictions + noise
```

---

## 12. Team Collaboration

### 12.1 Code Review Guidelines

**ML Code Review Checklist:**

```markdown
✅ Functionality
- [ ] Code works as intended
- [ ] Handles edge cases
- [ ] No data leakage
- [ ] Reproducible results

✅ ML-Specific
- [ ] Train/test split correct
- [ ] No look-ahead bias
- [ ] Cross-validation properly done
- [ ] Metrics appropriate for problem
- [ ] Baseline comparison included

✅ Experiment Tracking
- [ ] All parameters logged
- [ ] Results logged to MLflow
- [ ] Artifacts saved
- [ ] Runs tagged appropriately

✅ Code Quality
- [ ] Type hints used
- [ ] Docstrings present
- [ ] Tests included
- [ ] Performance acceptable

✅ Production Readiness
- [ ] Error handling
- [ ] Logging
- [ ] Monitoring
- [ ] Documentation
```

### 12.2 Documentation Standards

**Model Card Template:**

```markdown
# Model Card: [Model Name]

## Model Description
- **Model Type**: XGBoost Classifier
- **Version**: 2.1.0
- **Training Date**: 2024-01-15
- **Trained By**: data-science-team
- **Repository**: github.com/org/ml-pipeline

## Intended Use
- **Primary Use**: Predict customer churn
- **Primary Users**: Product team, Customer success
- **Out-of-Scope**: Not for legal decisions

## Training Data
- **Dataset**: Customer behavior data
- **Size**: 1M samples, 50 features
- **Time Period**: 2023-01-01 to 2023-12-31
- **Preprocessing**: See preprocessing.py

## Model Performance
| Metric | Value |
|--------|-------|
| Accuracy | 0.87 |
| Precision | 0.85 |
| Recall | 0.83 |
| F1 Score | 0.84 |
| ROC-AUC | 0.91 |

## Fairness & Bias
- **Bias Analysis**: Conducted across gender, age groups
- **Fairness Metrics**: Similar performance across groups
- **Known Limitations**: Lower performance for edge cases

## Ethical Considerations
- **Potential Harm**: False negatives may miss at-risk customers
- **Mitigation**: Human review for high-risk cases
- **Privacy**: PII removed from training data

## Monitoring
- **Drift Detection**: Weekly checks on input distribution
- **Performance Monitoring**: Daily accuracy evaluation
- **Retraining**: Monthly or when drift detected

## Contact
- **Team**: data-science@company.com
- **Slack**: #ml-platform
```

---

## 13. Cost Management

### 13.1 Cost Tracking

```python
class CostTracker:
    """
    Track ML infrastructure costs.

    Costs to track:
    - Training compute
    - Inference compute
    - Storage
    - Data transfer
    - External services (APIs)
    """

    def calculate_training_cost(self, duration_hours, instance_type):
        """Calculate training job cost."""
        instance_costs = {
            'ml.m5.large': 0.115,     # per hour
            'ml.p3.2xlarge': 3.825,   # GPU instance
        }

        return duration_hours * instance_costs[instance_type]

    def calculate_inference_cost(self, requests_per_day, avg_latency_ms):
        """Calculate inference cost."""
        # Compute cost
        compute_hours_per_day = (requests_per_day * avg_latency_ms / 1000) / 3600
        compute_cost = compute_hours_per_day * 0.115  # instance cost

        # Storage cost (model + cache)
        storage_cost = 0.023 * 10  # $0.023/GB, 10GB

        # Data transfer
        data_transfer_cost = 0.09 * requests_per_day * 0.001  # $0.09/GB

        return compute_cost + storage_cost + data_transfer_cost
```

### 13.2 Cost Optimization Opportunities

**Quick Wins:**

```python
# 1. Use smaller models (10x cost reduction)
- XGBoost instead of neural networks
- Feature selection (fewer features = faster)
- Model compression (quantization)

# 2. Cache predictions (50-90% cost reduction)
- Cache common prediction inputs
- TTL based on use case
- Redis for distributed cache

# 3. Batch processing (5-10x improvement)
- Batch predictions when possible
- Use GPU for batch inference
- Async processing

# 4. Right-size infrastructure (30-50% savings)
- Auto-scaling based on traffic
- Spot instances for training
- Scheduled scaling (night/weekend)

# 5. Optimize storage (20-30% savings)
- Delete old model versions
- Compress artifacts
- Use cheaper storage tiers
```

---

## 14. Common Pitfalls

### 14.1 Data Leakage

**Most Common Leakage Scenarios:**

```python
# Pitfall 1: Information from future
# ❌ WRONG: Using future information
df['target'] = df['target'].shift(-1)  # Looking ahead!

# ✅ CORRECT: Only past information
df['lag_feature'] = df['value'].shift(1)  # Looking back


# Pitfall 2: Fitting on all data
# ❌ WRONG
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Leak!
X_train, X_test = train_test_split(X_scaled)

# ✅ CORRECT
X_train, X_test = train_test_split(X)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# Pitfall 3: Target leakage in features
# ❌ WRONG: Feature highly correlated with target
df['days_until_churn'] = (df['churn_date'] - df['current_date']).days

# ✅ CORRECT: Feature available at prediction time
df['days_since_signup'] = (df['current_date'] - df['signup_date']).days
```

### 14.2 Training/Serving Skew

**Common Causes:**

```python
# Problem: Training and serving preprocessing differs

# Training pipeline:
def preprocess_training(df):
    df['age_normalized'] = (df['age'] - df['age'].mean()) / df['age'].std()
    return df

# Serving pipeline (WRONG!):
def preprocess_serving(features):
    # Uses different normalization!
    age_normalized = (features['age'] - 30) / 10  # Hardcoded!
    return age_normalized

# Solution: Save and reuse same preprocessing
preprocessor = StandardScaler()
preprocessor.fit(training_data['age'].values.reshape(-1, 1))
joblib.dump(preprocessor, 'age_scaler.pkl')

# In serving:
preprocessor = joblib.load('age_scaler.pkl')
age_normalized = preprocessor.transform([[age]])
```

### 14.3 Silent Failures

**Models Can Fail Silently:**

```python
# Problem: Model returns predictions but they're wrong

# Example: Feature preprocessing changes upstream
# Model still works but uses wrong features

# Solution: Monitor input distributions
def check_feature_distribution(features):
    """Alert if features out of expected range."""

    expected_ranges = {
        'age': (18, 100),
        'income': (0, 1000000),
        'credit_score': (300, 850)
    }

    for feature, (min_val, max_val) in expected_ranges.items():
        if not (min_val <= features[feature] <= max_val):
            alert(f"Feature {feature} out of range: {features[feature]}")

    # Also check distributions
    if detect_drift(features):
        alert("Input distribution changed!")
```

---

## Conclusion

Production ML is 90% software engineering and 10% machine learning. Follow these best practices to:

- **Avoid common pitfalls** (data leakage, training/serving skew)
- **Build reliable systems** (monitoring, rollback, incident response)
- **Optimize costs** (right-size, cache, batch)
- **Ensure security** (auth, encryption, rate limiting)
- **Enable collaboration** (documentation, code review, model cards)

**Remember:**
- Start simple, add complexity as needed
- Monitor everything
- Automate what you can
- Document what you can't
- Learn from incidents
- Share knowledge with team

---

**Next Steps:**
1. Review your current system against this checklist
2. Identify top 3 gaps
3. Create action plan to address them
4. Iterate and improve continuously
