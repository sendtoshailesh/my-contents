#!/bin/bash
set -e

# Configuration
LOCAL_PROJECT_NAME="my-contents-venv"
LOCAL_VENV_PATH="$HOME/.virtualenvs/$LOCAL_PROJECT_NAME"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "---------------------------------------------------------"
echo "Setting up virtual environment for my-contents"
echo "Project Location: $PROJECT_ROOT"
echo "Virtual Environment: $LOCAL_VENV_PATH"
echo "---------------------------------------------------------"

# Step 1: Ensure local venv parent directory exists
if [ ! -d "$HOME/.virtualenvs" ]; then
    echo "Creating directory: $HOME/.virtualenvs"
    mkdir -p "$HOME/.virtualenvs"
fi

# Step 2: Remove old local venv if exists to start fresh
if [ -d "$LOCAL_VENV_PATH" ]; then
    echo "Removing existing local venv at $LOCAL_VENV_PATH..."
    rm -rf "$LOCAL_VENV_PATH"
fi

# Step 3: Create the new virtual environment in the local directory (clean, no symlinks)
echo "Creating new virtual environment at $LOCAL_VENV_PATH..."
python3 -m venv "$LOCAL_VENV_PATH"

# Step 4: Activate and install dependencies
echo "Activating virtual environment and installing dependencies..."
source "$LOCAL_VENV_PATH/bin/activate"

# Upgrade pip first
pip install --upgrade pip

if [ -f "$PROJECT_ROOT/requirements-clean.txt" ]; then
    echo "Installing packages from requirements-clean.txt..."
    pip install -r "$PROJECT_ROOT/requirements-clean.txt" 2>&1 | grep -v "Ignoring the following" || true
    # Try requirements.txt as fallback
elif [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "Installing packages from requirements.txt..."
    pip install -r "$PROJECT_ROOT/requirements.txt"
else
    echo "No requirements files found. Skipping dependency installation."
fi

echo ""
echo "---------------------------------------------------------"
echo "✓ Success! Virtual environment created at:"
echo "  $LOCAL_VENV_PATH"
echo ""
echo "This fixes the OneDrive alert issue."
echo ""
echo "IMPORTANT: Update your activation method:"
echo ""
echo "Instead of: source .venv/bin/activate"
echo "Use this:   source ~/.virtualenvs/$LOCAL_PROJECT_NAME/bin/activate"
echo ""
echo "Or add this to your .zshrc/.bashrc for convenience:"
echo "  alias venv='source ~/.virtualenvs/$LOCAL_PROJECT_NAME/bin/activate'"
echo ""
echo "Then you can just type: venv"
echo "---------------------------------------------------------"
