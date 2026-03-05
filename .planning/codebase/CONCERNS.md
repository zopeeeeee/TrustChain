# Codebase Concerns

**Analysis Date:** 2026-03-05

## Tech Debt

**Monolithic App.tsx (523 lines):**
- Issue: The entire application UI, state management, API calls, and rendering logic are packed into a single `Frontend/src/App.tsx` file. Separate component files exist (`AnalysisResults.tsx`, `FileUploader.tsx`, `BlockchainSection.tsx`, `AuthenticityMeter.tsx`, `MetricCard.tsx`, `InterpretationSection.tsx`, `ImagePreview.tsx`, `Header.tsx`) but are NOT imported or used.
- Files: `Frontend/src/App.tsx`
- Impact: Difficult to maintain, test, or extend. All UI changes require editing one massive file. The existing component decomposition is wasted.
- Fix approach: Refactor `App.tsx` to import and use the existing component files. Export the `AnalysisData` interface from `App.tsx` (or a shared types file) so `AnalysisResults.tsx` can consume it. Wire up `FileUploader`, `BlockchainSection`, `ImagePreview`, `Header`, and `InterpretationSection` as child components.

**Dead Component Files:**
- Issue: `AnalysisResults.tsx` imports `{ AnalysisData } from '../App'` but `App.tsx` does not export `AnalysisData`. This means the component file would fail at compile time if actually imported. The other component files (`FileUploader.tsx`, `BlockchainSection.tsx`, etc.) are also never imported anywhere.
- Files: `Frontend/src/components/AnalysisResults.tsx`, `Frontend/src/components/FileUploader.tsx`, `Frontend/src/components/BlockchainSection.tsx`, `Frontend/src/components/AuthenticityMeter.tsx`, `Frontend/src/components/MetricCard.tsx`, `Frontend/src/components/InterpretationSection.tsx`, `Frontend/src/components/ImagePreview.tsx`, `Frontend/src/components/Header.tsx`
- Impact: Code duplication between `App.tsx` and these files. Confusing for developers who may edit the wrong file.
- Fix approach: Either delete these files or refactor `App.tsx` to use them. If keeping them, export `AnalysisData` from a shared `types.ts` file.

**Unused UI Component Library (48 files):**
- Issue: 48 shadcn/ui component files exist in `Frontend/src/components/ui/`, but only `button.tsx` and `badge.tsx` are imported by the application. The remaining 46 components (accordion, alert-dialog, calendar, carousel, chart, checkbox, collapsible, command, context-menu, dialog, drawer, dropdown-menu, form, hover-card, input-otp, input, label, menubar, navigation-menu, pagination, popover, progress, radio-group, resizable, scroll-area, select, separator, sheet, sidebar, skeleton, slider, sonner, switch, table, tabs, textarea, toggle-group, toggle, tooltip, etc.) are dead weight.
- Files: `Frontend/src/components/ui/*.tsx`
- Impact: Bloats the codebase. Each file has corresponding Radix UI dependencies in `package.json` that increase `node_modules` size and install time. Over 20 `@radix-ui/*` packages are installed but unused.
- Fix approach: Remove unused UI component files and their corresponding `@radix-ui/*` dependencies from `package.json`. Keep only `button.tsx`, `badge.tsx`, `utils.ts`, and `use-mobile.ts`.

**Duplicate Streamlit Prototype Not Removed:**
- Issue: `backend/Image Processing.py` is an older Streamlit-based prototype of the same analysis logic now served by `backend/app.py` (Flask API). Both files contain nearly identical ResNet50 + image metrics logic.
- Files: `backend/Image Processing.py`, `backend/app.py`
- Impact: Confusion about which is the real entry point. Risk of someone modifying the wrong file.
- Fix approach: Archive or delete `backend/Image Processing.py`. It served its purpose as a prototype.

**Vite Config Bloat - Versioned Aliases:**
- Issue: `Frontend/vite.config.ts` contains ~30 resolve aliases mapping versioned package names (e.g., `'vaul@1.1.2': 'vaul'`). These are unnecessary and appear to be auto-generated artifacts. They create maintenance burden when upgrading packages.
- Files: `Frontend/vite.config.ts`
- Impact: Config file is 60 lines when it should be ~15. Aliases break silently if package versions change.
- Fix approach: Remove all versioned aliases. Keep only the `'@': path.resolve(...)` alias.

**Hardcoded Backend URL:**
- Issue: The frontend hardcodes `http://localhost:5000/api/analyze` directly in `App.tsx` line 37. Despite `package.json` having a `"proxy": "http://localhost:5000"` setting (which is a Create React App feature, not Vite), the actual fetch uses the full URL.
- Files: `Frontend/src/App.tsx` (line 37), `Frontend/package.json`
- Impact: Cannot deploy to production without code changes. The `proxy` field in `package.json` does nothing in a Vite project.
- Fix approach: Use an environment variable (e.g., `VITE_API_URL`) for the backend base URL. Configure Vite's `server.proxy` in `vite.config.ts` for local development. Remove the CRA-style `proxy` field from `package.json`.

## Known Bugs

**AnalysisData export missing:**
- Symptoms: If `AnalysisResults.tsx` were imported, the build would fail with "Module has no exported member 'AnalysisData'"
- Files: `Frontend/src/App.tsx` (line 7, `interface AnalysisData` is not exported), `Frontend/src/components/AnalysisResults.tsx` (line 1, imports it)
- Trigger: Attempting to use the decomposed component files
- Workaround: Currently avoided because components are not imported

**Object URL Memory Leak:**
- Symptoms: Each image upload creates a blob URL via `URL.createObjectURL(file)` (line 27) that is never revoked with `URL.revokeObjectURL()`.
- Files: `Frontend/src/App.tsx` (line 27)
- Trigger: Uploading multiple images in sequence without page refresh
- Workaround: Page refresh clears blob URLs

**Sharpness and Color Variance displayed as percentages but are raw values:**
- Symptoms: The frontend displays sharpness score and color variance with a `%` suffix in the metric cards (lines 370, 377), but these backend values are raw metrics (e.g., sharpness can be 0-1000+, color variance can be 0-millions). They are not percentages.
- Files: `Frontend/src/App.tsx` (lines 370, 377), `backend/app.py` (lines in `analyze_image`)
- Trigger: Any image analysis
- Workaround: None; the display is misleading

## Security Considerations

**Flask Debug Mode in Production:**
- Risk: `backend/app.py` runs with `debug=True` (line at `app.run(debug=True)`). Debug mode exposes a Werkzeug debugger that allows arbitrary code execution if accessible.
- Files: `backend/app.py` (last line)
- Current mitigation: Server binds to `127.0.0.1` only
- Recommendations: Use environment variable to control debug mode. Set `debug=False` for any non-local deployment. Use a production WSGI server (gunicorn/waitress).

**Unrestricted CORS:**
- Risk: `CORS(app)` with no arguments allows all origins, all methods, all headers. Any website can call the API.
- Files: `backend/app.py` (line 23)
- Current mitigation: None
- Recommendations: Restrict CORS to the frontend origin only: `CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])`.

**No Input Sanitization on Image Files:**
- Risk: File extension check exists but no content-type verification or magic byte validation. A malicious file with a `.jpg` extension could be processed by PIL/OpenCV, potentially triggering vulnerabilities in image parsing libraries.
- Files: `backend/app.py` (function `allowed_file`, line 32)
- Current mitigation: PIL's `Image.open()` will fail on non-image data, but parsing happens before validation
- Recommendations: Validate magic bytes before passing to PIL. Use `imghdr` or check PIL format after opening.

**Error Messages Expose Internal Details:**
- Risk: Exception messages are returned to the client in error responses (e.g., `f'An error occurred during analysis: {str(e)}'`), which can leak stack traces, file paths, or library versions.
- Files: `backend/app.py` (line 140)
- Current mitigation: None
- Recommendations: Log detailed errors server-side, return generic error messages to the client.

**No Rate Limiting:**
- Risk: The `/api/analyze` endpoint performs CPU-intensive ResNet50 inference on every request. No rate limiting means a single client can exhaust server resources.
- Files: `backend/app.py`
- Current mitigation: None
- Recommendations: Add Flask-Limiter or similar rate limiting middleware.

## Performance Bottlenecks

**ResNet50 Model Loaded Per Request:**
- Problem: The `analyze_image` function loads the full ResNet50 model from disk on every single API call (`models.resnet50(weights=...)` inside the function body).
- Files: `backend/app.py` (inside `analyze_image` function, around line 64)
- Cause: Model instantiation is inside the request handler rather than at module level
- Improvement path: Load the model once at application startup as a module-level global. This saves ~2-3 seconds per request.

**No Image Size Limits Beyond File Size:**
- Problem: A 16MB PNG could decode to an extremely large resolution image (e.g., 10000x10000 pixels). OpenCV and ResNet processing on such images is very slow.
- Files: `backend/app.py` (line 28 sets 16MB file limit, but no pixel dimension limit)
- Cause: Only file byte size is checked, not image dimensions
- Improvement path: After `Image.open()`, check `image.size` and reject or resize images exceeding reasonable dimensions (e.g., 4096x4096).

**48 Unused UI Dependencies Slow Install:**
- Problem: `npm install` pulls ~25 `@radix-ui/*` packages and other UI libraries that are never used in the application.
- Files: `Frontend/package.json`
- Cause: Full shadcn/ui component library was scaffolded but only 2 components are used
- Improvement path: Remove unused dependencies from `package.json`.

## Fragile Areas

**Authenticity Score Algorithm:**
- Files: `backend/app.py` (function `analyze_image`, lines 60-80)
- Why fragile: The scoring formula `score1 + score2 + score3` combines three metrics with arbitrary divisors (100, 10, 1e6), then applies `tanh * 100`. The thresholds (60, 80) for classification are hardcoded magic numbers with no documented justification. Small changes to divisors or thresholds drastically change results.
- Safe modification: Document the rationale for each constant. Add unit tests with known test images to prevent regression. Consider making thresholds configurable.
- Test coverage: Zero automated tests exist for the scoring algorithm.

**Single-File Frontend Architecture:**
- Files: `Frontend/src/App.tsx`
- Why fragile: All state, UI, and API logic in one file. Any change to upload flow, display, or API response format requires editing this file, risking unintended side effects.
- Safe modification: Extract into components first, then modify individual components.
- Test coverage: No frontend tests exist.

## Scaling Limits

**Single-Process Flask Server:**
- Current capacity: Handles one request at a time (Flask dev server is single-threaded)
- Limit: Any concurrent requests queue behind the current ResNet50 inference (~3-5 seconds per image)
- Scaling path: Use gunicorn with multiple workers. Consider async processing with a task queue (Celery) for image analysis.

**No Caching:**
- Current capacity: Every identical image upload triggers full re-analysis
- Limit: Repeated analysis of the same image wastes compute
- Scaling path: Cache results by SHA-256 hash. Return cached results for previously analyzed images.

## Dependencies at Risk

**Pinned Old Versions:**
- Risk: `requirements.txt` pins `torch==2.0.1`, `numpy==1.24.3`, `Pillow==10.0.0`, `opencv-python==4.8.0.74`. These are from mid-2023 and may have known security vulnerabilities.
- Impact: Security patches and performance improvements are missed
- Migration plan: Update to latest compatible versions. Test with `pip install --upgrade` and verify analysis results remain consistent.

**No TypeScript Configuration:**
- Risk: No `tsconfig.json` found in the Frontend directory. TypeScript compilation behavior relies entirely on Vite defaults.
- Impact: No strict type checking, implicit `any` types allowed, no path mapping for `@/` alias at the TS level
- Migration plan: Add a `tsconfig.json` with `strict: true` and proper path aliases.

## Missing Critical Features

**No Actual Blockchain Integration:**
- Problem: The UI displays "Verified on Blockchain" and shows SHA-256 hashes, but there is no blockchain whatsoever. The backend hardcodes `'blockchainStatus': 'verified'` in every response.
- Files: `backend/app.py` (line 103), `Frontend/src/App.tsx` (lines 432-434)
- Blocks: The entire "blockchain verification" feature claimed by the application name (TrustChain-AV) is non-functional.

**No User Authentication:**
- Problem: No login, sessions, or user identification. Anyone with network access to the server can use the API.
- Blocks: Usage tracking, result history, audit trails.

**No Result Persistence:**
- Problem: Analysis results exist only in frontend state. Refreshing the page loses all results. No database or file storage for analysis history.
- Blocks: Historical analysis lookup, comparison of results over time.

## Test Coverage Gaps

**Zero Frontend Tests:**
- What's not tested: All React components, state management, API integration, file upload handling, drag-and-drop behavior
- Files: `Frontend/src/App.tsx`, all files in `Frontend/src/components/`
- Risk: Any UI refactoring could silently break functionality
- Priority: High

**Backend Tests Are Manual/External Only:**
- What's not tested: The test files (`test_backend.py`, `test_backend_check.py`) require a running server and make HTTP requests. They are integration smoke tests, not unit tests. The core `analyze_image` function has zero unit tests.
- Files: `test_backend.py`, `test_backend_check.py`, `backend/app.py`
- Risk: The scoring algorithm, image processing pipeline, and error handling paths are completely untested. Changes to thresholds or metric calculations could break classification without detection.
- Priority: High -- the scoring algorithm is the core value proposition and has no test coverage.

**No CI/CD Pipeline:**
- What's not tested: No automated test runner, no linting, no build verification on commits
- Files: No `.github/workflows/`, no `Jenkinsfile`, no CI config detected
- Risk: Broken commits can be pushed without detection
- Priority: Medium

---

*Concerns audit: 2026-03-05*
