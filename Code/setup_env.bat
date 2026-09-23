@echo off
REM setup_env.bat - Create virtual environment and install dependencies

echo [1/3] Checking Python virtual environment...
IF NOT EXIST venv (
    python -m venv venv
)

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/3] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Environment is ready.
pause
