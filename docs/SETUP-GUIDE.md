# TrustChain-AV Comprehensive Setup Guide

A complete step-by-step guide to get TrustChain-AV running on your computer. This guide is written for developers who are new to technical setup processes.

---

## What is TrustChain-AV?

TrustChain-AV is a deepfake detection system that analyzes videos to determine if they are REAL or FAKE. It uses artificial intelligence to:
- Examine video frames (visual analysis)
- Examine audio tracks (voice analysis)
- Combine both analyses for a final verdict

Think of it as a video truth-verifier!

---

## What You Need Before Starting

### Required Software

| Software | Why You Need It | Where to Download |
|----------|-----------------|-------------------|
| **Git** | To download/copy the project code | https://git-scm.com |
| **Docker Desktop** | To run the entire application without installing anything else | https://www.docker.com/products/docker-desktop |

### What These Do (In Simple Terms)

- **Git** is like Google Drive for code - it lets you download the project and track changes
- **Docker Desktop** is like a "mini-computer inside your computer" that runs everything the project needs (database, backend, frontend) without you having to install Python, Node.js, databases, or anything else

---

## Part 1: Installing Docker Desktop (Windows)

### Step 1: Check Your Windows Version

1. Press `Windows Key + R`
2. Type `winver` and press Enter
3. Make sure you see **version 22H2** or later

If you have an older Windows, you'll need to update Windows first.

### Step 2: Enable Required Windows Features

1. Open **Windows Features** (search in Start menu)
2. Enable these if not already enabled:
   - **Virtual Machine Platform**
   - **Windows Subsystem for Linux (WSL2)**

### Step 3: Install Docker Desktop

1. Go to https://www.docker.com/products/docker-desktop
2. Click **Download for Windows**
3. Run the installer
4. During installation, check **Use WSL2 instead of Hyper-V** (recommended)

### Step 4: Verify Docker is Working

1. Open **PowerShell** (search in Start menu, right-click, Run as Administrator)
2. Type this and press Enter:
   ```
   docker --version
   ```
3. You should see something like `Docker version 24.x.x`

### Step 5: Verify Docker Compose

Docker Compose comes with Docker Desktop. Verify it:
   ```
   docker compose version
   ```
You should see something like `Docker Compose version v2.x.x`

> **Troubleshooting Docker Issues:**
> - If Docker won't start, make sure virtualization is enabled in BIOS
> - If you get permission errors, run PowerShell as Administrator
> - Restart your computer after installing Docker

---

## Part 2: Getting the Project Code

### Step 1: Install Git (if not already installed)

1. Go to https://git-scm.com
2. Download the Windows version
3. Run the installer with all default options

### Step 2: Clone the Repository

1. Create a folder where you want the project (e.g., `C:\Projects`)
2. Open **PowerShell** in that folder
3. Run this command:
   ```
   git clone https://github.com/zopeeeeee/TrustChain.git
   ```
4. Enter the project folder:
   ```
   cd TrustChain
   ```

---

## Part 3: Setting Up Environment Variables

### What Are Environment Variables? (Simple Explanation)

Think of environment variables as "settings" that tell the application how to connect to the database and other services. They're stored in a special file called `.env`.

### Step 1: Create the .env File

1. In the project folder (`TrustChain`), look for a file called `.env.example`
2. Copy it and rename the copy to `.env`
   - On Windows: Copy the file, then right-click > Rename, or use PowerShell:
     ```
     copy .env.example .env
     ```

### Step 2: Edit the .env File

Right-click the `.env` file → Open with → Notepad (or any text editor)

Make sure it contains exactly these values:

```
POSTGRES_USER=trustchain
POSTGRES_PASSWORD=trustchain
POSTGRES_DB=trustchain_db
DATABASE_URL=postgresql+asyncpg://trustchain:trustchain@db:5432/trustchain_db
DEBUG=true
```

Save and close the file.

> **Important:** Don't share this file if you change the password - it's like a database password!

---

## Part 4: Running the Application

### Starting Everything

1. Open **PowerShell** in the project folder
2. Run this command:
   ```
   docker compose up --build
   ```

**What happens next:**
- Docker will download PostgreSQL (the database)
- Docker will build the backend (Python + AI models)
- Docker will build the frontend (React web interface)
- The database will be set up automatically
- AI models will download on the first run

> **First Run Takes Time:** The first time you run this, it will take 5-15 minutes because Docker needs to download Python, AI models, and other dependencies. This is NORMAL. Be patient!

### Checking If It Works

Once you see messages indicating everything started, open your web browser and go to:

**http://localhost:5173**

You should see the TrustChain-AV web interface!

### Quick Health Check

To verify the backend is working, open a new tab:

**http://localhost:8000/api/health**

You should see a JSON response showing system status.

### Stopping the Application

When you want to stop the application:

1. In PowerShell, press `Ctrl + C` (or close the window)
2. Or run:
   ```
   docker compose down
   ```

---

## Part 5: Using the Application

### The Basics

1. Open **http://localhost:5173** in your browser
2. You'll see the main page with navigation options

### How to Analyze a Video

1. Click **Upload** in the navigation menu
2. Drag and drop a video file onto the page
   - Supported formats: MP4, AVI, MOV, MKV
3. Wait for processing (this takes time - the AI is analyzing!)
4. See the **REAL or FAKE** verdict with confidence score
5. Optionally download a PDF verification report

### Navigation Pages

| Page | What It Does |
|------|--------------|
| **Home** | Welcome page with overview |
| **Upload** | Upload videos for analysis |
| **Results** | See detailed analysis results |
| **History** | View past video analyses |

---

## Common Commands Reference

Here are commands you'll use often:

```bash
# Start the application (run in background)
docker compose up -d

# View all logs (scrolls continuously)
docker compose logs -f

# View backend logs only
docker compose logs -f backend

# View frontend logs only  
docker compose logs -f frontend

# Stop the application
docker compose down

# Rebuild (after code changes)
docker compose up --build

# Fresh start (deletes database too!)
docker compose down -v
docker compose up --build
```

---

## Troubleshooting Guide

### Problem: "Port already in use"

This means another program is using port 5173, 8000, or 5432.

**Solution:**
```bash
# Find what's using the port (example: port 8000)
netstat -ano | findstr :8000
```
Then either stop that program or change the port in `docker-compose.yml`.

### Problem: Frontend shows "Cannot connect to backend"

- Make sure the backend is running: `docker compose ps`
- Check backend logs: `docker compose logs backend`
- Wait a few seconds - the backend may still be starting up

### Problem: "jspdf import error"

The frontend needs to reinstall its dependencies:

```bash
docker compose exec frontend npm install
```

### Problem: Backend keeps restarting

Check the logs:
```bash
docker compose logs backend
```

Common causes:
- Database not ready yet (wait and it retries automatically)
- Missing `.env` file (see Part 3)

### Problem: "docker: command not found"

- Make sure Docker Desktop is installed and running
- Try restarting PowerShell/terminal
- Make sure "Add Docker to system PATH" was checked during installation

---

## Understanding the Project Structure

Here's what each folder does:

```
TrustChain/
├── backend/              # The server-side code (Python)
│   ├── app/              # Application logic
│   │   ├── api/          # Web API endpoints
│   │   ├── models/       # Database structures
│   │   ├── services/     # AI detection logic
│   │   └── main.py       # Application entry point
│   └── requirements.txt  # Python dependencies
├── frontend/             # The web interface (React)
│   ├── src/
│   │   ├── pages/        # Website pages
│   │   ├── components/   # Reusable UI pieces
│   │   └── lib/          # Helper functions
│   └── package.json      # JavaScript dependencies
├── docs/                 # Documentation (you're here!)
├── docker-compose.yml    # Container configuration
├── .env.example          # Environment template
└── SETUP.md              # Quick setup reference
```

---

## Technical Details (Optional)

### How It Works

1. **Frontend** (React + TypeScript)
   - A modern web interface built with React 19
   - Handles user interaction, video uploads, results display

2. **Backend** (FastAPI + Python)
   - Processes uploaded videos
   - Runs AI models for deepfake detection
   - Stores results in PostgreSQL database

3. **Database** (PostgreSQL)
   - Stores user uploads metadata
   - Stores analysis results
   - Stores audit trail

4. **AI Detection**
   - **Visual**: Uses ResNet-50 to analyze video frames
   - **Audio**: Uses Wav2Vec2 to analyze voice/audio
   - **Fusion**: Combines both for final verdict

### Ports Used

| Service | Port | URL |
|---------|------|-----|
| Frontend | 5173 | http://localhost:5173 |
| Backend API | 8000 | http://localhost:8000 |
| Database | 5432 | (internal only) |

---

## Getting Help

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Check Docker logs: `docker compose logs -f`
3. Make sure all services are running: `docker compose ps`
4. Try a fresh start:
   ```
   docker compose down -v
   docker compose up --build
   ```

### Useful Docker Commands

```bash
# See running containers
docker compose ps

# Restart a specific service
docker compose restart backend

# Enter the backend container (for debugging)
docker compose exec backend bash

# See disk usage (cleanup old volumes)
docker system df
```

---

## Summary

To get TrustChain-AV running:

1. Install **Docker Desktop**
2. Clone the repository: `git clone https://github.com/zopeeeeee/TrustChain.git`
3. Copy `.env.example` to `.env`
4. Run `docker compose up --build`
5. Open **http://localhost:5173**

That's it! The application will be running with all dependencies handled by Docker.