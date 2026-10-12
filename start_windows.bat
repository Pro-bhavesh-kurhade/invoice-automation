@echo off
setlocal
cd /d "%~dp0"
echo ===========================================
echo InvoiceDesk - Local Invoice Review Starter
echo ===========================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.11 or newer from https://www.python.org/downloads/
  echo During installation, enable "Add Python to PATH".
  pause
  exit /b 1
)
if not exist .venv (
  echo Creating local Python environment...
  py -m venv .venv
  if errorlevel 1 goto error
)
call .venv\Scripts\activate.bat
echo Installing/updating the small set of dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto error
echo Starting local app. Keep this window open while using InvoiceDesk.
start "" http://127.0.0.1:5000
python app.py
pause
exit /b 0
:error
echo Setup failed. Check the error above and try again.
pause
exit /b 1
