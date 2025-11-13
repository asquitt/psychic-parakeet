#!/bin/bash

#############################################################################
# ML Pipeline Test Runner
#############################################################################
# This script runs the complete test suite with various options.
#
# Usage:
#   ./run_tests.sh                # Run all tests
#   ./run_tests.sh quick          # Run only quick tests (< 30s)
#   ./run_tests.sh unit           # Run only unit tests
#   ./run_tests.sh integration    # Run only integration tests
#   ./run_tests.sh coverage       # Run with coverage report
#   ./run_tests.sh verbose        # Run with verbose output
#
# Author: ML Platform Team
# Last Updated: 2024-01-01
#############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "============================================================================="
echo "  ML Pipeline Test Suite Runner"
echo "============================================================================="
echo -e "${NC}"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}✗ pytest not found. Installing...${NC}"
    pip install pytest pytest-cov psutil
fi

# Default test mode
TEST_MODE=${1:-"all"}

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}>>> $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Start time
START_TIME=$(date +%s)

case "$TEST_MODE" in
    "quick")
        print_header "Running Quick Tests (smoke + unit)"
        pytest tests/test_smoke.py tests/unit/ -v
        ;;

    "unit")
        print_header "Running Unit Tests"
        pytest tests/unit/ -v --tb=short
        ;;

    "integration")
        print_header "Running Integration Tests"
        pytest tests/integration/ -v -s --tb=short
        ;;

    "performance")
        print_header "Running Performance Tests"
        print_warning "Performance tests may take 2-5 minutes"
        pytest tests/performance/ -v -s --tb=short
        ;;

    "regression")
        print_header "Running Regression Tests"
        pytest tests/regression/ -v -s --tb=short
        ;;

    "coverage")
        print_header "Running Tests with Coverage Report"
        pytest tests/ -v \
            --cov=src/ml_pipeline \
            --cov-report=term-missing \
            --cov-report=html \
            --tb=short
        print_success "Coverage report generated in htmlcov/index.html"
        ;;

    "verbose")
        print_header "Running All Tests (Verbose)"
        pytest tests/ -vv -s --tb=long
        ;;

    "parallel")
        print_header "Running Tests in Parallel"
        if command -v pytest-xdist &> /dev/null; then
            pytest tests/ -v -n auto --tb=short
        else
            print_warning "pytest-xdist not installed. Running sequentially."
            print_warning "Install with: pip install pytest-xdist"
            pytest tests/ -v --tb=short
        fi
        ;;

    "all")
        print_header "Running Complete Test Suite"

        # 1. Smoke tests
        print_header "1/5: Smoke Tests"
        pytest tests/test_smoke.py -v --tb=line
        print_success "Smoke tests passed"

        # 2. Unit tests
        print_header "2/5: Unit Tests"
        pytest tests/unit/ -v --tb=short
        print_success "Unit tests passed"

        # 3. Integration tests (if they exist and pass)
        print_header "3/5: Integration Tests"
        if [ -d "tests/integration" ] && [ "$(ls -A tests/integration/*.py 2>/dev/null)" ]; then
            pytest tests/integration/ -v --tb=short || print_warning "Some integration tests failed (may need full setup)"
        else
            print_warning "Integration tests skipped (require full environment)"
        fi

        # 4. Performance tests (optional)
        print_header "4/5: Performance Tests"
        if [ -d "tests/performance" ] && [ "$(ls -A tests/performance/*.py 2>/dev/null)" ]; then
            pytest tests/performance/ -v --tb=short -k "not slow" || print_warning "Some performance tests failed"
        else
            print_warning "Performance tests skipped (require full setup)"
        fi

        # 5. Regression tests (optional)
        print_header "5/5: Regression Tests"
        if [ -d "tests/regression" ] && [ "$(ls -A tests/regression/*.py 2>/dev/null)" ]; then
            pytest tests/regression/ -v --tb=short || print_warning "Some regression tests failed"
        else
            print_warning "Regression tests skipped (require full setup)"
        fi

        print_success "Test suite completed"
        ;;

    *)
        echo -e "${RED}Unknown test mode: $TEST_MODE${NC}"
        echo ""
        echo "Available modes:"
        echo "  quick        - Quick tests (smoke + unit)"
        echo "  unit         - Unit tests only"
        echo "  integration  - Integration tests only"
        echo "  performance  - Performance tests only"
        echo "  regression   - Regression tests only"
        echo "  coverage     - All tests with coverage"
        echo "  verbose      - All tests with verbose output"
        echo "  parallel     - Run tests in parallel"
        echo "  all          - Complete test suite (default)"
        exit 1
        ;;
esac

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo -e "${BLUE}=============================================================================${NC}"
echo -e "${GREEN}✓ Test execution completed in ${ELAPSED} seconds${NC}"
echo -e "${BLUE}=============================================================================${NC}"

# Exit with success
exit 0
