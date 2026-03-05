# Architecture

**Analysis Date:** 2026-03-05

## Pattern Overview

**Overall:** Client-Server Monorepo with separate React SPA frontend and Python Flask REST API backend.

**Key Characteristics:**
- Two-tier architecture: React (Vite) frontend communicates with Flask backend via REST API
- No routing library on the frontend -- single-page application with one view
- All application logic lives in a single monolithic `App.tsx` component; extracted component files exist but are not imported by the main App
- Backend is a stateless Flask API with no database -- all analysis is computed per-request
- A legacy Streamlit prototype (`Image Processing.py`) exists alongside the Flask API

## Layers

**Presentation Layer (Frontend):**
- Purpose: Renders the UI, handles file upload, displays analysis results
- Location: `Frontend/src/`
- Contains: React components (TSX), CSS styles, UI primitives (shadcn/ui)
- Depends on: Backend REST API at `http://localhost:5000`
- Used by: End users via browser

**API Layer (Backend):**
- Purpose: Receives uploaded images, performs analysis, returns JSON results
- Location: `backend/app.py`
- Contains: Flask routes, image analysis logic, ML model inference
- Depends on: PyTorch, OpenCV, Pillow, NumPy
- Used by: Frontend via HTTP fetch calls

**UI Component Library:**
- Purpose: Reusable styled primitives (buttons, badges, dialogs, etc.)
- Location: `Frontend/src/components/ui/`
- Contains: 46 shadcn/ui component files built on Radix UI primitives
- Depends on: Radix UI, class-variance-authority, tailwind-merge, clsx
- Used by: Application components in `Frontend/src/components/`

## Data Flow

**Image Analysis Flow:**

1. User uploads an image file via drag-and-drop or file picker in `Frontend/src/App.tsx`
2. Frontend creates a `FormData` object with the image and sends `POST /api/analyze` to `http://localhost:5000`
3. Flask backend (`backend/app.py`) validates the file (extension, size), opens it with Pillow
4. `analyze_image()` function computes: sharpness (Laplacian variance via OpenCV), color variance (NumPy), ResNet50 feature extraction (PyTorch -- optional, degrades gracefully if unavailable)
5. Authenticity score is calculated from combined metrics using `tanh` normalization (0-100 scale)
6. Prediction label is determined by threshold: `<60` = authentic, `60-80` = modified, `>=80` = AI-generated
7. SHA-256 hash of file bytes is generated for blockchain verification reference
8. JSON response is returned with all scores, prediction, hash, and interpretation
9. Frontend updates React state and renders results (meter, metric cards, blockchain section, insights)

**State Management:**
- React `useState` hooks in the root `App.tsx` component
- No global state management library (no Redux, Zustand, etc.)
- State includes: `uploadedImage` (object URL string), `analysisData` (API response), `isAnalyzing` (loading flag), `isDragging`, `isZoomed`, `copied`

## Key Abstractions

**AnalysisData Interface:**
- Purpose: Represents the structured result from the backend analysis API
- Defined in: `Frontend/src/App.tsx` (lines 7-15)
- Fields: `authenticityScore`, `sharpnessScore`, `colorVariance`, `prediction`, `explanation`, `hash`, `blockchainStatus`
- Pattern: TypeScript interface used for type-safe state management

**Component Extraction (Partial):**
- Purpose: Extracted UI sections for reusability
- Examples: `Frontend/src/components/FileUploader.tsx`, `Frontend/src/components/AnalysisResults.tsx`, `Frontend/src/components/BlockchainSection.tsx`, `Frontend/src/components/AuthenticityMeter.tsx`, `Frontend/src/components/MetricCard.tsx`, `Frontend/src/components/ImagePreview.tsx`, `Frontend/src/components/InterpretationSection.tsx`, `Frontend/src/components/Header.tsx`
- Pattern: These components are defined but NOT used -- `App.tsx` contains all UI inline. The `AnalysisResults.tsx` imports `AnalysisData` from `../App` suggesting they were designed to be used but were never wired in.

**shadcn/ui Utility:**
- Purpose: Tailwind CSS class merging utility
- Location: `Frontend/src/components/ui/utils.ts`
- Pattern: `cn()` function combining `clsx` + `twMerge` for conditional class composition

## Entry Points

**Frontend Entry:**
- Location: `Frontend/src/main.tsx`
- Triggers: Vite dev server or built bundle loaded by `Frontend/index.html`
- Responsibilities: Mounts the React app to `#root` DOM element

**Backend Entry:**
- Location: `backend/app.py` (line 208: `app.run(debug=True, host='127.0.0.1', port=5000)`)
- Triggers: Direct Python execution or startup scripts
- Responsibilities: Starts Flask development server on port 5000

**Startup Scripts:**
- Location: `start.sh`, `start.bat`, `start.ps1`
- Triggers: Manual execution by developer
- Responsibilities: Start both backend (Flask on port 5000) and frontend (Vite on port 3000/5173) simultaneously

**Legacy Streamlit App:**
- Location: `backend/Image Processing.py`
- Triggers: `streamlit run "Image Processing.py"`
- Responsibilities: Original prototype UI -- standalone Streamlit app with identical analysis logic

## API Endpoints

**`GET /api/health`** (`backend/app.py` line 138):
- Returns `{ status: 'healthy' }` with HTTP 200

**`POST /api/analyze`** (`backend/app.py` line 144):
- Accepts: `multipart/form-data` with `image` field (JPG/JPEG/PNG, max 16MB)
- Returns: JSON with `authenticityScore`, `sharpnessScore`, `colorVariance`, `prediction`, `label`, `interpretation`, `hash`, `blockchainStatus`
- Error responses: 400 (bad input), 500 (analysis failure)

**`GET /api/info`** (`backend/app.py` line 191):
- Returns system metadata (name, version, capabilities)

## Error Handling

**Strategy:** Basic try-catch with user alerts on the frontend; try-except with JSON error responses on the backend.

**Frontend Patterns:**
- `fetch().catch()` displays `alert()` messages to the user (no toast/notification system used despite `sonner` being installed)
- Console.error for logging
- No error boundary components

**Backend Patterns:**
- Top-level try-except in route handlers returns `{ success: false, error: <message> }` with appropriate HTTP status codes
- `analyze_image()` returns error dict on failure rather than raising
- ML model loading failures are caught silently -- analysis degrades to metrics-only mode (`MODEL_AVAILABLE` flag)

## Cross-Cutting Concerns

**Logging:** `console.error` on frontend; no structured logging on backend (Flask default only)
**Validation:** Backend validates file extension, file size (16MB max), file presence. Frontend accepts `image/jpeg,image/png,image/jpg` via input accept attribute.
**Authentication:** None -- no auth on any endpoint
**CORS:** Enabled globally via `flask_cors.CORS(app)` with no origin restrictions

---

*Architecture analysis: 2026-03-05*
