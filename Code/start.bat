@echo off
REM start.bat - Helper script for Sprint 3.1 (Windows)

echo ==========================================================
echo   Sprint 3.1: Finalization ^& Delivery (Streamlit Dashboard)
echo ==========================================================

echo.
echo [1] Setting up Python Virtual Environment...
IF NOT EXIST venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo.
echo [2] Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1

echo.
echo [3] Running Model Training ^& Serialization Pipeline...
python src\modeling_pipeline.py

echo.
echo [4] Starting Interactive Streamlit Dashboard...
echo =========================================================================
echo If you are running this in GitHub Codespaces, look for a popup in the 
echo bottom right corner saying "Your application running on port 8501 is available."
echo Click "Open in Browser" to view the dashboard.
echo Alternatively, go to the "Ports" tab next to "Terminal" and click the URL.
echo =========================================================================
python -m streamlit run app.py --server.address=0.0.0.0

echo.
echo [5] Complete!
pause
