# Requirements: TrustChain-AV

**Defined:** 2026-03-05
**Core Value:** Detect whether a video is AI-generated or manipulated by analyzing both audio and visual signals simultaneously, and provide cryptographic proof of authenticity via blockchain.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Infrastructure

- [x] **INFR-01**: FastAPI backend serves REST API with async background job processing
- [x] **INFR-02**: PostgreSQL database stores uploads, results, and blockchain records
- [x] **INFR-03**: Docker + Docker Compose containerizes all services (backend, frontend, database)
- [x] **INFR-04**: Health check endpoint returns system status at GET /api/health
- [x] **INFR-05**: Models load once at server startup via FastAPI lifespan, not per-request

### Upload & Preprocessing

- [x] **UPLD-01**: User can upload video via drag-and-drop or file picker
- [ ] **UPLD-02**: System validates file format (MP4, AVI, MOV, MKV) and size (max 500MB)
- [x] **UPLD-03**: Upload returns job ID immediately; frontend polls for completion
- [ ] **PREP-01**: FFmpeg extracts frames at configurable interval (default every 10th frame), resizes to 224x224, normalizes to ImageNet mean/std
- [ ] **PREP-02**: FFmpeg extracts audio track, resamples to 16kHz mono WAV
- [ ] **PREP-03**: System handles edge cases: no audio track, video < 1 second, corrupted file

### Detection Pipeline

- [x] **DETC-01**: ResNet-50 frozen backbone extracts 2048-dim visual feature vector averaged across sampled frames
- [x] **DETC-02**: Wav2Vec2 frozen backbone extracts 768-dim audio feature vector averaged across time
- [x] **DETC-03**: WebRTC VAD determines speech presence; if no speech, audio_weight=0.0 and zero vector used
- [x] **DETC-04**: Stage 1 Fusion MLP concatenates visual (2048) + weighted audio (768) features, outputs REAL/FAKE with confidence score
- [x] **DETC-05**: Frontend shows multi-stage processing status (extracting frames, extracting audio, running visual analysis, running audio analysis, computing fusion)
- [x] **DETC-06**: System computes SHA-256 hash of uploaded video file

### Blockchain

- [ ] **BLKC-01**: Solidity smart contract accepts file hash (bytes32), Merkle root, and registers with timestamp
- [ ] **BLKC-02**: Smart contract provides lookup function: given hash, returns existence, timestamp
- [ ] **BLKC-03**: Hardhat project tests contract locally before Sepolia deployment
- [ ] **BLKC-04**: Backend calls registerMedia() via Web3.py after user triggers registration
- [ ] **BLKC-05**: Smart contract emits MediaRegistered events for auditability
- [ ] **BLKC-06**: Transaction hash and block number stored in PostgreSQL
- [ ] **BLKC-07**: Contract deployed to Ethereum Sepolia testnet

### Results UI

- [x] **RSLT-01**: Results screen shows REAL/FAKE verdict with color-coded confidence bar (green=real, red=fake)
- [x] **RSLT-02**: Results screen shows modality breakdown: visual score, audio score, whether audio was analyzed, decision basis
- [ ] **RSLT-03**: Results screen shows "Register on Blockchain" button for completed analyses
- [ ] **RSLT-04**: Blockchain registration screen shows SHA-256 hash, transaction hash, Sepolia explorer link, registration timestamp
- [ ] **RSLT-05**: Blockchain transaction status shows live progress (Pending -> Confirmed)

### History

- [x] **HIST-01**: History page shows paginated table of all past analyses with status, date, verdict, and confidence
- [x] **HIST-02**: User can click a history entry to view full results

### Export

- [x] **EXPT-01**: User can download a PDF verification report for any completed analysis with blockchain registration

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Detection

- **DETC-07**: Stage 2 Cross-Modal Attention fusion layer upgrade
- **DETC-08**: Per-frame confidence timeline chart visualization
- **DETC-09**: Fine-tune ResNet-50 last 2 layers on DFDC dataset

### Verification

- **VRFY-01**: Verification page allows re-upload or hash input to verify against on-chain record
- **VRFY-02**: Verification result shows AUTHENTIC/TAMPERED/UNREGISTERED status

### Storage

- **STOR-01**: IPFS storage of video and metadata via Pinata API
- **STOR-02**: IPFS CID stored on-chain alongside file hash

## Out of Scope

| Feature | Reason |
|---------|--------|
| Live video stream analysis | Prototype handles file uploads only |
| Mobile application | Web-first prototype |
| Ethereum mainnet deployment | Uses free testnet only |
| Wav2Vec2 backbone fine-tuning | Frozen in this version, reduces complexity |
| Multi-language speech support | English-focused prototype |
| User authentication/accounts | Open access academic prototype |
| GradCAM explainability heatmaps | Future enhancement |
| Audio-only file support | Video container required |
| In-app model training | Training done separately on Google Colab |
| Batch video analysis | Single upload workflow only |
| Real-time A/V sync checking | Out of scope for prototype |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFR-01 | Phase 1 | Complete |
| INFR-02 | Phase 1 | Complete |
| INFR-03 | Phase 1 | Complete |
| INFR-04 | Phase 1 | Complete |
| INFR-05 | Phase 1 | Complete |
| UPLD-01 | Phase 2 | Complete |
| UPLD-02 | Phase 2 | Pending |
| UPLD-03 | Phase 2 | Complete |
| PREP-01 | Phase 2 | Pending |
| PREP-02 | Phase 2 | Pending |
| PREP-03 | Phase 2 | Pending |
| DETC-01 | Phase 3 | Complete |
| DETC-02 | Phase 3 | Complete |
| DETC-03 | Phase 3 | Complete |
| DETC-04 | Phase 3 | Complete |
| DETC-05 | Phase 3 | Complete |
| DETC-06 | Phase 3 | Complete |
| RSLT-01 | Phase 4 | Complete |
| RSLT-02 | Phase 4 | Complete |
| RSLT-03 | Phase 5 | Pending |
| RSLT-04 | Phase 5 | Pending |
| RSLT-05 | Phase 5 | Pending |
| HIST-01 | Phase 4 | Complete |
| HIST-02 | Phase 4 | Complete |
| EXPT-01 | Phase 4 | Complete |
| BLKC-01 | Phase 5 | Pending |
| BLKC-02 | Phase 5 | Pending |
| BLKC-03 | Phase 5 | Pending |
| BLKC-04 | Phase 5 | Pending |
| BLKC-05 | Phase 5 | Pending |
| BLKC-06 | Phase 5 | Pending |
| BLKC-07 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 32
- Unmapped: 0

---
*Requirements defined: 2026-03-05*
*Last updated: 2026-03-05 after roadmap revision (Phase 4/5 swap)*
