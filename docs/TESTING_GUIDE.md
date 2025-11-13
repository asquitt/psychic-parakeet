# Testing Guide

**Comprehensive Testing Documentation for ML Pipeline**

This guide covers all aspects of testing the ML pipeline, including unit tests, integration tests, performance tests, and regression tests.

---

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Unit Tests](#unit-tests)
5. [Integration Tests](#integration-tests)
6. [Performance Tests](#performance-tests)
7. [Regression Tests](#regression-tests)
8. [Writing New Tests](#writing-new-tests)
9. [CI/CD Integration](#cicd-integration)
10. [Troubleshooting](#troubleshooting)

---

## Testing Overview

### Testing Philosophy

Our testing strategy follows the **testing pyramid**:

```
           /\
          /  \         E2E Tests (Few)
         /____\        - Complete pipeline flows
        /      \       - Real-world scenarios
       /________\      Integration Tests (Some)
      /          \     - Component interactions
     /            \    - API endpoints
    /______________\   Unit Tests (Many)
                       - Individual functions
                       - Data validation
                       - Model components
```

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test individual functions and classes
   - Fast execution (< 1 second per test)
   - No external dependencies
   - High code coverage (>80%)

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - End-to-end pipeline flows
   - MLflow integration
   - Medium execution time (1-10 seconds per test)

3. **Performance Tests** (`tests/performance/`)
   - API latency and throughput
   - Model inference speed
   - Resource usage profiling
   - Load and stress testing

4. **Regression Tests** (`tests/regression/`)
   - Model quality consistency
   - Prediction reproducibility
   - Feature engineering stability
   - Cross-version compatibility

### Testing Goals

- ✅ **Confidence**: Ensure code changes don't break functionality
- ✅ **Quality**: Maintain model performance standards
- ✅ **Performance**: Verify latency and throughput requirements
- ✅ **Reproducibility**: Guarantee consistent predictions
- ✅ **Documentation**: Tests serve as living documentation

---

## Test Structure

### Directory Organization

```
tests/
├── __init__.py
├── unit/                          # Unit tests
│   ├── __init__.py
│   └── test_validation.py         # Data validation tests
├── integration/                   # Integration tests
│   ├── __init__.py
│   └── test_pipeline_integration.py  # Full pipeline tests
├── performance/                   # Performance tests
│   ├── __init__.py
│   └── test_performance.py        # Latency, throughput tests
├── regression/                    # Regression tests
│   ├── __init__.py
│   └── test_model_regression.py   # Model quality tests
└── conftest.py                    # Shared fixtures (optional)
```

### Test File Naming

- Test files must start with `test_` (e.g., `test_validation.py`)
- Test functions must start with `test_` (e.g., `test_validate_schema()`)
- Test classes must start with `Test` (e.g., `class TestDataValidator`)

### Fixtures

Fixtures provide reusable test data and setup:

```python
@pytest.fixture(scope="module")
def sample_data():
    """Create sample data for tests."""
    return pd.DataFrame({
        'feature1': [1, 2, 3],
        'target': [0, 1, 0]
    })
```

**Fixture Scopes:**
- `function`: New instance per test function (default)
- `class`: New instance per test class
- `module`: New instance per test module (file)
- `session`: One instance for entire test session

---

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements.txt

# Or specifically
pip install pytest pytest-cov pytest-xdist
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with output (print statements visible)
pytest -s

# Run specific test file
pytest tests/unit/test_validation.py

# Run specific test function
pytest tests/unit/test_validation.py::test_validate_schema_success

# Run specific test class
pytest tests/unit/test_validation.py::TestDataValidator
```

### Test Coverage

```bash
# Run tests with coverage report
pytest --cov=src/ml_pipeline --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src/ml_pipeline --cov-report=html

# View HTML report
open htmlcov/index.html
```

### Parallel Test Execution

```bash
# Run tests in parallel (faster)
pytest -n auto  # Uses all CPU cores

# Run with specific number of workers
pytest -n 4
```

### Test Filtering

```bash
# Run tests by marker
pytest -m "not slow"  # Skip slow tests
pytest -m "integration"  # Run only integration tests

# Run tests matching pattern
pytest -k "validation"  # Run tests with "validation" in name
pytest -k "test_data or test_model"  # Multiple patterns

# Run only failed tests from last run
pytest --lf

# Run failed tests first
pytest --ff
```

### Performance Testing Options

```bash
# Run performance tests with detailed output
pytest tests/performance/ -v -s

# Run specific performance test
pytest tests/performance/test_performance.py::TestModelInferencePerformance::test_single_prediction_latency

# Skip performance tests (they can be slow)
pytest -m "not performance"
```

---

## Unit Tests

### Overview

Unit tests verify individual components work correctly in isolation.

**Location:** `tests/unit/`

**Execution Time:** Fast (<1s per test)

**Purpose:**
- Test individual functions
- Verify edge cases
- Validate error handling
- Ensure code correctness

### Example: Data Validation Tests

**File:** `tests/unit/test_validation.py`

```python
def test_validate_schema_success(self):
    """Test schema validation passes with all required columns."""
    df = pd.DataFrame({
        'feature1': [1, 2, 3],
        'feature2': [4, 5, 6],
        'target': [0, 1, 0]
    })

    required_columns = ['feature1', 'feature2', 'target']
    result = self.validator.validate_schema(df, required_columns)

    assert result is True
```

### What to Test

1. **Happy Path**: Normal, expected usage
2. **Edge Cases**: Boundary conditions, empty inputs
3. **Error Handling**: Invalid inputs, missing data
4. **Data Types**: Type validation and conversion
5. **Business Logic**: Calculations, transformations

### Best Practices

```python
# ✅ Good: Descriptive test name
def test_validation_fails_with_missing_required_columns():
    pass

# ❌ Bad: Vague test name
def test_validation():
    pass

# ✅ Good: Single assertion per test
def test_accuracy_above_threshold():
    accuracy = calculate_accuracy(y_true, y_pred)
    assert accuracy > 0.8

# ❌ Bad: Multiple unrelated assertions
def test_model_training():
    model = train_model(X, y)
    assert model is not None
    assert accuracy > 0.8
    assert file_exists("model.pkl")
```

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run with coverage
pytest tests/unit/ --cov=src/ml_pipeline/data --cov-report=term-missing

# Fast execution with parallel workers
pytest tests/unit/ -n auto
```

---

## Integration Tests

### Overview

Integration tests verify that multiple components work together correctly.

**Location:** `tests/integration/`

**Execution Time:** Medium (1-10s per test)

**Purpose:**
- Test component interactions
- Verify end-to-end flows
- Test with real dependencies
- Validate system integration

### Test Categories

1. **Data Pipeline Integration**
   - Validation → Preprocessing → Feature Engineering
   - Data flow consistency
   - Pipeline determinism

2. **Model Training Integration**
   - Data → Training → Evaluation
   - MLflow tracking integration
   - Model registry operations

3. **End-to-End Pipeline**
   - Complete workflow from raw data to predictions
   - Model registration and loading
   - Full system validation

### Example: End-to-End Pipeline Test

```python
def test_complete_pipeline_flow(
    sample_training_data,
    mlflow_tracking_uri,
    temp_data_dir
):
    """Test the complete end-to-end ML pipeline."""

    # Step 1: Data Validation
    validated_df = validate_training_data(
        sample_training_data,
        feature_columns,
        target_column
    )

    # Step 2: Preprocessing
    X_processed = preprocessor.fit_transform(X_train)

    # Step 3: Feature Engineering
    X_engineered = engineer.fit_transform(X_processed)

    # Step 4: Model Training
    model_result = trainer.train_model(
        X_engineered,
        y_train,
        model_type="random_forest"
    )

    # Step 5: Evaluation
    metrics = evaluator.evaluate(X_test_engineered, y_test)

    # Step 6: Model Registration
    registered_model = mlflow.register_model(model_uri, model_name)

    # Step 7: Model Loading and Inference
    loaded_model = mlflow.pyfunc.load_model(f"models:/{model_name}/latest")
    predictions = loaded_model.predict(X_test_engineered)

    # Assertions
    assert metrics['accuracy'] > 0.5
    assert len(predictions) == len(y_test)
```

### Key Integration Points Tested

1. **Data Pipeline:**
   - Validator → Preprocessor interface
   - Preprocessor → Feature Engineer interface
   - Consistent data transformations

2. **Training Pipeline:**
   - Data → Model Trainer interface
   - Model Trainer → MLflow integration
   - Evaluation metrics logging

3. **Serving Pipeline:**
   - Model registry → Model loading
   - Loaded model → Prediction interface
   - Prediction format consistency

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run with detailed output
pytest tests/integration/ -v -s

# Run specific test class
pytest tests/integration/test_pipeline_integration.py::TestEndToEndPipeline
```

### Integration Test Best Practices

1. **Use Fixtures**: Share setup code across tests
2. **Isolated Tests**: Each test should be independent
3. **Cleanup**: Clean up resources after tests (use fixtures with yield)
4. **Real Dependencies**: Use actual components, not mocks
5. **Performance**: Keep tests reasonably fast (<30s)

---

## Performance Tests

### Overview

Performance tests verify the system meets latency, throughput, and resource usage requirements.

**Location:** `tests/performance/`

**Execution Time:** Variable (10s - 5min)

**Purpose:**
- Verify performance requirements
- Detect performance regressions
- Profile resource usage
- Load and stress testing

### Performance Requirements

| Component | Metric | Target |
|-----------|--------|--------|
| Single Prediction | P95 Latency | < 100ms |
| Single Prediction | P99 Latency | < 150ms |
| Batch Prediction | Throughput | > 10,000/s |
| Data Pipeline | Throughput | > 1,000 rows/s |
| API Endpoint | P95 Latency | < 500ms |
| Memory Usage | Prediction (10k) | < 100MB |

### Test Categories

1. **Latency Tests**
   - Single prediction latency (P50, P95, P99)
   - Batch prediction latency
   - Data preprocessing latency

2. **Throughput Tests**
   - Predictions per second
   - Data processing throughput
   - API request handling

3. **Resource Usage Tests**
   - Memory usage profiling
   - CPU utilization
   - Disk I/O

4. **Load Tests**
   - Sustained load performance
   - Concurrent request handling
   - Stress testing

### Example: Single Prediction Latency Test

```python
def test_single_prediction_latency(self, trained_model):
    """Test single prediction latency."""
    model, preprocessor = trained_model

    # Measure latency over multiple iterations
    latencies = []
    n_iterations = 1000

    for _ in range(n_iterations):
        start_time = time.perf_counter()
        _ = model.predict(sample_processed)
        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)

    # Calculate percentiles
    stats = calculate_percentiles(latencies)

    print(f"P50 latency: {stats['p50']:.2f}ms")
    print(f"P95 latency: {stats['p95']:.2f}ms")
    print(f"P99 latency: {stats['p99']:.2f}ms")

    # Assertions
    assert stats['p95'] < 100, "P95 latency should be < 100ms"
```

### Performance Testing Tools

```python
# 1. Time measurement
import time

start = time.perf_counter()
result = some_function()
elapsed = (time.perf_counter() - start) * 1000  # ms

# 2. Memory profiling
import psutil

process = psutil.Process()
mem_before = process.memory_info().rss / 1024 / 1024  # MB
result = some_function()
mem_after = process.memory_info().rss / 1024 / 1024
memory_used = mem_after - mem_before

# 3. Statistical analysis
import statistics

p50 = statistics.median(latencies)
p95 = sorted(latencies)[int(len(latencies) * 0.95)]
```

### Running Performance Tests

```bash
# Run all performance tests
pytest tests/performance/ -v -s

# Run specific performance test
pytest tests/performance/test_performance.py::TestModelInferencePerformance

# Run with markers
pytest -m performance -v -s

# Generate performance report
pytest tests/performance/ -v -s > performance_report.txt
```

### Performance Benchmarking

```bash
# Run comprehensive benchmark
pytest tests/performance/test_performance.py::TestPerformanceBenchmarks::test_complete_performance_benchmark -v -s

# Output format:
# - Data preprocessing: 50ms for 1,000 rows
# - Single prediction P95: 45ms
# - Batch throughput: 25,000 predictions/s
# - Memory usage: 150MB
```

### Interpreting Results

**Green (Meeting Requirements):**
- ✅ P95 latency < 100ms
- ✅ Throughput > target
- ✅ Memory usage within limits

**Yellow (Warning):**
- ⚠️ Performance close to thresholds
- ⚠️ Inconsistent latencies (high variance)
- ⚠️ Memory usage increasing

**Red (Failing):**
- ❌ Latency exceeds requirements
- ❌ Throughput below minimum
- ❌ Resource exhaustion

---

## Regression Tests

### Overview

Regression tests ensure model quality and system behavior remains consistent across changes.

**Location:** `tests/regression/`

**Execution Time:** Medium (5-30s per test)

**Purpose:**
- Detect model performance degradation
- Ensure prediction consistency
- Verify deterministic behavior
- Catch unintended changes

### Test Categories

1. **Model Performance Regression**
   - Accuracy, precision, recall, F1
   - ROC-AUC, confusion matrix
   - Performance vs. baseline thresholds

2. **Prediction Consistency**
   - Reproducible predictions
   - Deterministic probabilities
   - Stable under perturbations

3. **Feature Engineering Regression**
   - Preprocessing determinism
   - Feature engineering consistency
   - Feature count stability

4. **Edge Case Behavior**
   - All-zero inputs
   - Extreme values
   - Identical features

### Baseline Thresholds

```python
BASELINE_THRESHOLDS = {
    'accuracy': 0.70,
    'precision': 0.68,
    'recall': 0.68,
    'f1_score': 0.70,
    'roc_auc': 0.75
}

DEGRADATION_TOLERANCE = 0.05  # 5% acceptable degradation
```

### Example: Accuracy Regression Test

```python
def test_accuracy_no_regression(self, trained_baseline_model):
    """Test that model accuracy meets baseline threshold."""
    metrics = trained_baseline_model['metrics']
    accuracy = metrics['accuracy']

    print(f"Current accuracy: {accuracy:.4f}")
    print(f"Baseline threshold: {BASELINE_THRESHOLDS['accuracy']:.4f}")

    # Check against absolute threshold
    assert accuracy >= BASELINE_THRESHOLDS['accuracy'], \
        f"Accuracy {accuracy:.4f} below baseline {BASELINE_THRESHOLDS['accuracy']:.4f}"

    print(f"✓ Accuracy meets baseline requirements")
```

### Example: Prediction Reproducibility Test

```python
def test_prediction_reproducibility(self, trained_baseline_model):
    """Test that predictions are reproducible."""
    model = trained_baseline_model['model']
    X_test = trained_baseline_model['X_test_processed'][:100]

    # Make predictions multiple times
    predictions_1 = model.predict(X_test)
    predictions_2 = model.predict(X_test)
    predictions_3 = model.predict(X_test)

    # All predictions should be identical
    assert np.array_equal(predictions_1, predictions_2)
    assert np.array_equal(predictions_2, predictions_3)

    print(f"✓ Predictions are fully reproducible")
```

### Running Regression Tests

```bash
# Run all regression tests
pytest tests/regression/ -v

# Run specific regression test category
pytest tests/regression/test_model_regression.py::TestModelPerformanceRegression

# Run with baseline comparison
pytest tests/regression/ -v -s
```

### Managing Baselines

**Option 1: Hardcoded Thresholds (Current)**
```python
BASELINE_THRESHOLDS = {
    'accuracy': 0.70,
    'precision': 0.68,
    ...
}
```

**Option 2: JSON Baseline File**
```python
# baselines/model_v1_baseline.json
{
    "model_version": "1.0.0",
    "accuracy": 0.7234,
    "roc_auc": 0.7891,
    ...
}

# Load in test
with open('baselines/model_v1_baseline.json') as f:
    baseline = json.load(f)
```

**Option 3: Historical Tracking**
```python
# Store metrics in database/file after each run
# Compare against historical average
```

### When to Update Baselines

Update baseline thresholds when:
- ✅ Model improvements are intentional and verified
- ✅ New training data improves performance
- ✅ Algorithm changes yield better results
- ✅ Business requirements change

Do NOT update baselines to:
- ❌ Make failing tests pass
- ❌ Hide performance degradation
- ❌ Avoid investigating issues

---

## Writing New Tests

### Test Writing Checklist

- [ ] **Descriptive name**: Test name clearly describes what's being tested
- [ ] **Documentation**: Docstring explains purpose and expectations
- [ ] **Setup**: Proper fixtures or setup for test data
- [ ] **Execution**: Clear test logic
- [ ] **Assertions**: Explicit, meaningful assertions
- [ ] **Cleanup**: Resources cleaned up after test
- [ ] **Independence**: Test doesn't depend on other tests

### Test Template

```python
def test_feature_description(self, fixture_name):
    """
    Test that [component] [does something] [under conditions].

    This test verifies:
    1. [First thing being tested]
    2. [Second thing being tested]
    3. [Third thing being tested]

    Args:
        fixture_name: Description of fixture

    Expected behavior:
        - [Expected outcome 1]
        - [Expected outcome 2]
    """
    # Arrange: Set up test data and conditions
    test_data = create_test_data()
    expected_result = calculate_expected_result()

    # Act: Execute the code being tested
    actual_result = function_under_test(test_data)

    # Assert: Verify the results
    assert actual_result == expected_result, \
        f"Expected {expected_result}, got {actual_result}"

    print(f"✓ Test passed: [description]")
```

### Assertion Best Practices

```python
# ✅ Good: Descriptive assertion message
assert accuracy > 0.8, f"Accuracy {accuracy:.4f} below threshold 0.8"

# ❌ Bad: No message
assert accuracy > 0.8

# ✅ Good: Specific comparison
assert len(predictions) == len(y_test)

# ❌ Bad: Vague comparison
assert len(predictions) > 0

# ✅ Good: Float comparison with tolerance
np.testing.assert_almost_equal(a, b, decimal=6)

# ❌ Bad: Direct float comparison
assert a == b  # May fail due to floating point precision
```

### Parameterized Tests

Test the same logic with multiple inputs:

```python
@pytest.mark.parametrize("model_type,expected_min_accuracy", [
    ("logistic_regression", 0.70),
    ("random_forest", 0.75),
    ("xgboost", 0.78),
])
def test_model_type_performance(model_type, expected_min_accuracy):
    """Test different model types meet minimum accuracy."""
    model = train_model(X_train, y_train, model_type=model_type)
    accuracy = evaluate_model(model, X_test, y_test)

    assert accuracy >= expected_min_accuracy, \
        f"{model_type} accuracy {accuracy:.4f} below minimum {expected_min_accuracy}"
```

### Test Fixtures

```python
@pytest.fixture(scope="module")
def large_dataset():
    """Create a large dataset for integration tests."""
    # This runs once per test module
    data = generate_large_dataset(n_samples=10000)
    yield data
    # Cleanup code here if needed

@pytest.fixture(scope="function")
def temp_directory():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
    # Automatically cleaned up after test
```

---

## CI/CD Integration

### GitHub Actions Configuration

**File:** `.github/workflows/ci.yml`

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=src/ml_pipeline --cov-report=xml

    - name: Run integration tests
      run: |
        pytest tests/integration/ -v

    - name: Run regression tests
      run: |
        pytest tests/regression/ -v

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: pytest unit tests
        entry: pytest tests/unit/ -v
        language: system
        pass_filenames: false
        always_run: true
EOF

# Install hooks
pre-commit install
```

### Test Stages in CI/CD

```
Stage 1: Fast Tests (< 1 min)
├── Unit tests
├── Code linting
└── Type checking

Stage 2: Integration Tests (1-5 min)
├── Integration tests
└── Regression tests

Stage 3: Performance Tests (5-15 min)
├── Performance benchmarks
├── Load testing
└── Stress testing (optional)

Stage 4: Deploy
└── If all tests pass
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Tests Pass Locally but Fail in CI

**Symptoms:**
- Tests work on your machine
- Same tests fail in CI/CD pipeline

**Causes:**
- Different Python versions
- Missing dependencies
- Environment-specific behavior
- Race conditions

**Solutions:**
```bash
# 1. Match Python version
python --version  # Check your version
# Update CI config to match

# 2. Verify dependencies
pip freeze > requirements-test.txt
# Add to CI

# 3. Use explicit seeds
np.random.seed(42)
random.seed(42)

# 4. Add test markers for flaky tests
@pytest.mark.flaky(reruns=3)
def test_sometimes_fails():
    pass
```

#### Issue 2: Slow Test Execution

**Symptoms:**
- Tests take too long to run
- CI/CD pipeline timeouts

**Solutions:**
```bash
# 1. Run in parallel
pytest -n auto

# 2. Skip slow tests in development
pytest -m "not slow"

# 3. Use faster fixtures
@pytest.fixture(scope="module")  # Instead of "function"
def expensive_setup():
    pass

# 4. Optimize test data
# Use smaller datasets for unit tests
# Reserve large datasets for integration tests
```

#### Issue 3: Flaky Tests

**Symptoms:**
- Tests sometimes pass, sometimes fail
- Non-deterministic behavior

**Causes:**
- Randomness not controlled
- Time-dependent logic
- External dependencies
- Concurrency issues

**Solutions:**
```python
# 1. Fix random seeds
np.random.seed(42)
random.seed(42)
tf.random.set_seed(42)  # If using TensorFlow

# 2. Mock time-dependent logic
from unittest.mock import patch

@patch('time.time', return_value=1234567890)
def test_with_fixed_time(mock_time):
    pass

# 3. Isolate tests
# Each test should clean up after itself
# Use fixtures with yield for cleanup

# 4. Mark and rerun flaky tests
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_flaky():
    pass
```

#### Issue 4: Import Errors

**Symptoms:**
```
ImportError: No module named 'ml_pipeline'
ModuleNotFoundError: No module named 'src'
```

**Solutions:**
```bash
# 1. Install package in editable mode
pip install -e .

# 2. Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# 3. Use pytest's pythonpath
# Create pytest.ini
[pytest]
pythonpath = src

# 4. Run from project root
cd /path/to/project
pytest tests/
```

#### Issue 5: MLflow Tracking Errors

**Symptoms:**
```
MlflowException: Failed to connect to tracking server
ConnectionError: [Errno 111] Connection refused
```

**Solutions:**
```python
# 1. Use local file tracking in tests
import mlflow
mlflow.set_tracking_uri("file:///tmp/mlruns")

# 2. Use fixture to set up tracking
@pytest.fixture(scope="module")
def mlflow_tracking():
    tracking_uri = "file:///tmp/test_mlruns"
    mlflow.set_tracking_uri(tracking_uri)
    yield tracking_uri

# 3. Mock MLflow in unit tests
from unittest.mock import patch

@patch('mlflow.log_metric')
@patch('mlflow.log_param')
def test_with_mocked_mlflow(mock_param, mock_metric):
    pass
```

### Debug Mode

```bash
# Run tests in debug mode
pytest --pdb  # Drop into debugger on failure

# Run with full traceback
pytest --tb=long

# Show local variables in traceback
pytest --showlocals

# Run with warnings visible
pytest -W all

# Verbose output with print statements
pytest -vv -s
```

### Test Performance Profiling

```bash
# Install pytest-profiling
pip install pytest-profiling

# Profile tests
pytest --profile

# Profile and save SVG
pytest --profile-svg

# Show top slowest tests
pytest --durations=10
```

---

## Best Practices Summary

### Do's ✅

- **Write tests first** (TDD when possible)
- **Use descriptive test names** that explain what's being tested
- **Keep tests independent** - no dependencies between tests
- **Use fixtures** for shared setup code
- **Test edge cases** and error conditions
- **Maintain tests** like production code
- **Run tests frequently** during development
- **Use CI/CD** to run tests automatically
- **Document complex test logic**
- **Measure and improve coverage**

### Don'ts ❌

- **Don't test external libraries** (trust they work)
- **Don't write tests that always pass**
- **Don't ignore flaky tests**
- **Don't use time.sleep()** in tests (use mocks instead)
- **Don't commit commented-out tests**
- **Don't skip cleanup code**
- **Don't use production data** in tests
- **Don't make tests too complex**
- **Don't test implementation details** (test behavior)
- **Don't let test debt accumulate**

---

## Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Data Pipeline | 90%+ |
| Model Training | 85%+ |
| Feature Engineering | 90%+ |
| API Endpoints | 95%+ |
| Utilities | 80%+ |
| Overall | 85%+ |

```bash
# Check current coverage
pytest --cov=src/ml_pipeline --cov-report=term-missing

# Generate coverage badge
coverage-badge -o coverage.svg
```

---

## Continuous Improvement

### Regular Test Maintenance

- **Weekly**: Review test failures and flaky tests
- **Monthly**: Analyze test coverage and add missing tests
- **Quarterly**: Review and update baseline thresholds
- **Yearly**: Refactor and optimize test suite

### Test Metrics to Track

1. **Test Count**: Total number of tests
2. **Test Coverage**: Code coverage percentage
3. **Test Duration**: Time to run full suite
4. **Failure Rate**: Percentage of test runs that fail
5. **Flaky Rate**: Percentage of tests that are flaky

### Improving Test Quality

1. **Regular reviews**: Review new tests in code reviews
2. **Refactoring**: Clean up duplicate test code
3. **Documentation**: Keep test docs up to date
4. **Training**: Share testing best practices with team
5. **Tooling**: Invest in better testing tools

---

## Quick Reference

### Common Commands

```bash
# Run all tests
pytest

# Run specific category
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
pytest tests/regression/

# Run with coverage
pytest --cov=src/ml_pipeline --cov-report=html

# Run in parallel
pytest -n auto

# Run verbose
pytest -v -s

# Run specific test
pytest tests/unit/test_validation.py::test_specific_function

# Run failed tests
pytest --lf

# Show slowest tests
pytest --durations=10
```

### Test Markers

```python
# Mark slow tests
@pytest.mark.slow
def test_expensive_operation():
    pass

# Mark performance tests
@pytest.mark.performance
def test_latency():
    pass

# Mark integration tests
@pytest.mark.integration
def test_end_to_end():
    pass

# Skip test conditionally
@pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires Python 3.9+")
def test_new_feature():
    pass
```

---

## Conclusion

Comprehensive testing is essential for maintaining a reliable, high-quality ML pipeline. This guide provides the framework and tools needed to:

- ✅ Verify code correctness
- ✅ Ensure model quality
- ✅ Maintain performance standards
- ✅ Catch regressions early
- ✅ Build confidence in deployments

**Remember:** Tests are not just for catching bugs—they're living documentation of how your system should behave.

For questions or improvements to this testing guide, please open an issue or submit a pull request.

---

*Last Updated: 2024-01-01*
*Maintained by: ML Platform Team*
