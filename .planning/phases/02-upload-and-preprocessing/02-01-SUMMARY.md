---
phase: 02-upload-and-preprocessing
plan: 01
subsystem: backend-upload-preprocessing
tags: [upload, ffmpeg, preprocessing, api, tdd]
dependency_graph:
  requires: [01-01, 01-03]
  provides: [upload-api, preprocessing-service, upload-schemas]
  affects: [02-02, 03-01]
tech_stack:
  added: [python-multipart, aiofiles, numpy, Pillow]
  patterns: [async-file-streaming, sha256-on-upload, background-task-processing, ffmpeg-subprocess]
key_files:
  created:
    - backend/app/api/uploads.py
    - backend/app/schemas/__init__.py
    - backend/app/schemas/upload.py
    - backend/app/services/preprocessing.py
    - backend/tests/test_uploads.py
    - backend/tests/test_preprocessing.py
    - backend/tests/fixtures/__init__.py
    - backend/tests/fixtures/conftest.py
  modified:
    - backend/app/config.py
    - backend/app/models/upload.py
    - backend/app/api/router.py
    - backend/requirements.txt
decisions:
  - Used FastAPI dependency_overrides for test isolation instead of module-level patching
  - SHA-256 hash computed during upload stream (not as separate pass) for efficiency
  - Preprocessing service creates its own async_session (not request-scoped) for background task safety
  - FakeUpload class pattern for tracking status changes in process_video tests
metrics:
  tasks_completed: 2
  tasks_total: 2
  tests_written: 13
  tests_passing: 13
  completed_date: "2026-03-06"
---

# Phase 2 Plan 1: Backend Upload API and FFmpeg Preprocessing Summary

Backend upload API with multipart file validation, async disk streaming with SHA-256 hashing, and FFmpeg preprocessing service that extracts 224x224 frames every 10th frame and 16kHz mono WAV audio with graceful edge case handling.

## Task Completion

| Task | Name | Commit | Tests | Status |
|------|------|--------|-------|--------|
| 1 | Upload API endpoints, schemas, config | b04eaf3 | 5/5 | DONE |
| 2 | FFmpeg preprocessing service | PENDING | 8/8 | CODE COMPLETE, COMMIT PENDING |

## What Was Built

### Task 1: Upload API Endpoints
- **POST /api/uploads**: Accepts multipart video upload, validates file extension against allowed list (.mp4, .avi, .mov, .mkv), checks Content-Length against 500MB limit, streams to /data/{upload_id}/{filename} in 1MB chunks, computes SHA-256 hash during stream, fires background preprocessing task, returns 201 with job ID
- **GET /api/uploads/{id}/status**: Returns current processing stage with filename, status, error_message, and created_at
- **Pydantic schemas**: UploadResponse and UploadStatusResponse with proper type annotations
- **Config additions**: upload_dir, max_file_size, allowed_extensions, frame_interval settings
- **Model update**: Added error_message column to Upload model

### Task 2: FFmpeg Preprocessing Service
- **probe_video**: Runs ffprobe with JSON output, parses metadata, raises on failure
- **validate_video**: Checks duration >= 1 second, detects corrupted files via ffprobe failure
- **extract_frames**: FFmpeg frame extraction at configurable interval, 224x224 resize, JPEG output
- **extract_audio**: FFmpeg audio extraction to 16kHz mono WAV, graceful handling of no-audio streams
- **process_video**: Background orchestrator with multi-stage status updates (extracting_frames -> extracting_audio -> queued), sets audio_weight=0.0 when no audio track, catches all exceptions and sets status=failed with error_message
- **Test fixtures**: conftest.py with FFmpeg-based synthetic video generation for future integration tests

## Tests

- **test_uploads.py (5 tests)**: Valid upload 201, invalid extension 400, oversized 400, status lookup 200, nonexistent 404
- **test_preprocessing.py (8 tests)**: probe_video JSON parsing, extract_frames produces JPGs, extract_audio success, no-audio-stream handling, short video rejection, corrupted file rejection, process_video stage orchestration, process_video failure handling

All 13 tests pass without requiring a running database or FFmpeg (fully mocked).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed missing aiofiles and python-multipart packages**
- Found during: Task 1 test execution
- Issue: aiofiles package not installed locally despite being in requirements.txt
- Fix: pip install aiofiles python-multipart
- Files: N/A (local env only, requirements.txt already correct)

**2. [Rule 1 - Bug] Fixed test isolation using FastAPI dependency_overrides**
- Found during: Task 1 test execution
- Issue: Module-level patching of get_db didn't work because FastAPI resolves dependencies from the app, not the module
- Fix: Used app.dependency_overrides[get_db] pattern for proper DI override
- Files: backend/tests/test_uploads.py

**3. [Rule 1 - Bug] Fixed process_video status tracking in tests**
- Found during: Task 2 test execution
- Issue: patch.object on MagicMock class for 'status' property fails because MagicMock doesn't expose real attributes
- Fix: Created FakeUpload class with property-based status tracking
- Files: backend/tests/test_preprocessing.py

## Pending Manual Steps

Task 2 git commit is pending due to bash permission issues. Run:
```bash
cd "C:/Users/zopev/Desktop/Final Year Project/Implementation"
git add backend/app/services/preprocessing.py backend/requirements.txt backend/tests/test_preprocessing.py backend/tests/fixtures/__init__.py backend/tests/fixtures/conftest.py
git commit -m "feat(02-01): FFmpeg preprocessing service with edge case handling

- probe_video, validate_video, extract_frames, extract_audio, process_video
- Multi-stage status updates: extracting_frames -> extracting_audio -> queued
- Edge cases: no audio (audio_weight=0.0), short video, corrupted file
- 8 tests with mocked subprocess, test fixture generators
- Added numpy and Pillow to requirements.txt

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```
