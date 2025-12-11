@echo off
REM Dream Axis Lead Collection Website - Startup Script for Windows

echo Starting Dream Axis Lead Collection Website...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3 first.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Start the server
echo.
echo Starting server on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python server.py

pause

