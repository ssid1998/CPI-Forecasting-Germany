@echo off
REM run_dashboard.bat - Launch the Streamlit dashboard

IF NOT EXIST venv (
    echo Virtual environment not found. Run setup_env.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python -m streamlit run app.py --server.address=0.0.0.0
