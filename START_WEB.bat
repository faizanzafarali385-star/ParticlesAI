@echo off
REM AI Voice Assistant - Windows Batch Startup Script

cd /d "%~dp0"

echo.
echo ====================================================================
echo   AI VOICE ASSISTANT - STARTING WEB SERVER
echo ====================================================================
echo.

REM Prefer virtual environment python if it exists
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
) else (
    set "PYTHON_CMD=python"
)

echo [1] Checking if Python is available...
%PYTHON_CMD% --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2] Starting Flask web server...
echo     URL: http://localhost:5000
echo.
echo IMPORTANT: 
echo   - Make sure your API key is in .env file
echo   - Don't close this window while using the assistant
echo   - Press Ctrl+C to stop the server
echo.
echo ====================================================================
echo.

%PYTHON_CMD% src/assistant.py web

pause
