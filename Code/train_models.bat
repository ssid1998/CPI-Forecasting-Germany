@echo off
REM train_models.bat - Retrain forecasting models and regenerate outputs

IF NOT EXIST venv (
    echo Virtual environment not found. Run setup_env.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python src\modeling_pipeline.py

echo Model training completed.
pause
