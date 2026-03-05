# TrustChain-AV

## What This Is

A blockchain-enhanced audiovisual deepfake detection system. Users upload video files, the system analyzes both audio and visual streams using a multimodal AI pipeline (ResNet-50 + Wav2Vec2) to classify videos as REAL or FAKE, then registers authentic media on the Ethereum Sepolia testnet with IPFS storage for tamper-proof provenance. Built as a final year project prototype for IIIT Pune's Computer Engineering department.

## Core Value

Detect whether a video is AI-generated or manipulated by analyzing both audio and visual signals simultaneously, and provide cryptographic proof of authenticity via blockchain.

## Requirements

### Validated

- ✓ React + TailwindCSS frontend shell — existing
- ✓ Basic image analysis with ResNet-50 feature extraction — existing
- ✓ SHA-256 file hashing — existing
- ✓ shadcn/ui component library setup — existing

### Active

- [ ] Video file upload with format validation (MP4, AVI, MOV, MKV, max 500MB)
- [ ] FFmpeg preprocessing pipeline (frame extraction + audio extraction)
- [ ] ResNet-50 visual feature extractor (frozen backbone, 2048-dim output)
- [ ] Wav2Vec2 audio feature extractor (frozen backbone, 768-dim output)
- [ ] WebRTC VAD for speech detection with fallback logic
- [ ] Stage 1 Fusion Layer — Concatenation MLP (2816 -> REAL/FAKE)
- [ ] Stage 2 Fusion Layer — Cross-Modal Attention upgrade
- [ ] FastAPI backend with async job processing
- [ ] PostgreSQL database (uploads, results, blockchain_records)
- [ ] Solidity smart contract for media hash registration
- [ ] Hardhat development + Sepolia testnet deployment
- [ ] Web3.py integration for blockchain interaction
- [ ] IPFS storage via Pinata API
- [ ] Verification service (re-upload to verify against on-chain record)
- [ ] Upload Dashboard with drag-and-drop, progress indicator
- [ ] Detection Results screen (verdict, confidence, modality breakdown)
- [ ] Blockchain Registration screen (hash, tx hash, IPFS CID, explorer link)
- [ ] Verification Page (re-upload or paste hash)
- [ ] History Page (paginated past analyses)
- [ ] Docker + Docker Compose containerization
- [ ] Verification report export (PDF)

### Out of Scope

- Live video stream analysis — prototype handles file uploads only
- Mobile application — web-first
- Ethereum mainnet deployment — testnet only
- Wav2Vec2 backbone fine-tuning — frozen in this version
- Multi-language speech support — English-focused
- User authentication and accounts — open access prototype
- Explainability heatmaps (GradCAM) — future enhancement
- Audio-only file support — video required
- Model training — inference pipeline only, training done separately on Colab
- Paid tier or SLA guarantees — academic prototype

## Context

- Final year project for Computer Engineering at IIIT Pune (March 2026)
- Team of 4 members, guided by Dr. Poonam Deokar
- Existing codebase is image-only analysis (Flask + React) — rebuilding from scratch per PRD
- Existing codebase has extracted React components (shadcn/ui) and ResNet-50 inference that informed the architecture but won't be reused directly
- Models (ResNet-50, Wav2Vec2) use frozen pretrained weights — only the fusion layer is trained
- Training happens separately on Google Colab using DFDC + FakeAVCeleb datasets
- Sepolia testnet provides free test ETH for blockchain operations
- Pinata API free tier for IPFS storage

## Constraints

- **Tech Stack**: FastAPI (Python) backend, React + TailwindCSS frontend, PostgreSQL, Docker — as specified in PRD
- **ML Framework**: PyTorch + HuggingFace Transformers — required for Wav2Vec2 and ResNet-50
- **Blockchain**: Ethereum Sepolia testnet + Hardhat + Web3.py + Solidity
- **Storage**: IPFS via Pinata API (free tier)
- **Performance**: Inference under 30 seconds for 5-min video, blockchain registration under 15 seconds
- **Accuracy**: Target >=90% on test set (>=85% acceptable for Phase 1)
- **File Limits**: Max 500MB upload, formats MP4/AVI/MOV/MKV
- **Inference Only**: No training in the build — pretrained/mock weights for the fusion layer

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Rebuild from scratch (not evolve existing) | Existing codebase is image-only Flask; PRD requires fundamentally different architecture | -- Pending |
| FastAPI over Flask | Better async support for ML background jobs, matches PRD specification | -- Pending |
| PostgreSQL over SQLite | Production-grade, supports concurrent access, matches PRD specification | -- Pending |
| Docker containerization | Consistent environment across team of 4, easier deployment | -- Pending |
| Frozen backbones + trained fusion only | Reduces training complexity, keeps inference simple | -- Pending |
| Two-stage fusion (MLP first, attention upgrade) | Gets pipeline working fast, provides academic comparison experiment | -- Pending |

---
*Last updated: 2026-03-05 after initialization*
