# External Integrations

**Analysis Date:** 2026-03-05

## APIs & External Services

**Internal REST API:**
- Flask backend (`backend/app.py`) exposes a REST API consumed by the React frontend
  - `GET /api/health` - Health check, returns `{ status: 'healthy' }`
  - `POST /api/analyze` - Image analysis endpoint, accepts `multipart/form-data` with `image` field
  - `GET /api/info` - System metadata (name, version, capabilities)

**External APIs:**
- None detected. The application is fully self-contained with no external API calls.

**Pre-trained Model:**
- ResNet50 weights downloaded from PyTorch Hub (`models.ResNet50_Weights.DEFAULT`)
  - Downloaded automatically on first run by `torchvision`
  - Cached locally by PyTorch in the user's cache directory
  - Used for image feature extraction (not classification)

## Data Storage

**Databases:**
- None. No database is used. All processing is stateless and per-request.

**File Storage:**
- Local filesystem only
- Uploaded images are processed in-memory (`io.BytesIO`) and not persisted to disk
- No file upload storage directory

**Caching:**
- None. No caching layer exists. ResNet50 model is re-loaded on every request in `backend/app.py` (line 71).

## Authentication & Identity

**Auth Provider:**
- None. The application has no authentication or authorization.
- All API endpoints are publicly accessible on localhost.
- CORS is fully open via `flask-cors` with default settings (all origins allowed).

## Monitoring & Observability

**Error Tracking:**
- None. No error tracking service (no Sentry, etc.).

**Logs:**
- Flask default logging to stdout
- Frontend uses `console.error()` for API failures (`Frontend/src/App.tsx`, lines 62, 66)
- No structured logging framework

## CI/CD & Deployment

**Hosting:**
- Local development only. No deployment target configured.
- No Dockerfile, no cloud config, no hosting platform files.

**CI Pipeline:**
- None. No CI/CD configuration files detected (no `.github/workflows/`, no `Jenkinsfile`, etc.).

## Environment Configuration

**Required env vars:**
- None. All configuration is hardcoded in source files.

**Secrets location:**
- No secrets required. No API keys, no database credentials.

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Frontend-Backend Communication

**Protocol:** HTTP REST (JSON responses)

**Connection Details:**
- Frontend calls backend at hardcoded `http://localhost:5000/api/analyze` (`Frontend/src/App.tsx`, line 37)
- Uses native `fetch()` API (no Axios or other HTTP client library)
- `package.json` has a `"proxy": "http://localhost:5000"` setting but this is a CRA convention not used by Vite

**Request Format:**
- `POST /api/analyze`: `multipart/form-data` with field name `image`
- Accepted file types: `jpg`, `jpeg`, `png`
- Max file size: 16MB (enforced server-side)

**Response Format:**
```json
{
  "success": true,
  "authenticityScore": 72.45,
  "sharpnessScore": 45.23,
  "colorVariance": 1234.56,
  "prediction": "authentic|modified|ai-generated",
  "label": "Likely Original / Authentic",
  "interpretation": ["Natural sharpness..."],
  "hash": "sha256-hex-string",
  "blockchainStatus": "verified"
}
```

## Legacy/Prototype Components

**Streamlit Prototype:**
- `backend/Image Processing.py` - An earlier Streamlit-based prototype of the same functionality
- Uses `streamlit` (not listed in `requirements.txt`)
- Same ResNet50 + image metrics approach
- Not actively used by the current React + Flask architecture

## Blockchain Integration

**Current State:** Simulated only
- SHA-256 hash is generated from uploaded file bytes (`backend/app.py`, line 105)
- `blockchainStatus` is hardcoded to `"verified"` (line 128) - no actual blockchain integration exists
- Frontend displays "Verified on Blockchain" badge but this is cosmetic (`Frontend/src/App.tsx`, line 432)
- No blockchain SDK, smart contract, or distributed ledger integration is present

---

*Integration audit: 2026-03-05*
