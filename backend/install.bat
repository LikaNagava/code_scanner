@echo off
setlocal
cd /d "%~dp0"

if not exist "main.py" (
  echo ERROR: main.py was not found.
  echo Extract the whole ZIP archive before running this file.
  goto :error
)

where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python Launcher was not found.
  echo Install Python 3.11 and enable the Python Launcher option.
  goto :error
)

py -3.11 --version >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python 3.11 was not found.
  echo Install Python 3.11 and run this file again.
  goto :error
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating the Python environment...
  py -3.11 -m venv ".venv"
  if errorlevel 1 goto :error
)

echo Installing project packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error
".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 goto :error

echo.
echo Installation completed. Run start.bat now.
pause
exit /b 0

:error
echo.
echo Installation failed. See the message above.
pause
exit /b 1
