# Roadmap: TrustChain-AV

## Overview

TrustChain-AV delivers a blockchain-enhanced audiovisual deepfake detection system in five phases. We start with the backend foundation (FastAPI, PostgreSQL, Docker), then build the video ingestion and preprocessing pipeline, followed by the core ML detection engine (ResNet-50 + Wav2Vec2 fusion). Next, the user-facing screens (results display, history page, PDF export) are integrated into the React frontend. Finally, the blockchain layer (Solidity smart contract, Sepolia deployment, Web3.py integration, and blockchain registration UI wiring) completes the system. Each phase delivers a complete, verifiable capability that the next phase builds upon.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation and Infrastructure** - FastAPI backend, PostgreSQL database, Docker containerization, and project skeleton (completed 2026-03-05)
- [ ] **Phase 2: Upload and Preprocessing** - Video upload with validation, FFmpeg frame and audio extraction, edge case handling
- [x] **Phase 3: Detection Pipeline** - ResNet-50 visual analysis, Wav2Vec2 audio analysis, VAD, fusion MLP, and file hashing (completed 2026-03-06)
- [x] **Phase 4: Results UI and Frontend Integration** - Verdict display, history page, detection results screens, PDF export scaffold (completed 2026-03-06)
- [ ] **Phase 5: Blockchain Layer** - Solidity smart contract, Hardhat testing, Sepolia deployment, Web3.py registration service, blockchain registration UI wiring

## Phase Details

### Phase 1: Foundation and Infrastructure
**Goal**: A running FastAPI application with PostgreSQL database, health endpoint, model preloading, and Docker Compose orchestration -- the skeleton that every subsequent phase builds on
**Depends on**: Nothing (first phase)
**Requirements**: INFR-01, INFR-02, INFR-03, INFR-04, INFR-05
**Success Criteria** (what must be TRUE):
  1. Running `docker compose up` starts the backend, frontend, and database containers without errors
  2. GET /api/health returns a 200 response with system status information
  3. The PostgreSQL database is accessible from the backend with tables for uploads, results, and blockchain records
  4. ML model stubs load once at server startup (visible in startup logs), not on each request
  5. The React frontend shell loads in the browser with routing between pages
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md -- Backend foundation: FastAPI app, database models, health endpoint, model stubs, Alembic migrations, tests
- [x] 01-02-PLAN.md -- Frontend scaffold: Vite/React project, React Router, page shells, navigation bar, shadcn/ui init
- [x] 01-03-PLAN.md -- Docker Compose orchestration, Dockerfiles, environment config, integration verification

### Phase 2: Upload and Preprocessing
**Goal**: Users can upload video files and the system extracts frames and audio tracks ready for ML analysis, with proper validation and error handling for edge cases
**Depends on**: Phase 1
**Requirements**: UPLD-01, UPLD-02, UPLD-03, PREP-01, PREP-02, PREP-03
**Success Criteria** (what must be TRUE):
  1. User can drag-and-drop or select a video file (MP4, AVI, MOV, MKV up to 500MB) and receive a job ID immediately
  2. Uploading an invalid format or oversized file shows a clear rejection message before processing starts
  3. The system extracts frames (224x224, normalized) and a 16kHz mono WAV audio track from the uploaded video
  4. Videos with no audio track, videos under 1 second, and corrupted files are handled gracefully with appropriate error messages
  5. The frontend can poll the job status endpoint and see progress updates
**Plans**: 3 plans

Plans:
- [ ] 02-01-PLAN.md -- Backend upload API, Pydantic schemas, FFmpeg preprocessing service, edge case handling, tests
- [ ] 02-02-PLAN.md -- Frontend upload card UI, API client, status polling hook, results page status display
- [ ] 02-03-PLAN.md -- Docker integration (FFmpeg, /data volume, Alembic migration, Vite proxy), end-to-end verification

### Phase 3: Detection Pipeline
**Goal**: The system analyzes uploaded videos using dual-stream ML (visual + audio) and returns a REAL/FAKE verdict with confidence score and modality breakdown
**Depends on**: Phase 2
**Requirements**: DETC-01, DETC-02, DETC-03, DETC-04, DETC-05, DETC-06
**Success Criteria** (what must be TRUE):
  1. Uploading a video produces a REAL or FAKE verdict with a numerical confidence score stored in the database
  2. The detection result includes separate visual and audio scores alongside the fused verdict
  3. Videos without speech are detected by VAD and analyzed using visual-only mode (audio weight set to zero) without failing
  4. The frontend displays multi-stage processing status (extracting frames, extracting audio, visual analysis, audio analysis, fusion) during analysis
  5. A SHA-256 hash of the uploaded file is computed and stored alongside the detection result
**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md -- ML modules (ResNet-50, Wav2Vec2, WebRTC VAD, Fusion MLP), real model loading, Docker PyTorch setup
- [x] 03-02-PLAN.md -- Detection orchestrator, pipeline wiring, status column migration, frontend status stages and result display

### Phase 4: Results UI and Frontend Integration
**Goal**: Users see complete analysis results, browse their analysis history, and export verification reports -- the detection-facing user experience
**Depends on**: Phase 3
**Requirements**: RSLT-01, RSLT-02, HIST-01, HIST-02, EXPT-01
**Success Criteria** (what must be TRUE):
  1. After analysis completes, the results screen shows a color-coded REAL/FAKE verdict with confidence bar and modality breakdown (visual score, audio score, decision basis)
  2. The history page shows a paginated table of all past analyses with status, date, verdict, and confidence
  3. Clicking any history entry navigates to its full results screen
  4. User can download a PDF verification report for any completed analysis
**Plans**: 2 plans

Plans:
- [x] 04-01-PLAN.md -- Backend list/stats endpoints, processing_time, ResultsPage multi-card refactor, HomePage quick stats
- [x] 04-02-PLAN.md -- History page (paginated table, search, filter, expandable rows), PDF export utility, Download PDF wiring

### Phase 5: Blockchain Layer
**Goal**: Authenticated media can be registered on-chain via a Solidity smart contract deployed to Sepolia, with transaction records stored locally and verifiable on Etherscan, and the frontend provides full blockchain registration and status UI
**Depends on**: Phase 1, Phase 4
**Requirements**: BLKC-01, BLKC-02, BLKC-03, BLKC-04, BLKC-05, BLKC-06, BLKC-07, RSLT-03, RSLT-04, RSLT-05
**Success Criteria** (what must be TRUE):
  1. The MediaRegistry smart contract passes all Hardhat tests for registration, lookup, and event emission
  2. The smart contract is deployed to Ethereum Sepolia testnet and accessible at a known address
  3. Backend can call registerMedia() via Web3.py, and the transaction hash and block number are stored in PostgreSQL
  4. Given a file hash, the smart contract returns whether it exists on-chain and its registration timestamp
  5. MediaRegistered events are emitted for every registration and are queryable
  6. For REAL verdicts, the user can click "Register on Blockchain" and see the registration progress (Pending to Confirmed) with transaction hash, SHA-256 hash, and Sepolia explorer link
**Plans**: 2 plans

Plans:
- [ ] 05-01: TBD
- [ ] 05-02: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5
Note: Phase 5 (Blockchain) depends on Phase 1 and Phase 4, so it must follow Phase 4.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation and Infrastructure | 3/3 | Complete   | 2026-03-05 |
| 2. Upload and Preprocessing | 1/3 | In Progress|  |
| 3. Detection Pipeline | 2/2 | Complete    | 2026-03-05 |
| 4. Results UI and Frontend Integration | 2/2 | Complete | 2026-03-06 |
| 5. Blockchain Layer | 0/? | Not started | - |
