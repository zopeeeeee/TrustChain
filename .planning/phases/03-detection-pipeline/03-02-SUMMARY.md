---
phase: 03-detection-pipeline
plan: 02
subsystem: detection
tags: [pytorch, asyncio, fusion, detection-pipeline, status-polling, verdict]

# Dependency graph
requires:
  - phase: 03-detection-pipeline
    provides: ML modules (visual, audio, VAD, fusion) loaded at startup
  - phase: 02-upload-preprocessing
    provides: Preprocessing pipeline (frame extraction, audio extraction)
provides:
  - Detection orchestrator service (run_detection)
  - End-to-end pipeline from upload to REAL/FAKE verdict
  - Status endpoint with verdict, confidence, scores, file_hash
  - Frontend results display with verdict badge, confidence bar, modality breakdown
affects: [04-results-ui, 05-blockchain]

# Tech tracking
tech-stack:
  added: []
  patterns: [asyncio.to_thread for CPU-bound ML inference, status-driven pipeline orchestration]

key-files:
  created:
    - backend/app/services/detection.py
    - backend/alembic/versions/003_widen_status_column.py
    - backend/tests/test_detection.py
  modified:
    - backend/app/services/preprocessing.py
    - backend/app/api/uploads.py
    - backend/app/models/upload.py
    - backend/app/schemas/upload.py
    - backend/tests/test_uploads.py
    - frontend/src/lib/api.ts
    - frontend/src/hooks/useJobStatus.ts
    - frontend/src/pages/ResultsPage.tsx

key-decisions:
  - "Detection runs via asyncio.to_thread to prevent event loop blocking during ML inference"
  - "No-speech videos use zero audio vector with audio_weight=0.0 for fusion"
  - "Visual score and audio score set to fusion confidence for prototype (placeholder until separate scoring)"

patterns-established:
  - "Pipeline chaining: process_video chains into run_detection after preprocessing"
  - "Status-driven stages: each pipeline stage updates DB status before running"
  - "Lazy import of run_detection in preprocessing to avoid circular imports"

requirements-completed: [DETC-05, DETC-06]

# Metrics
duration: 6min
completed: 2026-03-06
---

# Phase 3 Plan 2: Detection Pipeline Wiring Summary

**Detection orchestrator wiring ML modules into end-to-end pipeline with status-driven stages, no-speech fallback, and frontend verdict display with confidence bar and modality breakdown**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-05T21:41:07Z
- **Completed:** 2026-03-05T21:47:42Z
- **Tasks:** 2
- **Files modified:** 11

## Accomplishments
- Created detection orchestrator that chains visual analysis, audio analysis, and fusion into a single pipeline
- Extended process_video to automatically trigger detection after preprocessing (no manual trigger)
- Frontend displays all 6 processing stages with verdict badge, confidence bar, and modality breakdown
- 6 new detection tests covering status transitions, result storage, no-speech handling, error handling, and pipeline chaining
- All 34 tests passing (6 new + 28 existing)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create detection orchestrator and wire into processing pipeline** - `aa05486` (test, RED), `7fceea9` (feat, GREEN)
2. **Task 2: Update frontend for detection status stages and result fields** - `e1484f0` (feat)

## Files Created/Modified
- `backend/app/services/detection.py` - Detection orchestrator: visual_analysis -> audio_analysis -> computing_fusion -> completed
- `backend/app/services/preprocessing.py` - Modified to accept models dict and chain into run_detection
- `backend/app/api/uploads.py` - Passes ML models from app.state; status endpoint returns detection fields
- `backend/app/models/upload.py` - Status column widened from String(20) to String(30)
- `backend/app/schemas/upload.py` - Added verdict, confidence, scores, speech_detected, audio_weight, file_hash
- `backend/alembic/versions/003_widen_status_column.py` - Migration to widen status column
- `backend/tests/test_detection.py` - 6 tests for detection orchestrator
- `backend/tests/test_uploads.py` - Updated make_mock_upload with detection fields
- `frontend/src/lib/api.ts` - Extended UploadStatusResponse with detection fields
- `frontend/src/hooks/useJobStatus.ts` - TERMINAL_STATES changed to [completed, failed]
- `frontend/src/pages/ResultsPage.tsx` - Verdict badge, confidence bar, modality breakdown, SHA-256 hash display

## Decisions Made
- Used asyncio.to_thread for ML inference calls (extract_visual_features, extract_audio_features, fusion forward) to prevent blocking the event loop
- No-speech videos use torch.zeros(768) as audio features with audio_weight=0.0, still producing a verdict
- Visual score and audio score are set to the fusion confidence value for the prototype phase (separate scoring will come with model training)
- Used lazy import of run_detection inside process_video to avoid circular import between preprocessing and detection modules

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated make_mock_upload with detection result fields**
- **Found during:** Task 1 (GREEN phase, full test suite verification)
- **Issue:** test_get_status_returns_upload_info failed because MagicMock(spec=Upload) returned MagicMock objects for new fields (verdict, confidence, etc.) that Pydantic could not serialize
- **Fix:** Added explicit None defaults for verdict, confidence, visual_score, audio_score, speech_detected, audio_weight in make_mock_upload helper
- **Files modified:** backend/tests/test_uploads.py
- **Verification:** All 34 tests pass
- **Committed in:** 7fceea9 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Auto-fix essential for test compatibility with new schema fields. No scope creep.

## Issues Encountered
None - implementation followed plan straightforwardly.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Complete detection pipeline operational from upload to verdict
- Frontend displays all processing stages and results
- Ready for Phase 4 (Results UI) to build more detailed results views
- Ready for Phase 5 (Blockchain) to anchor verdicts on-chain

## Self-Check: PASSED

- All 3 created files verified present on disk
- All 8 modified files verified present on disk
- Commit aa05486 (Task 1 RED) verified in git log
- Commit 7fceea9 (Task 1 GREEN) verified in git log
- Commit e1484f0 (Task 2) verified in git log
- All 34 tests pass

---
*Phase: 03-detection-pipeline*
*Completed: 2026-03-06*
