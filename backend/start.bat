@echo off
setlocal
cd /d "%~dp0"

if not exist "main.py" (
  echo ERROR: main.py was not found.
  echo Extract the whole ZIP archive before running this file.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo The Python environment is not installed yet.
  call "install.bat"
  if errorlevel 1 exit /b 1
)

echo.
echo Server address: http://127.0.0.1:8000
echo Open this address manually in Chrome, Edge, or another browser.
echo Keep this window open while using the service.
echo.
".venv\Scripts\python.exe" "main.py"

echo.
echo The server has stopped.
pause
