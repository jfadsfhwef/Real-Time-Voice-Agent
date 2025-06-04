#!/bin/bash
# Script to run all tests for the Voice Agent

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run pytest with coverage
echo "Running tests with coverage..."
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Exit status
exit $? 