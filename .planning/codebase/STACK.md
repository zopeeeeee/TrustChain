# Technology Stack

**Analysis Date:** 2026-03-05

## Languages

**Primary:**
- TypeScript / TSX - Frontend UI (`Frontend/src/`)
- Python 3.x - Backend API and ML processing (`backend/`)

**Secondary:**
- HTML - Entry point (`Frontend/index.html`)
- CSS (Tailwind v4) - Styling (`Frontend/src/index.css`, `Frontend/src/styles/globals.css`)

## Runtime

**Environment:**
- Node.js - Frontend development and build
- Python 3.8+ - Backend Flask server (checked in `start.bat`)

**Package Manager:**
- npm - Frontend (`Frontend/package.json`, `Frontend/package-lock.json`)
- pip - Backend (`backend/requirements.txt`, uses venv)
- Lockfile: `Frontend/package-lock.json` present; no `pip` lockfile (only `requirements.txt` with pinned versions)

## Frameworks

**Core:**
- React 18.3.1 - Frontend UI library (`Frontend/package.json`)
- Flask 3.0.0 - Backend REST API framework (`backend/app.py`)

**UI Component Library:**
- Radix UI - Headless component primitives (22 packages: accordion, dialog, dropdown-menu, tabs, etc.)
- shadcn/ui pattern - Pre-built components in `Frontend/src/components/ui/` (47 component files)
- class-variance-authority 0.7.1 - Component variant management
- lucide-react 0.487.0 - Icon library

**ML/AI:**
- PyTorch 2.0.1 - Deep learning framework (`backend/requirements.txt`)
- torchvision 0.15.2 - Pre-trained ResNet50 model for image feature extraction
- OpenCV (opencv-python 4.8.0.74) - Image quality metrics (sharpness via Laplacian)
- Pillow 10.0.0 - Image loading and format handling
- NumPy 1.24.3 - Numerical computations

**Build/Dev:**
- Vite 6.3.5 - Frontend bundler and dev server (`Frontend/vite.config.ts`)
- @vitejs/plugin-react-swc 3.10.2 - React Fast Refresh with SWC compiler

**Testing:**
- No test framework installed for frontend (no jest/vitest in `package.json`)
- Manual test scripts for backend: `test_backend.py`, `test_backend_check.py` (use `requests` library)

## Key Dependencies

**Critical:**
- `react` 18.3.1 / `react-dom` 18.3.1 - Core UI rendering
- `flask` 3.0.0 - API server
- `flask-cors` 4.0.0 - Cross-origin requests (frontend on port 3000/5173 to backend on port 5000)
- `torch` 2.0.1 - ML inference (optional at runtime, graceful fallback in `backend/app.py`)
- `torchvision` 0.15.2 - ResNet50 pre-trained weights

**UI/UX:**
- `recharts` 2.15.2 - Data visualization/charting
- `react-hook-form` 7.55.0 - Form handling
- `sonner` 2.0.3 - Toast notifications
- `vaul` 1.1.2 - Drawer component
- `cmdk` 1.1.1 - Command palette
- `embla-carousel-react` 8.6.0 - Carousel
- `react-day-picker` 8.10.1 - Date picker
- `react-resizable-panels` 2.1.7 - Resizable panel layouts
- `next-themes` 0.4.6 - Theme management (dark/light)
- `input-otp` 1.4.2 - OTP input component

**Infrastructure:**
- `tailwind-merge` - Tailwind class merging utility
- `clsx` - Conditional class name builder
- `werkzeug` 3.0.0 - WSGI utilities (Flask dependency)

## Configuration

**Frontend Build:**
- `Frontend/vite.config.ts` - Vite configuration
  - Path alias: `@` maps to `./src`
  - Versioned package aliases for all Radix UI and utility packages
  - Build target: `esnext`
  - Output directory: `build`
  - Dev server port: 3000 (configured), 5173 (npm default in start script)
- `Frontend/index.html` - SPA entry point
- No `tsconfig.json` in Frontend directory (uses Vite defaults)
- Tailwind CSS v4.1.3 - Loaded via CSS `@layer` directives in `Frontend/src/index.css`

**Backend:**
- `backend/app.py` - Flask app configuration
  - Debug mode: enabled in development
  - Host: `127.0.0.1`, Port: `5000`
  - CORS: enabled globally
  - Max file size: 16MB
  - Allowed extensions: jpg, jpeg, png

**Environment:**
- No `.env` files detected
- No environment variables required (all config is hardcoded)
- Backend uses Python venv: `backend/venv/`
- Frontend uses `node_modules/`

## Platform Requirements

**Development:**
- Python 3.8+ with venv support
- Node.js (any recent LTS)
- npm
- Windows-oriented start scripts (`start.bat`, `start.ps1`) plus `start.sh` for Unix

**Production:**
- Flask development server (no production WSGI server configured)
- No containerization (no Dockerfile)
- No deployment configuration

**Startup:**
- Use `start.bat` (Windows) or `start.sh` (Unix) from the `Implementation/` directory
- Backend starts on `http://localhost:5000`
- Frontend starts on `http://localhost:5173` (Vite dev) or `http://localhost:3000` (configured)

---

*Stack analysis: 2026-03-05*
