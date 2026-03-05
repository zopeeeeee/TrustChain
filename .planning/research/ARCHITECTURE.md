# Architecture Patterns

**Domain:** Multimodal Deepfake Detection with Blockchain Verification
**Project:** TrustChain-AV
**Researched:** 2026-03-05

## Recommended Architecture

A three-tier system with an async job queue bridging the gap between the fast HTTP layer and the slow ML inference layer:

```
                        +-------------------+
                        |   React Frontend  |
                        |  (Vite + shadcn)  |
                        +--------+----------+
                                 |  REST + Polling
                                 v
                        +-------------------+
                        |  FastAPI Gateway   |
                        |  (async, uvicorn) |
                        +--------+----------+
                                 |
              +------------------+------------------+
              |                  |                  |
              v                  v                  v
     +----------------+  +---------------+  +----------------+
     |  ML Worker      |  |  Blockchain   |  |  PostgreSQL    |
     |  (Background    |  |  Service      |  |  Database      |
     |   Task Queue)   |  |  (Web3.py)    |  |                |
     +-------+--------+  +-------+-------+  +----------------+
             |                    |
     +-------+--------+  +-------+-------+
     | PyTorch Models  |  | Sepolia RPC   |
     | ResNet-50       |  | + Pinata IPFS |
     | Wav2Vec2        |  +---------------+
     | Fusion Layer    |
     +----------------+
```

### Component Boundaries

| Component | Responsibility | Communicates With | Protocol |
|-----------|---------------|-------------------|----------|
| **React Frontend** | UI rendering, file upload, result display, polling | FastAPI Gateway | HTTP REST, multipart upload |
| **FastAPI Gateway** | Request validation, job orchestration, API routing, file storage | All backend components | Internal function calls, DB queries |
| **ML Worker** | Video preprocessing (FFmpeg), feature extraction (ResNet-50, Wav2Vec2), fusion inference | FastAPI (task queue), filesystem | In-process background tasks or Celery |
| **Blockchain Service** | Smart contract interaction, IPFS upload, transaction management | Sepolia RPC node, Pinata API, PostgreSQL | JSON-RPC (Web3.py), HTTP (Pinata) |
| **PostgreSQL** | Persistent storage for uploads, results, blockchain records | FastAPI Gateway | asyncpg / SQLAlchemy async |
| **Solidity Contract** | On-chain hash registration, verification lookups | Blockchain Service via Web3.py | Ethereum ABI calls |
| **IPFS (Pinata)** | Immutable metadata/report storage | Blockchain Service | HTTP REST API |

### Data Flow

**Detection Flow (Primary):**

```
1. User drops video file in Upload Dashboard
2. Frontend sends multipart POST to /api/upload
3. FastAPI validates file (format, size), saves to temp storage
4. FastAPI creates DB record (status: QUEUED), returns job_id
5. Frontend polls GET /api/jobs/{job_id} for status updates
6. ML Worker picks up job:
   a. FFmpeg extracts frames (1 fps or keyframes) + audio track
   b. ResNet-50 extracts visual features (2048-dim per frame)
   c. Wav2Vec2 extracts audio features (768-dim)
   d. Temporal pooling (mean/max) reduces frame-level to video-level
   e. Fusion layer concatenates [2048 + 768] -> MLP -> REAL/FAKE + confidence
   f. Updates DB record (status: COMPLETE, verdict, scores)
7. Frontend receives completed result, displays verdict
```

**Blockchain Registration Flow (Secondary, for REAL verdicts):**

```
1. User clicks "Register on Blockchain" for a REAL result
2. Frontend sends POST /api/register/{job_id}
3. FastAPI computes SHA-256 of original file
4. Blockchain Service uploads verification metadata to IPFS via Pinata
   -> Returns IPFS CID
5. Blockchain Service calls smart contract registerMedia(fileHash, ipfsCid)
   -> Signs transaction with server wallet
   -> Submits to Sepolia network
6. Waits for transaction confirmation (1-2 blocks)
7. Stores tx_hash, block_number, IPFS CID in PostgreSQL
8. Returns blockchain receipt to frontend
```

**Verification Flow (Tertiary):**

```
1. User uploads file or pastes SHA-256 hash on Verification Page
2. Frontend sends POST /api/verify with file or hash
3. FastAPI computes hash (if file), queries smart contract isRegistered(hash)
4. If found: returns registration timestamp, IPFS CID, original tx_hash
5. Frontend displays verification status with Etherscan link
```

## Component Deep Dives

### 1. FastAPI Gateway

**Structure:**
```
backend/
  app/
    main.py              # FastAPI app factory, CORS, lifespan
    config.py            # Settings via pydantic-settings
    api/
      routes/
        upload.py        # POST /api/upload, GET /api/jobs/{id}
        blockchain.py    # POST /api/register, POST /api/verify
        health.py        # GET /api/health
    models/
      database.py        # SQLAlchemy models (Upload, Result, BlockchainRecord)
      schemas.py         # Pydantic request/response schemas
    services/
      ml_worker.py       # ML inference orchestration
      blockchain.py      # Web3.py + Pinata integration
      preprocessing.py   # FFmpeg operations
    core/
      database.py        # Async engine, session factory
      dependencies.py    # FastAPI dependency injection
    ml/
      visual.py          # ResNet-50 feature extractor
      audio.py           # Wav2Vec2 feature extractor
      fusion.py          # Fusion layer (MLP or attention)
      models/            # Saved model weights (.pt files)
  Dockerfile
  requirements.txt
```

**Key design decisions:**
- Use `BackgroundTasks` for the prototype (simpler than Celery for a team of 4). Celery/Redis adds operational complexity that is unnecessary for a single-server academic prototype.
- Use `asyncpg` via SQLAlchemy async for non-blocking DB access.
- Load ML models once at startup via FastAPI `lifespan` context manager -- do NOT reload per-request.
- Store uploaded files on local disk (Docker volume), not in the DB.

### 2. ML Pipeline

**Architecture pattern: Pipeline with shared model registry**

```python
# Pseudocode for the inference pipeline
class DeepfakeDetector:
    def __init__(self):
        self.visual_extractor = ResNet50FeatureExtractor()   # frozen, 2048-dim
        self.audio_extractor = Wav2Vec2FeatureExtractor()    # frozen, 768-dim
        self.fusion = FusionMLP(input_dim=2816, hidden=512, output=2)

    def predict(self, video_path: str) -> dict:
        frames = extract_frames(video_path, fps=1)          # FFmpeg
        audio = extract_audio(video_path)                    # FFmpeg

        visual_features = self.visual_extractor(frames)      # [N, 2048]
        visual_pooled = temporal_pool(visual_features)       # [2048]

        if has_speech(audio):                                # WebRTC VAD
            audio_features = self.audio_extractor(audio)     # [768]
        else:
            audio_features = torch.zeros(768)                # fallback

        fused = torch.cat([visual_pooled, audio_features])   # [2816]
        logits = self.fusion(fused)                          # [2]
        verdict = "REAL" if logits.argmax() == 0 else "FAKE"
        confidence = torch.softmax(logits, dim=0).max().item()

        return {"verdict": verdict, "confidence": confidence}
```

**Critical design: Temporal pooling strategy.**
- Mean pooling across frames is the simplest and works well for uniform-length clips.
- Extract at 1 fps to keep inference under 30 seconds for a 5-minute video (300 frames through ResNet-50 is ~15s on GPU, ~45s on CPU with batching).
- For CPU-only inference (likely for prototype), batch frames in groups of 8-16 to manage memory.

### 3. Blockchain Service

**Smart Contract (Solidity):**
```solidity
// Simplified structure
contract MediaRegistry {
    struct MediaRecord {
        bytes32 fileHash;
        string ipfsCid;
        address registrar;
        uint256 timestamp;
        bool exists;
    }

    mapping(bytes32 => MediaRecord) public records;

    event MediaRegistered(bytes32 indexed fileHash, string ipfsCid, uint256 timestamp);

    function registerMedia(bytes32 _fileHash, string calldata _ipfsCid) external {
        require(!records[_fileHash].exists, "Already registered");
        records[_fileHash] = MediaRecord(_fileHash, _ipfsCid, msg.sender, block.timestamp, true);
        emit MediaRegistered(_fileHash, _ipfsCid, block.timestamp);
    }

    function verifyMedia(bytes32 _fileHash) external view returns (bool, string memory, uint256) {
        MediaRecord memory record = records[_fileHash];
        return (record.exists, record.ipfsCid, record.timestamp);
    }
}
```

**Web3.py integration pattern:**
- Use a dedicated server-side wallet (private key in env var, never in code).
- Hardhat for local development, deploy to Sepolia for integration testing.
- Transaction nonce management is critical -- use a mutex/lock to prevent nonce collisions if multiple registrations happen concurrently.

### 4. Frontend Architecture

**Structure:**
```
Frontend/
  src/
    pages/
      UploadPage.tsx        # Drag-drop upload, progress
      ResultsPage.tsx       # Verdict, confidence, modality breakdown
      BlockchainPage.tsx    # Registration status, tx details
      VerifyPage.tsx        # Re-upload or paste hash
      HistoryPage.tsx       # Paginated past analyses
    components/
      ui/                   # shadcn/ui primitives (existing)
      FileDropzone.tsx
      VerdictDisplay.tsx
      BlockchainReceipt.tsx
      ConfidenceGauge.tsx
    hooks/
      useJobPolling.ts      # Poll job status with exponential backoff
      useFileUpload.ts      # Upload with progress tracking
    lib/
      api.ts                # Axios/fetch wrapper for backend calls
      types.ts              # TypeScript interfaces
    App.tsx
    main.tsx
```

**Key patterns:**
- React Router for page navigation (5 pages).
- Polling over WebSocket for job status -- simpler, and job completion is not latency-sensitive (users expect 10-30s waits for video analysis).
- Use `XMLHttpRequest` or `axios` with `onUploadProgress` for upload progress bars.
- TanStack Query (React Query) for server state management -- handles polling, caching, and refetching cleanly.

### 5. Database Schema

```sql
-- Core tables
CREATE TABLE uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,        -- SHA-256
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'queued',   -- queued, processing, complete, failed
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE detection_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id UUID REFERENCES uploads(id),
    verdict VARCHAR(10) NOT NULL,          -- REAL or FAKE
    confidence FLOAT NOT NULL,
    visual_score FLOAT,
    audio_score FLOAT,
    has_audio BOOLEAN DEFAULT true,
    processing_time_ms INTEGER,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE blockchain_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id UUID REFERENCES uploads(id),
    file_hash VARCHAR(64) NOT NULL,
    tx_hash VARCHAR(66),                   -- 0x-prefixed
    block_number BIGINT,
    ipfs_cid VARCHAR(100),
    contract_address VARCHAR(42),
    network VARCHAR(20) DEFAULT 'sepolia',
    status VARCHAR(20) DEFAULT 'pending',  -- pending, confirmed, failed
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Patterns to Follow

### Pattern 1: Model Singleton with Lifespan
**What:** Load ML models once at application startup, share across all requests.
**When:** Always for inference services.
**Why:** ResNet-50 + Wav2Vec2 take 5-10 seconds to load. Loading per-request would make the API unusable.

```python
from contextlib import asynccontextmanager

detector = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global detector
    detector = DeepfakeDetector()  # loads models into memory
    yield
    del detector  # cleanup on shutdown

app = FastAPI(lifespan=lifespan)
```

### Pattern 2: Job Queue with Polling
**What:** Return job ID immediately, process in background, client polls for result.
**When:** Any operation taking more than 2-3 seconds (ML inference takes 10-30s).

```python
@router.post("/upload")
async def upload_video(file: UploadFile, background_tasks: BackgroundTasks, db: AsyncSession):
    # Validate, save file, create DB record
    upload = Upload(filename=file.filename, status="queued", ...)
    db.add(upload)
    await db.commit()
    # Queue processing
    background_tasks.add_task(process_video, upload.id)
    return {"job_id": str(upload.id), "status": "queued"}

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: UUID, db: AsyncSession):
    upload = await db.get(Upload, job_id)
    result = await db.execute(select(DetectionResult).where(...))
    return {"status": upload.status, "result": result.scalar_one_or_none()}
```

### Pattern 3: Service Layer Separation
**What:** Keep route handlers thin. Business logic lives in service classes.
**When:** Always. Routes validate input and return responses. Services do the work.

### Pattern 4: Docker Compose Multi-Service
**What:** Separate containers for frontend, backend, and database.

```yaml
# docker-compose.yml structure
services:
  frontend:
    build: ./Frontend
    ports: ["3000:80"]          # Nginx serves built React
    depends_on: [backend]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://...
      - SEPOLIA_RPC_URL=...
      - WALLET_PRIVATE_KEY=...
      - PINATA_API_KEY=...
    depends_on: [db]
    volumes:
      - uploads:/app/uploads    # Persistent upload storage

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=trustchain
      - POSTGRES_USER=...
      - POSTGRES_PASSWORD=...
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  uploads:
  pgdata:
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Synchronous ML Inference in Request Handler
**What:** Running the full inference pipeline inside an `async def` endpoint without offloading.
**Why bad:** Blocks the FastAPI event loop for 10-30 seconds. All other requests stall.
**Instead:** Use `BackgroundTasks` or `run_in_executor` for CPU-bound work. Return a job ID immediately.

### Anti-Pattern 2: Loading Models Per-Request
**What:** Calling `models.resnet50(weights=...)` inside every request handler.
**Why bad:** 5-10 second model load time on every request. The existing Flask code does exactly this.
**Instead:** Load once at startup (lifespan pattern above).

### Anti-Pattern 3: Storing Files in the Database
**What:** Saving video file bytes as BYTEA columns in PostgreSQL.
**Why bad:** 500MB files in the database cause backup/query performance nightmares.
**Instead:** Store files on disk (Docker volume), store only the path in the DB.

### Anti-Pattern 4: Hardcoding Blockchain Private Keys
**What:** Putting wallet private keys directly in source code.
**Why bad:** Leaked keys = drained wallet (even on testnet, bad practice for academic review).
**Instead:** Environment variables loaded via `pydantic-settings`, `.env` file in `.gitignore`.

### Anti-Pattern 5: Monolithic Preprocessing
**What:** One giant function that does FFmpeg extraction + feature extraction + fusion in sequence without checkpoints.
**Why bad:** If fusion fails, you redo all the expensive FFmpeg + feature extraction.
**Instead:** Pipeline stages with intermediate results. Save extracted features before fusion step.

## Scalability Considerations

| Concern | Prototype (1-5 users) | Demo Day (10-20 users) | Notes |
|---------|----------------------|------------------------|-------|
| ML Inference | BackgroundTasks, single worker | Same -- sequential processing acceptable | If needed, add a simple queue with max concurrency |
| File Storage | Local Docker volume | Same | Not a bottleneck at this scale |
| Database | Single PostgreSQL container | Same | More than sufficient |
| Blockchain | Direct Web3.py calls | Same -- Sepolia has no congestion | Nonce management matters even at low scale |
| Frontend | Vite dev server or Nginx | Nginx static serve | Build once, serve static files |

For an academic prototype, horizontal scaling is out of scope. The architecture should be clean and well-separated, but does not need Kubernetes, load balancers, or distributed task queues.

## Suggested Build Order (Dependency Graph)

Build order is driven by the dependency chain. Components at the bottom of the stack must exist before components above them can be integrated.

```
Phase 1: Foundation (no dependencies)
  |- PostgreSQL schema + Docker Compose
  |- FastAPI skeleton (health, config, DB connection)
  |- React app shell (routing, layout, pages)

Phase 2: Core Detection Pipeline (depends on Phase 1)
  |- FFmpeg preprocessing service
  |- ResNet-50 visual extractor (standalone, testable)
  |- Wav2Vec2 audio extractor (standalone, testable)
  |- Fusion layer (depends on both extractors)
  |- Upload endpoint + background job queue
  |- Job polling endpoint

Phase 3: Frontend Integration (depends on Phase 2 API)
  |- Upload Dashboard (drag-drop, progress)
  |- Results Display (verdict, confidence, breakdown)
  |- History Page (list past analyses)

Phase 4: Blockchain Layer (depends on Phase 1 DB, independent of ML)
  |- Solidity smart contract + Hardhat tests
  |- Deploy to Sepolia
  |- Web3.py service (register + verify)
  |- Pinata IPFS integration
  |- Blockchain API endpoints

Phase 5: Full Integration + Polish
  |- Connect blockchain UI to backend
  |- Verification page (re-upload flow)
  |- PDF report export
  |- End-to-end testing
  |- Docker production build
```

**Critical dependency:** The blockchain layer (Phase 4) can be developed in parallel with the ML pipeline (Phase 2-3) since they share only the database and file hash. This parallelism is important for a 4-person team.

**Riskiest component:** The ML pipeline (Phase 2) has the most unknowns -- FFmpeg edge cases, model memory usage on CPU, inference time budget. Build and test this before committing to the full integration.

## Sources

- Architecture patterns derived from established FastAPI + ML inference patterns (FastAPI documentation, PyTorch serving best practices)
- Blockchain integration patterns from Web3.py documentation and Hardhat development workflows
- Confidence: MEDIUM -- based on training data for mature, well-documented technologies. No live verification available due to WebSearch unavailability.
- Existing codebase (`app.py`) informed anti-pattern identification (model loading per-request, synchronous inference)
