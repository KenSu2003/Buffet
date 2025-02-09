#!/bin/bash

# Path to your virtual environment's activate script
VENV_PATH="Buffet/venv/bin/activate"

# Directory where the code is located
CODE_DIR="Buffet/Code"

# Path to the Python file you want to execute
PYTHON_FILE="paper_trading.py"

# Log file with a timestamp
LOG_FILE="/home/admin/Buffet/output_$(date '+%Y-%m-%d_%H-%M-%S').log"

# Activate the virtual environment
echo "Activating virtual environment: $VENV_PATH"
source "$VENV_PATH"

# Navigate to the Code directory
echo "Navigating to code directory: $CODE_DIR"
cd "$CODE_DIR" || { echo "Failed to navigate to $CODE_DIR"; exit 1; }

# Run the Python script with nohup and log output
echo "Starting Python script in the background: $PYTHON_FILE"
nohup python -u "$PYTHON_FILE" > "$LOG_FILE" 2>&1 &

echo "Script is running in the background. Check $LOG_FILE for details."
