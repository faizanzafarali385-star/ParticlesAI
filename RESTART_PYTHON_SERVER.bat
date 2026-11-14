@echo off
cd /d "%~dp0"
echo Stopping python server...
taskkill /F /IM python.exe 2>nul
echo.
echo Starting Python Web Server...
echo Open http://localhost:5000 in your browser

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" src/web_server.py
) else (
    python src/web_server.py
)
pause
