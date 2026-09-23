@echo off
REM run_docs.bat
REM Generates HTML documentation from docstrings using Doxygen

echo ===========================================================
echo  Generating HTML Software Documentation (Doxygen)
echo ===========================================================

REM Ensure doxygen is installed
doxygen --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo doxygen could not be found. Please install Doxygen from:
    echo https://www.doxygen.nl/download.html
    echo And ensure it is in your system PATH.
    pause
    exit /b 1
)

echo Building documentation...
doxygen Doxyfile

echo ===========================================================
echo  Documentation generated successfully in doxygen\html\
echo  Open doxygen\html\index.html in your browser.
echo ===========================================================
pause
