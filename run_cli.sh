#!/bin/bash
# Script to run the Voice Agent CLI

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Parse command line arguments
ROOM_NAME=""
DEBUG_MODE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--room)
            ROOM_NAME="--room $2"
            shift 2
            ;;
        -d|--debug)
            DEBUG_MODE="--debug"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run the CLI tool
echo "Starting Voice Agent CLI..."
python -m src.run_cli $ROOM_NAME $DEBUG_MODE

# Exit status
exit $? 