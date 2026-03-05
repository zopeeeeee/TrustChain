# Phase 1: Foundation and Infrastructure - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a running FastAPI application with PostgreSQL database, health endpoint, ML model preloading stubs, React frontend shell with routing, and Docker Compose orchestration. This is the skeleton that every subsequent phase builds on. No upload handling, no ML inference, no blockchain — just the foundation.

</domain>

<decisions>
## Implementation Decisions

### Project Structure
- Clean monorepo: `backend/`, `frontend/`, `contracts/` at root with shared `docker-compose.yml`
- Delete existing Frontend/ and backend/ code entirely — start fresh
- FastAPI backend uses modular packages: `app/api/`, `app/models/`, `app/services/`, `app/ml/` — separated by concern

### Database Design
- Simplify PRD's 3 tables to 2 tables: merge results into uploads (one row per video, fewer joins). Blockchain records remain a separate table.
- Use Alembic for schema migrations — versioned, standard for FastAPI projects
- Async SQLAlchemy with AsyncSession + asyncpg — matches FastAPI's async nature

### Docker Setup
- 3 services in docker-compose.yml: backend (FastAPI/Uvicorn), frontend (Vite dev server), db (PostgreSQL)
- Volume mounts for hot-reload during development — source code mounted into containers
- No pgAdmin — team uses CLI or external tools

### Claude's Discretion
- PyTorch Docker image optimization (CPU-only slim vs full) — Claude picks what minimizes image size while working
- Exact Alembic configuration and initial migration structure
- React routing library choice
- Frontend shell page layout and navigation structure
- Environment variable management (.env files, Docker env)

</decisions>

<specifics>
## Specific Ideas

- PRD specifies exact database schema columns (see PRD Section 12) — use as reference but adapt for the 2-table design
- Models load once at startup via FastAPI lifespan events, not per-request (INFR-05)
- Health endpoint should return model loading status (research note: existing Flask code loads models per-request — explicitly avoid this)

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- shadcn/ui component library (46 components) exists in current Frontend/ — can be re-installed fresh via shadcn CLI in the new frontend
- Existing `cn()` utility pattern (clsx + tailwind-merge) is standard and should be replicated
- Start scripts (start.sh, start.bat, start.ps1) pattern is useful but Docker Compose replaces them

### Established Patterns
- Frontend: PascalCase component files, camelCase functions, 2-space indent
- Backend: snake_case functions, 4-space indent, UPPER_SNAKE_CASE constants
- TypeScript interfaces follow `{ComponentName}Props` pattern

### Integration Points
- Backend serves on port 5000 (or configurable), frontend on port 5173 (Vite default)
- CORS configuration needed (existing code uses flask_cors — FastAPI has CORSMiddleware)
- Frontend fetches from backend via REST API (existing pattern: POST /api/analyze)

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation-and-infrastructure*
*Context gathered: 2026-03-06*
