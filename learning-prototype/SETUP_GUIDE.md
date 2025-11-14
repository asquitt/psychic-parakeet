# Setup Guide - ML Pipeline Learning Prototype

## 🚀 Quick Setup (5 minutes)

```bash
# 1. Navigate to the learning prototype folder
cd learning-prototype

# 2. Run the automated setup script
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh

# 3. Verify installation
python scripts/verify_setup.py

# 4. You're ready to go!
cd week-1-basics
```

---

## 📋 Detailed Setup Instructions

### Step 1: System Requirements

**Minimum Requirements:**
- Python 3.8 or higher
- 4 GB RAM
- 2 GB free disk space
- Internet connection (for installations)

**Recommended:**
- Python 3.10+
- 8 GB RAM
- 5 GB free disk space
- Code editor (VS Code, PyCharm, or Sublime)

**Operating System:**
- ✅ Linux (Ubuntu 18.04+, recommended)
- ✅ macOS (10.14+)
- ✅ Windows 10+ (with WSL2 recommended)

---

### Step 2: Install Python

#### On Linux (Ubuntu/Debian):
```bash
# Update package list
sudo apt update

# Install Python 3.10
sudo apt install python3.10 python3.10-venv python3-pip

# Verify installation
python3 --version  # Should show 3.10.x
```

#### On macOS:
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10

# Verify installation
python3 --version
```

#### On Windows:
```bash
# Download from python.org
# https://www.python.org/downloads/windows/

# Or use Windows Package Manager
winget install Python.Python.3.10

# Verify installation (in PowerShell)
python --version
```

---

### Step 3: Create Virtual Environment

**Why use virtual environments?**
- Isolate project dependencies
- Avoid package conflicts
- Easy to reproduce environment
- Clean project management

```bash
# Navigate to project root
cd /path/to/psychic-parakeet/learning-prototype

# Create virtual environment
python3 -m venv venv

# Activate virtual environment

# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

---

### Step 4: Install Core Dependencies

```bash
# Ensure pip is up to date
pip install --upgrade pip

# Install core ML packages
pip install numpy pandas scikit-learn

# Install visualization libraries
pip install matplotlib seaborn

# Install testing framework
pip install pytest pytest-cov

# Install Jupyter (optional, for notebooks)
pip install jupyter ipython

# Verify installations
python -c "import numpy; import pandas; import sklearn; print('✓ All core packages installed')"
```

**Expected Output:**
```
✓ All core packages installed
```

---

### Step 5: Install MLOps Tools (Week 4)

You can install these later when you reach Week 4:

```bash
# MLflow for experiment tracking
pip install mlflow

# FastAPI for model deployment
pip install fastapi uvicorn

# Additional tools
pip install pydantic python-multipart

# Verify MLflow installation
mlflow --version
```

---

### Step 6: Install Development Tools

```bash
# Code formatting
pip install black flake8

# Type checking
pip install mypy

# Documentation
pip install sphinx

# Git pre-commit hooks (optional)
pip install pre-commit
```

---

### Step 7: Configure Git

```bash
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main

# Enable colored output
git config --global color.ui auto

# Verify configuration
git config --list
```

---

### Step 8: Set Up Code Editor

#### VS Code (Recommended)

```bash
# Install VS Code
# Download from: https://code.visualstudio.com/

# Install Python extension
# In VS Code: Ctrl+Shift+X, search "Python", install

# Recommended extensions:
# - Python (Microsoft)
# - Pylance
# - Jupyter
# - GitLens
# - autoDocstring
```

**VS Code Settings** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

#### PyCharm

```bash
# Download PyCharm Community Edition
# https://www.jetbrains.com/pycharm/download/

# Configure Python interpreter:
# File → Settings → Project → Python Interpreter
# Add → Virtualenv Environment → Existing environment
# Select: /path/to/venv/bin/python
```

---

### Step 9: Verify Complete Setup

Run the verification script:

```bash
# Navigate to scripts folder
cd learning-prototype/scripts

# Run verification
python verify_setup.py
```

**Expected Output:**
```
╔═══════════════════════════════════════════════════════════╗
║        ML Pipeline Setup Verification                     ║
╚═══════════════════════════════════════════════════════════╝

✓ Python version: 3.10.x
✓ Virtual environment: Active
✓ NumPy: 1.24.x
✓ pandas: 2.0.x
✓ scikit-learn: 1.3.x
✓ pytest: 7.4.x
✓ Git configured

═══════════════════════════════════════════════════════════
     All checks passed! You're ready to start learning!
═══════════════════════════════════════════════════════════
```

---

## 🛠️ Alternative Setup Methods

### Method 1: Using requirements.txt

```bash
# All dependencies in one file
pip install -r requirements-learning.txt

# requirements-learning.txt content:
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
pytest>=7.4.0
pytest-cov>=4.1.0
jupyter>=1.0.0
```

### Method 2: Using Docker

```bash
# Build Docker image
docker build -t ml-pipeline-learning -f Dockerfile.learning .

# Run container
docker run -it -v $(pwd):/workspace ml-pipeline-learning

# You'll be in the container with everything installed
```

### Method 3: Using Conda

```bash
# Create conda environment
conda create -n ml-pipeline python=3.10

# Activate environment
conda activate ml-pipeline

# Install packages
conda install numpy pandas scikit-learn matplotlib seaborn
conda install pytest jupyter

# Verify
conda list
```

---

## 🧪 Test Your Setup

### Quick Test

```python
# test_setup.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Test NumPy
arr = np.array([1, 2, 3, 4, 5])
print(f"✓ NumPy works: {arr.mean()}")

# Test pandas
df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
print(f"✓ pandas works: {len(df)} rows")

# Test scikit-learn
clf = RandomForestClassifier(n_estimators=10)
print("✓ scikit-learn works: Model created")

print("\n🎉 All packages working correctly!")
```

```bash
# Run test
python test_setup.py
```

---

## 🐛 Troubleshooting

### Issue 1: Python not found

```bash
# Try different commands
python --version
python3 --version
python3.10 --version

# On Windows, might need:
py --version
py -3.10 --version
```

### Issue 2: Permission denied

```bash
# On Linux/macOS, add sudo:
sudo apt install python3.10

# Or fix permissions:
sudo chown -R $USER:$USER /path/to/learning-prototype
```

### Issue 3: Virtual environment not activating

```bash
# Linux/macOS: Make sure to use source
source venv/bin/activate

# Windows: Might need to change execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate:
venv\Scripts\activate
```

### Issue 4: Package installation fails

```bash
# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Try installing with --user flag
pip install --user numpy pandas scikit-learn

# Or use conda instead
conda install numpy pandas scikit-learn
```

### Issue 5: Import errors

```bash
# Make sure virtual environment is activated
which python  # Should show venv/bin/python

# Reinstall packages
pip uninstall numpy pandas scikit-learn
pip install numpy pandas scikit-learn

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Issue 6: M1/M2 Mac specific issues

```bash
# For Apple Silicon Macs, use conda
# Install miniforge
brew install miniforge

# Create environment
conda create -n ml-pipeline python=3.10
conda activate ml-pipeline

# Install packages (conda will use ARM-optimized versions)
conda install numpy pandas scikit-learn
```

---

## 📚 Environment Management

### Save Your Environment

```bash
# Save installed packages
pip freeze > requirements-learning.txt

# Save conda environment
conda env export > environment.yml
```

### Recreate Environment

```bash
# From requirements.txt
pip install -r requirements-learning.txt

# From environment.yml
conda env create -f environment.yml
```

### Update Packages

```bash
# Update all packages
pip install --upgrade pip
pip list --outdated
pip install --upgrade numpy pandas scikit-learn

# Or with conda
conda update --all
```

---

## 🚀 Optional Enhancements

### 1. Jupyter Notebook Setup

```bash
# Install Jupyter
pip install jupyter notebook jupyterlab

# Install extensions
pip install jupyter_contrib_nbextensions
jupyter contrib nbextension install --user

# Start Jupyter
jupyter notebook
# Or JupyterLab
jupyter lab
```

### 2. GPU Support (Advanced)

```bash
# Check if GPU is available
nvidia-smi

# Install CUDA-enabled packages (NVIDIA GPU only)
pip install tensorflow  # TensorFlow with GPU
# or
pip install torch torchvision  # PyTorch with GPU

# Verify GPU support
python -c "import torch; print(torch.cuda.is_available())"
```

### 3. Database Setup (Week 4)

```bash
# Install PostgreSQL client
pip install psycopg2-binary

# Install SQLAlchemy
pip install sqlalchemy

# For SQLite (no installation needed)
# Python comes with SQLite support
```

---

## ✅ Post-Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Core packages installed (numpy, pandas, scikit-learn)
- [ ] Code editor configured
- [ ] Git configured
- [ ] Verification script passed
- [ ] Test script runs successfully
- [ ] Can run: `python -c "import numpy; import pandas; import sklearn"`

---

## 📞 Getting Help

If you're still having issues:

1. **Check the troubleshooting guide**: `notes/troubleshooting.md`
2. **Search the error message**: Google the exact error
3. **Check package versions**: `pip list` or `conda list`
4. **Recreate environment**: Start fresh if needed
5. **Use Docker**: If all else fails, use Docker setup

---

## 🎯 You're Ready!

Once all checks pass, you're ready to start learning:

```bash
cd week-1-basics
cat README.md
python 1-python-refresher.py
```

**Happy learning! 🚀**
