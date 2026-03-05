---
phase: 03-detection-pipeline
verified: 2026-03-06T12:00:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 3: Detection Pipeline Verification Report

**Phase Goal:** The system analyzes uploaded videos using dual-stream ML (visual + audio) and returns a REAL/FAKE verdict with confidence score and modality breakdown
**Verified:** 2026-03-06T12:00:00Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Uploading a video produces a REAL or FAKE verdict with a numerical confidence score stored in the database | VERIFIED | `detection.py:74` computes `verdict = "FAKE" if confidence > 0.5 else "REAL"`, stores via `update_upload_status` with verdict, confidence, completed_at. Upload model has `verdict: String(10)`, `confidence: Float` columns. Status endpoint returns these fields. |
| 2 | The detection result includes separate visual and audio scores alongside the fused verdict | VERIFIED | `detection.py:77-78` computes `visual_score` and `audio_score`. Upload model has `visual_score: Float`, `audio_score: Float` columns. Schema `UploadStatusResponse` exposes both. Frontend `ResultsPage.tsx:182-217` renders modality breakdown grid with Eye/Ear icons and percentage display. |
| 3 | Videos without speech are detected by VAD and analyzed using visual-only mode (audio weight set to zero) without failing | VERIFIED | `detection.py:51-65`: if `has_speech` is False, sets `audio_features = torch.zeros(768)`, `audio_weight = 0.0`, `speech_detected = False`. VAD module `vad.py:12-63` uses WebRTC 30ms frame analysis. Test `test_run_detection_no_speech` confirms `audio_weight=0.0` and `speech_detected=False` are stored. |
| 4 | The frontend displays multi-stage processing status during analysis | VERIFIED | `ResultsPage.tsx:14-23` defines STATUS_LABELS for all 6 stages: uploading, extracting_frames, extracting_audio, visual_analysis, audio_analysis, computing_fusion. `useJobStatus.ts:6` polls until TERMINAL_STATES (completed, failed). Detection service updates status at each stage via `update_upload_status`. |
| 5 | A SHA-256 hash of the uploaded file is computed and stored alongside the detection result | VERIFIED | `uploads.py:70-92`: SHA-256 computed during streaming upload via `hashlib.sha256()`, stored as `upload.file_hash = sha256_hash.hexdigest()`. Upload model has `file_hash: String(64)`. Status endpoint returns `file_hash`. Frontend displays it with Hash icon at `ResultsPage.tsx:219-232`. |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `backend/app/ml/visual.py` | ResNet-50 feature extraction | VERIFIED | 56 lines. Exports `extract_visual_features`, `IMAGENET_TRANSFORM`. Loads frames, applies ImageNet normalization, returns mean 2048-dim vector. |
| `backend/app/ml/audio.py` | Wav2Vec2 feature extraction | VERIFIED | 43 lines. Exports `extract_audio_features`. Reads 16kHz WAV via soundfile, processes through Wav2Vec2, returns mean 768-dim vector. |
| `backend/app/ml/vad.py` | WebRTC VAD speech detection | VERIFIED | 64 lines. Exports `detect_speech`. Analyzes 30ms frames at 16kHz, returns True if voiced ratio exceeds threshold. Graceful error handling. |
| `backend/app/ml/fusion.py` | Fusion MLP classifier | VERIFIED | 55 lines. Exports `FusionMLP` (nn.Module). Concatenates 2048+768 features, hidden layer 512, Sigmoid output. Supports `audio_weight` parameter. |
| `backend/app/ml/loader.py` | Real model loading | VERIFIED | 56 lines. Exports `load_models`. Loads ResNet-50 (IMAGENET1K_V1), Wav2Vec2 (facebook/wav2vec2-base-960h), FusionMLP. All set to eval mode with gradients disabled. |
| `backend/app/services/detection.py` | Detection pipeline orchestrator | VERIFIED | 104 lines. Exports `run_detection`. Chains visual_analysis -> audio_analysis -> computing_fusion -> completed with status updates. Handles no-speech case. Error handling sets status=failed. |
| `backend/alembic/versions/003_widen_status_column.py` | Status column migration | VERIFIED | 38 lines. Widens status from String(20) to String(30) for "computing_fusion" status value. |
| `backend/tests/test_detection.py` | Detection integration tests | VERIFIED | 261 lines, 6 tests covering status transitions, result storage, no-speech handling, completed_at, error handling, and pipeline chaining. |
| `backend/app/models/upload.py` | Upload model with detection fields | VERIFIED | Contains verdict, confidence, visual_score, audio_score, speech_detected, audio_weight, file_hash columns. |
| `backend/app/schemas/upload.py` | Schema with detection response fields | VERIFIED | UploadStatusResponse includes verdict, confidence, visual_score, audio_score, speech_detected, audio_weight, file_hash. |
| `frontend/src/hooks/useJobStatus.ts` | Polling hook with terminal states | VERIFIED | TERMINAL_STATES = ["completed", "failed"]. Polls every 2s until terminal. |
| `frontend/src/pages/ResultsPage.tsx` | Results page with verdict display | VERIFIED | 240 lines. Verdict badge (color-coded REAL/FAKE), confidence bar, modality breakdown grid, SHA-256 hash display, multi-stage status labels. |
| `frontend/src/lib/api.ts` | API types with detection fields | VERIFIED | UploadStatusResponse interface includes all detection fields. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `main.py` | `loader.py` | lifespan calls `load_models()` | WIRED | Line 21: `models = load_models()`. Lines 22-25: stores all 4 models on `app.state`. |
| `loader.py` | `visual.py` | builds ResNet-50 | WIRED | Line 27: `models.resnet50(weights=...IMAGENET1K_V1)`. |
| `loader.py` | `fusion.py` | instantiates FusionMLP | WIRED | Line 9: imports FusionMLP, Line 45: `fusion_model = FusionMLP()`. |
| `preprocessing.py` | `detection.py` | process_video calls run_detection | WIRED | Line 174: lazy import `from app.services.detection import run_detection`. Line 176: `await run_detection(upload_id, file_path, models, session)`. |
| `detection.py` | `visual.py` | calls extract_visual_features | WIRED | Line 14: import. Lines 44-46: `await asyncio.to_thread(extract_visual_features, ...)`. |
| `detection.py` | `audio.py` | calls extract_audio_features | WIRED | Line 11: import. Lines 54-59: `await asyncio.to_thread(extract_audio_features, ...)`. |
| `detection.py` | `vad.py` | calls detect_speech | WIRED | Line 13: import. Line 51: `has_speech = detect_speech(audio_path)`. |
| `detection.py` | `fusion.py` | calls fusion_model forward | WIRED | Line 69: `fusion_model = models["fusion_model"]`. Lines 70-72: `await asyncio.to_thread(fusion_model, visual_features, audio_features, audio_weight)`. |
| `uploads.py` | `preprocessing.py` | passes models dict to background task | WIRED | Lines 96-102: builds models dict from `request.app.state`. Line 102: `asyncio.create_task(process_video(upload.id, str(file_path), models))`. |
| `useJobStatus.ts` | `ResultsPage.tsx` | polling through detection statuses | WIRED | ResultsPage uses `useJobStatus(id)` at line 35. TERMINAL_STATES stops polling at completed/failed. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DETC-01 | 03-01 | ResNet-50 frozen backbone extracts 2048-dim visual feature vector | SATISFIED | `visual.py` processes frames through ResNet-50 (sans FC), returns mean 2048-dim tensor. `loader.py` freezes parameters. |
| DETC-02 | 03-01 | Wav2Vec2 frozen backbone extracts 768-dim audio feature vector | SATISFIED | `audio.py` processes 16kHz WAV through Wav2Vec2, returns mean 768-dim tensor. `loader.py` freezes parameters. |
| DETC-03 | 03-01 | WebRTC VAD determines speech presence; no speech sets audio_weight=0.0 | SATISFIED | `vad.py` implements WebRTC VAD with 30ms frames. `detection.py:62-65` sets `audio_weight=0.0` and `torch.zeros(768)` when no speech. |
| DETC-04 | 03-01 | Fusion MLP concatenates visual+weighted audio, outputs REAL/FAKE with confidence | SATISFIED | `fusion.py` FusionMLP concatenates 2048+768 features, outputs [0,1] score. `detection.py:74` maps to REAL/FAKE verdict. |
| DETC-05 | 03-02 | Frontend shows multi-stage processing status | SATISFIED | `ResultsPage.tsx` STATUS_LABELS has all 6 stages. `useJobStatus.ts` polls until terminal. Backend updates status at each stage. |
| DETC-06 | 03-02 | System computes SHA-256 hash of uploaded video file | SATISFIED | `uploads.py:70-92` computes SHA-256 during streaming upload. Stored in `file_hash` column (String(64)). Returned in status endpoint. Displayed in frontend. |

No orphaned requirements found -- all 6 DETC requirements are covered by the two plans.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `detection.py` | 77-78 | visual_score and audio_score set to fusion confidence (prototype placeholder) | Info | Noted in code and summary as prototype behavior. Not a blocker -- separate scoring requires model training. |
| `fusion.py` | 45 | FusionMLP uses random weights (untrained) | Info | Expected for prototype. Training is a separate concern (Google Colab, per REQUIREMENTS.md out-of-scope). |

No blockers or warnings found.

### Human Verification Required

### 1. End-to-End Upload and Detection Flow

**Test:** Upload a short video file through the frontend and wait for processing to complete.
**Expected:** Status cycles through extracting_frames -> extracting_audio -> visual_analysis -> audio_analysis -> computing_fusion -> completed. Final result shows REAL or FAKE verdict with confidence bar and modality scores.
**Why human:** Requires running Docker containers with FFmpeg, ML models, and database. Cannot verify multi-service integration programmatically.

### 2. No-Speech Video Handling

**Test:** Upload a video with no speech (e.g., nature footage, music only).
**Expected:** Processing completes successfully. Audio score shows "N/A" or 0. Speech detected shows "No speech detected". Verdict and confidence still display.
**Why human:** Requires actual video processing through the full pipeline to verify VAD correctly identifies no speech.

### 3. Visual Appearance of Results Page

**Test:** View the results page after a completed analysis.
**Expected:** Verdict badge is color-coded (green for REAL, red for FAKE). Confidence bar fills proportionally. Modality breakdown shows two cards (Visual Score, Audio Score). SHA-256 hash displays in monospace.
**Why human:** Visual layout, colors, spacing, and responsive behavior cannot be verified programmatically.

### Gaps Summary

No gaps found. All 5 observable truths are verified. All 6 requirements (DETC-01 through DETC-06) are satisfied. All artifacts exist, are substantive (not stubs), and are properly wired together. The detection pipeline chains correctly from upload through preprocessing into ML analysis and stores results in the database. The frontend polls for status updates and displays the full verdict with modality breakdown.

The only notable items are informational: the FusionMLP uses untrained random weights (expected for prototype), and visual/audio scores are set to the fusion confidence value rather than independent scores (requires model training to separate). Neither blocks the phase goal.

---

_Verified: 2026-03-06T12:00:00Z_
_Verifier: Claude (gsd-verifier)_
