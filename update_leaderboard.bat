@echo off
echo ===================================================
echo [CIT Coders Arena] Initiating Weekly Database Update
echo Date: %date% %time%
echo ===================================================
cd /d "%~dp0"
python scan_entire_college.py
echo ===================================================
echo [CIT Coders Arena] Update completed successfully!
echo ===================================================
pause
