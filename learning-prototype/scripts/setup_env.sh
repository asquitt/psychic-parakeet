#!/bin/bash
# ============================================================================
# ML Pipeline Learning Environment Setup Script
# ============================================================================
# This script sets up your development environment for the learning prototype

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║       ML Pipeline Learning Environment Setup                 ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# Step 1: Check Python version
# ============================================================================

echo -e "${BLUE}[1/7] Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"

    # Check if version is 3.8 or higher
    if (( $(echo "$PYTHON_VERSION >= 3.8" | bc -l) )); then
        echo -e "${GREEN}✓${NC} Version $PYTHON_VERSION is compatible"
    else
        echo -e "${YELLOW}⚠${NC} Python 3.8+ recommended, found $PYTHON_VERSION"
    fi
else
    echo -e "${RED}✗${NC} Python 3 not found!"
    echo "  Please install Python 3.8 or higher"
    exit 1
fi

# ============================================================================
# Step 2: Create virtual environment
# ============================================================================

echo -e "\n${BLUE}[2/7] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠${NC} Virtual environment already exists"
    read -p "  Recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓${NC} Virtual environment recreated"
    else
        echo -e "${GREEN}✓${NC} Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# ============================================================================
# Step 3: Activate virtual environment
# ============================================================================

echo -e "\n${BLUE}[3/7] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# ============================================================================
# Step 4: Upgrade pip
# ============================================================================

echo -e "\n${BLUE}[4/7] Upgrading pip...${NC}"
python -m pip install --upgrade pip --quiet
echo -e "${GREEN}✓${NC} Pip upgraded to $(pip --version | cut -d' ' -f2)"

# ============================================================================
# Step 5: Install core dependencies
# ============================================================================

echo -e "\n${BLUE}[5/7] Installing core ML packages...${NC}"
echo "  This may take a few minutes..."

# Create requirements file if it doesn't exist
cat > requirements-learning.txt << EOF
# Core ML packages
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Utilities
jupyter>=1.0.0
ipython>=8.12.0

# Optional (comment out if not needed)
# mlflow>=2.9.0
# fastapi>=0.104.0
# uvicorn>=0.24.0
EOF

pip install -r requirements-learning.txt --quiet
echo -e "${GREEN}✓${NC} Core packages installed"

# ============================================================================
# Step 6: Verify installations
# ============================================================================

echo -e "\n${BLUE}[6/7] Verifying installations...${NC}"

# Check NumPy
if python -c "import numpy" 2>/dev/null; then
    NUMPY_VERSION=$(python -c "import numpy; print(numpy.__version__)")
    echo -e "${GREEN}✓${NC} NumPy: $NUMPY_VERSION"
else
    echo -e "${RED}✗${NC} NumPy installation failed"
    exit 1
fi

# Check pandas
if python -c "import pandas" 2>/dev/null; then
    PANDAS_VERSION=$(python -c "import pandas; print(pandas.__version__)")
    echo -e "${GREEN}✓${NC} pandas: $PANDAS_VERSION"
else
    echo -e "${RED}✗${NC} pandas installation failed"
    exit 1
fi

# Check scikit-learn
if python -c "import sklearn" 2>/dev/null; then
    SKLEARN_VERSION=$(python -c "import sklearn; print(sklearn.__version__)")
    echo -e "${GREEN}✓${NC} scikit-learn: $SKLEARN_VERSION"
else
    echo -e "${RED}✗${NC} scikit-learn installation failed"
    exit 1
fi

# Check pytest
if python -c "import pytest" 2>/dev/null; then
    PYTEST_VERSION=$(python -c "import pytest; print(pytest.__version__)")
    echo -e "${GREEN}✓${NC} pytest: $PYTEST_VERSION"
else
    echo -e "${RED}✗${NC} pytest installation failed"
    exit 1
fi

# ============================================================================
# Step 7: Run quick smoke test
# ============================================================================

echo -e "\n${BLUE}[7/7] Running smoke tests...${NC}"

# Create and run a simple test script
cat > /tmp/test_setup.py << 'EOF'
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Test NumPy
arr = np.array([1, 2, 3, 4, 5])
assert arr.mean() == 3.0, "NumPy test failed"

# Test pandas
df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
assert len(df) == 3, "pandas test failed"

# Test scikit-learn
clf = RandomForestClassifier(n_estimators=10)
assert clf.n_estimators == 10, "scikit-learn test failed"

print("✓ All smoke tests passed!")
EOF

if python /tmp/test_setup.py; then
    echo -e "${GREEN}✓${NC} Smoke tests passed"
else
    echo -e "${RED}✗${NC} Some tests failed"
    exit 1
fi

rm /tmp/test_setup.py

# ============================================================================
# Success message
# ============================================================================

echo -e "\n${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║              ✓ Setup Complete! ✓                             ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo "Environment successfully configured!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo -e "     ${BLUE}source venv/bin/activate${NC}"
echo ""
echo "  2. Start learning:"
echo -e "     ${BLUE}cd week-1-basics${NC}"
echo -e "     ${BLUE}cat README.md${NC}"
echo ""
echo "  3. Run your first script:"
echo -e "     ${BLUE}python 1-python-refresher.py${NC}"
echo ""
echo -e "${GREEN}Happy learning! 🚀${NC}"
