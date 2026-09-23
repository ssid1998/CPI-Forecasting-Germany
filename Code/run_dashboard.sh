#!/usr/bin/env bash
# run_dashboard.sh - Launch the Streamlit dashboard

set -e

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run ./setup_env.sh first."
    exit 1
fi

source venv/bin/activate
python3 -m streamlit run app.py --server.address=0.0.0.0
