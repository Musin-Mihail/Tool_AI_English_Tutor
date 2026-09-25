@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Starting English Tutor AI...
echo Open http://127.0.0.1:8000 in your browser after startup.
echo.

if not exist ".env" (
    echo [ERROR] File .env not found.
    echo Copying from .env.example...
    copy /Y ".env.example" ".env" >nul
    echo.
    echo Open .env and set CURSOR_API_KEY=
    echo Dashboard - API and SSH Keys - Add: https://cursor.com/dashboard
    echo.
    pause
    exit /b 1
)

findstr /B /C:"CURSOR_API_KEY=your_cursor_api_key_here" ".env" >nul
if not errorlevel 1 (
    echo [ERROR] CURSOR_API_KEY is not set in .env
    echo Replace your_cursor_api_key_here with your real key.
    echo Dashboard - API and SSH Keys - Add: https://cursor.com/dashboard
    echo.
    pause
    exit /b 1
)

findstr /B /C:"CURSOR_API_KEY=" ".env" >nul
if errorlevel 1 (
    echo [ERROR] CURSOR_API_KEY is missing in .env
    echo.
    pause
    exit /b 1
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run.py
) else if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" run.py
) else (
    python run.py
)

if errorlevel 1 (
    echo.
    echo Launch failed. Check .env and dependencies.
    pause
)
