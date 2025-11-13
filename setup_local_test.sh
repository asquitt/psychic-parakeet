#!/bin/bash

#############################################################################
# Local Testing Environment Setup
#############################################################################
# This script sets up a lightweight local testing environment without
# requiring Docker, PostgreSQL, or other external services.
#
# What it does:
# - Installs minimal Python dependencies
# - Creates local test configuration
# - Runs validation tests
# - Generates test report
#
# Usage:
#   ./setup_local_test.sh
#
# Requirements:
#   - Python 3.8+
#   - pip
#
# Author: ML Platform Team
# Last Updated: 2024-01-01
#############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║              ML Pipeline - Local Testing Environment Setup               ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check Python version
echo -e "${BLUE}[1/6] Checking Python version...${NC}"
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}✗ Python 3.8+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python version OK${NC}"

# Install minimal dependencies
echo -e "\n${BLUE}[2/6] Installing minimal test dependencies...${NC}"
pip install -q pytest pytest-cov pandas numpy scikit-learn psutil 2>&1 | grep -v "already satisfied" || true
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Verify installations
echo -e "\n${BLUE}[3/6] Verifying installations...${NC}"
python -c "import pytest; import pandas; import numpy; import sklearn; print('All imports successful')"
echo -e "${GREEN}✓ All packages verified${NC}"

# Run environment check
echo -e "\n${BLUE}[4/6] Running environment check...${NC}"
cat > /tmp/env_check.py << 'PYTHON_SCRIPT'
import sys
import pandas as pd
import numpy as np
import sklearn

print(f"Python: {sys.version}")
print(f"Pandas: {pd.__version__}")
print(f"NumPy: {np.__version__}")
print(f"scikit-learn: {sklearn.__version__}")
PYTHON_SCRIPT

python /tmp/env_check.py
rm /tmp/env_check.py
echo -e "${GREEN}✓ Environment check passed${NC}"

# Run quick tests
echo -e "\n${BLUE}[5/6] Running validation tests...${NC}"
pytest tests/test_smoke.py -v -q --tb=line

# Test summary
echo -e "\n${BLUE}[6/6] Running quick unit tests...${NC}"
pytest tests/unit/ -v -q --tb=line

# Success message
echo -e "\n${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                    ✓ Local Testing Environment Ready!                    ║
║                                                                           ║
║  You can now run:                                                         ║
║    ./quick_test.sh          - Quick tests (< 30s)                         ║
║    ./run_tests.sh quick     - Smoke + unit tests                          ║
║    ./run_tests.sh unit      - All unit tests                              ║
║    pytest tests/ -v         - Full test suite                             ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

exit 0
