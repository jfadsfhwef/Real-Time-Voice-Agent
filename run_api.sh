#!/bin/bash
# Script to run the FastAPI server

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Get port from environment or use default (8000)
PORT=${PORT:-8000}

# Run the FastAPI server
echo "Starting FastAPI server on port $PORT..."
uvicorn src.main:app --host 0.0.0.0 --port $PORT --reload

# Exit status
exit $? 