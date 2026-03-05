#!/bin/bash

# TrustChain-AV Start Script for macOS/Linux

echo "=========================================="
echo " TrustChain-AV: Frontend-Backend Launcher"
echo "=========================================="
echo ""

# Check if running from correct directory
if [ ! -d "backend" ]; then
    echo "Error: Please run this script from the Implementation folder"
    echo "Expected structure: Implementation/backend, Implementation/Frontend"
    exit 1
fi

echo "Starting Backend Server..."
echo "Opening Flask server on http://localhost:5000"
echo ""

# Start backend in background
cd backend

# Create and activate virtual environment if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt
python app.py &
BACKEND_PID=$!

cd ..

sleep 3

echo "Starting Frontend Server..."
echo "Opening dev server on http://localhost:5173"
echo ""

# Start frontend in background
cd Frontend

npm install --silent
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "=========================================="
echo "Both servers are starting..."
echo ""
echo "Frontend:  http://localhost:5173"
echo "Backend:   http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "=========================================="
echo ""

# Wait for both processes
wait
