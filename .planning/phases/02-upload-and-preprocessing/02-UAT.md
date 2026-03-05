---
status: complete
phase: 02-upload-and-preprocessing
source: [02-01-SUMMARY.md, 02-02-SUMMARY.md, 02-03-SUMMARY.md]
started: 2026-03-06T20:30:00Z
updated: 2026-03-06T21:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running services. Start fresh with `docker compose down && docker compose up -d --build`. Frontend loads at localhost:5173 with TrustChain-AV heading and nav bar. Backend health check at localhost:8000/api/health returns status ok.
result: pass

### 2. Upload Card UI
expected: Navigate to /upload page. A compact upload card is shown with a cloud/upload icon, "Drag and drop video files here, or" text, and a "Browse files" button. Below the card: "Supported: MP4, AVI, MOV, MKV (max 500MB)" text.
result: pass

### 3. Client-Side Validation - Invalid Format
expected: On the upload page, try to drag or browse a non-video file (e.g., a .txt or .png file). A red error message appears inline below the upload card saying the format is invalid. No upload request is sent to the server.
result: pass

### 4. Upload and Auto-Redirect
expected: Select or drag a valid MP4 video file onto the upload card. An indeterminate spinner appears during upload. After upload completes, the browser auto-redirects to /results/{id} where {id} is a UUID.
result: pass

### 5. Results Page Status Polling
expected: On the results page after upload, you see Job ID (UUID), filename, and a status that updates through processing stages. A spinning loader icon appears next to non-terminal statuses. Terminal state shows appropriate icon.
result: pass

### 6. FFmpeg Frame Extraction
expected: After a video finishes processing, /data/{uuid}/frames/ contains .jpg files (224x224 pixel JPEG frames extracted from the video). Original video file exists in /data/{uuid}/.
result: pass

### 7. FFmpeg Audio Extraction
expected: If video has audio, audio.wav exists in /data/{uuid}/. If no audio track, audio.wav is absent and status still reaches "queued" with audio_weight=0.0.
result: pass

### 8. Failed Upload - Server Validation
expected: Try uploading a file with an unsupported extension. The server returns a 400 error and the upload page shows an error message about invalid format.
result: pass

### 9. Results Page Error Display
expected: If a video fails during preprocessing (corrupted file or video under 1 second), the results page shows status "Processing failed" with a red alert icon and an error message.
result: pass

## Summary

total: 9
passed: 9
issues: 0
pending: 0
skipped: 0

## Gaps

[none]
