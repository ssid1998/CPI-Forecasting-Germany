#!/usr/bin/env bash
# train_models.sh - Retrain forecasting models and regenerate outputs

set -e

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run ./setup_env.sh first."
    exit 1
fi

source venv/bin/activate
python3 src/modeling_pipeline.py

echo "Model training completed."
