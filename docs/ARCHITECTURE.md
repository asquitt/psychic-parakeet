# ML Pipeline Architecture

## Overview

This document provides an in-depth explanation of the ML pipeline architecture, design decisions, and component interactions.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Data Ingestion Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  CSV Files   │  │  Databases   │  │  APIs        │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Data Processing Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Validation (Pydantic, Great Expectations)         │  │
│  │  • Schema validation                                      │  │
│  │  • Quality checks                                         │  │
│  │  • Outlier detection                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Preprocessing (sklearn pipelines)                  │  │
│  │  • Scaling and normalization                             │  │
│  │  • Missing value imputation                              │  │
│  │  • Categorical encoding                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Feature Engineering                                      │  │
│  │  • Mathematical transformations                           │  │
│  │  • Feature interactions                                   │  │
│  │  • Feature selection                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Model Training Layer                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Model Training (MLflow)                                  │  │
│  │  • Multiple algorithms                                    │  │
│  │  • Hyperparameter tuning                                  │  │
│  │  • Cross-validation                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Model Evaluation                                         │  │
│  │  • Performance metrics                                    │  │
│  │  • Feature importance                                     │  │
│  │  • Model comparison                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Model Registry (MLflow)                                  │  │
│  │  • Version management                                     │  │
│  │  • Staging (None → Staging → Production → Archived)      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Orchestration Layer (Prefect)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Training    │  │  Monitoring  │  │  Retraining  │         │
│  │  Pipeline    │  │  Pipeline    │  │  Pipeline    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Deployment Layer                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Deployment Strategies                                    │  │
│  │  • Canary: Gradual rollout                               │  │
│  │  • Blue/Green: Zero-downtime switch                       │  │
│  │  • Shadow: A/B testing                                    │  │
│  │  • Auto-rollback: Performance-based                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Serving Layer (FastAPI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  REST API    │  │  Validation  │  │  Load        │         │
│  │  Endpoints   │  │  (Pydantic)  │  │  Balancing   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Monitoring & Alerting Layer                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Drift Detection (Evidently)                        │  │
│  │  • Distribution shifts                                    │  │
│  │  • Feature drift                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Performance Monitoring (Prometheus)                      │  │
│  │  • Latency tracking                                       │  │
│  │  • Throughput measurement                                 │  │
│  │  • Error rate monitoring                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Visualization (Grafana)                                  │  │
│  │  • Real-time dashboards                                   │  │
│  │  • Alerts and notifications                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Layer

#### Data Validation
- **Purpose:** Ensure data quality before training/inference
- **Tools:** Pydantic for schema validation, custom validators
- **Checks:**
  - Schema conformance
  - Missing value ratios
  - Duplicate detection
  - Outlier identification
  - Statistical properties

#### Data Preprocessing
- **Purpose:** Transform raw data into model-ready format
- **Tools:** sklearn pipelines
- **Operations:**
  - Scaling (StandardScaler, RobustScaler, MinMaxScaler)
  - Encoding (OneHotEncoder for categoricals)
  - Imputation (mean, median, mode)
- **Key Design:** Preprocessing pipeline is saved and reused in production

#### Feature Engineering
- **Purpose:** Create meaningful features from raw data
- **Techniques:**
  - Mathematical transformations (log, sqrt, polynomial)
  - Feature interactions (products, ratios)
  - Statistical features (rolling mean, std)
  - Feature selection (statistical tests)

### 2. Model Layer

#### Training
- **Purpose:** Train and optimize ML models
- **Algorithms:** XGBoost, Random Forest, Gradient Boosting, Logistic Regression
- **Hyperparameter Tuning:**
  - Grid Search: Exhaustive search
  - Random Search: Efficient sampling
- **Tracking:** All experiments logged to MLflow

#### Evaluation
- **Metrics:**
  - Classification: accuracy, precision, recall, F1, ROC-AUC
  - Confusion matrix
  - Feature importance
- **Comparison:** Compare multiple models and select best

#### Model Registry
- **Tool:** MLflow Model Registry
- **Stages:**
  - None: Newly registered
  - Staging: Under testing
  - Production: Live deployment
  - Archived: Deprecated
- **Versioning:** Automatic version management

### 3. Orchestration Layer

#### Prefect Workflows
- **Purpose:** Orchestrate complex multi-step pipelines
- **Features:**
  - Task dependencies
  - Retry logic
  - Caching
  - Scheduling

#### Workflows Implemented
1. **Training Pipeline:**
   - Load data → Validate → Engineer features → Train → Evaluate → Register
2. **Monitoring Pipeline:**
   - Load data → Detect drift → Alert if needed
3. **Retraining Pipeline:**
   - Triggered by drift detection or schedule

### 4. Deployment Layer

#### Canary Deployment
```python
# Start with 10% traffic to new version
canary.start_deployment(traffic_percentage=10)

# Monitor performance
if performance_good:
    canary.increment_traffic()  # Increase to 20%, 30%, etc.
else:
    canary.rollback()  # Revert to old version
```

**Use Cases:**
- Gradual rollout of major changes
- Risk mitigation
- Performance validation with real traffic

#### Blue/Green Deployment
```python
# Blue = current production, Green = new version
deployment.deploy_to_green(new_version)
deployment.test_green()
deployment.switch_to_green()  # Instant switch
# Rollback if needed
deployment.rollback_to_blue()
```

**Use Cases:**
- Zero-downtime deployments
- Quick rollback capability
- Full environment testing

#### Shadow Deployment
```python
# Both versions receive traffic, only current returns results
shadow.start_shadow_deployment(current_version, new_version)

# After collecting enough data
analysis = shadow.analyze_performance()
if analysis.satisfactory:
    shadow.promote_to_production()
```

**Use Cases:**
- A/B testing
- Risk-free evaluation
- Performance comparison

### 5. Serving Layer

#### FastAPI REST API
- **Endpoints:**
  - `/health`: Health check
  - `/ready`: Readiness probe
  - `/predict`: Single prediction
  - `/predict/batch`: Batch predictions
  - `/metrics`: Prometheus metrics
  - `/model/reload`: Reload model

#### Request Flow
```
Client Request
    ↓
FastAPI (validation)
    ↓
Load model from MLflow
    ↓
Preprocessing pipeline
    ↓
Model prediction
    ↓
Response formatting
    ↓
Metrics recording
    ↓
Response to client
```

### 6. Monitoring Layer

#### Data Drift Detection
**Statistical Tests:**
- Kolmogorov-Smirnov (K-S) test: Compare distributions
- Population Stability Index (PSI): Measure distribution shift
- Chi-squared test: For categorical features

**Process:**
1. Set reference distribution (training data)
2. Compare production data periodically
3. Alert if drift exceeds threshold
4. Trigger retraining if needed

#### Performance Monitoring
**Metrics Tracked:**
- Latency (p50, p95, p99)
- Throughput (RPS)
- Error rate
- Prediction distribution
- Model accuracy (when labels available)

**SLA Monitoring:**
- P95 latency < threshold
- Error rate < threshold
- Automatic alerts on violations

## Technology Stack Rationale

### Why Prefect over Airflow?
- **More Pythonic:** Native Python, not DAG DSL
- **Easier Testing:** Can test workflows locally
- **Lighter Weight:** Lower resource requirements
- **Modern Architecture:** Cloud-native design
- **Cost Efficient:** Simpler deployment

### Why MLflow?
- **Complete Solution:** Tracking + Registry + Deployment
- **Open Source:** No vendor lock-in
- **Easy Integration:** Works with any ML library
- **Industry Standard:** Widely adopted

### Why FastAPI?
- **Performance:** Async support, very fast
- **Validation:** Automatic with Pydantic
- **Documentation:** Auto-generated OpenAPI docs
- **Modern:** Python 3.6+ type hints
- **Easy Testing:** Built-in test client

### Why Prometheus + Grafana?
- **Prometheus:** De facto standard for metrics
- **Grafana:** Beautiful, powerful visualizations
- **Integration:** Works seamlessly together
- **Alerting:** Flexible alerting rules
- **Cost:** Open source, self-hosted

## Design Decisions

### 1. Separation of Concerns
Each component has a single responsibility:
- Data modules: Only data handling
- Model modules: Only model operations
- Serving modules: Only API serving
- Monitoring modules: Only monitoring

### 2. Reusability
Components are designed to be reusable:
- Preprocessing pipelines saved and loaded
- Feature engineering can be version-controlled
- Models are versioned in registry
- Deployment strategies are generic

### 3. Observability
Everything is logged and tracked:
- MLflow tracks all experiments
- Prometheus collects all metrics
- Logs are structured and searchable
- Errors are captured with context

### 4. Testability
Code is designed for testing:
- Functions are pure when possible
- Dependencies are injected
- Mocking is straightforward
- Integration tests are easy

### 5. Cost Efficiency
Choices made for cost efficiency:
- Caching in workflows
- Efficient algorithms (XGBoost over deep learning)
- Batch processing support
- Resource monitoring
- Auto-scaling ready

## Data Flow

### Training Flow
```
Raw Data
  ↓ (validation)
Validated Data
  ↓ (feature engineering)
Engineered Features
  ↓ (preprocessing)
Scaled Features
  ↓ (training)
Trained Model
  ↓ (evaluation)
Evaluated Model
  ↓ (registration)
Model Registry
```

### Inference Flow
```
Client Request
  ↓ (validation)
Validated Request
  ↓ (feature extraction)
Features
  ↓ (preprocessing)
Scaled Features
  ↓ (prediction)
Raw Prediction
  ↓ (post-processing)
Formatted Response
  ↓ (monitoring)
Metrics Recorded
```

### Monitoring Flow
```
Production Data
  ↓ (collection)
Reference Data
  ↓ (comparison)
Drift Metrics
  ↓ (evaluation)
Drift Detection
  ↓ (alert)
Alert/Action
  ↓ (retrain)
New Model
```

## Scalability Considerations

### Horizontal Scaling
- API: Multiple replicas behind load balancer
- Workers: Multiple Prefect workers
- Database: Read replicas for MLflow

### Vertical Scaling
- Increase resources for training jobs
- Use GPU for deep learning models
- Scale database for large experiments

### Future Enhancements
- Kubernetes deployment
- Distributed training (Ray, Dask)
- Feature store integration
- Real-time streaming predictions
- Advanced A/B testing framework

## Security Considerations

### Current Implementation
- Environment variables for secrets
- Container isolation
- Network policies in Docker Compose
- Health check endpoints

### Production Recommendations
- Use secrets management (Vault, AWS Secrets Manager)
- Enable HTTPS/TLS
- Implement authentication (OAuth2, JWT)
- Rate limiting
- Input sanitization
- Regular security audits

## Cost Optimization

### Current Optimizations
- Lightweight containers
- Efficient algorithms
- Caching strategy
- Batch processing
- Resource monitoring

### Further Optimizations
- Spot instances for training
- Auto-scaling policies
- Model compression
- Feature caching
- Query optimization

## Maintenance and Operations

### Regular Tasks
- Monitor drift metrics
- Check model performance
- Review error logs
- Update dependencies
- Backup data and models

### Automation
- Scheduled retraining
- Automated testing
- Dependency updates
- Performance reports

## Conclusion

This architecture provides a production-ready ML pipeline with:
- **Reliability:** Retry logic, error handling, monitoring
- **Scalability:** Horizontal and vertical scaling options
- **Maintainability:** Clear structure, good documentation
- **Cost Efficiency:** Optimized resource usage
- **Flexibility:** Easy to extend and modify

The design follows industry best practices while remaining accessible for learning and experimentation.
