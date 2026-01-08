@echo off
echo ===============================================
echo    ML Network Anomaly Detection
echo    Yhlas - Diploma Project 2025
echo ===============================================
echo.

cd /d "%~dp0"

echo Checking Python environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ===============================================
echo Starting Streamlit Dashboard...
echo.
echo Dashboard will open at:
echo   http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo ===============================================
echo.

start "" "http://localhost:8501"

streamlit run dashboard/app.py
