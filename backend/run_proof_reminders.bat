@echo off
REM Proof Deadline Reminder Script
REM Run this daily to send reminder emails to students 2 days before their deadlines

echo ================================================
echo Proof Deadline Reminder System
echo ================================================
echo.

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "..\..\.venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "..\..\.venv\Scripts\activate.bat"
)

REM Run the reminder script
echo Running proof deadline reminders...
python proof_deadline_reminders.py

echo.
echo ================================================
echo Reminder process completed
echo ================================================
echo.

pause
