#!/usr/bin/env bash
# start.sh - Helper script for Sprint 3.1 (Streamlit Dashboard)

echo "=========================================================="
echo "  Sprint 3.1: Finalization & Delivery (Streamlit Dashboard)"
echo "=========================================================="

echo -e "\n[1] Setting up Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo -e "\n[2] Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo -e "\n[3] Running Model Training & Serialization Pipeline..."
python3 src/modeling_pipeline.py

echo -e "\n[4] Starting Interactive Streamlit Dashboard..."
echo "========================================================================="
echo "If you are running this in GitHub Codespaces, look for a popup in the "
echo "bottom right corner saying 'Your application running on port 8501 is available.'"
echo "Click 'Open in Browser' to view the dashboard."
echo "Alternatively, go to the 'Ports' tab next to 'Terminal' and click the URL."
echo "========================================================================="
python3 -m streamlit run app.py --server.address=0.0.0.0

echo -e "\n[5] Complete!"
