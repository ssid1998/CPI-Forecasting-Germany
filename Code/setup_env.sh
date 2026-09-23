#!/usr/bin/env bash
# setup_env.sh - Create virtual environment and install dependencies

set -e

echo "[1/3] Checking Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "[2/3] Activating virtual environment..."
source venv/bin/activate

echo "[3/3] Installing dependencies..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt

echo "Environment is ready."
