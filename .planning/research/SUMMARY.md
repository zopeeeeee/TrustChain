# Project Research Summary

**Project:** TrustChain-AV (Blockchain-Enhanced Audiovisual Deepfake Detection)
**Domain:** Multimodal ML Inference + Blockchain Provenance Verification
**Researched:** 2026-03-05
**Confidence:** MEDIUM

## Executive Summary

TrustChain-AV is a multimodal deepfake detection system that combines visual analysis (ResNet-50), audio analysis (Wav2Vec2), and blockchain-based provenance verification (Solidity on Sepolia). The recommended approach is a three-tier architecture: React frontend, async FastAPI gateway with background ML workers, and a blockchain service layer. The existing codebase has a React + Flask foundation that needs to be migrated to FastAPI with async patterns -- the current Flask code loads models per-request and runs synchronous inference, both of which must be eliminated. The stack is well-established (PyTorch, FastAPI, PostgreSQL, Hardhat) with high confidence, and the architecture follows proven patterns for ML serving behind an API.

The critical path runs through the ML pipeline: video upload, FFmpeg preprocessing, dual-stream feature extraction, fusion, and verdict. Everything else -- blockchain registration, IPFS storage, verification, history -- branches from the detection verdict. The blockchain layer and ML pipeline share only the database and file hash, which means a 4-person team can develop them in parallel. This parallelism is the key scheduling insight for the roadmap.

The top risks are: (1) audio-visual temporal misalignment making the fusion layer useless, (2) dataset distribution mismatch producing inflated accuracy that fails on real-world videos, (3) Sepolia testnet instability killing the demo, and (4) Docker image bloat from ML dependencies crashing deployment. All are preventable with specific technical strategies documented in the pitfalls research. The project's unique academic contribution is the combination of multimodal detection + blockchain verification + web UI -- each piece exists individually, but the integrated pipeline is novel.

## Key Findings

### Recommended Stack

The backend is Python-centric: FastAPI (async, auto-docs, BackgroundTasks) with PostgreSQL via SQLAlchemy async + asyncpg. The ML pipeline uses PyTorch with frozen ResNet-50 and Wav2Vec2 backbones, only training the fusion layer. The blockchain layer uses Hardhat for Solidity development and Web3.py for Python-side Ethereum interaction. The frontend stays on the existing React 18 + Vite + shadcn/ui stack with TanStack Query added for server state management.

**Core technologies:**
- **FastAPI + Uvicorn** -- async API gateway replacing Flask; native BackgroundTasks for ML job offloading
- **PyTorch + torchvision + torchaudio** -- ResNet-50 (visual, 2048-dim) and Wav2Vec2 (audio, 768-dim) frozen backbones
- **PostgreSQL + SQLAlchemy async + asyncpg** -- relational storage for uploads, results, blockchain records; JSONB for variable metadata
- **Hardhat + Solidity ^0.8.24** -- smart contract dev, testing, deployment; replaces deprecated Truffle
- **Web3.py v7** -- Python Ethereum interaction (note: breaking API changes from v6, needs careful migration)
- **Pinata HTTP API** -- IPFS pinning via httpx; free tier has 500 uploads/1GB limit
- **React 18 + Vite + TanStack Query** -- existing frontend with added polling/caching for async job status

**Critical version note:** Web3.py v7 has significant breaking changes. Pin `web3>=7.0,<8.0` and verify the API surface before implementation. Install PyTorch from the PyTorch index URL (not PyPI default) to get the correct CUDA/CPU variant.

### Expected Features

**Must have (table stakes):**
- Video upload with drag-and-drop, progress indicator, format validation
- Real/Fake binary verdict with confidence score (color-coded)
- Visual stream analysis (ResNet-50) and audio stream analysis (Wav2Vec2)
- Modality breakdown display (separate audio + visual scores alongside fused verdict)
- Blockchain hash registration for REAL verdicts on Sepolia
- On-chain verification lookup with Etherscan transaction links
- Analysis history log (PostgreSQL-backed)
- Multi-stage processing status feedback (not just a spinner)
- Docker containerization for reproducible demos
- Health check endpoint

**Should have (differentiators for academic evaluation):**
- Cross-modal attention fusion (Stage 2) -- the key academic contribution, enables MLP vs. attention comparison experiment
- IPFS content storage via Pinata with CID stored on-chain
- Per-frame confidence timeline chart
- PDF verification report export
- Silent/no-speech audio fallback with clear user indication
- Smart contract event logging for auditability

**Defer indefinitely:**
- User authentication, real-time streaming, model training in-app, mainnet deployment, GradCAM heatmaps, mobile app, batch analysis, A/V sync check, comparison mode

### Architecture Approach

Three-tier async architecture: React frontend communicates via REST + polling to a FastAPI gateway, which orchestrates background ML workers and a blockchain service layer. ML models load once at startup via FastAPI lifespan. File uploads return a job ID immediately; the client polls for completion. Blockchain registration is a separate user-initiated action (only for REAL verdicts) that also runs as a background task to avoid blocking the event loop.

**Major components:**
1. **React Frontend** -- 5 pages (Upload, Results, Blockchain, Verify, History); polling via TanStack Query
2. **FastAPI Gateway** -- request validation, job orchestration, file storage on disk (not DB)
3. **ML Worker** -- FFmpeg preprocessing, ResNet-50 + Wav2Vec2 feature extraction, fusion inference
4. **Blockchain Service** -- Web3.py + Pinata integration, transaction management with nonce locking
5. **PostgreSQL** -- uploads, detection_results, blockchain_records tables with UUID primary keys
6. **Solidity Contract (MediaRegistry)** -- on-chain hash registration with minimal storage, event emission

### Critical Pitfalls

1. **Audio-visual temporal misalignment** -- Use consistent timestamp references for frame and audio extraction. For Stage 1 MLP (average pooling), this is less critical, but for Stage 2 attention, temporal alignment is mandatory. Test by comparing accuracy with and without audio branch.
2. **Dataset distribution mismatch** -- Train on DFDC, test on FakeAVCeleb (and vice versa). Prepare a "wild test set" of 20-30 diverse videos. Split by source identity, not by clip. Target 85-90% cross-dataset accuracy, not 95%+.
3. **Blockchain registration of fake media** -- Gate registration at both API level and UI level: only REAL verdicts can register. Store verdict in the smart contract alongside the hash.
4. **Sepolia testnet instability** -- Pre-register sample videos before demos. Implement Hardhat local node as fallback. Cache blockchain results in PostgreSQL so verification works even when the chain is slow.
5. **Docker image size explosion** -- Use CPU-only PyTorch (saves ~1.5GB), multi-stage Docker builds, download model weights at build time. Target <3GB image size. Set memory limits in docker-compose.yml.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Foundation and Infrastructure
**Rationale:** Everything depends on the database schema, API skeleton, and project structure. The existing codebase needs migration from Flask to FastAPI. Docker Compose setup here prevents "works on my machine" issues for the 4-person team.
**Delivers:** Working FastAPI app with health endpoint, PostgreSQL with Alembic migrations, Docker Compose (backend + frontend + db), React app shell with routing
**Addresses:** Docker containerization, health check endpoint, database setup
**Avoids:** Schema migration nightmares (Pitfall 15) by establishing Alembic from day one

### Phase 2: ML Detection Pipeline
**Rationale:** This is the critical path and the riskiest component. FFmpeg edge cases, model memory usage, and inference time budget are the biggest unknowns. Must be built and validated before anything depends on the verdict output.
**Delivers:** End-to-end detection: upload video, extract frames + audio, run ResNet-50 + Wav2Vec2, fuse features via MLP, return REAL/FAKE verdict with confidence
**Addresses:** Video upload, visual analysis, audio analysis, modality breakdown, processing status, silent audio fallback
**Avoids:** Temporal misalignment (Pitfall 1) by storing timestamps throughout pipeline; Wav2Vec2 silent failure (Pitfall 6) by implementing VAD first; FFmpeg bottleneck (Pitfall 9) by profiling early and batching inference

### Phase 3: Blockchain and IPFS Layer
**Rationale:** Can be developed in parallel with Phase 2 by a separate team member since it only depends on Phase 1 (database + API skeleton). The smart contract and Web3.py integration are independent of the ML pipeline until the final wiring.
**Delivers:** Solidity MediaRegistry contract, Hardhat tests + Sepolia deployment, Web3.py registration + verification service, Pinata IPFS integration, blockchain API endpoints
**Addresses:** Blockchain hash registration, on-chain verification, transaction explorer links, IPFS storage, smart contract events
**Avoids:** Registering fakes (Pitfall 3) by enforcing verdict-gated registration; Testnet instability (Pitfall 4) by building Hardhat local fallback; Event loop blocking (Pitfall 10) by running blockchain calls as background tasks; IPFS quota exhaustion (Pitfall 7) by mocking during development; Gas cost concerns (Pitfall 8) by storing minimal data on-chain

### Phase 4: Frontend Integration and Results UI
**Rationale:** Requires Phase 2 API (detection endpoints) and Phase 3 API (blockchain endpoints) to be functional. This is where the user-facing experience comes together.
**Delivers:** Upload dashboard with drag-drop and progress, verdict display with confidence gauge and modality breakdown, blockchain registration UI (only for REAL), verification page, analysis history page
**Addresses:** All frontend table-stakes features, multi-stage progress indicator
**Avoids:** Misleading upload progress (Pitfall 13) by implementing multi-stage SSE or polling status updates

### Phase 5: Academic Differentiators and Polish
**Rationale:** These features elevate the project from "functional prototype" to "publishable academic work." They depend on all prior phases being stable. Cross-modal attention fusion is the key academic contribution.
**Delivers:** Cross-modal attention fusion (Stage 2) with comparison experiment vs. MLP, per-frame confidence timeline, PDF verification report export, end-to-end testing, Docker production build optimization
**Addresses:** Cross-modal attention (key differentiator), per-frame timeline, PDF export, model confidence display
**Avoids:** Docker image bloat (Pitfall 5) by optimizing in the final build phase; Dataset mismatch (Pitfall 2) by running cross-dataset evaluation before finalizing

### Phase Ordering Rationale

- **Phase 1 before everything:** Database schema, API skeleton, and Docker Compose are dependencies for all other phases. Alembic migrations prevent schema drift across 4 developers.
- **Phase 2 and 3 in parallel:** The ML pipeline and blockchain layer share only the database and file hash. A 4-person team should split: 2 on ML, 1-2 on blockchain. This is the key scheduling optimization.
- **Phase 4 after 2+3:** Frontend integration requires working API endpoints from both the detection and blockchain services.
- **Phase 5 last:** Academic differentiators (attention fusion, per-frame timeline) are enhancements that require a stable base. Cross-modal attention specifically requires the Stage 1 MLP to be working as a baseline for comparison.
- **Pitfall avoidance drives ordering:** VAD before Wav2Vec2, Alembic before any schema changes, mock IPFS before real Pinata calls, Hardhat local before Sepolia dependency.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (ML Pipeline):** FFmpeg frame extraction strategy (keyframes vs. uniform sampling), temporal pooling approach, inference time profiling on CPU vs. GPU, WebRTC VAD integration specifics
- **Phase 3 (Blockchain):** Web3.py v7 exact API surface (breaking changes from v6), AsyncWeb3 provider configuration, Pinata API v2 endpoints and authentication flow, nonce management for concurrent transactions
- **Phase 5 (Attention Fusion):** Cross-modal attention mechanism design, temporal alignment requirements for attention (much stricter than MLP), training hyperparameters

Phases with standard patterns (skip deep research):
- **Phase 1 (Foundation):** FastAPI app factory, SQLAlchemy async setup, Alembic configuration, Docker Compose -- all extremely well-documented
- **Phase 4 (Frontend):** React Router, TanStack Query polling, file upload with progress, shadcn/ui components -- standard React patterns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All core technologies (FastAPI, PyTorch, PostgreSQL, React) are mature and well-documented. Web3.py v7 and Pinata API are MEDIUM confidence due to recent changes. |
| Features | MEDIUM | Table stakes are clear from competitive analysis. Differentiator complexity estimates need validation during implementation. Cross-modal attention is the highest-risk feature. |
| Architecture | MEDIUM-HIGH | Three-tier async pattern is proven for ML serving. Specific integration points (Web3.py async + FastAPI, model lifespan loading) have well-documented patterns but project-specific edge cases. |
| Pitfalls | MEDIUM | Pitfalls are drawn from established domain knowledge. Temporal misalignment and dataset mismatch are well-known ML issues. Blockchain pitfalls are specific to testnet deployment patterns. No live 2026 community reports were available for verification. |

**Overall confidence:** MEDIUM -- the individual technologies are HIGH confidence, but the integration of ML inference + blockchain + async web framework introduces compound complexity that needs careful implementation.

### Gaps to Address

- **Web3.py v7 API verification:** The exact v7 API surface needs to be verified before implementation. Run `pip install web3` and test basic contract interaction against Hardhat local node early.
- **Inference time budget on CPU:** The 30-second target for 5-minute videos needs profiling. ResNet-50 on CPU with 300 frames may exceed this. Plan for FPS reduction or ONNX export as fallbacks.
- **Pinata API v2 authentication flow:** The Python SDK is unmaintained. Direct HTTP calls via httpx need endpoint and auth header verification against current Pinata docs.
- **Cross-modal attention design:** No specific architecture was researched. During Phase 5 planning, research attention mechanisms used in audio-visual fusion literature (e.g., from AV-HuBERT, audio-visual transformer papers).
- **Model training data pipeline:** Training happens on Colab, not in the app. The split strategy (by identity), dataset preparation, and weight export process need documentation before training begins.
- **Existing codebase migration path:** The current Flask + synchronous code needs a clear migration strategy to FastAPI async. Decide whether to port incrementally or rewrite the backend.

## Sources

### Primary (HIGH confidence)
- FastAPI documentation -- async patterns, BackgroundTasks, lifespan, file upload
- PyTorch documentation -- model loading, inference, torchvision models API
- HuggingFace Transformers -- Wav2Vec2 model card and usage patterns
- Hardhat documentation -- project setup, testing, deployment workflows
- SQLAlchemy 2.0 documentation -- async engine, session management

### Secondary (MEDIUM confidence)
- Web3.py documentation -- v7 migration details need verification against current release
- Pinata API documentation -- endpoint versioning may have changed since training data cutoff
- Docker multi-stage build patterns for ML applications
- DFDC and FakeAVCeleb dataset documentation -- split strategies, evaluation protocols

### Tertiary (LOW confidence)
- Cross-modal attention fusion architectures -- general knowledge, specific design needs literature review
- WebRTC VAD Python bindings -- integration specifics with PyTorch pipeline need testing
- Sepolia testnet reliability patterns -- anecdotal, no SLA documentation

---
*Research completed: 2026-03-05*
*Ready for roadmap: yes*
