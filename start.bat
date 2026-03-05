@echo off
REM TrustChain-AV Start Script for Windows
REM Enhanced with dependency checks and checkpoints

echo ==========================================
echo  TrustChain-AV: Frontend-Backend Launcher
echo ==========================================
echo.

REM Check if running from correct directory
if not exist "backend" (
    echo Error: Please run this script from the Implementation folder
    echo Expected structure: Implementation/backend, Implementation/Frontend
    pause
    exit /b 1
)

echo [CHECKPOINT 1] Verifying directory structure...
if not exist "backend\app.py" (
    echo Error: backend\app.py not found
    pause
    exit /b 1
)
if not exist "Frontend" (
    echo Error: Frontend folder not found
    pause
    exit /b 1
)
echo [OK] Directory structure verified
echo.

echo [CHECKPOINT 2] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [OK] %%i found
echo.

echo [CHECKPOINT 3] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo Warning: Node.js not found in PATH
    echo Frontend will not start. Install from https://nodejs.org
    echo Continuing with backend only...
    echo.
) else (
    for /f "tokens=*" %%i in ('node --version') do echo [OK] Node.js %%i found
    echo.
)

echo [CHECKPOINT 4] Verifying backend dependencies...
if not exist "backend\requirements.txt" (
    echo Error: backend\requirements.txt not found
    pause
    exit /b 1
)
echo [OK] requirements.txt found
echo.

echo [CHECKPOINT 5] Starting backend server...
echo Opening Flask server on http://localhost:5000
echo.

REM Start backend in a new window with venv activation and dependency check
start "TrustChain-AV Backend" cmd /k "cd backend && (
    if not exist venv (echo [INFO] venv not found. Creating venv... && python -m venv venv) && \
    call venv\Scripts\activate.bat && \
    echo [INFO] Upgrading pip... && python -m pip install --upgrade pip >nul 2>&1 && \
    echo [INFO] Installing required Python packages (if missing)... && python -m pip install -q -r requirements.txt || echo [WARN] pip install returned non-zero && \
    echo. && echo ========================================== && echo [Backend Ready] Starting Flask server... && echo ========================================== && echo. && python app.py
)"

echo Waiting for backend to initialize (5 seconds)...
timeout /t 5 /nobreak
echo.

echo [CHECKPOINT 6] Starting frontend server...
echo Opening dev server on http://localhost:5173
echo.

REM Start frontend in a new window (install only if node_modules missing)
start "TrustChain-AV Frontend" cmd /k "cd Frontend && (
    if not exist node_modules (echo [INFO] Installing frontend dependencies... && npm install) || echo [INFO] node_modules present, skipping npm install && \
    echo. && echo ========================================== && echo [Frontend Ready] Starting dev server... && echo ========================================== && echo. && npm run dev
)"

echo.
echo ==========================================
echo Setup in progress...
echo ==========================================
echo.
echo Frontend:  http://localhost:5173
echo Backend:   http://localhost:5000
echo.
echo [TIP] Both windows will show when servers are ready
echo [TIP] Keep both windows open for the app to work
echo [TIP] Press Ctrl+C in either window to stop that server
echo.
echo ==========================================
pause
