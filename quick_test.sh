#!/bin/bash

#############################################################################
# Quick ML Pipeline Test Script
#############################################################################
# This script runs essential tests quickly for rapid feedback during
# development. Optimized for speed (< 30 seconds).
#
# Usage:
#   ./quick_test.sh
#
# Author: ML Platform Team
# Last Updated: 2024-01-01
#############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Quick Test Suite (< 30s)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check Python and pytest
echo "Checking environment..."
python --version
pytest --version

# Run tests
echo ""
echo -e "${BLUE}Running smoke tests...${NC}"
pytest tests/test_smoke.py -v -q

echo ""
echo -e "${BLUE}Running unit tests...${NC}"
pytest tests/unit/ -v -q

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Quick tests completed successfully!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
