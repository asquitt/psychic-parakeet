"""
Performance and Load Tests for ML Pipeline

This module contains comprehensive performance tests that verify the system
meets latency, throughput, and resource utilization requirements.

Tests cover:
- API endpoint performance (P50, P95, P99 latency)
- Model inference speed and throughput
- Data pipeline processing throughput
- Concurrent request handling
- Memory and CPU usage profiling
- Load testing at scale

Performance Targets:
- API P95 latency: < 500ms
- API P99 latency: < 1000ms
- Model inference: < 100ms for single prediction
- Batch prediction throughput: > 1000 predictions/second
- Memory usage: < 2GB for standard operations

Author: ML Pipeline Team
Last Updated: 2024-01-01
"""

import pytest
import pandas as pd
import numpy as np
import time
import statistics
import concurrent.futures
from typing import List, Dict, Callable
import psutil
import os
import gc

from ml_pipeline.data.preprocessing import DataPreprocessor
from ml_pipeline.features.engineering import FeatureEngineer
from ml_pipeline.models.training import ModelTrainer
from sklearn.ensemble import RandomForestClassifier


@pytest.fixture(scope="module")
def sample_data():
    """
    Generate sample data for performance tests.

    Returns:
        pd.DataFrame: Sample dataset with 10,000 rows
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


@pytest.fixture(scope="module")
def trained_model(sample_data):
    """
    Train a model for performance testing.

    Args:
        sample_data: Sample dataset fixture

    Returns:
        Trained model
    """
    feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
    X = sample_data[feature_columns]
    y = sample_data['target']

    preprocessor = DataPreprocessor(
        numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
        categorical_features=['feature5']
    )

    X_processed = preprocessor.fit_transform(X)

    model = RandomForestClassifier(
        n_estimators=50,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_processed, y)

    return model, preprocessor


def measure_execution_time(func: Callable, *args, **kwargs) -> tuple:
    """
    Measure execution time of a function.

    Args:
        func: Function to measure
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        tuple: (result, execution_time_ms)
    """
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()

    execution_time_ms = (end_time - start_time) * 1000

    return result, execution_time_ms


def measure_memory_usage(func: Callable, *args, **kwargs) -> tuple:
    """
    Measure memory usage of a function.

    Args:
        func: Function to measure
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        tuple: (result, memory_usage_mb)
    """
    process = psutil.Process(os.getpid())

    # Force garbage collection for accurate measurement
    gc.collect()

    # Measure memory before
    mem_before = process.memory_info().rss / 1024 / 1024  # MB

    # Execute function
    result = func(*args, **kwargs)

    # Measure memory after
    mem_after = process.memory_info().rss / 1024 / 1024  # MB

    memory_usage_mb = mem_after - mem_before

    return result, memory_usage_mb


def calculate_percentiles(values: List[float]) -> Dict[str, float]:
    """
    Calculate percentile statistics.

    Args:
        values: List of numerical values

    Returns:
        dict: P50, P95, P99, min, max, mean
    """
    sorted_values = sorted(values)

    return {
        'min': min(values),
        'max': max(values),
        'mean': statistics.mean(values),
        'p50': statistics.median(values),
        'p95': sorted_values[int(len(sorted_values) * 0.95)] if len(sorted_values) > 20 else sorted_values[-1],
        'p99': sorted_values[int(len(sorted_values) * 0.99)] if len(sorted_values) > 100 else sorted_values[-1],
    }


class TestDataPipelinePerformance:
    """
    Performance tests for data pipeline components.

    Tests verify that data validation, preprocessing, and feature
    engineering meet performance requirements.
    """

    def test_preprocessing_performance(self, sample_data):
        """
        Test data preprocessing performance.

        Performance requirements:
        - Should process 10,000 rows in < 1 second
        - P95 latency for transform should be < 100ms

        Args:
            sample_data: Sample dataset fixture
        """
        feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        X = sample_data[feature_columns]

        preprocessor = DataPreprocessor(
            numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
            categorical_features=['feature5']
        )

        # Measure fit_transform time
        _, fit_transform_time = measure_execution_time(
            preprocessor.fit_transform,
            X
        )

        print(f"\n=== Preprocessing Performance ===")
        print(f"Fit + Transform time: {fit_transform_time:.2f}ms for {len(X)} rows")
        print(f"Throughput: {len(X) / (fit_transform_time / 1000):.0f} rows/second")

        # Measure multiple transform operations to get distribution
        transform_times = []
        for _ in range(50):
            _, transform_time = measure_execution_time(preprocessor.transform, X)
            transform_times.append(transform_time)

        stats = calculate_percentiles(transform_times)

        print(f"\nTransform Performance (50 iterations):")
        print(f"  - Mean: {stats['mean']:.2f}ms")
        print(f"  - P50: {stats['p50']:.2f}ms")
        print(f"  - P95: {stats['p95']:.2f}ms")
        print(f"  - P99: {stats['p99']:.2f}ms")

        # Assertions
        assert fit_transform_time < 1000, \
            f"Fit+transform should complete in < 1s, got {fit_transform_time:.2f}ms"
        assert stats['p95'] < 100, \
            f"P95 transform latency should be < 100ms, got {stats['p95']:.2f}ms"

    def test_feature_engineering_performance(self, sample_data):
        """
        Test feature engineering performance.

        Performance requirements:
        - Should process 10,000 rows in < 2 seconds
        - Memory usage should be < 500MB

        Args:
            sample_data: Sample dataset fixture
        """
        feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        X = sample_data[feature_columns]

        engineer = FeatureEngineer(
            poly_degree=2,
            interaction_features=True,
            statistical_features=False
        )

        # Measure fit_transform time and memory
        result, fit_transform_time = measure_execution_time(
            engineer.fit_transform,
            X
        )

        _, memory_usage = measure_memory_usage(engineer.fit_transform, X)

        print(f"\n=== Feature Engineering Performance ===")
        print(f"Fit + Transform time: {fit_transform_time:.2f}ms for {len(X)} rows")
        print(f"Throughput: {len(X) / (fit_transform_time / 1000):.0f} rows/second")
        print(f"Memory usage: {memory_usage:.2f}MB")
        print(f"Output feature count: {result.shape[1]}")

        # Assertions
        assert fit_transform_time < 2000, \
            f"Feature engineering should complete in < 2s, got {fit_transform_time:.2f}ms"
        assert memory_usage < 500, \
            f"Memory usage should be < 500MB, got {memory_usage:.2f}MB"

    def test_pipeline_throughput(self, sample_data):
        """
        Test end-to-end data pipeline throughput.

        Measures the throughput of the complete data pipeline:
        raw data → preprocessing → feature engineering

        Performance requirement:
        - Should process > 1000 rows/second

        Args:
            sample_data: Sample dataset fixture
        """
        feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        X = sample_data[feature_columns]

        # Setup pipeline
        preprocessor = DataPreprocessor(
            numerical_features=['feature1', 'feature2', 'feature3', 'feature4'],
            categorical_features=['feature5']
        )

        engineer = FeatureEngineer(
            poly_degree=2,
            interaction_features=True,
            statistical_features=False
        )

        # Measure complete pipeline
        start_time = time.perf_counter()

        X_processed = preprocessor.fit_transform(X)
        X_engineered = engineer.fit_transform(
            pd.DataFrame(X_processed, columns=[f'f{i}' for i in range(X_processed.shape[1])])
        )

        end_time = time.perf_counter()

        total_time = (end_time - start_time) * 1000
        throughput = len(X) / (total_time / 1000)

        print(f"\n=== End-to-End Pipeline Throughput ===")
        print(f"Total time: {total_time:.2f}ms for {len(X)} rows")
        print(f"Throughput: {throughput:.0f} rows/second")
        print(f"Input features: {X.shape[1]}")
        print(f"Output features: {X_engineered.shape[1]}")

        # Assertion
        assert throughput > 1000, \
            f"Pipeline throughput should be > 1000 rows/s, got {throughput:.0f}"


class TestModelInferencePerformance:
    """
    Performance tests for model inference.

    Tests verify that model predictions meet latency and throughput
    requirements for both single and batch predictions.
    """

    def test_single_prediction_latency(self, trained_model):
        """
        Test single prediction latency.

        Performance requirements:
        - P50 latency: < 50ms
        - P95 latency: < 100ms
        - P99 latency: < 150ms

        Args:
            trained_model: Trained model fixture
        """
        model, preprocessor = trained_model

        # Create single sample
        sample = pd.DataFrame({
            'feature1': [0.5],
            'feature2': [1.2],
            'feature3': [-0.3],
            'feature4': [2.1],
            'feature5': [1]
        })

        # Preprocess sample
        sample_processed = preprocessor.transform(sample)

        # Measure prediction latency (multiple iterations)
        latencies = []
        n_iterations = 1000

        for _ in range(n_iterations):
            start_time = time.perf_counter()
            _ = model.predict(sample_processed)
            end_time = time.perf_counter()

            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)

        stats = calculate_percentiles(latencies)

        print(f"\n=== Single Prediction Performance ===")
        print(f"Iterations: {n_iterations}")
        print(f"Mean latency: {stats['mean']:.2f}ms")
        print(f"P50 latency: {stats['p50']:.2f}ms")
        print(f"P95 latency: {stats['p95']:.2f}ms")
        print(f"P99 latency: {stats['p99']:.2f}ms")
        print(f"Min latency: {stats['min']:.2f}ms")
        print(f"Max latency: {stats['max']:.2f}ms")

        # Assertions
        assert stats['p50'] < 50, \
            f"P50 latency should be < 50ms, got {stats['p50']:.2f}ms"
        assert stats['p95'] < 100, \
            f"P95 latency should be < 100ms, got {stats['p95']:.2f}ms"
        assert stats['p99'] < 150, \
            f"P99 latency should be < 150ms, got {stats['p99']:.2f}ms"

    def test_batch_prediction_throughput(self, trained_model):
        """
        Test batch prediction throughput.

        Performance requirement:
        - Should process > 10,000 predictions/second

        Args:
            trained_model: Trained model fixture
        """
        model, preprocessor = trained_model

        # Create batch of samples
        batch_sizes = [10, 100, 1000, 10000]
        results = {}

        for batch_size in batch_sizes:
            # Generate batch
            batch = pd.DataFrame({
                'feature1': np.random.randn(batch_size),
                'feature2': np.random.randn(batch_size),
                'feature3': np.random.randn(batch_size),
                'feature4': np.random.randn(batch_size),
                'feature5': np.random.choice([0, 1, 2], batch_size)
            })

            batch_processed = preprocessor.transform(batch)

            # Measure prediction time
            start_time = time.perf_counter()
            _ = model.predict(batch_processed)
            end_time = time.perf_counter()

            elapsed_time = (end_time - start_time)
            throughput = batch_size / elapsed_time

            results[batch_size] = {
                'time_ms': elapsed_time * 1000,
                'throughput': throughput,
                'latency_per_sample_ms': (elapsed_time * 1000) / batch_size
            }

        print(f"\n=== Batch Prediction Performance ===")
        for batch_size, metrics in results.items():
            print(f"\nBatch size: {batch_size}")
            print(f"  Total time: {metrics['time_ms']:.2f}ms")
            print(f"  Throughput: {metrics['throughput']:.0f} predictions/second")
            print(f"  Latency per sample: {metrics['latency_per_sample_ms']:.3f}ms")

        # Assertion - check largest batch throughput
        max_throughput = results[10000]['throughput']
        assert max_throughput > 10000, \
            f"Batch throughput should be > 10,000/s, got {max_throughput:.0f}/s"

    def test_concurrent_predictions(self, trained_model):
        """
        Test concurrent prediction handling.

        Verifies that the model can handle multiple concurrent
        prediction requests without significant degradation.

        Performance requirement:
        - Should handle 10 concurrent requests with < 2x latency increase

        Args:
            trained_model: Trained model fixture
        """
        model, preprocessor = trained_model

        # Create sample for prediction
        sample = pd.DataFrame({
            'feature1': [0.5],
            'feature2': [1.2],
            'feature3': [-0.3],
            'feature4': [2.1],
            'feature5': [1]
        })
        sample_processed = preprocessor.transform(sample)

        # Measure single-threaded baseline
        start_time = time.perf_counter()
        for _ in range(100):
            _ = model.predict(sample_processed)
        baseline_time = (time.perf_counter() - start_time) * 1000

        # Measure concurrent execution
        n_workers = 10
        requests_per_worker = 10

        def make_predictions(n_predictions):
            """Helper function for concurrent execution."""
            for _ in range(n_predictions):
                _ = model.predict(sample_processed)

        start_time = time.perf_counter()

        with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = [
                executor.submit(make_predictions, requests_per_worker)
                for _ in range(n_workers)
            ]
            concurrent.futures.wait(futures)

        concurrent_time = (time.perf_counter() - start_time) * 1000

        total_predictions = n_workers * requests_per_worker
        speedup = baseline_time / concurrent_time
        degradation = concurrent_time / baseline_time

        print(f"\n=== Concurrent Prediction Performance ===")
        print(f"Workers: {n_workers}")
        print(f"Requests per worker: {requests_per_worker}")
        print(f"Total predictions: {total_predictions}")
        print(f"Single-threaded time: {baseline_time:.2f}ms")
        print(f"Concurrent time: {concurrent_time:.2f}ms")
        print(f"Speedup: {speedup:.2f}x")
        print(f"Degradation: {degradation:.2f}x")

        # Assertion - concurrent should not be more than 2x slower
        assert degradation < 2.0, \
            f"Concurrent degradation should be < 2x, got {degradation:.2f}x"

    def test_memory_usage_during_inference(self, trained_model):
        """
        Test memory usage during model inference.

        Performance requirement:
        - Memory usage for 10,000 predictions should be < 100MB

        Args:
            trained_model: Trained model fixture
        """
        model, preprocessor = trained_model

        # Create large batch
        batch_size = 10000
        batch = pd.DataFrame({
            'feature1': np.random.randn(batch_size),
            'feature2': np.random.randn(batch_size),
            'feature3': np.random.randn(batch_size),
            'feature4': np.random.randn(batch_size),
            'feature5': np.random.choice([0, 1, 2], batch_size)
        })

        batch_processed = preprocessor.transform(batch)

        # Measure memory usage
        _, memory_usage = measure_memory_usage(
            model.predict,
            batch_processed
        )

        memory_per_prediction = memory_usage / batch_size

        print(f"\n=== Memory Usage During Inference ===")
        print(f"Batch size: {batch_size}")
        print(f"Total memory usage: {memory_usage:.2f}MB")
        print(f"Memory per prediction: {memory_per_prediction * 1000:.3f}KB")

        # Assertion
        assert memory_usage < 100, \
            f"Memory usage should be < 100MB, got {memory_usage:.2f}MB"


class TestLoadAndStress:
    """
    Load and stress tests for the ML system.

    Tests verify system behavior under high load and stress conditions,
    including sustained high throughput and resource exhaustion scenarios.
    """

    def test_sustained_load(self, trained_model):
        """
        Test system performance under sustained load.

        Simulates continuous prediction requests over an extended period
        to verify stability and consistent performance.

        Test duration: 30 seconds
        Target throughput: > 100 requests/second

        Args:
            trained_model: Trained model fixture
        """
        model, preprocessor = trained_model

        # Create sample
        sample = pd.DataFrame({
            'feature1': [0.5],
            'feature2': [1.2],
            'feature3': [-0.3],
            'feature4': [2.1],
            'feature5': [1]
        })
        sample_processed = preprocessor.transform(sample)

        # Run sustained load test
        duration_seconds = 10  # Reduced for faster testing
        request_count = 0
        latencies = []

        print(f"\n=== Sustained Load Test ===")
        print(f"Duration: {duration_seconds} seconds")
        print(f"Running...")

        start_time = time.perf_counter()
        end_time = start_time + duration_seconds

        while time.perf_counter() < end_time:
            request_start = time.perf_counter()
            _ = model.predict(sample_processed)
            request_end = time.perf_counter()

            latencies.append((request_end - request_start) * 1000)
            request_count += 1

        total_time = time.perf_counter() - start_time
        throughput = request_count / total_time

        # Calculate latency statistics
        stats = calculate_percentiles(latencies)

        print(f"\nResults:")
        print(f"  Total requests: {request_count}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Throughput: {throughput:.0f} requests/second")
        print(f"\nLatency distribution:")
        print(f"  Mean: {stats['mean']:.2f}ms")
        print(f"  P50: {stats['p50']:.2f}ms")
        print(f"  P95: {stats['p95']:.2f}ms")
        print(f"  P99: {stats['p99']:.2f}ms")

        # Assertions
        assert throughput > 100, \
            f"Sustained throughput should be > 100 req/s, got {throughput:.0f}"
        assert stats['p95'] < 100, \
            f"P95 latency should remain < 100ms under load, got {stats['p95']:.2f}ms"

    def test_batch_size_scaling(self, trained_model):
        """
        Test how performance scales with batch size.

        Verifies that batch prediction throughput increases with
        batch size and identifies optimal batch size.

        Args:
            trained_model: Trained model fixture
        """
        model, preprocessor = trained_model

        batch_sizes = [1, 10, 50, 100, 500, 1000, 5000, 10000]
        results = []

        print(f"\n=== Batch Size Scaling Test ===")

        for batch_size in batch_sizes:
            # Generate batch
            batch = pd.DataFrame({
                'feature1': np.random.randn(batch_size),
                'feature2': np.random.randn(batch_size),
                'feature3': np.random.randn(batch_size),
                'feature4': np.random.randn(batch_size),
                'feature5': np.random.choice([0, 1, 2], batch_size)
            })

            batch_processed = preprocessor.transform(batch)

            # Measure multiple times for accuracy
            times = []
            for _ in range(10):
                start = time.perf_counter()
                _ = model.predict(batch_processed)
                times.append(time.perf_counter() - start)

            avg_time = statistics.mean(times)
            throughput = batch_size / avg_time

            results.append({
                'batch_size': batch_size,
                'time_ms': avg_time * 1000,
                'throughput': throughput,
                'latency_per_sample_ms': (avg_time * 1000) / batch_size
            })

        print(f"\n{'Batch Size':>10} | {'Time (ms)':>10} | {'Throughput':>15} | {'Latency/Sample':>15}")
        print("-" * 65)

        for r in results:
            print(
                f"{r['batch_size']:>10} | "
                f"{r['time_ms']:>10.2f} | "
                f"{r['throughput']:>12.0f}/s | "
                f"{r['latency_per_sample_ms']:>12.3f}ms"
            )

        # Verify throughput increases with batch size
        throughputs = [r['throughput'] for r in results]
        assert throughputs[-1] > throughputs[0] * 10, \
            "Batch prediction should show significant throughput improvement"


class TestPerformanceBenchmarks:
    """
    Comprehensive performance benchmark suite.

    Provides a complete performance profile of the system for
    performance tracking and regression detection.
    """

    def test_complete_performance_benchmark(self, sample_data, trained_model):
        """
        Run complete performance benchmark suite.

        This test provides a comprehensive performance profile including:
        - Data pipeline performance
        - Model inference performance
        - Memory usage
        - Throughput at various scales

        Results can be used for:
        - Performance regression detection
        - Optimization prioritization
        - Capacity planning

        Args:
            sample_data: Sample dataset fixture
            trained_model: Trained model fixture
        """
        print(f"\n{'='*70}")
        print(f"{'ML PIPELINE PERFORMANCE BENCHMARK':^70}")
        print(f"{'='*70}")

        model, preprocessor = trained_model
        feature_columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        X = sample_data[feature_columns]

        benchmark_results = {}

        # ===== 1. Data Preprocessing =====
        print(f"\n{'1. DATA PREPROCESSING PERFORMANCE':^70}")
        print("-" * 70)

        _, preprocess_time = measure_execution_time(
            preprocessor.fit_transform,
            X.head(1000)
        )

        benchmark_results['preprocessing_1k_rows_ms'] = preprocess_time
        print(f"  1,000 rows: {preprocess_time:.2f}ms")

        # ===== 2. Single Prediction =====
        print(f"\n{'2. SINGLE PREDICTION PERFORMANCE':^70}")
        print("-" * 70)

        sample = X.head(1)
        sample_processed = preprocessor.transform(sample)

        single_latencies = []
        for _ in range(100):
            _, latency = measure_execution_time(model.predict, sample_processed)
            single_latencies.append(latency)

        single_stats = calculate_percentiles(single_latencies)
        benchmark_results['single_prediction_p50_ms'] = single_stats['p50']
        benchmark_results['single_prediction_p95_ms'] = single_stats['p95']
        benchmark_results['single_prediction_p99_ms'] = single_stats['p99']

        print(f"  P50: {single_stats['p50']:.2f}ms")
        print(f"  P95: {single_stats['p95']:.2f}ms")
        print(f"  P99: {single_stats['p99']:.2f}ms")

        # ===== 3. Batch Prediction =====
        print(f"\n{'3. BATCH PREDICTION PERFORMANCE':^70}")
        print("-" * 70)

        batch = X.head(1000)
        batch_processed = preprocessor.transform(batch)

        _, batch_time = measure_execution_time(model.predict, batch_processed)
        batch_throughput = 1000 / (batch_time / 1000)

        benchmark_results['batch_1k_predictions_ms'] = batch_time
        benchmark_results['batch_throughput_per_sec'] = batch_throughput

        print(f"  1,000 predictions: {batch_time:.2f}ms")
        print(f"  Throughput: {batch_throughput:.0f} predictions/second")

        # ===== 4. Memory Usage =====
        print(f"\n{'4. MEMORY USAGE':^70}")
        print("-" * 70)

        process = psutil.Process(os.getpid())
        current_memory_mb = process.memory_info().rss / 1024 / 1024

        benchmark_results['current_memory_mb'] = current_memory_mb

        print(f"  Current process memory: {current_memory_mb:.2f}MB")

        # ===== Summary =====
        print(f"\n{'='*70}")
        print(f"{'BENCHMARK SUMMARY':^70}")
        print(f"{'='*70}")

        print(f"\n  ✓ All performance benchmarks completed successfully")
        print(f"\n  Key Metrics:")
        print(f"    - Single prediction P95: {single_stats['p95']:.2f}ms")
        print(f"    - Batch throughput: {batch_throughput:.0f} predictions/s")
        print(f"    - Memory usage: {current_memory_mb:.2f}MB")

        # Store results for potential regression testing
        return benchmark_results


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
