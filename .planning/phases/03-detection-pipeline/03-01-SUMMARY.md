---
phase: 03-detection-pipeline
plan: 01
subsystem: ml
tags: [pytorch, resnet50, wav2vec2, webrtcvad, transformers, fusion-mlp]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: FastAPI app with lifespan, model stub loader, health endpoint
provides:
  - ResNet-50 visual feature extraction (2048-dim)
  - Wav2Vec2 audio feature extraction (768-dim)
  - WebRTC VAD speech detection
  - FusionMLP classifier (visual+audio to confidence score)
  - Real model loading via load_models() at startup
  - Docker config for CPU-only PyTorch with model cache
affects: [03-detection-pipeline, 04-results-ui]

# Tech tracking
tech-stack:
  added: [torch, torchvision, torchaudio, transformers, webrtcvad-wheels, soundfile]
  patterns: [torch.no_grad inference, mock-based ML testing, CPU-only PyTorch in Docker]

key-files:
  created:
    - backend/app/ml/visual.py
    - backend/app/ml/audio.py
    - backend/app/ml/vad.py
    - backend/app/ml/fusion.py
    - backend/tests/test_visual.py
    - backend/tests/test_audio.py
    - backend/tests/test_vad.py
    - backend/tests/test_fusion.py
  modified:
    - backend/requirements.txt
    - backend/app/ml/loader.py
    - backend/app/main.py
    - backend/app/api/health.py
    - backend/Dockerfile
    - docker-compose.yml
    - backend/tests/conftest.py
    - backend/tests/test_health.py

key-decisions:
  - "Torch/torchvision/torchaudio installed via Dockerfile separate pip step with CPU index, not in requirements.txt"
  - "Health endpoint changed from stub dict status to loaded/not_loaded presence check"
  - "FusionMLP uses random weights for prototype (untrained)"

patterns-established:
  - "ML module pattern: pure function taking model+input, returning tensor"
  - "Mock-based ML testing: mock models return tensors of correct shape, no network calls"
  - "Separate CPU PyTorch install in Dockerfile before requirements.txt"

requirements-completed: [DETC-01, DETC-02, DETC-03, DETC-04]

# Metrics
duration: 14min
completed: 2026-03-06
---

# Phase 3 Plan 1: ML Modules Summary

**Four ML modules (ResNet-50 visual, Wav2Vec2 audio, WebRTC VAD, FusionMLP) with real model loading, Docker CPU-only PyTorch, and 9 mocked unit tests**

## Performance

- **Duration:** 14 min
- **Started:** 2026-03-05T21:23:45Z
- **Completed:** 2026-03-05T21:37:59Z
- **Tasks:** 2
- **Files modified:** 16

## Accomplishments
- Created four ML modules with correct function signatures and type contracts
- Replaced model stubs with real PyTorch/HuggingFace model loading at startup
- Updated Docker configuration for CPU-only PyTorch with persistent model cache
- 9 new unit tests passing with fully mocked models (no network calls, <5s runtime)
- All 28 tests (9 new + 19 existing) pass after integration

## Task Commits

Each task was committed atomically:

1. **Task 1: Install ML dependencies and create four ML modules with tests** - `280d6d9` (feat)
2. **Task 2: Replace model stubs with real loading, update Dockerfile and Docker Compose** - `6889f02` (feat)

## Files Created/Modified
- `backend/app/ml/visual.py` - ResNet-50 feature extraction (2048-dim output from frame directory)
- `backend/app/ml/audio.py` - Wav2Vec2 feature extraction (768-dim output from WAV file)
- `backend/app/ml/vad.py` - WebRTC VAD speech detection (boolean result from audio analysis)
- `backend/app/ml/fusion.py` - FusionMLP classifier (2816-dim input to [0,1] confidence score)
- `backend/app/ml/loader.py` - Real model loading (ResNet-50, Wav2Vec2, FusionMLP)
- `backend/app/main.py` - Updated lifespan to store all four models on app.state
- `backend/app/api/health.py` - Updated to report loaded/not_loaded for visual, audio, fusion
- `backend/Dockerfile` - CPU-only PyTorch install before requirements.txt
- `docker-compose.yml` - Added model_cache volume for HuggingFace cache persistence
- `backend/requirements.txt` - Added transformers, webrtcvad-wheels, soundfile
- `backend/tests/test_visual.py` - 2 tests for visual feature extraction
- `backend/tests/test_audio.py` - 1 test for audio feature extraction
- `backend/tests/test_vad.py` - 4 tests for VAD speech detection
- `backend/tests/test_fusion.py` - 2 tests for FusionMLP forward pass
- `backend/tests/conftest.py` - Updated to mock load_models instead of load_model_stubs
- `backend/tests/test_health.py` - Updated assertions for new model status format

## Decisions Made
- Installed torch/torchvision/torchaudio via separate Dockerfile pip step with CPU index URL, keeping only transformers/webrtcvad-wheels/soundfile in requirements.txt (avoids invalid --index-url syntax in requirements files)
- Changed health endpoint from dict-based status ("stub") to presence-based status ("loaded"/"not_loaded") since real models are PyTorch modules, not dicts
- FusionMLP initialized with random weights (untrained prototype) -- training will come later

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed visual test to mock IMAGENET_TRANSFORM**
- **Found during:** Task 1 (GREEN phase)
- **Issue:** Mocking PIL Image alone was insufficient; torchvision's ToTensor checks isinstance(pic, PIL.Image) and rejects MagicMock
- **Fix:** Added @patch("app.ml.visual.IMAGENET_TRANSFORM") to return a tensor directly
- **Files modified:** backend/tests/test_visual.py
- **Verification:** All 9 ML tests pass
- **Committed in:** 280d6d9 (Task 1 commit)

**2. [Rule 2 - Missing Critical] Updated health endpoint for real models**
- **Found during:** Task 2
- **Issue:** Health endpoint used dict subscript (visual_model["status"]) which would crash with real PyTorch models
- **Fix:** Changed to presence-based check (is not None -> "loaded"), added fusion model status
- **Files modified:** backend/app/api/health.py, backend/tests/test_health.py
- **Verification:** Health tests pass with mocked models
- **Committed in:** 6889f02 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 missing critical)
**Impact on plan:** Both fixes essential for correctness. No scope creep.

## Issues Encountered
- Windows pip script installation errors prevented normal `pip install transformers` (WinError 2 on .exe files). Resolved by using `--target` flag to bypass script creation.
- torchvision installation initially failed silently due to Windows script errors; required retry with `python -m pip`.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All four ML modules ready for Plan 02 to wire into the background processing pipeline
- Models load at startup via lifespan, stored on app.state for route/service access
- Docker configuration ready for CPU-only inference with cached models

## Self-Check: PASSED

- All 9 created files verified present on disk
- Commit 280d6d9 (Task 1) verified in git log
- Commit 6889f02 (Task 2) verified in git log
- All 28 tests pass

---
*Phase: 03-detection-pipeline*
*Completed: 2026-03-06*
