# Docker and Containerization

## The Problem: "It Works on My Machine"

One of the most common problems in software development is environmental inconsistency. A developer builds an application on their laptop, everything works perfectly, but when they deploy it to a server or a teammate tries to run it, things break. Different operating systems, different library versions, different configurations -- any of these can cause failures.

TrustChain-AV has a lot of dependencies:
- Python 3.11 with specific library versions
- PyTorch (CPU version, not GPU)
- FFmpeg for video processing
- Node.js 20 for the frontend
- PostgreSQL 16 for the database
- System libraries like libpq

Asking every developer or evaluator to install all of these correctly is impractical. Docker solves this.

## What is Docker?

Docker is a platform for packaging applications into **containers** -- self-contained units that include everything the application needs to run: code, runtime, libraries, and system tools.

### The Shipping Container Analogy

Before standardized shipping containers, moving goods was chaotic. Every product had different packaging, different handling requirements, and different loading procedures. Ports needed specialized equipment for each type of cargo.

The invention of the standardized shipping container transformed global trade. Any container fits on any ship, truck, or train. The contents do not matter -- the container is the same standard size.

Docker containers work the same way:
- The "container" is a standardized package
- The "contents" are your application and its dependencies
- The "ship" is any computer that has Docker installed
- It does not matter what is inside -- the container always works the same way

### Container vs. Virtual Machine

You might have heard of virtual machines (VMs). Containers serve a similar purpose but are lighter:

| Aspect | Virtual Machine | Container |
|--------|----------------|-----------|
| Includes | Full operating system (GB) | Just the app and its dependencies (MB) |
| Startup time | Minutes | Seconds |
| Resource usage | Heavy (each VM needs its own OS) | Light (shares the host OS kernel) |
| Isolation | Complete (separate OS) | Process-level (shared kernel) |

A VM is like renting an entire apartment (separate kitchen, bathroom, living room). A container is like renting a desk in a co-working space (you have your workspace but share the building's utilities).

## How Docker Works

### Images and Containers

Two key concepts:

**Docker Image**: A blueprint or recipe. It is a read-only template that describes how to set up an environment. Think of it as a frozen snapshot: "Start with Python 3.11, install these packages, copy this code."

**Docker Container**: A running instance of an image. You can run multiple containers from the same image, like printing multiple copies of the same photo. Each container runs independently.

The relationship is like:
- Image = cookie cutter (the template)
- Container = cookie (the actual running thing)

### Dockerfile: The Recipe

A **Dockerfile** is a text file with step-by-step instructions for building an image. TrustChain-AV has two Dockerfiles:

**Backend Dockerfile** (simplified explanation):
1. Start with the official Python 3.11 image
2. Install system tools (FFmpeg for video processing, PostgreSQL client libraries)
3. Install PyTorch (CPU version -- no GPU needed)
4. Install Python dependencies (FastAPI, SQLAlchemy, etc.)
5. Copy the application code
6. Set up the startup command (run migrations, then start the server)

**Frontend Dockerfile** (simplified explanation):
1. Start with the official Node.js 20 image
2. Copy package.json (the list of JavaScript dependencies)
3. Install dependencies (React, Vite, Tailwind, etc.)
4. Copy the application code
5. Set up the startup command (start the development server)

### Layers and Caching

Docker builds images in **layers**. Each instruction in the Dockerfile creates a layer, and Docker caches these layers. If a layer has not changed, Docker reuses the cached version instead of rebuilding it.

This is why the Dockerfile copies `requirements.txt` before copying the full application code. The dependencies change rarely, but the code changes frequently. With this ordering:

- Change code only? Docker reuses the cached dependency layer (fast rebuild)
- Change dependencies? Docker rebuilds from that layer onward (slower, but rare)

Think of it like baking a cake. If you already mixed the batter (dependencies) and just need to add frosting (code changes), you do not start from scratch -- you just add the frosting.

## Docker Compose: Running Multiple Containers

TrustChain-AV is not a single application -- it is three services that work together:
1. **Backend** (FastAPI + Python)
2. **Frontend** (React + Node.js)
3. **Database** (PostgreSQL)

**Docker Compose** is a tool for defining and running multi-container applications. Instead of starting each container manually with a long command, you describe all services in a single file (`docker-compose.yml`) and start everything with one command: `docker compose up`.

### How TrustChain-AV's Compose Works

The `docker-compose.yml` file defines:

**Database service (db)**:
- Uses the official PostgreSQL 16 Alpine image (no custom build needed)
- Stores data in a Docker volume (survives container restarts)
- Has a health check (the backend waits for the database to be ready before starting)
- Exposes port 5432

**Backend service (backend)**:
- Builds from the backend Dockerfile
- Depends on the database (only starts after the database is healthy)
- Mounts the backend code folder (changes in code are reflected immediately without rebuilding)
- Runs migrations, then starts the API server
- Exposes port 8000

**Frontend service (frontend)**:
- Builds from the frontend Dockerfile
- Depends on the backend
- Mounts the frontend code folder for hot reloading
- Exposes port 5173

### Service Communication

Inside Docker Compose, services can talk to each other using their service names as hostnames:
- The backend connects to the database using hostname `db` (not `localhost`)
- The backend's API is available to the frontend at `backend:8000`

Docker Compose creates a private network for all the services. They can find each other by name, like colleagues in the same office.

## Volumes: Persistent Storage

By default, when a Docker container is deleted, everything inside it is lost. This is fine for the application code (it exists on your disk), but terrible for the database (you would lose all your data).

**Volumes** solve this by providing persistent storage that exists outside the container:

TrustChain-AV uses three volumes:

| Volume | Purpose |
|--------|---------|
| `pgdata` | PostgreSQL database files -- your analysis history survives container restarts |
| `upload_data` | Uploaded video files -- stored at /data inside the backend container |
| `model_cache` | Downloaded ML model weights -- avoids re-downloading ResNet-50 and Wav2Vec2 every time |

Think of volumes like external hard drives. The container is the computer -- you can replace the computer, but the external drive keeps your data safe.

### The Anonymous Volume Trick

The frontend service has a special volume: `/app/node_modules`. This tells Docker: "Use the node_modules that were installed during the image build, not the ones from my host machine." This prevents conflicts between Windows/macOS/Linux versions of native modules.

## Environment Variables

Sensitive configuration (database passwords, API keys) should not be hardcoded in source code. TrustChain-AV uses a `.env` file that Docker Compose reads automatically.

The `.env` file is not committed to Git (it is in `.gitignore`). Instead, a `.env.example` file shows what variables are needed without revealing actual values. Each developer copies `.env.example` to `.env` and fills in their values.

## Common Docker Commands Explained

| Command | What It Does |
|---------|-------------|
| `docker compose up` | Start all services defined in docker-compose.yml |
| `docker compose up --build` | Rebuild images, then start (use after changing Dockerfile or dependencies) |
| `docker compose up -d` | Start in detached mode (runs in background) |
| `docker compose down` | Stop and remove all containers (data in volumes is preserved) |
| `docker compose down -v` | Stop and remove containers AND volumes (deletes all data) |
| `docker compose logs -f` | Stream logs from all services in real time |
| `docker compose exec backend bash` | Open a shell inside the running backend container |

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **Container** | A lightweight, self-contained package with an app and all its dependencies |
| **Image** | A read-only template for creating containers |
| **Dockerfile** | Instructions for building an image |
| **Docker Compose** | Tool for running multi-container applications |
| **Volume** | Persistent storage that survives container deletion |
| **Layer** | A cached step in the image build process |
| **Service** | A single container definition in Docker Compose (e.g., backend, frontend, db) |
| **Port mapping** | Connecting a port on your machine to a port in the container (e.g., 5173:5173) |
| **Health check** | A test that Docker runs to verify a service is ready |

## Further Reading

- [FastAPI](fastapi.md) -- The backend application running inside a container
- [PostgreSQL](postgresql.md) -- The database running in its own container
- [React and Vite](react-and-vite.md) -- The frontend running in its own container
