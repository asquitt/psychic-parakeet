"""
Test Model Serving API

This script tests the FastAPI model serving endpoints.

Usage:
    python scripts/test_api.py
"""

import requests
import json
import time


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get("http://localhost:8000/health")

    if response.status_code == 200:
        data = response.json()
        print("✅ Health check passed")
        print(f"   Status: {data['status']}")
        print(f"   Model loaded: {data['model_loaded']}")
        print(f"   Model: {data['model_name']} v{data['model_version']}")
    else:
        print(f"❌ Health check failed: {response.status_code}")


def test_prediction():
    """Test prediction endpoint."""
    print("\nTesting prediction endpoint...")

    # Sample request
    request_data = {
        "features": {
            "feature_1": 1.5,
            "feature_2": -0.5,
            "feature_3": 0.8,
            "feature_4": 1.2,
            "feature_5": -0.3
        }
    }

    start_time = time.time()
    response = requests.post(
        "http://localhost:8000/predict",
        json=request_data
    )
    latency = (time.time() - start_time) * 1000

    if response.status_code == 200:
        data = response.json()
        print("✅ Prediction successful")
        print(f"   Prediction: {data['prediction']}")
        print(f"   Probability: {data.get('probability', 'N/A')}")
        print(f"   Model version: {data['model_version']}")
        print(f"   Latency: {data['latency_ms']:.2f}ms (total: {latency:.2f}ms)")
    else:
        print(f"❌ Prediction failed: {response.status_code}")
        print(f"   Error: {response.text}")


def test_batch_prediction():
    """Test batch prediction endpoint."""
    print("\nTesting batch prediction endpoint...")

    # Sample batch request
    request_data = [
        {
            "features": {
                "feature_1": 1.5, "feature_2": -0.5, "feature_3": 0.8,
                "feature_4": 1.2, "feature_5": -0.3
            }
        },
        {
            "features": {
                "feature_1": -1.0, "feature_2": 0.5, "feature_3": -0.3,
                "feature_4": 0.8, "feature_5": 1.1
            }
        },
        {
            "features": {
                "feature_1": 0.3, "feature_2": 1.2, "feature_3": -0.5,
                "feature_4": -0.2, "feature_5": 0.7
            }
        }
    ]

    start_time = time.time()
    response = requests.post(
        "http://localhost:8000/predict/batch",
        json=request_data
    )
    latency = (time.time() - start_time) * 1000

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Batch prediction successful")
        print(f"   Predictions: {len(data)}")
        print(f"   Total latency: {latency:.2f}ms")
        print(f"   Avg latency per prediction: {latency/len(data):.2f}ms")

        for i, pred in enumerate(data):
            print(f"   [{i+1}] Prediction: {pred['prediction']}, "
                  f"Probability: {pred.get('probability', 'N/A')}")
    else:
        print(f"❌ Batch prediction failed: {response.status_code}")
        print(f"   Error: {response.text}")


def test_metrics():
    """Test metrics endpoint."""
    print("\nTesting metrics endpoint...")
    response = requests.get("http://localhost:8000/metrics")

    if response.status_code == 200:
        print("✅ Metrics endpoint accessible")
        print("   View in Prometheus: http://localhost:9090")
    else:
        print(f"❌ Metrics endpoint failed: {response.status_code}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING MODEL SERVING API")
    print("=" * 60)
    print("\nMake sure the API is running:")
    print("  make serve")
    print("  or")
    print("  docker-compose up model-api")
    print()

    try:
        test_health()
        test_prediction()
        test_batch_prediction()
        test_metrics()

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETE")
        print("=" * 60)
        print("\n📊 API Documentation: http://localhost:8000/docs")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Please make sure the API is running on http://localhost:8000")


if __name__ == "__main__":
    main()
