# Coding Conventions

**Analysis Date:** 2026-03-05

## Naming Patterns

**Files (Frontend - Custom Components):**
- Use PascalCase for component files: `FileUploader.tsx`, `AnalysisResults.tsx`, `AuthenticityMeter.tsx`
- One component per file, file name matches the exported component name

**Files (Frontend - UI Library / shadcn):**
- Use kebab-case for shadcn/ui primitives: `alert-dialog.tsx`, `hover-card.tsx`, `toggle-group.tsx`
- Hooks use kebab-case with `use-` prefix: `use-mobile.ts`
- Utility files use lowercase: `utils.ts`

**Files (Backend):**
- Use lowercase with spaces for standalone scripts: `Image Processing.py`
- Use lowercase for Flask modules: `app.py`
- Use snake_case for test scripts: `test_backend.py`, `test_backend_check.py`

**Functions (Frontend):**
- Use camelCase for functions and handlers: `handleFileUpload`, `handleReset`, `getStatusConfig`
- Prefix event handlers with `handle`: `handleDragOver`, `handleDrop`, `handleFileSelect`, `handleCopy`
- Prefix getter helpers with `get`: `getStatusConfig`, `getColor`

**Functions (Backend):**
- Use snake_case: `allowed_file`, `analyze_image`
- Flask route functions use short lowercase names: `health`, `analyze`, `info`

**Variables (Frontend):**
- Use camelCase for state and local variables: `uploadedImage`, `isAnalyzing`, `isDragging`
- Boolean state variables prefix with `is` or `has`: `isZoomed`, `isDragging`, `isAnalyzing`

**Variables (Backend):**
- Use snake_case: `file_bytes`, `sharpness_score`, `authenticity_score`
- Use UPPER_SNAKE_CASE for constants: `ALLOWED_EXTENSIONS`, `MAX_FILE_SIZE`, `MODEL_AVAILABLE`

**Types/Interfaces (Frontend):**
- Use PascalCase for interfaces: `AnalysisData`, `FileUploaderProps`, `AuthenticityMeterProps`
- Props interfaces follow `{ComponentName}Props` pattern: `BlockchainSectionProps`, `ImagePreviewProps`
- Union types for constrained values: `'authentic' | 'modified' | 'ai-generated'`

## Code Style

**Formatting:**
- No ESLint or Prettier configuration detected. Formatting is manual/IDE-driven.
- Frontend uses 2-space indentation consistently across `.tsx` files
- Backend uses 4-space indentation (Python standard)
- Single quotes for string literals in frontend TypeScript
- Single quotes for Python strings in backend

**Linting:**
- No linting tools configured in either frontend or backend
- No `eslint`, `prettier`, `biome`, `ruff`, or `flake8` configs detected
- No `tsconfig.json` detected in Frontend directory (TypeScript compilation relies on Vite defaults)

## Import Organization

**Order (Frontend custom components):**
1. React hooks: `import { useState, useRef } from 'react'`
2. Third-party icons: `import { Brain, Upload, X } from 'lucide-react'`
3. Internal UI components: `import { Button } from './ui/button'`
4. Internal custom components: `import { AuthenticityMeter } from './AuthenticityMeter'`
5. Types (when separate): `import { AnalysisData } from '../App'`

**Order (Frontend shadcn/ui components):**
1. React: `import * as React from "react"`
2. Radix UI primitives: `import { Slot } from "@radix-ui/react-slot@1.1.2"`
3. CVA/utilities: `import { cva } from "class-variance-authority@0.7.1"`
4. Local utils: `import { cn } from "./utils"`

**Order (Backend):**
1. Flask and extensions: `from flask import Flask, request, jsonify`
2. ML libraries (guarded): `import torch`, `import torchvision`
3. Image processing: `from PIL import Image`, `import cv2`
4. Standard library: `import hashlib`, `import io`

**Path Aliases:**
- `@` maps to `./src` (configured in `Frontend/vite.config.ts` line 49)
- Versioned package aliases in `Frontend/vite.config.ts` (e.g., `'@radix-ui/react-slot@1.1.2': '@radix-ui/react-slot'`)
- In practice, components import using relative paths, not the `@` alias

## Component Patterns

**Frontend Component Structure:**
- Use function declarations with named exports for custom components:
  ```tsx
  export function FileUploader({ onFileUpload, onReset }: FileUploaderProps) {
    // state hooks
    // handler functions
    // return JSX
  }
  ```
- Use default export only for the root `App` component (`Frontend/src/App.tsx`)
- Props are destructured in the function signature
- Interfaces defined immediately above the component in the same file

**State Management:**
- Use React `useState` for all local state. No global state library (no Redux, Zustand, or Context).
- All application state lives in `Frontend/src/App.tsx` and is passed down as props
- No custom hooks for business logic (only shadcn's `useIsMobile` in `Frontend/src/components/ui/use-mobile.ts`)

**Styling:**
- Tailwind CSS v4.1.3 via utility classes directly in JSX
- Use `cn()` utility from `Frontend/src/components/ui/utils.ts` for conditional class merging (clsx + tailwind-merge)
- CSS custom properties defined in `Frontend/src/styles/globals.css` for theming (shadcn design tokens)
- Dark theme uses a slate-950/purple-950 gradient palette applied inline, not via the `dark:` variant system
- Component variants use `class-variance-authority` (CVA) pattern (see `Frontend/src/components/ui/button.tsx`)

## Error Handling

**Frontend Patterns:**
- API errors caught with `.catch()` on fetch promises in `Frontend/src/App.tsx` (lines 65-69)
- Errors displayed to user via `alert()` calls -- no toast/notification system used for errors
- `console.error()` for logging API failures
- No error boundary components
- Image load errors handled with fallback component in `Frontend/src/components/figma/ImageWithFallback.tsx`

**Backend Patterns:**
- Top-level try/catch in route handlers returning `{'success': False, 'error': str(e)}` with appropriate HTTP status codes (`backend/app.py` lines 150-188)
- Inner try/catch in `analyze_image()` function returns error dict instead of raising (`backend/app.py` lines 131-135)
- Graceful degradation for optional ML dependencies using module-level try/except (`backend/app.py` lines 5-17)
- Input validation at the route level: file presence, filename, extension, file size (`backend/app.py` lines 152-171)

## Logging

**Framework:** Console only (both frontend and backend)

**Patterns:**
- Frontend: `console.error()` for API errors. No structured logging.
- Backend: No logging framework. Flask debug mode enabled in development (`app.run(debug=True)`)
- No log levels, no log formatting, no log aggregation

## Comments

**When to Comment:**
- JSX section comments using `{/* Section Name */}` to delineate major UI blocks (used extensively in `Frontend/src/App.tsx`)
- Python docstrings on all functions in `backend/app.py` using triple-quote format
- Inline comments for non-obvious logic (e.g., `# Make heavy ML dependencies optional`)
- No JSDoc/TSDoc on TypeScript functions or interfaces

## Function Design

**Size:** Functions are generally short (under 30 lines). The main exception is `App()` in `Frontend/src/App.tsx` which is a 500+ line monolithic component.

**Parameters:** Frontend components accept a single destructured props object typed by an interface. Backend functions accept typed parameters.

**Return Values:**
- Frontend: Components return JSX. Helper functions return config objects or primitive values.
- Backend: Functions return dicts with `success` boolean flag. Routes return `jsonify()` tuples with status codes.

## Module Design

**Exports:**
- Custom components use named exports: `export function ComponentName`
- Root App uses default export: `export default function App()`
- shadcn/ui components use named exports at file bottom: `export { Button, buttonVariants }`

**Barrel Files:** Not used. All imports reference specific files directly.

## API Communication

**Pattern:** Direct `fetch()` calls in component event handlers (no API service layer, no axios)
- Base URL hardcoded: `http://localhost:5000`
- FormData for file uploads
- `.then()/.catch()` chain pattern (not async/await)

## Backend API Design

**URL Pattern:** All endpoints under `/api/` prefix
- `GET /api/health` - Health check
- `GET /api/info` - System information
- `POST /api/analyze` - Image analysis (multipart/form-data)

**Response Format:**
```json
{
  "success": true|false,
  "error": "message if failed",
  "authenticityScore": 85.5,
  "prediction": "authentic"
}
```

---

*Convention analysis: 2026-03-05*
