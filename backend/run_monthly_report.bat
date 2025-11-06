@echo off
REM Monthly OD Report Generator for Windows
REM This script activates the virtual environment and runs the monthly report

cd /d "%~dp0"
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Generating and sending monthly OD report...
echo.

python monthly_report.py

echo.
echo Report generation completed!
echo.
pause
