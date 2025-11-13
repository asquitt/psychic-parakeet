# Tests Directory

This directory contains comprehensive tests for the ML Pipeline project.

## Test Structure

```
tests/
├── test_smoke.py              # Smoke tests (verify test infrastructure works)
├── unit/                      # Unit tests (fast, isolated)
│   ├── __init__.py
│   └── test_validation.py     # Data validation unit tests
├── integration/               # Integration tests (component interactions)
│   ├── __init__.py
│   └── test_pipeline_integration.py  # Full pipeline tests
├── performance/               # Performance tests (latency, throughput)
│   ├── __init__.py
│   └── test_performance.py    # Performance benchmarks
└── regression/                # Regression tests (model quality)
    ├── __init__.py
    └── test_model_regression.py  # Model quality tests
```

## Quick Start

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov psutil

# Install project dependencies
pip install -r requirements.txt

# Install project in editable mode (recommended)
pip install -e .
```

### Running Tests

```bash
# Run smoke tests (verify setup)
pytest tests/test_smoke.py -v

# Run all tests
pytest

# Run specific test category
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest tests/performance/    # Performance tests
pytest tests/regression/     # Regression tests

# Run with verbose output
pytest -v

# Run with output visible (print statements)
pytest -s

# Run specific test file
pytest tests/unit/test_validation.py

# Run specific test function
pytest tests/unit/test_validation.py::test_validate_schema_success
```

### Test Coverage

```bash
# Run with coverage report
pytest --cov=src/ml_pipeline --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src/ml_pipeline --cov-report=html
open htmlcov/index.html
```

## Test Categories

### 1. Smoke Tests (`test_smoke.py`)

**Purpose:** Verify test infrastructure is properly configured

**Run Time:** < 1 second

**Run Command:**
```bash
pytest tests/test_smoke.py -v
```

**What it tests:**
- Test framework setup
- Basic Python operations
- Pytest fixtures
- Parametrized tests

### 2. Unit Tests (`unit/`)

**Purpose:** Test individual components in isolation

**Run Time:** Fast (< 10 seconds total)

**Run Command:**
```bash
pytest tests/unit/ -v
```

**What it tests:**
- Data validation logic
- Individual class methods
- Error handling
- Edge cases

**Coverage Goal:** 80%+ of core logic

### 3. Integration Tests (`integration/`)

**Purpose:** Test component interactions and end-to-end flows

**Run Time:** Medium (1-2 minutes)

**Run Command:**
```bash
pytest tests/integration/ -v -s
```

**What it tests:**
- Data pipeline flow (validation → preprocessing → feature engineering)
- Model training pipeline (data → training → evaluation)
- MLflow integration
- End-to-end workflow (data → model → predictions)

**Note:** Requires MLflow and may create temporary tracking directories

### 4. Performance Tests (`performance/`)

**Purpose:** Verify performance requirements (latency, throughput)

**Run Time:** Longer (2-5 minutes)

**Run Command:**
```bash
pytest tests/performance/ -v -s
```

**What it tests:**
- Single prediction latency (P50, P95, P99)
- Batch prediction throughput
- Data pipeline throughput
- Concurrent request handling
- Memory usage
- Load testing

**Performance Targets:**
- Single prediction P95: < 100ms
- Batch throughput: > 10,000 predictions/second
- Data pipeline: > 1,000 rows/second

### 5. Regression Tests (`regression/`)

**Purpose:** Detect model quality degradation and ensure consistency

**Run Time:** Medium (1-2 minutes)

**Run Command:**
```bash
pytest tests/regression/ -v -s
```

**What it tests:**
- Model accuracy vs. baseline thresholds
- Prediction reproducibility
- Feature engineering determinism
- Edge case handling
- Model serialization consistency

**Baseline Thresholds:**
- Accuracy: >= 0.70
- ROC-AUC: >= 0.75
- F1 Score: >= 0.70

## Common Use Cases

### Development Workflow

```bash
# 1. Run smoke test to verify setup
pytest tests/test_smoke.py -v

# 2. Run unit tests (fast feedback during development)
pytest tests/unit/ -v

# 3. Run integration tests before commit
pytest tests/integration/ -v

# 4. Run full test suite before PR
pytest -v
```

### CI/CD Pipeline

```bash
# Stage 1: Fast tests
pytest tests/test_smoke.py tests/unit/ -v

# Stage 2: Integration tests
pytest tests/integration/ -v

# Stage 3: Regression tests
pytest tests/regression/ -v

# Stage 4: Performance tests (optional, on schedule)
pytest tests/performance/ -v -s
```

### Performance Benchmarking

```bash
# Run comprehensive performance benchmark
pytest tests/performance/test_performance.py::TestPerformanceBenchmarks::test_complete_performance_benchmark -v -s

# Profile test execution time
pytest --durations=10

# Generate performance report
pytest tests/performance/ -v -s > performance_report.txt
```

### Regression Detection

```bash
# Run regression tests after code changes
pytest tests/regression/ -v -s

# Run regression tests after dependency updates
pytest tests/regression/ -v -s

# Run regression tests after model retraining
pytest tests/regression/ -v -s
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'ml_pipeline'`:

```bash
# Solution 1: Install package in editable mode
pip install -e .

# Solution 2: Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Solution 3: Run from project root
cd /path/to/project
pytest tests/
```

### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install test-specific dependencies
pip install pytest pytest-cov psutil
```

### Slow Tests

```bash
# Run tests in parallel (faster)
pip install pytest-xdist
pytest -n auto

# Skip slow tests during development
pytest -m "not slow"

# Run only fast unit tests
pytest tests/unit/ -v
```

### Failed Tests

```bash
# Run only failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff

# Get detailed error information
pytest --tb=long --showlocals

# Drop into debugger on failure
pytest --pdb
```

## Test Markers

Tests can be marked with custom markers:

```python
@pytest.mark.slow
def test_expensive_operation():
    pass

@pytest.mark.integration
def test_pipeline_flow():
    pass

@pytest.mark.performance
def test_latency():
    pass
```

Run tests by marker:

```bash
# Skip slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration

# Run integration or performance tests
pytest -m "integration or performance"
```

## Best Practices

1. **Run smoke tests first** to verify setup
2. **Run unit tests frequently** during development (fast feedback)
3. **Run integration tests before commits** to catch integration issues
4. **Run regression tests** after significant changes
5. **Run performance tests** periodically or before releases
6. **Keep tests independent** - no dependencies between tests
7. **Use descriptive test names** that explain what's being tested
8. **Document complex test logic** with comments and docstrings

## Test Maintenance

- **Weekly**: Review and fix failing tests
- **Monthly**: Update baseline thresholds in regression tests
- **Quarterly**: Review test coverage and add missing tests
- **Annually**: Refactor and optimize test suite

## Documentation

For comprehensive testing documentation, see:
- [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) - Complete testing guide
- [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) - Troubleshooting guide

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure tests pass locally
3. Verify CI/CD pipeline passes
4. Update test documentation if needed

## Questions or Issues

For questions about tests or issues with the test suite:
1. Check the [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md)
2. Check the [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
3. Open an issue on GitHub

---

**Last Updated:** 2024-01-01
**Test Framework:** pytest
**Coverage Target:** 85%+
