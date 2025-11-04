@echo off
REM Start College Buddy Backend Server
REM This script ensures proper WebSocket configuration

echo.
echo ================================================================================
echo     College Buddy - Backend Server Startup
echo ================================================================================
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Start the server with proper WebSocket settings
echo Starting server with WebSocket keep-alive configuration...
echo.
python start_backend.py

pause
