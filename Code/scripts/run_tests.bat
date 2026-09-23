@echo off
REM run_tests.bat
REM Runs the automated test suite for the machine learning pipeline

echo ===========================================================
echo  Starting Automated Test Suite (PyTest) 
echo ===========================================================

IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Virtual environment not found in venv. Please run the start script first.
    exit /b 1
)

call venv\Scripts\activate.bat

REM Check if pytest is installed, install if missing
pytest --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo pytest could not be found, installing...
    pip install pytest
)

REM Run the tests
echo Executing PyTest...
pytest tests\ -v

echo ===========================================================
echo  Testing Complete.
echo ===========================================================
pause
