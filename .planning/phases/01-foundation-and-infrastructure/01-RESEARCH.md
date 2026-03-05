# Phase 1: Foundation and Infrastructure - Research

**Researched:** 2026-03-06
**Domain:** FastAPI + PostgreSQL + Docker Compose + React/Vite full-stack foundation
**Confidence:** HIGH

## Summary

Phase 1 builds the project skeleton: a FastAPI backend with async PostgreSQL via SQLAlchemy 2.0, a React/Vite frontend shell with client-side routing, and Docker Compose orchestration binding all three services. The existing `Frontend/` and `backend/` directories will be deleted and replaced with a clean monorepo structure (`backend/`, `frontend/`, `contracts/`).

The core technical decisions are locked: FastAPI with lifespan-based model preloading, async SQLAlchemy + asyncpg, Alembic migrations, two database tables (merged uploads+results, plus blockchain_records), and three Docker Compose services. The main discretionary choices are React Router (recommended: React Router v7 in library mode -- simplest for an SPA) and PyTorch Docker image optimization (recommended: `python:3.11-slim` with CPU-only torch installed via pip).

**Primary recommendation:** Use FastAPI's `@asynccontextmanager` lifespan for model stub loading, SQLAlchemy 2.0 `create_async_engine` with asyncpg, Alembic `init -t async` for migrations, React Router v7 in library mode for routing, and a 3-service docker-compose.yml with volume mounts for hot-reload.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Clean monorepo: `backend/`, `frontend/`, `contracts/` at root with shared `docker-compose.yml`
- Delete existing Frontend/ and backend/ code entirely -- start fresh
- FastAPI backend uses modular packages: `app/api/`, `app/models/`, `app/services/`, `app/ml/` -- separated by concern
- Simplify PRD's 3 tables to 2 tables: merge results into uploads (one row per video, fewer joins). Blockchain records remain a separate table.
- Use Alembic for schema migrations -- versioned, standard for FastAPI projects
- Async SQLAlchemy with AsyncSession + asyncpg -- matches FastAPI's async nature
- 3 services in docker-compose.yml: backend (FastAPI/Uvicorn), frontend (Vite dev server), db (PostgreSQL)
- Volume mounts for hot-reload during development -- source code mounted into containers
- No pgAdmin -- team uses CLI or external tools
- PRD specifies exact database schema columns (see PRD Section 12) -- use as reference but adapt for the 2-table design
- Models load once at startup via FastAPI lifespan events, not per-request (INFR-05)
- Health endpoint should return model loading status

### Claude's Discretion
- PyTorch Docker image optimization (CPU-only slim vs full) -- Claude picks what minimizes image size while working
- Exact Alembic configuration and initial migration structure
- React routing library choice
- Frontend shell page layout and navigation structure
- Environment variable management (.env files, Docker env)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFR-01 | FastAPI backend serves REST API with async background job processing | FastAPI lifespan pattern, async SQLAlchemy engine, Uvicorn ASGI server |
| INFR-02 | PostgreSQL database stores uploads, results, and blockchain records | 2-table merged schema, Alembic async migrations, asyncpg driver |
| INFR-03 | Docker + Docker Compose containerizes all services (backend, frontend, database) | 3-service docker-compose.yml with volume mounts, Dockerfiles for backend and frontend |
| INFR-04 | Health check endpoint returns system status at GET /api/health | FastAPI router with DB connectivity check and model load status |
| INFR-05 | Models load once at server startup via FastAPI lifespan, not per-request | `@asynccontextmanager` lifespan function yielding model stubs via `app.state` |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | >=0.115 (latest) | ASGI web framework | De facto Python async API framework, lifespan support built-in |
| uvicorn[standard] | >=0.30 | ASGI server | Official FastAPI recommendation, includes uvloop |
| SQLAlchemy[asyncio] | 2.0.x (stable) | Async ORM | First-class async support since 2.0, `create_async_engine` with asyncpg |
| asyncpg | >=0.29 | PostgreSQL async driver | Fastest Python PostgreSQL driver for async |
| alembic | >=1.13 | Database migrations | Standard for SQLAlchemy projects, async template available |
| pydantic | v2.x | Data validation/serialization | Ships with FastAPI, Pydantic v2 is default |
| React | 18.x | Frontend UI library | Existing project uses React 18, stable |
| Vite | 6.x | Frontend build tool | Already in existing project, fast HMR |
| react-router-dom | 7.x | Client-side routing | Most widely used React routing library, simple SPA library mode |
| PostgreSQL | 16 | Relational database | Stable, Docker image readily available |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | >=1.0 | Environment variable loading | Load `.env` files in development |
| httpx | >=0.27 | Async HTTP client | Future phases need it; install now for health check tests |
| tailwindcss | 4.x | CSS utility framework | Already established in existing frontend |
| clsx + tailwind-merge | latest | Class name utilities | Existing `cn()` utility pattern from shadcn/ui |
| lucide-react | latest | Icon library | Already in existing frontend dependencies |
| @vitejs/plugin-react-swc | 3.x | Vite React plugin (SWC) | Already in existing devDependencies, faster than Babel |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| react-router-dom v7 | TanStack Router | TanStack has better type safety but steeper learning curve; overkill for this prototype's 4-5 routes |
| SQLAlchemy | SQLModel | SQLModel is simpler but less mature async support and fewer migration patterns |
| asyncpg | psycopg3 (async) | psycopg3 is newer but asyncpg is more battle-tested for async FastAPI |

**Installation (backend):**
```bash
pip install "fastapi[standard]" "sqlalchemy[asyncio]" asyncpg alembic pydantic-settings python-dotenv httpx
```

**Installation (frontend):**
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install react-router-dom
npx shadcn@latest init
```

## Architecture Patterns

### Recommended Project Structure
```
project-root/
├── docker-compose.yml
├── .env                        # Shared env vars (DB creds, ports)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   └── app/
│       ├── __init__.py
│       ├── main.py             # FastAPI app + lifespan
│       ├── config.py           # Settings via pydantic-settings
│       ├── database.py         # Async engine + session factory
│       ├── api/
│       │   ├── __init__.py
│       │   ├── health.py       # GET /api/health
│       │   └── router.py       # Main API router
│       ├── models/
│       │   ├── __init__.py
│       │   ├── base.py         # DeclarativeBase
│       │   ├── upload.py       # Upload model (merged with results)
│       │   └── blockchain.py   # BlockchainRecord model
│       ├── services/           # Business logic (empty stubs for now)
│       │   └── __init__.py
│       └── ml/
│           ├── __init__.py
│           └── loader.py       # Model loading stubs
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── tsconfig.json
│   └── src/
│       ├── main.tsx
│       ├── App.tsx             # Router setup
│       ├── lib/
│       │   └── utils.ts        # cn() utility
│       ├── components/
│       │   └── ui/             # shadcn components (added incrementally)
│       └── pages/
│           ├── HomePage.tsx
│           ├── UploadPage.tsx   # Shell only
│           ├── ResultsPage.tsx  # Shell only
│           └── HistoryPage.tsx  # Shell only
└── contracts/                  # Empty for Phase 1, used in Phase 5
    └── .gitkeep
```

### Pattern 1: FastAPI Lifespan for Model Preloading (INFR-05)

**What:** Use the `@asynccontextmanager` lifespan to load ML model stubs once at startup and store them on `app.state`.
**When to use:** Always -- this is the current recommended pattern, replacing deprecated `@app.on_event()`.

```python
# Source: https://fastapi.tiangolo.com/advanced/events/
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load model stubs
    logger.info("Loading ML model stubs...")
    app.state.visual_model = {"name": "ResNet-50", "status": "stub", "loaded": True}
    app.state.audio_model = {"name": "Wav2Vec2", "status": "stub", "loaded": True}
    logger.info("ML model stubs loaded successfully")
    yield
    # Shutdown: cleanup
    logger.info("Shutting down, releasing model resources...")
    app.state.visual_model = None
    app.state.audio_model = None

app = FastAPI(title="TrustChain-AV", lifespan=lifespan)
```

**Key rule:** If you use `lifespan`, do NOT also use `@app.on_event("startup")` -- they are mutually exclusive and mixing them causes silent failures.

### Pattern 2: Async SQLAlchemy Database Session

**What:** Create an async engine and session factory, use dependency injection to provide sessions to routes.
**When to use:** Every route that accesses the database.

```python
# Source: SQLAlchemy 2.0 async documentation
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

engine = create_async_engine(
    settings.database_url,  # "postgresql+asyncpg://user:pass@db:5432/trustchain"
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

**Critical:** Use `expire_on_commit=False` for async sessions -- without it, accessing attributes after commit triggers lazy loads that fail in async context.

### Pattern 3: Pydantic Settings for Configuration

**What:** Use `pydantic-settings` BaseSettings to load config from environment variables and `.env` files.
**When to use:** All configuration management.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://trustchain:trustchain@db:5432/trustchain_db"
    debug: bool = False
    api_prefix: str = "/api"
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

### Pattern 4: Merged Upload Table (2-table design)

**What:** Combine PRD's `uploads` and `results` tables into a single `uploads` table.
**When to use:** This is the locked decision from CONTEXT.md.

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Boolean, DateTime, func
import uuid

class Base(DeclarativeBase):
    pass

class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str | None] = mapped_column(String(500))
    file_hash: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # Merged from results table
    verdict: Mapped[str | None] = mapped_column(String(10))  # REAL or FAKE
    confidence: Mapped[float | None] = mapped_column(Float)
    visual_score: Mapped[float | None] = mapped_column(Float)
    audio_score: Mapped[float | None] = mapped_column(Float)
    speech_detected: Mapped[bool | None] = mapped_column(Boolean)
    audio_weight: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime)

class BlockchainRecord(Base):
    __tablename__ = "blockchain_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    upload_id: Mapped[uuid.UUID] = mapped_column()  # FK to uploads.id
    file_hash: Mapped[str] = mapped_column(String(64))
    merkle_root: Mapped[str | None] = mapped_column(String(66))
    tx_hash: Mapped[str | None] = mapped_column(String(66))
    block_number: Mapped[int | None] = mapped_column()
    registered_at: Mapped[DateTime | None] = mapped_column(DateTime)
```

### Anti-Patterns to Avoid
- **Using `@app.on_event("startup")`:** Deprecated. Use lifespan context manager instead. Mixing both causes startup handlers to silently not fire.
- **Sync SQLAlchemy in async FastAPI:** Using `create_engine` (sync) blocks the event loop. Always use `create_async_engine`.
- **Loading models per-request:** The existing Flask backend does this. Explicitly avoid -- use `app.state` populated during lifespan.
- **Running Alembic migrations in lifespan:** Known issue in 2025 where async context can be None. Run migrations via CLI command before starting the server (in Dockerfile or entrypoint script).
- **Global mutable state instead of `app.state`:** Don't use module-level globals for models. `app.state` is the FastAPI-blessed way to share startup resources.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Environment configuration | Custom config parser | `pydantic-settings` BaseSettings | Handles env vars, .env files, type coercion, validation |
| Database migrations | Raw SQL scripts or manual schema creation | Alembic with `--autogenerate` | Tracks schema changes, supports rollbacks, generates diffs |
| CORS handling | Custom middleware | `fastapi.middleware.cors.CORSMiddleware` | Built into FastAPI, handles preflight correctly |
| API routing | Manual URL dispatch | FastAPI `APIRouter` with prefix | Modular, supports dependency injection, auto-docs |
| CSS utilities | Custom utility functions | tailwind-merge + clsx via `cn()` | Standard shadcn/ui pattern, handles class conflicts |

**Key insight:** This is foundation phase -- resist the urge to build custom abstractions. Use the standard tools exactly as documented. Future phases will layer on top.

## Common Pitfalls

### Pitfall 1: Alembic Can't Find Models for Autogenerate
**What goes wrong:** Running `alembic revision --autogenerate` produces empty migrations because models aren't imported.
**Why it happens:** Alembic's `env.py` must import all model classes so `target_metadata` reflects the full schema.
**How to avoid:** In `alembic/env.py`, set `target_metadata = Base.metadata` and ensure all model modules are imported (e.g., `from app.models import upload, blockchain`).
**Warning signs:** Migration file says "empty migration" or has no `op.create_table` calls.

### Pitfall 2: asyncpg Connection String Format
**What goes wrong:** Database connection fails at startup with driver errors.
**Why it happens:** asyncpg requires `postgresql+asyncpg://` prefix, not `postgresql://` or `postgres://`.
**How to avoid:** Always construct the URL with the async prefix: `postgresql+asyncpg://user:pass@host:port/dbname`.
**Warning signs:** `ModuleNotFoundError` or `NoSuchModuleError` for the driver.

### Pitfall 3: Docker Compose Service Startup Order
**What goes wrong:** Backend tries to connect to PostgreSQL before it's ready, crashes on startup.
**Why it happens:** `depends_on` only waits for the container to start, not for PostgreSQL to be ready to accept connections.
**How to avoid:** Either use `depends_on` with `condition: service_healthy` and a healthcheck on the db service, OR add retry logic in the backend's database connection code.
**Warning signs:** `ConnectionRefusedError` on first `docker compose up`.

### Pitfall 4: Vite Dev Server Not Accessible from Docker
**What goes wrong:** Frontend container starts but browser can't connect on the mapped port.
**Why it happens:** Vite defaults to `localhost` which is container-internal. Must bind to `0.0.0.0`.
**How to avoid:** Use `vite --host 0.0.0.0` or set `server.host: '0.0.0.0'` in `vite.config.ts`.
**Warning signs:** Container logs show Vite running but browser gets `ERR_CONNECTION_REFUSED`.

### Pitfall 5: SQLAlchemy asyncio Greenlet Dependency
**What goes wrong:** ImportError for greenlet when using async SQLAlchemy.
**Why it happens:** As of SQLAlchemy 2.0.45+, the greenlet dependency no longer installs by default.
**How to avoid:** Install with `pip install "sqlalchemy[asyncio]"` (the `[asyncio]` extra includes greenlet).
**Warning signs:** `ImportError: cannot import name 'greenlet'` at runtime.

### Pitfall 6: Volume Mount Overwrites node_modules
**What goes wrong:** Frontend container can't find node_modules after volume mount.
**Why it happens:** Mounting `./frontend:/app` overwrites the container's `/app/node_modules`.
**How to avoid:** Use an anonymous volume for node_modules: `volumes: ["./frontend:/app", "/app/node_modules"]`.
**Warning signs:** `MODULE_NOT_FOUND` errors in frontend container despite successful `npm install` in Dockerfile.

## Code Examples

### Docker Compose Configuration (3 services)

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: trustchain
      POSTGRES_PASSWORD: trustchain
      POSTGRES_DB: trustchain_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U trustchain -d trustchain_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      DATABASE_URL: postgresql+asyncpg://trustchain:trustchain@db:5432/trustchain_db
      DEBUG: "true"
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    command: npm run dev -- --host 0.0.0.0

volumes:
  pgdata:
```

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile (Development)

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### Health Check Endpoint (INFR-04)

```python
# app/api/health.py
from fastapi import APIRouter, Request
from sqlalchemy import text
from app.database import async_session

router = APIRouter()

@router.get("/health")
async def health_check(request: Request):
    # Check database connectivity
    db_status = "healthy"
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    # Check model loading status
    visual_model = getattr(request.app.state, "visual_model", None)
    audio_model = getattr(request.app.state, "audio_model", None)

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "models": {
            "visual": visual_model.get("status") if visual_model else "not_loaded",
            "audio": audio_model.get("status") if audio_model else "not_loaded",
        },
        "version": "0.1.0",
    }
```

### React Router Setup (Library Mode)

```tsx
// src/App.tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import UploadPage from "./pages/UploadPage";
import ResultsPage from "./pages/ResultsPage";
import HistoryPage from "./pages/HistoryPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/results/:id" element={<ResultsPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

### Alembic Async Initialization

```bash
# From backend/ directory
alembic init -t async alembic
```

Then in `alembic/env.py`, update:
```python
from app.models.base import Base
from app.models import upload, blockchain  # Ensure models are imported
from app.config import settings

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata
```

And in the Dockerfile entrypoint or docker-compose command:
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@app.on_event("startup")` | `lifespan` async context manager | FastAPI 0.95+ (2023) | Old decorators deprecated, do not mix with lifespan |
| SQLAlchemy 1.4 async | SQLAlchemy 2.0 `create_async_engine` | SQLAlchemy 2.0 (2023) | New `Mapped[]` type annotations, `mapped_column()` |
| `pip install sqlalchemy` (includes greenlet) | `pip install "sqlalchemy[asyncio]"` | SQLAlchemy 2.0.45+ (late 2025) | Greenlet no longer auto-installed, must use extras |
| Create React App | Vite | CRA deprecated 2023 | Vite is the standard for new React projects |
| React Router v6 | React Router v7 (library mode) | React Router v7 (2024) | v7 adds framework mode; library mode works like v6 for SPAs |

**Deprecated/outdated:**
- `@app.on_event("startup"/"shutdown")`: Replaced by lifespan. Still works but should not be used.
- `create_engine` for async: Use `create_async_engine` exclusively in async FastAPI apps.
- Flask for new ML APIs: FastAPI is now the standard for async Python APIs.

## Open Questions

1. **PyTorch CPU-only image size**
   - What we know: `torch` CPU-only wheel is ~200MB; full CUDA torch is 2GB+. For Phase 1 we only need stubs.
   - What's unclear: Whether to install torch now (for stub structure) or defer until Phase 3 (when real models are needed).
   - Recommendation: Do NOT install PyTorch in Phase 1. Model stubs are plain Python dicts. Install torch in Phase 3 when actual model loading is implemented. This keeps the Docker image small (~300MB vs ~2GB).

2. **shadcn/ui Re-installation**
   - What we know: Existing Frontend/ has 46 shadcn components. Starting fresh means re-initializing shadcn.
   - What's unclear: Exactly which components are needed in Phase 1 (just navigation shell).
   - Recommendation: Initialize shadcn with `npx shadcn@latest init`, then add only components needed per phase (button, navigation-menu for Phase 1 shell).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio + httpx (backend), Vitest (frontend -- defer to later phase) |
| Config file | `backend/pytest.ini` or `backend/pyproject.toml` -- Wave 0 |
| Quick run command | `docker compose exec backend pytest tests/ -x -q` |
| Full suite command | `docker compose exec backend pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFR-01 | FastAPI app starts and serves API | smoke | `docker compose exec backend pytest tests/test_health.py -x` | No -- Wave 0 |
| INFR-02 | Database tables exist and are accessible | integration | `docker compose exec backend pytest tests/test_database.py -x` | No -- Wave 0 |
| INFR-03 | Docker Compose starts all 3 services | smoke | `docker compose up -d && docker compose ps` | Manual verification |
| INFR-04 | GET /api/health returns 200 with status | unit | `docker compose exec backend pytest tests/test_health.py::test_health_returns_200 -x` | No -- Wave 0 |
| INFR-05 | Models load once at startup via lifespan | unit | `docker compose exec backend pytest tests/test_health.py::test_models_loaded -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `docker compose exec backend pytest tests/ -x -q`
- **Per wave merge:** `docker compose exec backend pytest tests/ -v`
- **Phase gate:** Full suite green + `docker compose up` runs all 3 services + health endpoint returns 200

### Wave 0 Gaps
- [ ] `backend/tests/__init__.py` -- test package init
- [ ] `backend/tests/conftest.py` -- async test client fixture with `httpx.AsyncClient` and test DB override
- [ ] `backend/tests/test_health.py` -- covers INFR-01, INFR-04, INFR-05
- [ ] `backend/tests/test_database.py` -- covers INFR-02 (table creation, basic CRUD)
- [ ] `backend/pytest.ini` or `pyproject.toml` with asyncio_mode = "auto"
- [ ] Framework install: `pip install pytest pytest-asyncio httpx` in requirements.txt

## Sources

### Primary (HIGH confidence)
- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/) - Official docs on lifespan pattern, mutual exclusivity with on_event
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/) - Official Docker guidance
- [FastAPI Full-Stack Template](https://github.com/fastapi/full-stack-fastapi-template) - Official reference architecture
- [SQLAlchemy 2.0 Async Docs](https://docs.sqlalchemy.org/en/21/intro.html) - Async engine, session patterns
- [SQLAlchemy PyPI](https://pypi.org/project/SQLAlchemy/) - Version 2.0.48 (latest stable as of March 2026)

### Secondary (MEDIUM confidence)
- [FastAPI + SQLAlchemy 2.0 Modern Async Patterns](https://dev-faizan.medium.com/fastapi-sqlalchemy-2-0-modern-async-database-patterns-7879d39b6843) - Verified async session patterns
- [Setup FastAPI with Async SQLAlchemy 2, Alembic, PostgreSQL and Docker](https://berkkaraal.com/blog/2024/09/19/setup-fastapi-project-with-async-sqlalchemy-2-alembic-postgresql-and-docker/) - End-to-end setup guide
- [FastAPI + Async SQLAlchemy + asyncpg GitHub example](https://github.com/grillazz/fastapi-sqlalchemy-asyncpg) - Working reference implementation
- [TanStack Router vs React Router v7](https://medium.com/ekino-france/tanstack-router-vs-react-router-v7-32dddc4fcd58) - Comparison supporting React Router for SPAs

### Tertiary (LOW confidence)
- None -- all findings verified against official documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries are well-documented, widely used, and versions verified via PyPI/npm
- Architecture: HIGH -- patterns come from official FastAPI docs and established community templates
- Pitfalls: HIGH -- documented across multiple sources and official issue trackers
- Database schema: HIGH -- derived from PRD Section 12 with locked 2-table merge decision
- Docker setup: HIGH -- standard patterns verified across multiple production examples

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable stack, slow-moving dependencies)
