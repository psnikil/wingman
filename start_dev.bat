
@echo off
REM This script uses 'concurrently' to run both frontend and backend in the same terminal.
REM If you don't have concurrently, install it globally with:
REM   npm install -g concurrently

REM Start both servers
REM Start both servers (this will block until both are stopped)
start "" cmd /c "timeout /t 5 >nul && start "" "chrome.exe" --auto-open-devtools-for-tabs http://localhost:3000"
concurrently ^
  "cd frontend && npm run dev" ^
  "cd backend && call backend\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

