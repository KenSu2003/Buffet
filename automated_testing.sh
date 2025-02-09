#!/bin/bash

# Path to your virtual environment's activate script
VENV_PATH="Buffet/venv/bin/activate"

# Directory where the code is located
CODE_DIR="~/Buffet/Code"

# Path to the Python file you want to execute
PYTHON_FILE="~/Buffet/Code/paper_trading.py"

# Activate the virtual environment
source "$VENV_PATH"

# Navigate to the Code directory
cd "$CODE_DIR" || exit

# Run the Python script with nohup to keep it running in the background
nohup python -u "$PYTHON_FILE" &

echo "Script is running in the background. Check output.log for details."