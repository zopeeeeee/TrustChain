# Phase 2: Upload and Preprocessing - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can upload video files (MP4, AVI, MOV, MKV up to 500MB), receive a job ID immediately, and the system extracts frames (224x224, normalized) and a 16kHz mono WAV audio track via FFmpeg. Edge cases (no audio, corrupted files, too short) are handled gracefully. No ML inference — just upload, validation, and preprocessing.

</domain>

<decisions>
## Implementation Decisions

### Upload Experience
- Compact card with browse button (not full-page dropzone) — cleaner form-like feel
- Indeterminate spinner during upload (no percentage progress bar)
- Auto-redirect to /results/:id after upload completes — user sees processing status there
- Support multiple file queue — accept multiple files, process sequentially, show queue
- Client-side validation first (extension + size check), server re-validates on receipt

### Background Processing
- Use asyncio.create_task for background FFmpeg jobs — no Celery/Redis, keeps infrastructure simple for prototype
- FFmpeg installed inside the backend Docker container (apt-get install ffmpeg in Dockerfile)
- Detailed multi-stage status updates visible to user: Uploading → Extracting frames → Extracting audio → Queued for analysis
- Status stored in Upload model's status field, updated at each processing stage

### File Storage
- Clean up extracted frames and audio after analysis completes — keep only original video and results in DB
- Preserve original filename inside job directory: /data/{job_id}/{original_filename}
- Claude's Discretion: Storage location (Docker volume vs bind mount), directory structure (job-based vs type-based)

### Error UX
- Inline error below the upload card for validation failures (wrong format, too large) — red text, no upload attempt
- No audio track → continue with visual-only analysis, set audio_weight=0.0, show note in results
- FFmpeg failure (corrupted file) → status changes to "failed" with user-friendly message on results page
- Videos under 1 second → reject with clear message during preprocessing

### Claude's Discretion
- Polling mechanism (simple polling vs WebSocket) for frontend status tracking
- Exact storage directory structure and Docker volume configuration
- Frame extraction interval tuning (default every 10th frame per PREP-01)
- SHA-256 hashing timing (during upload or during preprocessing)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- Upload model (backend/app/models/upload.py): Already has status, filename, file_path, file_hash columns — ready for upload handling
- UploadPage.tsx: Empty shell with "Upload Video" heading — ready to populate with upload card
- backend/app/services/__init__.py: Empty services package — new preprocessing service goes here
- backend/app/api/router.py: API router with /api prefix — add upload endpoints here

### Established Patterns
- Async SQLAlchemy sessions via get_db() dependency injection
- Lifespan-based initialization (app.state for shared resources)
- API routing: nested routers under /api prefix
- Frontend: React Router with page shells, NavBar with active link state

### Integration Points
- POST /api/uploads → new upload endpoint (returns job ID)
- GET /api/uploads/:id/status → polling endpoint for frontend
- Upload model status field drives the frontend status display
- ResultsPage.tsx already reads :id param from URL — ready for redirect after upload

</code_context>

<specifics>
## Specific Ideas

- PREP-01 specifies: extract frames at configurable interval (default every 10th frame), resize to 224x224, normalize to ImageNet mean/std
- PREP-02 specifies: extract audio, resample to 16kHz mono WAV
- UPLD-03 specifies: upload returns job ID immediately, frontend polls for completion
- Processing stages per DETC-05: extracting frames → extracting audio → queued for analysis (ML stages added in Phase 3)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-upload-and-preprocessing*
*Context gathered: 2026-03-06*
