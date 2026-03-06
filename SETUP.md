# TrustChain-AV -- Setup Guide

How to get TrustChain-AV running on a new system from scratch.

## Prerequisites

Install the following before you begin:

| Tool | Version | Purpose |
|------|---------|---------|
| **Git** | 2.x+ | Clone the repository |
| **Docker Desktop** | 4.x+ | Runs all services (backend, frontend, database) |
| **Docker Compose** | v2 (bundled with Docker Desktop) | Multi-container orchestration |

> Docker Desktop includes Docker Compose v2 on Windows and macOS. On Linux, install `docker-compose-plugin` separately if needed.

No need to install Python, Node.js, PostgreSQL, or FFmpeg locally -- everything runs inside Docker containers.

## 1. Clone the Repository

```bash
git clone https://github.com/zopeeeeee/TrustChain.git
cd TrustChain
```

## 2. Create the Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

This creates a `.env` file with the following default values:

```
POSTGRES_USER=trustchain
POSTGRES_PASSWORD=trustchain
POSTGRES_DB=trustchain_db
DATABASE_URL=postgresql+asyncpg://trustchain:trustchain@db:5432/trustchain_db
DEBUG=true
```

These defaults work out of the box for local development. Change `POSTGRES_PASSWORD` if deploying beyond localhost.

## 3. Build and Start All Services

```bash
docker compose up --build
```

This will:
1. Pull the PostgreSQL 16 Alpine image
2. Build the **backend** image (Python 3.11 + PyTorch CPU + FFmpeg)
3. Build the **frontend** image (Node 20 Alpine)
4. Run Alembic database migrations automatically on startup
5. Download ML models (ResNet-50, Wav2Vec2) on first run -- this takes a few minutes

### First Run Notes

- The **backend build** takes 5-10 minutes due to PyTorch CPU installation (~800MB download).
- ML model weights are cached in a Docker volume (`model_cache`), so subsequent startups are fast.
- The `model_cache` volume persists across `docker compose down` / `docker compose up` cycles.

## 4. Verify Everything is Running

Once all three services are up:

| Service | URL | What to Check |
|---------|-----|---------------|
| **Frontend** | http://localhost:5173 | React app loads with navigation |
| **Backend API** | http://localhost:8000/api/health | Returns JSON with `"status"` and model info |
| **Database** | Accessed internally by backend | No direct access needed |

### Quick Health Check

```bash
curl http://localhost:8000/api/health
```

You should see a JSON response showing the system status and loaded ML models.

## 5. Using the Application

1. Open http://localhost:5173 in your browser
2. Navigate to **Upload** and drag-and-drop a video file (MP4, AVI, MOV, MKV)
3. The system will process the video through the detection pipeline:
   - Extract video frames
   - Extract audio track
   - Run visual analysis (ResNet-50)
   - Run audio analysis (Wav2Vec2)
   - Compute fusion verdict
4. View the **REAL/FAKE verdict** with confidence score on the results page
5. Browse past analyses on the **History** page
6. Download a **PDF verification report** for any completed analysis

## Common Commands

```bash
# Start all services (detached mode)
docker compose up -d

# View logs
docker compose logs -f

# View logs for a specific service
docker compose logs -f backend

# Stop all services
docker compose down

# Rebuild after code changes
docker compose up --build

# Reset database (removes all data)
docker compose down -v
docker compose up --build
```

## Troubleshooting

### "jspdf" import error in frontend
If the frontend container shows a Vite import error for `jspdf`, the node_modules volume is stale:
```bash
docker compose exec frontend npm install
```

### Backend keeps restarting
Check the logs for the specific error:
```bash
docker compose logs backend
```
Common causes:
- Database not ready yet (wait a few seconds, it retries automatically)
- Missing `.env` file (see Step 2)

### Port already in use
If ports 5173, 8000, or 5432 are in use by another process:
```bash
# Find what's using the port (example for port 8000)
# Windows
netstat -ano | findstr :8000

# Linux/macOS
lsof -i :8000
```
Stop the conflicting process or change the port mapping in `docker-compose.yml`.

### Fresh start (nuclear option)
Removes all containers, volumes, and cached images for this project:
```bash
docker compose down -v --rmi local
docker compose up --build
```

## Project Structure

```
TrustChain/
├── backend/                 # FastAPI backend (Python 3.11)
│   ├── app/
│   │   ├── api/             # API route handlers
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # ML detection, preprocessing
│   │   └── main.py          # FastAPI app entry point
│   ├── alembic/             # Database migrations
│   ├── tests/               # Backend test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # React frontend (Vite + TypeScript)
│   ├── src/
│   │   ├── pages/           # Page components (Home, Upload, Results, History)
│   │   ├── components/      # Shared UI components
│   │   ├── hooks/           # Custom React hooks
│   │   └── lib/             # API client, PDF generation
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml       # Multi-container orchestration
├── .env.example             # Environment variable template
└── SETUP.md                 # This file
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Tailwind CSS v4, Vite 7 |
| Backend | FastAPI, SQLAlchemy (async), Alembic, Python 3.11 |
| Database | PostgreSQL 16 |
| ML Models | ResNet-50 (visual), Wav2Vec2 (audio), WebRTC VAD |
| PDF Export | jsPDF (client-side) |
| Containerization | Docker, Docker Compose |
