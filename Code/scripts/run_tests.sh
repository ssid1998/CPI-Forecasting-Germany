#!/usr/bin/env bash
# run_tests.sh
# Runs the automated test suite for the machine learning pipeline

echo "==========================================================="
echo " Starting Automated Test Suite (PyTest) "
echo "==========================================================="

# Ensure virtual environment is active or exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found in venv. Please run the setup/start script first."
    exit 1
fi

source venv/bin/activate

# Check if pytest is installed, install if missing
if ! command -v pytest &> /dev/null
then
    echo "pytest could not be found, installing..."
    pip install pytest
fi

# Run the tests
echo "Executing PyTest..."
pytest tests/ -v

echo "==========================================================="
echo " Testing Complete."
echo "==========================================================="
