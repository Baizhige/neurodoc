@echo off
cd /d "%~dp0"
echo Starting EEG Kernel Scan Tool at http://127.0.0.1:5001
python server_scan.py
pause
