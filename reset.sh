#!/bin/bash
# Wrapper script to auto-activate venv and run reset_maestro.py

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_SCRIPT="$SCRIPT_DIR/scripts/reset_maestro.py"

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    cd "$SCRIPT_DIR"
    uv venv venv
    source venv/bin/activate
    uv pip install oracledb
    echo "Virtual environment created and dependencies installed."
elif [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Error: venv directory exists but is not a valid virtual environment."
    exit 1
else
    # Activate venv if not already activated
    if [ "$VIRTUAL_ENV" != "$VENV_DIR" ]; then
        source "$VENV_DIR/bin/activate"
    fi
fi

# Run the Python script with all arguments
exec python "$PYTHON_SCRIPT" "$@"
