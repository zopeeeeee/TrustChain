---
status: complete
phase: 03-detection-pipeline
source: [03-01-SUMMARY.md, 03-02-SUMMARY.md]
started: 2026-03-06
updated: 2026-03-06
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start with ML Models
expected: Rebuild and restart services with `docker compose up -d --build`. Backend starts successfully. Health endpoint at localhost:8000/api/health returns visual, audio, and fusion model statuses as "loaded". First startup may take several minutes to download models (~460MB total).
result: pass

### 2. Upload Triggers Full Detection Pipeline
expected: Upload a valid MP4 video with audio. Status polling on the results page cycles through stages: extracting_frames, extracting_audio, visual_analysis, audio_analysis, computing_fusion, completed. Final status is "completed" (not stuck at an intermediate stage).
result: pass

### 3. Verdict and Confidence Display
expected: After detection completes, the results page shows: a verdict badge (REAL or FAKE), a confidence percentage bar, and a modality breakdown showing visual score and audio score values. All values are numeric (not null or undefined).
result: pass

### 4. SHA-256 File Hash Display
expected: After detection completes, the results page displays a SHA-256 file hash string for the uploaded video. The hash is a 64-character hexadecimal string.
result: pass

### 5. No-Speech Video Handling
expected: Upload a video that has no speech (e.g., music-only or silent video). Detection still completes successfully with a verdict. The audio_weight should be 0.0 and speech_detected should be false (visible in status API response or results display).
result: pass

## Summary

total: 5
passed: 5
issues: 0
pending: 0
skipped: 0

## Gaps

[none]
