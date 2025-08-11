
@echo off
REM Start both frontend and backend in Windows Terminal tabs
REM The working directory is set for each tab

wt.exe ^
  new-tab -d "%CD%\frontend" cmd /k "npm run dev" ^
  ; split-pane -H -d "%CD%\backend" cmd /k "call backend\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" 

REM Wait for frontend to start (adjust timeout as needed)
timeout /t 5 >nul
REM Open Chrome to frontend with DevTools open
start "" "chrome.exe" --auto-open-devtools-for-tabs "http://localhost:3000"
