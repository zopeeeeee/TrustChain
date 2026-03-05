#!/usr/bin/env powershell
# TrustChain-AV Start Script for PowerShell
# Enhanced with dependency checks and checkpoints

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " TrustChain-AV: Frontend-Backend Launcher" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Checkpoint 1: Directory structure
Write-Host "[CHECKPOINT 1] Verifying directory structure..." -ForegroundColor Yellow
if (-not (Test-Path "backend")) {
    Write-Host "[ERROR] Backend folder not found" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "backend\app.py")) {
    Write-Host "[ERROR] backend\app.py not found" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "Frontend")) {
    Write-Host "[ERROR] Frontend folder not found" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Directory structure verified" -ForegroundColor Green
Write-Host ""

# Checkpoint 2: Python check
Write-Host "[CHECKPOINT 2] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Checkpoint 3: Node.js check
Write-Host "[CHECKPOINT 3] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Node.js not found in PATH" -ForegroundColor Yellow
    Write-Host "Frontend will not start. Install from https://nodejs.org" -ForegroundColor Yellow
    Write-Host "Continuing with backend only..." -ForegroundColor Yellow
}
Write-Host ""

# Checkpoint 4: Requirements file check
Write-Host "[CHECKPOINT 4] Verifying backend dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "backend\requirements.txt")) {
    Write-Host "[ERROR] backend\requirements.txt not found" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] requirements.txt found" -ForegroundColor Green
Write-Host ""

# Checkpoint 5: Start backend
Write-Host "[CHECKPOINT 5] Starting backend server..." -ForegroundColor Yellow
Write-Host "Opening Flask server on http://localhost:5000" -ForegroundColor Cyan
Write-Host ""

$backendScript = @"
cd backend
if (-not (Test-Path venv)) {
    Write-Host "[Backend] Creating virtual environment..."
    python -m venv venv
    Write-Host "[Backend] Virtual environment created"
}
& .\venv\Scripts\Activate.ps1
Write-Host "[Backend] Installing dependencies..."
pip install -q -r requirements.txt
Write-Host "[Backend] Dependencies installed"
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "[Backend Ready] Starting Flask server..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
python app.py
"@

$backendJob = Start-Job -ScriptBlock {
    param($script)
    powershell -Command $script
} -ArgumentList $backendScript

Write-Host "Waiting for backend to initialize (3 seconds)..."
Start-Sleep -Seconds 3
Write-Host ""

# Checkpoint 6: Start frontend
Write-Host "[CHECKPOINT 6] Starting frontend server..." -ForegroundColor Yellow
Write-Host "Opening dev server on http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

$frontendScript = @"
cd Frontend
if (-not (Test-Path node_modules)) {
    Write-Host "[Frontend] Installing npm packages..."
    npm install
    Write-Host "[Frontend] npm packages installed"
}
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "[Frontend Ready] Starting dev server..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
npm run dev
"@

$frontendJob = Start-Job -ScriptBlock {
    param($script)
    powershell -Command $script
} -ArgumentList $frontendScript

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup in progress..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend:  http://localhost:5173" -ForegroundColor Green
Write-Host "Backend:   http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "[TIP] Both windows will show when servers are ready" -ForegroundColor Yellow
Write-Host "[TIP] Keep both windows open for the app to work" -ForegroundColor Yellow
Write-Host "[TIP] Press Ctrl+C in either window to stop that server" -ForegroundColor Yellow
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan

# Wait for both jobs
Wait-Job -Job $backendJob, $frontendJob
