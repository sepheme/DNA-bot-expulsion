@echo off
REM start.bat - launcher for DNA-bot-expulsion main.py
REM - Changes directory to the script folder
REM - Attempts to activate a local virtual environment named .venv or venv (if present)
REM - Runs main.py with the system python

cd /d "%~dp0"

REM Try common venv names
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

echo Starting DNA-bot-expulsion (main.py)...
python "%~dp0main.py"
set rc=%ERRORLEVEL%
if %rc% neq 0 (
    echo.
    echo The script exited with error code %rc%.
    echo If Python is not found, install Python and add it to PATH or activate a virtualenv first.
    pause
)

exit /b %rc%
