# Codebase Structure

**Analysis Date:** 2026-03-05

## Directory Layout

```
Implementation/
├── Frontend/                    # React SPA (Vite + TypeScript)
│   ├── index.html               # HTML entry point
│   ├── package.json             # Node dependencies & scripts
│   ├── package-lock.json        # Lockfile
│   ├── vite.config.ts           # Vite build configuration
│   └── src/
│       ├── main.tsx             # React app bootstrap
│       ├── App.tsx              # Root component (all UI logic)
│       ├── index.css            # Global CSS / Tailwind imports
│       ├── components/          # Application-level components
│       │   ├── Header.tsx
│       │   ├── FileUploader.tsx
│       │   ├── ImagePreview.tsx
│       │   ├── AnalysisResults.tsx
│       │   ├── AuthenticityMeter.tsx
│       │   ├── MetricCard.tsx
│       │   ├── BlockchainSection.tsx
│       │   ├── InterpretationSection.tsx
│       │   ├── figma/           # Figma-exported utilities
│       │   │   └── ImageWithFallback.tsx
│       │   └── ui/             # shadcn/ui component library (46 files)
│       │       ├── utils.ts    # cn() utility
│       │       ├── button.tsx
│       │       ├── badge.tsx
│       │       └── ... (44 more primitives)
│       ├── styles/
│       │   └── globals.css      # Additional global styles
│       └── guidelines/
│           └── Guidelines.md    # UI/UX guidelines document
├── backend/                     # Python Flask API
│   ├── app.py                   # Flask server & analysis logic
│   ├── Image Processing.py     # Legacy Streamlit prototype
│   ├── requirements.txt         # Python dependencies
│   └── venv/                    # Python virtual environment
├── docs/                        # Project documentation
│   ├── Architecture/
│   ├── Reference/
│   └── Setup/
├── start.sh                     # macOS/Linux launcher
├── start.bat                    # Windows launcher
├── start.ps1                    # PowerShell launcher
├── test_backend.py              # Backend test script
├── test_backend_check.py        # Backend check script
└── venv/                        # Root-level virtual environment
```

## Directory Purposes

**`Frontend/`:**
- Purpose: Contains the complete React single-page application
- Contains: TypeScript/TSX source, Vite config, node_modules
- Key files: `src/App.tsx` (main UI), `src/main.tsx` (entry), `vite.config.ts` (build config)

**`Frontend/src/components/`:**
- Purpose: React components for the application UI
- Contains: Feature-specific components (8 files) that mirror sections of the main App
- Key files: `FileUploader.tsx`, `AnalysisResults.tsx`, `BlockchainSection.tsx`
- Note: These components exist but are NOT currently imported by `App.tsx` -- the main app has all UI inline

**`Frontend/src/components/ui/`:**
- Purpose: shadcn/ui component library -- reusable styled primitives
- Contains: 46 component files + `utils.ts` utility
- Key files: `button.tsx`, `badge.tsx`, `utils.ts` (cn helper)
- Note: Only `button.tsx` and `badge.tsx` are actually used by the app

**`Frontend/src/components/figma/`:**
- Purpose: Components exported from Figma design tool
- Contains: `ImageWithFallback.tsx` -- image component with error fallback

**`Frontend/src/styles/`:**
- Purpose: Global stylesheet definitions
- Contains: `globals.css`

**`Frontend/src/guidelines/`:**
- Purpose: UI/UX design guidelines documentation
- Contains: `Guidelines.md`

**`backend/`:**
- Purpose: Python Flask REST API server for image analysis
- Contains: Flask app, ML analysis logic, legacy Streamlit app, Python dependencies
- Key files: `app.py` (main server), `requirements.txt` (dependencies)

**`docs/`:**
- Purpose: Project documentation organized by category
- Contains: Architecture docs, Reference docs, Setup guides

## Key File Locations

**Entry Points:**
- `Frontend/src/main.tsx`: React app bootstrap, mounts to `#root`
- `Frontend/index.html`: HTML shell that loads the Vite app
- `backend/app.py`: Flask server entry point (runs on port 5000)
- `start.sh` / `start.bat` / `start.ps1`: Combined frontend+backend launchers

**Configuration:**
- `Frontend/vite.config.ts`: Vite build config with path aliases (`@` maps to `./src`)
- `Frontend/package.json`: Node dependencies, scripts (`dev`, `build`), proxy config
- `backend/requirements.txt`: Python dependency versions

**Core Logic:**
- `Frontend/src/App.tsx`: All frontend UI rendering, state management, API calls
- `backend/app.py`: Image analysis algorithm (`analyze_image`), Flask routes, file validation

**Testing:**
- `test_backend.py`: Backend test script (root level)
- `test_backend_check.py`: Backend verification script (root level)

## Naming Conventions

**Files:**
- React components: PascalCase (`FileUploader.tsx`, `MetricCard.tsx`)
- shadcn/ui components: kebab-case (`button.tsx`, `hover-card.tsx`, `input-otp.tsx`)
- Utility files: kebab-case (`utils.ts`, `use-mobile.ts`)
- Python files: snake_case or descriptive (`app.py`, `Image Processing.py`)
- Config files: kebab-case with dots (`vite.config.ts`, `package.json`)

**Directories:**
- Frontend top-level: PascalCase (`Frontend/`)
- Backend top-level: lowercase (`backend/`)
- Source subdirectories: lowercase (`components/`, `styles/`, `guidelines/`)
- Component subdirectories: lowercase (`ui/`, `figma/`)

**Functions/Variables (TypeScript):**
- Functions: camelCase (`handleFileUpload`, `getStatusConfig`, `handleCopy`)
- Components: PascalCase function exports (`FileUploader`, `AuthenticityMeter`)
- Interfaces: PascalCase with descriptive suffix (`AnalysisData`, `FileUploaderProps`, `MetricCardProps`)
- State variables: camelCase (`uploadedImage`, `isAnalyzing`, `analysisData`)
- Constants: camelCase (no UPPER_SNAKE used in frontend)

**Functions/Variables (Python):**
- Functions: snake_case (`allowed_file`, `analyze_image`)
- Constants: UPPER_SNAKE (`ALLOWED_EXTENSIONS`, `MAX_FILE_SIZE`, `MODEL_AVAILABLE`)
- Variables: snake_case (`file_bytes`, `sha_hash`, `authenticity_score`)

## Where to Add New Code

**New Feature (Frontend):**
- Primary code: `Frontend/src/components/` -- create a new PascalCase `.tsx` file
- Import and use in `Frontend/src/App.tsx` (or refactor App.tsx to use existing extracted components first)
- Tests: No frontend test infrastructure exists; would need to set up Vitest

**New API Endpoint:**
- Add route in `backend/app.py` following existing pattern (`@app.route(...)`)
- For complex logic, consider extracting to separate Python module in `backend/`

**New UI Primitive:**
- Add to `Frontend/src/components/ui/` using shadcn/ui conventions (kebab-case filename)
- Use `cn()` from `Frontend/src/components/ui/utils.ts` for class composition

**New Page/View:**
- Currently no router exists; would need to add `react-router-dom` first
- Then create pages directory: `Frontend/src/pages/`

**Utilities:**
- Frontend shared helpers: `Frontend/src/components/ui/utils.ts` (currently only has `cn()`)
- Consider creating `Frontend/src/lib/` or `Frontend/src/utils/` for non-UI utilities

**New Backend Module:**
- Create new `.py` file in `backend/` directory
- Import into `backend/app.py`

## Special Directories

**`Frontend/node_modules/`:**
- Purpose: Installed npm packages
- Generated: Yes (via `npm install`)
- Committed: No

**`backend/venv/` and `venv/`:**
- Purpose: Python virtual environments
- Generated: Yes (via `python -m venv`)
- Committed: No

**`Frontend/src/components/ui/`:**
- Purpose: shadcn/ui component library
- Generated: Semi-generated (scaffolded via shadcn CLI, then customizable)
- Committed: Yes -- these are source files meant to be modified

**`.agent/`:**
- Purpose: AI agent configuration, skills, and templates
- Generated: No -- configuration files
- Committed: Likely yes

**`docs/`:**
- Purpose: Project documentation
- Generated: No -- manually written
- Committed: Yes

---

*Structure analysis: 2026-03-05*
