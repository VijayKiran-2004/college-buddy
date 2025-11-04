@echo off
echo ========================================
echo  College Buddy - Starting Application
echo ========================================
echo.

echo [1/2] Starting Backend Server...
echo Opening backend in new window...
start "College Buddy - Backend" cmd /k "cd /d %~dp0 && python main.py"

timeout /t 3 /nobreak >nul

echo.
echo [2/2] Starting Frontend...
echo Opening frontend in default browser...
start "" "%~dp0static\index.html"

echo.
echo ========================================
echo  Application Started Successfully!
echo ========================================
echo.
echo Backend: Running on http://localhost:8001
echo Frontend: Opened in your default browser
echo.
echo To stop the backend, close the backend window
echo.
pause
