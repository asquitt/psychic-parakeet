"""
Shared Test Configuration and Fixtures

This module provides shared pytest configuration, fixtures, and utilities
for all test modules. It ensures consistent test setup and provides
reusable test data and mock objects.

Fixtures provided:
- sample_data: Consistent sample datasets
- mock_mlflow: Mocked MLflow for testing without real tracking
- temp_dir: Temporary directories for file operations
- mock_models: Pre-configured mock models
"""

import pytest
import sys
from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
from unittest.mock import Mock, MagicMock, patch
import warnings

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Suppress warnings during tests
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


# ============================================================================
# Data Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def sample_data_small():
    """
    Small dataset for quick tests (100 rows).

    Returns:
        pd.DataFrame: Small sample dataset
    """
    np.random.seed(42)
    n_samples = 100

    return pd.DataFrame({
        'feature1': np.random.randn(n_samples),
        'feature2': np.random.exponential(2, n_samples),
        'feature3': np.random.uniform(-5, 5, n_samples),
        'feature4': np.random.randn(n_samples) * 10 + 50,
        'feature5': np.random.choice([0, 1, 2], n_samples),
        'target': np.random.choice([0, 1], n_samples)
    })


@pytest.fixture(scope="session")
def sample_data_medium():
    """
    Medium dataset for integration tests (1000 rows).

    Returns:
        pd.DataFrame: Medium sample dataset
    """
    np.random.seed(42)
    n_samples = 1000

    data = {
        'feature1': np.random.randn(n_samples),
        'feature2': np.random.exponential(2, n_samples),
        'feature3': np.random.uniform(-5, 5, n_samples),
        'feature4': np.random.randn(n_samples) * 10 + 50,
        'feature5': np.random.choice([0, 1, 2], n_samples)
    }

    df = pd.DataFrame(data)

    # Create target with deterministic relationship
    df['target'] = (
        (df['feature1'] > 0).astype(int) * 0.3 +
        (df['feature2'] > 2).astype(int) * 0.3 +
        (df['feature3'] > 0).astype(int) * 0.4
    )
    noise = np.random.RandomState(42).randn(n_samples) * 0.1
    df['target'] = (df['target'] + noise > 0.5).astype(int)

    return df


@pytest.fixture(scope="session")
def sample_data_large():
    """
    Large dataset for performance tests (10000 rows).

    Returns:
        pd.DataFrame: Large sample dataset
    """
    np.random.seed(42)
    n_samples = 10000

    return pd.DataFrame({
        'feature1': np.random.randn(n_samples),
        'feature2': np.random.randn(n_samples),
        'feature3': np.random.randn(n_samples),
        'feature4': np.random.randn(n_samples),
        'feature5': np.random.choice([0, 1, 2], n_samples),
        'target': np.random.choice([0, 1], n_samples)
    })


@pytest.fixture
def sample_single_prediction():
    """
    Single prediction sample for API testing.

    Returns:
        dict: Single prediction features
    """
    return {
        'feature1': 0.5,
        'feature2': 1.2,
        'feature3': -0.3,
        'feature4': 55.0,
        'feature5': 1
    }


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_mlflow():
    """
    Mock MLflow for testing without real tracking.

    Returns:
        MagicMock: Mocked MLflow module
    """
    mock = MagicMock()

    # Mock start_run context manager
    mock_run = MagicMock()
    mock_run.info.run_id = "test_run_12345"
    mock_run.info.status = "FINISHED"
    mock.start_run.return_value.__enter__.return_value = mock_run
    mock.start_run.return_value.__exit__.return_value = None

    # Mock logging functions
    mock.log_param.return_value = None
    mock.log_metric.return_value = None
    mock.log_artifact.return_value = None

    # Mock model registry
    mock.register_model.return_value = MagicMock(name="test_model", version="1")

    return mock


@pytest.fixture
def mock_model():
    """
    Mock sklearn model for testing.

    Returns:
        Mock: Mocked model with predict/predict_proba
    """
    mock = Mock()

    # Mock predict to return binary predictions
    mock.predict.return_value = np.array([0, 1, 0, 1, 1])

    # Mock predict_proba to return probabilities
    mock.predict_proba.return_value = np.array([
        [0.7, 0.3],
        [0.4, 0.6],
        [0.8, 0.2],
        [0.3, 0.7],
        [0.2, 0.8]
    ])

    # Mock feature_importances_ for tree-based models
    mock.feature_importances_ = np.array([0.3, 0.25, 0.2, 0.15, 0.1])

    return mock


@pytest.fixture
def mock_preprocessor():
    """
    Mock data preprocessor for testing.

    Returns:
        Mock: Mocked preprocessor
    """
    mock = Mock()

    # Mock fit_transform
    def mock_fit_transform(X):
        if isinstance(X, pd.DataFrame):
            return X.values
        return X

    # Mock transform
    def mock_transform(X):
        if isinstance(X, pd.DataFrame):
            return X.values
        return X

    mock.fit_transform.side_effect = mock_fit_transform
    mock.transform.side_effect = mock_transform

    return mock


# ============================================================================
# File System Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """
    Temporary directory for test file operations.

    Yields:
        Path: Temporary directory path
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_file(temp_dir):
    """
    Temporary file for testing.

    Args:
        temp_dir: Temporary directory fixture

    Yields:
        Path: Temporary file path
    """
    temp_file = temp_dir / "test_file.txt"
    temp_file.write_text("test content")
    yield temp_file


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def local_config():
    """
    Local testing configuration (no external dependencies).

    Returns:
        dict: Local configuration
    """
    return {
        'database': {
            'type': 'sqlite',
            'path': ':memory:'  # In-memory database
        },
        'mlflow': {
            'tracking_uri': 'file:///tmp/test_mlruns',
            'experiment_name': 'test_experiment'
        },
        'model': {
            'type': 'random_forest',
            'hyperparameters': {
                'n_estimators': 10,  # Small for fast testing
                'max_depth': 5,
                'random_state': 42
            }
        },
        'features': {
            'numerical': ['feature1', 'feature2', 'feature3', 'feature4'],
            'categorical': ['feature5']
        }
    }


# ============================================================================
# Test Helpers
# ============================================================================

@pytest.fixture
def assert_array_equal():
    """
    Helper for array equality assertions.

    Returns:
        callable: Array comparison function
    """
    def _assert(arr1, arr2, decimal=7):
        np.testing.assert_array_almost_equal(arr1, arr2, decimal=decimal)
    return _assert


@pytest.fixture
def assert_dataframe_equal():
    """
    Helper for DataFrame equality assertions.

    Returns:
        callable: DataFrame comparison function
    """
    def _assert(df1, df2):
        pd.testing.assert_frame_equal(df1, df2)
    return _assert


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """
    Pytest configuration hook.

    Args:
        config: Pytest config object
    """
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "regression: marks tests as regression tests"
    )
    config.addinivalue_line(
        "markers", "local: marks tests for local execution only"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test items during collection.

    Args:
        config: Pytest config object
        items: List of test items
    """
    # Automatically mark slow tests
    for item in items:
        if "performance" in item.nodeid or "load" in item.nodeid:
            item.add_marker(pytest.mark.slow)


# ============================================================================
# Session Hooks
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up test environment before running tests.

    This runs once at the start of the test session.
    """
    # Set random seeds for reproducibility
    np.random.seed(42)

    # Configure pandas display options
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    yield

    # Cleanup after all tests
    pass


# ============================================================================
# Performance Test Helpers
# ============================================================================

@pytest.fixture
def benchmark_timer():
    """
    Simple benchmarking timer for performance tests.

    Returns:
        callable: Timer context manager
    """
    import time
    from contextlib import contextmanager

    @contextmanager
    def timer():
        start = time.perf_counter()
        result = {'elapsed': 0}
        yield result
        result['elapsed'] = (time.perf_counter() - start) * 1000  # ms

    return timer


# ============================================================================
# ML-Specific Fixtures
# ============================================================================

@pytest.fixture
def classification_metrics():
    """
    Expected classification metrics structure.

    Returns:
        dict: Metric names and types
    """
    return {
        'accuracy': float,
        'precision': float,
        'recall': float,
        'f1_score': float,
        'roc_auc': float
    }


@pytest.fixture
def baseline_thresholds():
    """
    Baseline performance thresholds for regression testing.

    Returns:
        dict: Metric thresholds
    """
    return {
        'accuracy': 0.70,
        'precision': 0.68,
        'recall': 0.68,
        'f1_score': 0.70,
        'roc_auc': 0.75
    }
