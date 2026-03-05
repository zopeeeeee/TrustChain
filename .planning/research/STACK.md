# Technology Stack

**Project:** TrustChain-AV (Blockchain-Enhanced Audiovisual Deepfake Detection)
**Researched:** 2026-03-05
**Overall Confidence:** MEDIUM (web verification tools unavailable; versions based on training data through May 2025 -- verify with `pip install --dry-run` and `npm info` before locking)

---

## Recommended Stack

### Backend Framework

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| FastAPI | >=0.115 | REST API server | Async-native, built-in OpenAPI docs, Pydantic v2 validation, BackgroundTasks for ML jobs. PRD-mandated. Replaces Flask which lacks native async. | HIGH |
| Uvicorn | >=0.32 | ASGI server | Standard production server for FastAPI. Use `--workers 2` behind Docker. | HIGH |
| Pydantic | v2 (bundled with FastAPI) | Request/response validation | v2 is 5-17x faster than v1. FastAPI 0.100+ requires it. Validate upload metadata, detection results, blockchain records. | HIGH |

**Why FastAPI over Flask:** Flask requires `flask[async]` and Celery for background ML jobs. FastAPI has native `BackgroundTasks`, dependency injection, and automatic API docs. For a team of 4 with mixed experience, the auto-generated Swagger UI alone saves hours of debugging API contracts.

### ML / AI Pipeline

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| PyTorch | >=2.4 | Deep learning framework | Industry standard for research. TorchScript export, CUDA support, stable frozen backbone inference. Existing team familiarity (current codebase uses 2.0.1). | HIGH |
| torchvision | >=0.19 | ResNet-50 pretrained model | `torchvision.models.resnet50(weights=ResNet50_Weights.DEFAULT)` -- frozen backbone outputs 2048-dim features. Ships with PyTorch. | HIGH |
| HuggingFace Transformers | >=4.46 | Wav2Vec2 audio model | `Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")` -- frozen backbone outputs 768-dim features. De facto standard for pretrained audio models. | HIGH |
| torchaudio | >=2.4 | Audio loading/resampling | Pairs with PyTorch. `torchaudio.load()` + `torchaudio.transforms.Resample(orig_sr, 16000)` for Wav2Vec2's required 16kHz input. | HIGH |
| OpenCV (opencv-python-headless) | >=4.10 | Frame extraction from video | Use `headless` variant (no GUI deps) for Docker. Frame sampling, face detection preprocessing. | HIGH |
| FFmpeg (system) | >=6.0 | Video/audio demuxing | Extract audio track from video, extract frames at target FPS. Install as system dependency in Docker, call via `subprocess`. | HIGH |
| webrtcvad | >=2.0.10 | Voice Activity Detection | Lightweight C extension. Detects speech segments to decide audio vs visual-only analysis. Fallback: if no speech detected, use visual-only classification. | MEDIUM |
| NumPy | >=1.26 | Tensor/array operations | Universal dependency. Pin to >=1.26 for NumPy 2.x compatibility with PyTorch. | HIGH |
| Pillow | >=10.4 | Image preprocessing | Frame resizing, normalization before ResNet-50 input. | HIGH |

**Why NOT ONNX Runtime:** For an academic prototype with inference under 30s for 5-min video, PyTorch eager mode is sufficient. ONNX adds export complexity without meaningful benefit at this scale. If inference becomes a bottleneck, export later.

**Why NOT TensorFlow:** PRD specifies PyTorch. Team has existing PyTorch experience. HuggingFace Transformers works best with PyTorch for Wav2Vec2.

### Database

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| PostgreSQL | 16 | Primary database | JSONB for detection result metadata, concurrent access for team dev, production-grade. PRD-mandated. | HIGH |
| SQLAlchemy | >=2.0 | ORM | Async support via `create_async_engine`. Type-safe query building. v2.0 has cleaner API than v1.x. | HIGH |
| asyncpg | >=0.29 | Async PostgreSQL driver | Required for SQLAlchemy async with PostgreSQL. 3x faster than psycopg2 for async workloads. | HIGH |
| Alembic | >=1.13 | Database migrations | Standard for SQLAlchemy. Auto-generates migration scripts from model changes. Essential for team collaboration. | HIGH |

**Why NOT SQLite:** PRD requires PostgreSQL. SQLite cannot handle concurrent writes from multiple Docker containers. PostgreSQL's JSONB is valuable for storing variable-length detection metadata.

**Why NOT Prisma/Drizzle:** Backend is Python, not Node.js. SQLAlchemy is the Python ecosystem standard.

### Blockchain

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Solidity | ^0.8.24 | Smart contract language | Latest 0.8.x has custom errors, user-defined value types. Use `pragma solidity ^0.8.24;`. | MEDIUM |
| Hardhat | >=2.22 | Smart contract dev environment | Compiles, tests, deploys Solidity. Built-in local testnet. Better TypeScript support than Truffle (which is deprecated). | HIGH |
| @nomicfoundation/hardhat-toolbox | latest | Hardhat plugin bundle | Bundles ethers.js, chai matchers, gas reporter, coverage. One install covers all testing needs. | HIGH |
| ethers.js | v6 (via Hardhat) | Contract interaction (JS side) | Used by Hardhat for deployment scripts and tests. Do NOT install separately -- comes with hardhat-toolbox. | HIGH |
| Web3.py | >=7.0 | Blockchain interaction (Python side) | Python-native Ethereum interaction from FastAPI backend. v7 has breaking changes from v6 -- use `w3.eth.send_transaction()` not `sendTransaction()`. PRD-mandated. | MEDIUM |
| Pinata SDK / HTTP API | REST API | IPFS pinning | Free tier: 500 uploads, 1GB storage. Use direct HTTP calls (`httpx`) to Pinata API v2 rather than the unmaintained Python SDK. | MEDIUM |

**Why Web3.py over ethers in Python:** PRD mandates Web3.py. It's the standard Python Ethereum library. Using ethers would require a Node.js sidecar, adding unnecessary complexity.

**Why Pinata over running IPFS node:** Running an IPFS node in Docker is resource-heavy and unreliable for pinning. Pinata's free tier is sufficient for a prototype and guarantees content persistence.

**Why NOT Foundry/Forge:** Foundry is excellent but uses Solidity for tests. For a team learning blockchain, Hardhat's JavaScript/TypeScript tests are more approachable. Hardhat has larger community resources for troubleshooting.

### Frontend

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| React | ^18.3 | UI framework | Already in use in existing codebase. Keep v18 -- React 19 has migration friction and is unnecessary for this project. | HIGH |
| Vite | ^6.3 | Build tool + dev server | Already configured. Fast HMR, SWC transform via plugin-react-swc. | HIGH |
| TailwindCSS | v4 (or keep v3 if already configured) | Utility CSS | PRD-mandated. Check if v4 is configured; if not, v3.4+ is fine. | MEDIUM |
| shadcn/ui | latest | Component library | Already installed (Radix primitives in package.json). Provides Dialog, Progress, Tabs, etc. | HIGH |
| React Router | ^7.0 | Client-side routing | Need routes for Upload, Results, Verification, History pages. v7 is the current major. If not already installed, add it. | MEDIUM |
| Axios or native fetch | -- | HTTP client | For API calls to FastAPI backend. `fetch` is sufficient; Axios adds request interceptors if needed for error handling. Prefer fetch to minimize deps. | HIGH |
| react-dropzone | ^14.3 | File upload drag-and-drop | Standard for drag-and-drop file upload UX. Handles file type/size validation client-side. | HIGH |
| TanStack Query (React Query) | ^5.0 | Server state management | Manages API call state (loading, error, cache). Handles polling for async job status. Far better than manual `useEffect` + `useState`. | HIGH |

**Why NOT Next.js:** This is a single-page app with a separate FastAPI backend. Next.js adds SSR complexity that provides zero value. Vite + React is simpler and already set up.

**Why TanStack Query:** The detection pipeline is async (submit job, poll for results). TanStack Query's `useQuery` with `refetchInterval` handles this cleanly. Without it, you'll write brittle polling logic in every component.

### Infrastructure

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Docker | >=24 | Containerization | PRD-mandated. Consistent env across team of 4. Isolates Python ML deps from Node.js blockchain deps. | HIGH |
| Docker Compose | v2 | Multi-container orchestration | Defines backend, frontend, postgres, hardhat-node as services. Single `docker compose up` for full stack. | HIGH |
| python-multipart | >=0.0.9 | File upload parsing | Required by FastAPI for `UploadFile` parameter. Often forgotten -- install explicitly. | HIGH |
| httpx | >=0.27 | Async HTTP client | For calling Pinata API from FastAPI. Async-native, better than `requests` for FastAPI. | HIGH |
| python-dotenv | >=1.0 | Environment config | Load `.env` files for Pinata API key, Sepolia RPC URL, contract address. | HIGH |
| pytest | >=8.0 | Python testing | Backend unit/integration tests. Use `pytest-asyncio` for async endpoint tests. | HIGH |
| pytest-asyncio | >=0.24 | Async test support | Required for testing FastAPI async endpoints and SQLAlchemy async sessions. | HIGH |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| celery + redis | >=5.4 / >=5.0 | Background task queue | ONLY if `BackgroundTasks` proves insufficient (>30s inference blocking API). Start without it. |
| jinja2 + weasyprint | >=3.1 / >=62 | PDF report generation | For verification report export feature. Add when implementing PDF export. |
| python-jose | >=3.3 | JWT tokens | ONLY if authentication is added later (currently out of scope). |
| loguru | >=0.7 | Structured logging | Better than stdlib logging. Add from the start for debugging ML pipeline. |

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not Alternative |
|----------|-------------|-------------|---------------------|
| Backend | FastAPI | Flask | No native async, needs Celery for background ML jobs, no auto API docs |
| Backend | FastAPI | Django | Overkill ORM/admin for an API-only backend, slower for ML microservice pattern |
| ML Framework | PyTorch | TensorFlow | PRD specifies PyTorch; Wav2Vec2 via HuggingFace works best with PyTorch |
| ML Runtime | PyTorch eager | ONNX Runtime | Premature optimization for prototype; adds export complexity |
| Audio Model | Wav2Vec2 (facebook/wav2vec2-base-960h) | Whisper | Whisper is for transcription, not feature extraction. Wav2Vec2 outputs embeddings directly. |
| Database | PostgreSQL + SQLAlchemy | MongoDB | Relational schema fits (uploads, results, blockchain_records have clear relationships) |
| Database Driver | asyncpg | psycopg2 | psycopg2 is synchronous; asyncpg required for FastAPI async patterns |
| Blockchain Dev | Hardhat | Foundry | Foundry uses Solidity tests (harder for beginners); Hardhat has larger JS ecosystem |
| Blockchain Dev | Hardhat | Truffle | Truffle is deprecated/unmaintained as of 2023 |
| Smart Contract | Solidity | Vyper | Smaller ecosystem, fewer learning resources, team unfamiliar |
| IPFS | Pinata API | Infura IPFS | Infura IPFS was sunset in late 2023. Pinata free tier is active and sufficient. |
| IPFS | Pinata HTTP API | pinata-python SDK | SDK is community-maintained, often outdated. Direct HTTP via httpx is more reliable. |
| Frontend | React 18 | React 19 | Migration friction, no meaningful benefit for this app, existing codebase is React 18 |
| Frontend | Vite | Create React App | CRA is deprecated. Vite already configured in project. |
| CSS | TailwindCSS | CSS Modules | PRD mandates Tailwind. shadcn/ui requires it. |
| Task Queue | BackgroundTasks (start) | Celery | Celery adds Redis dependency and operational complexity. Start simple, upgrade only if needed. |

---

## Architecture-Critical Version Notes

### Web3.py v7 Breaking Changes
Web3.py v7 (released mid-2025) has significant API changes from v6:
- `w3.eth.get_transaction_count()` replaces `getTransactionCount()`
- Middleware system overhauled
- `w3.middleware_onion` replaced
- **Recommendation:** Pin `web3>=7.0,<8.0` and follow v7 migration guide
- **Confidence:** MEDIUM -- verify exact v7 API surface before implementation

### PyTorch 2.4+ Compile Mode
PyTorch 2.4+ supports `torch.compile()` for inference speedup:
- Can provide 1.5-2x speedup on ResNet-50 inference
- **Recommendation:** Implement without `torch.compile()` first, add as optimization if inference target (30s) is not met
- **Confidence:** HIGH

### HuggingFace Transformers + PyTorch Compatibility
Transformers library pins specific PyTorch version ranges. Always install together:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers
```
Installing PyTorch from PyPI default may pull CPU-only version.

---

## Installation

### Backend (Python 3.11+)

```bash
# Use Python 3.11 -- stable, well-tested with PyTorch and all dependencies.
# Python 3.12 works but some C extensions (webrtcvad) may need compilation.
# Python 3.13 is too new -- avoid for now.

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# PyTorch with CUDA 12.1 (for GPU inference)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Or CPU-only (for dev machines without GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Core backend
pip install fastapi uvicorn[standard] python-multipart pydantic

# Database
pip install sqlalchemy[asyncio] asyncpg alembic

# ML pipeline
pip install transformers opencv-python-headless Pillow numpy webrtcvad

# Blockchain
pip install web3

# HTTP client (for Pinata API)
pip install httpx python-dotenv

# Logging
pip install loguru

# Dev/test
pip install pytest pytest-asyncio httpx  # httpx needed for FastAPI TestClient async
```

### Frontend (Node.js 20 LTS)

```bash
cd frontend

# Already has React, Vite, shadcn/ui. Add missing deps:
npm install react-router-dom @tanstack/react-query react-dropzone axios
npm install -D tailwindcss @types/react @types/react-dom typescript
```

### Blockchain (Node.js 20 LTS)

```bash
cd blockchain

npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npx hardhat init  # Select "Create a TypeScript project"
```

### Docker

```dockerfile
# Backend Dockerfile key points:
# - Base: python:3.11-slim
# - System deps: ffmpeg, libgl1 (for OpenCV)
# - Multi-stage build: install deps first, copy code second (layer caching)
# - Do NOT install full opencv-python in Docker -- use opencv-python-headless
```

```yaml
# docker-compose.yml services:
# - backend: FastAPI + Uvicorn (port 8000)
# - frontend: Vite dev or nginx for production (port 5173/80)
# - db: postgres:16-alpine (port 5432)
# - hardhat: local Ethereum node for dev (port 8545) -- optional, use Sepolia directly
```

---

## Environment Variables

```env
# .env (DO NOT COMMIT)

# Database
DATABASE_URL=postgresql+asyncpg://trustchain:password@localhost:5432/trustchain_av

# Blockchain
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
DEPLOYER_PRIVATE_KEY=0x...  # Sepolia testnet only!
CONTRACT_ADDRESS=0x...      # Set after deployment

# IPFS
PINATA_API_KEY=your_key
PINATA_SECRET_KEY=your_secret
PINATA_JWT=your_jwt          # Preferred over API key pair

# ML
MODEL_DEVICE=cuda             # or "cpu"
FUSION_WEIGHTS_PATH=./models/fusion_mlp.pth
```

---

## Version Verification Commands

Run these before locking versions to get exact current releases:

```bash
# Python packages
pip install --dry-run fastapi torch transformers web3 sqlalchemy 2>&1 | grep "Would install"

# Node packages
npm info hardhat version
npm info @nomicfoundation/hardhat-toolbox version

# System
ffmpeg -version
docker --version
python --version
```

---

## Sources

- FastAPI documentation: https://fastapi.tiangolo.com/ (HIGH confidence -- well-known stable API)
- PyTorch installation: https://pytorch.org/get-started/locally/ (HIGH confidence)
- HuggingFace Wav2Vec2: https://huggingface.co/facebook/wav2vec2-base-960h (HIGH confidence)
- Hardhat documentation: https://hardhat.org/docs (HIGH confidence)
- Web3.py documentation: https://web3py.readthedocs.io/ (MEDIUM confidence -- v7 migration details need verification)
- Pinata documentation: https://docs.pinata.cloud/ (MEDIUM confidence -- API versioning may have changed)
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/ (HIGH confidence)

**NOTE:** All version numbers are based on training data through May 2025. Versions marked MEDIUM confidence should be verified with `pip index versions <package>` or official release pages before pinning in requirements.txt.
