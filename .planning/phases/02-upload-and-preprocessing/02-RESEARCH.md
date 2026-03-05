# Phase 02: Upload and Preprocessing - Research

**Researched:** 2026-03-06
**Domain:** Video file upload, FFmpeg preprocessing, async background tasks
**Confidence:** HIGH

## Summary

This phase adds video file upload (drag-and-drop or file picker), server-side validation, and FFmpeg-based preprocessing (frame extraction at 224x224, audio extraction at 16kHz mono WAV). The existing FastAPI backend already has the Upload model with status tracking, async SQLAlchemy sessions, and an empty services package ready for the preprocessing service. The frontend has shell pages for Upload and Results.

The core technical challenges are: (1) handling up to 500MB file uploads efficiently via FastAPI's UploadFile with streaming to disk, (2) running FFmpeg as an async subprocess for frame/audio extraction without blocking the event loop, and (3) managing multi-stage status updates so the frontend can poll progress. The user has decided on `asyncio.create_task` for background processing (no Celery/Redis) and an indeterminate spinner UI (no progress percentage).

**Primary recommendation:** Use FastAPI UploadFile with `shutil.copyfileobj` for streaming to disk, `asyncio.create_subprocess_exec` for non-blocking FFmpeg calls, and native HTML5 drag-and-drop (no external library) for the compact upload card.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Compact card with browse button (not full-page dropzone) -- cleaner form-like feel
- Indeterminate spinner during upload (no percentage progress bar)
- Auto-redirect to /results/:id after upload completes -- user sees processing status there
- Support multiple file queue -- accept multiple files, process sequentially, show queue
- Client-side validation first (extension + size check), server re-validates on receipt
- Use asyncio.create_task for background FFmpeg jobs -- no Celery/Redis
- FFmpeg installed inside the backend Docker container (apt-get install ffmpeg in Dockerfile)
- Detailed multi-stage status updates: Uploading -> Extracting frames -> Extracting audio -> Queued for analysis
- Status stored in Upload model's status field, updated at each processing stage
- Clean up extracted frames and audio after analysis completes -- keep only original video and results in DB
- Preserve original filename inside job directory: /data/{job_id}/{original_filename}
- Inline error below the upload card for validation failures (wrong format, too large) -- red text, no upload attempt
- No audio track -> continue with visual-only analysis, set audio_weight=0.0, show note in results
- FFmpeg failure (corrupted file) -> status changes to "failed" with user-friendly message on results page
- Videos under 1 second -> reject with clear message during preprocessing

### Claude's Discretion
- Polling mechanism (simple polling vs WebSocket) for frontend status tracking
- Exact storage directory structure and Docker volume configuration
- Frame extraction interval tuning (default every 10th frame per PREP-01)
- SHA-256 hashing timing (during upload or during preprocessing)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| UPLD-01 | User can upload video via drag-and-drop or file picker | Native HTML5 drag-and-drop + input[type=file], compact card UI pattern |
| UPLD-02 | System validates file format (MP4, AVI, MOV, MKV) and size (max 500MB) | Client-side extension+size check, server-side Content-Type + magic bytes + size validation |
| UPLD-03 | Upload returns job ID immediately; frontend polls for completion | POST /api/uploads returns UUID, GET /api/uploads/:id/status for polling |
| PREP-01 | FFmpeg extracts frames at configurable interval (default every 10th frame), resizes to 224x224, normalizes to ImageNet mean/std | FFmpeg select filter + scale filter via asyncio.create_subprocess_exec, normalization done in NumPy post-extraction |
| PREP-02 | FFmpeg extracts audio track, resamples to 16kHz mono WAV | FFmpeg -ar 16000 -ac 1 output.wav via asyncio.create_subprocess_exec |
| PREP-03 | System handles edge cases: no audio track, video < 1s, corrupted file | FFprobe duration check, FFmpeg error code handling, audio stream detection |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | (existing) | File upload endpoint with UploadFile | Already in project, native async file handling |
| python-multipart | latest | Required by FastAPI for multipart/form-data file uploads | Mandatory dependency for UploadFile |
| FFmpeg | system package | Frame extraction, audio extraction, video probing | Industry standard for A/V processing, installed via apt-get |
| asyncio (stdlib) | Python 3.11 | create_subprocess_exec for non-blocking FFmpeg, create_task for background jobs | User decision: no Celery/Redis |
| aiofiles | latest | Async file I/O for writing uploaded files to disk | Avoids blocking event loop during disk writes |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| NumPy | latest | ImageNet normalization of extracted frames (mean/std) | PREP-01: post-FFmpeg frame normalization |
| Pillow | latest | Load extracted frame PNGs into arrays for normalization | PREP-01: image loading before NumPy normalization |
| hashlib (stdlib) | Python 3.11 | SHA-256 hashing of uploaded video files | DETC-06 preparation (compute during preprocessing) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| asyncio.create_subprocess_exec | ffmpeg-python / python-ffmpeg bindings | Bindings add dependency for simple CLI calls; raw subprocess is simpler and more debuggable |
| aiofiles | shutil.copyfileobj (sync) | shutil is simpler but blocks event loop for large files; aiofiles preferred for 500MB uploads |
| react-dropzone | Native HTML5 drag-and-drop | User wants compact card, not full dropzone; native API is sufficient and avoids dependency |

**Installation (backend):**
```bash
# Add to requirements.txt
python-multipart
aiofiles
numpy
Pillow
```

**Dockerfile addition:**
```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev ffmpeg && \
    rm -rf /var/lib/apt/lists/*
```

## Architecture Patterns

### Recommended Project Structure
```
backend/app/
├── api/
│   ├── router.py          # Add uploads router
│   └── uploads.py         # POST /api/uploads, GET /api/uploads/:id/status
├── schemas/
│   └── upload.py          # Pydantic request/response schemas
├── services/
│   └── preprocessing.py   # FFmpeg frame/audio extraction, background task orchestrator
├── models/
│   └── upload.py          # Existing Upload model (add error_message column)
└── config.py              # Add upload settings (max size, allowed formats, data dir)

frontend/src/
├── pages/
│   ├── UploadPage.tsx     # Upload card with drag-drop, queue, validation
│   └── ResultsPage.tsx    # Add status polling display
├── components/
│   └── UploadCard.tsx     # Compact upload card component
└── lib/
    └── api.ts             # Upload and status polling API client functions
```

### Pattern 1: Streaming Upload to Disk
**What:** Stream large files directly to disk without loading into memory
**When to use:** Always for video uploads (up to 500MB)
**Example:**
```python
# Source: FastAPI official docs + aiofiles pattern
import aiofiles
import uuid
from pathlib import Path
from fastapi import UploadFile

UPLOAD_DIR = Path("/data")

async def save_upload(file: UploadFile, job_id: uuid.UUID) -> Path:
    job_dir = UPLOAD_DIR / str(job_id)
    job_dir.mkdir(parents=True, exist_ok=True)
    file_path = job_dir / file.filename

    async with aiofiles.open(file_path, "wb") as out:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            await out.write(chunk)

    return file_path
```

### Pattern 2: Async FFmpeg Subprocess
**What:** Run FFmpeg as a non-blocking subprocess using asyncio
**When to use:** All frame extraction and audio extraction operations
**Example:**
```python
import asyncio

async def extract_frames(
    video_path: str,
    output_dir: str,
    frame_interval: int = 10,
    size: str = "224:224",
) -> list[str]:
    """Extract every Nth frame, resize to 224x224."""
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"select=not(mod(n\\,{frame_interval})),scale={size}",
        "-vsync", "vfr",
        "-q:v", "2",
        f"{output_dir}/frame_%04d.jpg",
        "-y",
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg frame extraction failed: {stderr.decode()}")
    # Return list of extracted frame paths
    ...

async def extract_audio(video_path: str, output_path: str) -> bool:
    """Extract audio as 16kHz mono WAV. Returns False if no audio stream."""
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn",              # no video
        "-acodec", "pcm_s16le",
        "-ar", "16000",     # 16kHz
        "-ac", "1",         # mono
        output_path,
        "-y",
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        stderr_text = stderr.decode()
        if "does not contain any stream" in stderr_text or "no audio" in stderr_text.lower():
            return False  # No audio track -- graceful handling
        raise RuntimeError(f"FFmpeg audio extraction failed: {stderr_text}")
    return True
```

### Pattern 3: Background Task with Status Updates
**What:** Use asyncio.create_task to run preprocessing in background, updating DB status at each stage
**When to use:** After upload is saved to disk, before returning job ID to client
**Example:**
```python
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

async def process_video(job_id: uuid.UUID, file_path: str):
    """Background task: extract frames, extract audio, update status."""
    async with async_session() as db:
        try:
            # Stage 1: Extract frames
            await update_status(db, job_id, "extracting_frames")
            frames = await extract_frames(file_path, frames_dir)

            # Stage 2: Extract audio
            await update_status(db, job_id, "extracting_audio")
            has_audio = await extract_audio(file_path, audio_path)
            if not has_audio:
                await update_field(db, job_id, audio_weight=0.0)

            # Stage 3: Ready for analysis
            await update_status(db, job_id, "queued")
        except Exception as e:
            await update_status(db, job_id, "failed", error_message=str(e))

# In the upload endpoint:
# asyncio.create_task(process_video(job_id, file_path))
```

### Pattern 4: FFprobe for Validation
**What:** Use FFprobe to check video metadata before processing
**When to use:** After upload, before frame extraction -- check duration, codec validity
**Example:**
```python
import json

async def probe_video(video_path: str) -> dict:
    """Get video metadata using ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        video_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError("Invalid or corrupted video file")
    return json.loads(stdout.decode())

async def validate_video(video_path: str) -> tuple[bool, str]:
    """Check duration >= 1s, valid streams."""
    try:
        info = await probe_video(video_path)
        duration = float(info["format"]["duration"])
        if duration < 1.0:
            return False, "Video must be at least 1 second long"
        return True, ""
    except (RuntimeError, KeyError, ValueError):
        return False, "File appears to be corrupted or not a valid video"
```

### Pattern 5: Frontend Polling
**What:** Simple setInterval polling for job status
**When to use:** After redirect to /results/:id page
**Recommendation:** Use simple polling (not WebSocket) -- simpler to implement, sufficient for this use case where updates happen every few seconds.
```typescript
// Polling interval: 2 seconds during active processing, stop when terminal state
const POLL_INTERVAL = 2000;
const TERMINAL_STATES = ["queued", "completed", "failed"];

function useJobStatus(jobId: string) {
  const [status, setStatus] = useState<JobStatus | null>(null);

  useEffect(() => {
    const poll = async () => {
      const res = await fetch(`/api/uploads/${jobId}/status`);
      const data = await res.json();
      setStatus(data);
      if (TERMINAL_STATES.includes(data.status)) {
        clearInterval(intervalId);
      }
    };
    const intervalId = setInterval(poll, POLL_INTERVAL);
    poll(); // immediate first call
    return () => clearInterval(intervalId);
  }, [jobId]);

  return status;
}
```

### Anti-Patterns to Avoid
- **Reading entire file into memory:** Never use `await file.read()` without chunking for large files -- will OOM on 500MB uploads
- **Blocking FFmpeg calls:** Never use `subprocess.run()` in async code -- blocks the entire event loop
- **Status updates without new DB session:** Background tasks need their own DB session (not the request's session which is closed)
- **Missing error handling in background tasks:** Unhandled exceptions in `create_task` are silently swallowed -- always wrap in try/except
- **Trusting Content-Length header alone:** Client can lie; always validate actual file size during/after streaming

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Video metadata extraction | Custom frame-counting logic | FFprobe JSON output | Handles all container formats, codec edge cases |
| Frame extraction + resize | OpenCV frame-by-frame loop | FFmpeg select + scale filters | FFmpeg is orders of magnitude faster, handles all codecs |
| Audio resampling | scipy/librosa resampling | FFmpeg -ar -ac flags | FFmpeg handles codec conversion + resampling in one pass |
| File type validation (server) | Extension check only | FFprobe probe (magic bytes) | Extensions can be renamed; FFprobe validates actual container |
| Multipart form parsing | Manual multipart parsing | python-multipart via FastAPI UploadFile | Battle-tested, handles edge cases in multipart spec |

**Key insight:** FFmpeg/FFprobe handle the heavy lifting for all A/V operations. Python code only orchestrates the subprocess calls and handles the results. Do not use OpenCV or other Python-native video libraries for extraction -- FFmpeg is faster and more reliable.

## Common Pitfalls

### Pitfall 1: Background Task Loses Database Session
**What goes wrong:** The upload endpoint's DB session closes after response is sent, but background task tries to use it for status updates
**Why it happens:** FastAPI's Depends(get_db) scopes session to request lifecycle
**How to avoid:** Create a NEW async_session() inside the background task function
**Warning signs:** "Session is closed" errors in logs after upload returns

### Pitfall 2: FFmpeg Select Filter Escaping
**What goes wrong:** The `select='not(mod(n,10))'` filter expression fails due to shell/subprocess escaping
**Why it happens:** Commas and parentheses have special meaning in shell and FFmpeg filter syntax
**How to avoid:** Use `create_subprocess_exec` (not `shell=True`), escape the backslash in the mod expression: `not(mod(n\\,10))`
**Warning signs:** "Invalid filter expression" errors from FFmpeg

### Pitfall 3: Docker Volume for /data Not Mounted
**What goes wrong:** Uploaded files disappear on container restart, or /data directory not writable
**Why it happens:** No volume mount for the data directory in docker-compose.yml
**How to avoid:** Add a named volume or bind mount for /data in docker-compose.yml backend service
**Warning signs:** FileNotFoundError on second request, or Permission denied errors

### Pitfall 4: No Audio Stream Detection
**What goes wrong:** FFmpeg returns non-zero exit code for videos without audio, treated as "corrupted"
**Why it happens:** Not distinguishing between "no audio stream" and "actual error" in FFmpeg stderr
**How to avoid:** Check FFprobe streams for audio type first, OR parse FFmpeg stderr for "does not contain any stream" message
**Warning signs:** Videos without audio being marked as "failed" instead of proceeding with visual-only

### Pitfall 5: Large File Upload Timeout
**What goes wrong:** 500MB upload on slow connection times out before completing
**Why it happens:** Default uvicorn/nginx/proxy timeouts are too short for large uploads
**How to avoid:** Increase uvicorn timeout settings; since this is Docker dev, default uvicorn has no request timeout, but ensure no reverse proxy with short timeouts is in front
**Warning signs:** Connection reset errors during large uploads

### Pitfall 6: ImageNet Normalization Off-by-One
**What goes wrong:** Frames normalized incorrectly, causing garbage ML predictions in Phase 3
**Why it happens:** Using 0-255 pixel values instead of 0-1 before applying ImageNet mean/std, or wrong mean/std values
**How to avoid:** Convert to float32, divide by 255.0, then subtract mean=[0.485, 0.456, 0.406] and divide by std=[0.229, 0.224, 0.225]
**Warning signs:** Model outputs near-random predictions (caught in Phase 3 but caused here)

### Pitfall 7: Race Condition on Multiple File Queue
**What goes wrong:** Multiple create_task calls for queued files run concurrently, overloading CPU
**Why it happens:** asyncio.create_task fires immediately, not sequentially
**How to avoid:** Use an asyncio.Queue or process files in a sequential loop within a single background task
**Warning signs:** CPU spike, FFmpeg processes competing for resources

## Code Examples

### Upload Endpoint (Complete Pattern)
```python
# Source: FastAPI docs + project patterns
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

@router.post("/")
async def upload_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    # Validate Content-Length header (early rejection)
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large. Maximum: 500MB")

    # Create DB record
    upload = Upload(filename=file.filename, status="uploading")
    db.add(upload)
    await db.commit()
    await db.refresh(upload)

    # Save file to disk (streaming)
    file_path = await save_upload(file, upload.id)

    # Verify actual size on disk
    actual_size = file_path.stat().st_size
    if actual_size > MAX_FILE_SIZE:
        file_path.unlink()
        await update_status(db, upload.id, "failed", error_message="File too large")
        raise HTTPException(400, "File too large. Maximum: 500MB")

    # Update record with file path
    upload.file_path = str(file_path)
    await db.commit()

    # Start background processing
    asyncio.create_task(process_video(upload.id, str(file_path)))

    return {"id": str(upload.id), "status": "uploading"}
```

### Status Endpoint
```python
@router.get("/{upload_id}/status")
async def get_upload_status(
    upload_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    upload = await db.get(Upload, upload_id)
    if not upload:
        raise HTTPException(404, "Upload not found")
    return {
        "id": str(upload.id),
        "filename": upload.filename,
        "status": upload.status,
        "error_message": getattr(upload, "error_message", None),
        "created_at": upload.created_at.isoformat(),
    }
```

### Upload Card Component (React)
```typescript
// Compact card with browse button + drag-drop support
interface UploadCardProps {
  onUpload: (files: FileList) => void;
  error: string | null;
  isUploading: boolean;
}

function UploadCard({ onUpload, error, isUploading }: UploadCardProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files.length) onUpload(e.dataTransfer.files);
  };

  const ALLOWED = [".mp4", ".avi", ".mov", ".mkv"];
  const MAX_SIZE = 500 * 1024 * 1024;

  const validate = (files: FileList): string | null => {
    for (const f of Array.from(files)) {
      const ext = f.name.substring(f.name.lastIndexOf(".")).toLowerCase();
      if (!ALLOWED.includes(ext)) return `Unsupported format: ${ext}`;
      if (f.size > MAX_SIZE) return `File too large: ${f.name} (max 500MB)`;
    }
    return null;
  };

  // ... render compact card with border, icon, browse button
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| OpenCV VideoCapture for frame extraction | FFmpeg subprocess | Long-standing | 10x faster, better codec support |
| Celery + Redis for background tasks | asyncio.create_task (for prototypes) | Appropriate for single-worker prototypes | No extra infrastructure needed |
| Base64 encoding file uploads | Multipart form-data with UploadFile | Long-standing | Proper streaming, no memory bloat |
| Synchronous subprocess.run | asyncio.create_subprocess_exec | Python 3.5+ | Non-blocking FFmpeg execution |

**Deprecated/outdated:**
- `@app.on_event("startup")` -- project already uses lifespan (correct)
- `subprocess.run` in async contexts -- use `asyncio.create_subprocess_exec`

## Open Questions

1. **Frame normalization storage format**
   - What we know: PREP-01 requires ImageNet mean/std normalization on 224x224 frames
   - What's unclear: Store normalized frames as .npy arrays or keep as JPEGs and normalize at inference time?
   - Recommendation: Store as JPEGs, normalize at inference time in Phase 3. This simplifies storage and cleanup, and normalization is fast via NumPy. The preprocessing service just needs to extract and resize frames.

2. **SHA-256 hashing timing (Claude's Discretion)**
   - What we know: DETC-06 requires SHA-256 hash of uploaded video
   - What's unclear: Compute during upload (streaming) or during preprocessing?
   - Recommendation: Compute during the file save loop (read chunks, hash chunks, write chunks). This avoids reading the file twice and is negligible overhead. Store hash in Upload.file_hash immediately after save.

3. **Polling vs WebSocket (Claude's Discretion)**
   - What we know: Frontend needs to track multi-stage status updates
   - Recommendation: **Simple polling at 2-second intervals.** WebSocket is overkill for this use case where status changes every few seconds during preprocessing. Polling is simpler to implement, works through proxies, and requires no additional server infrastructure. Stop polling when status reaches a terminal state (queued, completed, failed).

4. **Storage directory structure (Claude's Discretion)**
   - Recommendation: Job-based structure: `/data/{job_id}/{original_filename}` for the video, `/data/{job_id}/frames/` for extracted frames, `/data/{job_id}/audio.wav` for audio. Docker volume mount: `upload_data:/data` in docker-compose.yml.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio (already installed) |
| Config file | None explicit -- uses default pytest discovery |
| Quick run command | `docker compose exec backend pytest tests/ -x -q` |
| Full suite command | `docker compose exec backend pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| UPLD-01 | POST /api/uploads accepts multipart file | integration | `pytest tests/test_uploads.py::test_upload_video -x` | No -- Wave 0 |
| UPLD-02 | Rejects invalid format and oversized files | unit | `pytest tests/test_uploads.py::test_upload_validation -x` | No -- Wave 0 |
| UPLD-03 | Returns job ID immediately, status endpoint works | integration | `pytest tests/test_uploads.py::test_upload_returns_job_id -x` | No -- Wave 0 |
| PREP-01 | Frame extraction produces 224x224 JPEGs | unit | `pytest tests/test_preprocessing.py::test_extract_frames -x` | No -- Wave 0 |
| PREP-02 | Audio extraction produces 16kHz mono WAV | unit | `pytest tests/test_preprocessing.py::test_extract_audio -x` | No -- Wave 0 |
| PREP-03 | Handles no audio, short video, corrupted file | unit | `pytest tests/test_preprocessing.py::test_edge_cases -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `docker compose exec backend pytest tests/ -x -q`
- **Per wave merge:** `docker compose exec backend pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_uploads.py` -- covers UPLD-01, UPLD-02, UPLD-03
- [ ] `tests/test_preprocessing.py` -- covers PREP-01, PREP-02, PREP-03
- [ ] Small test video fixture (< 1MB, valid MP4 with audio) for integration tests
- [ ] FFmpeg must be available in test environment (or tests mock subprocess calls)

## Sources

### Primary (HIGH confidence)
- FastAPI official docs: Request Files, UploadFile -- file upload patterns, python-multipart requirement
- FFmpeg official documentation -- select filter, scale filter, audio extraction flags
- Python 3.11 asyncio docs -- create_subprocess_exec, create_task APIs
- Existing project codebase -- Upload model, database patterns, API router structure

### Secondary (MEDIUM confidence)
- [FastAPI file upload discussion #8167](https://github.com/fastapi/fastapi/discussions/8167) -- size limit strategies
- [BetterStack FastAPI uploads guide](https://betterstack.com/community/guides/scaling-python/uploading-files-using-fastapi/) -- streaming patterns
- [asyncio-subprocess-ffmpeg examples](https://github.com/scivision/asyncio-subprocess-ffmpeg) -- async FFmpeg patterns

### Tertiary (LOW confidence)
- None -- all findings verified with official sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- FastAPI UploadFile, FFmpeg, asyncio are well-documented, stable APIs
- Architecture: HIGH -- patterns follow existing project conventions (async SQLAlchemy, lifespan, API router)
- Pitfalls: HIGH -- common issues well-documented in FastAPI discussions and FFmpeg guides
- Validation: MEDIUM -- test structure follows project patterns but FFmpeg tests may need mock strategy

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable technologies, 30-day window)
