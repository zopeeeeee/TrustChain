# Feature Landscape

**Domain:** Blockchain-Enhanced Audiovisual Deepfake Detection
**Researched:** 2026-03-05
**Confidence:** MEDIUM (based on training data knowledge of products like Sensity AI, Deepware Scanner, Microsoft Video Authenticator, Intel FakeCatcher, Numbers Protocol, C2PA; no live web verification possible this session)

## Table Stakes

Features users (and academic evaluators) expect. Missing any of these makes the prototype feel incomplete for its stated purpose.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Video file upload with drag-and-drop | Every detection tool has this; it is the entry point for the entire system | Low | Support MP4/AVI/MOV/MKV; show file preview thumbnail |
| Upload progress indicator | Videos are large (up to 500MB); users need feedback that something is happening | Low | Use chunked upload or at minimum a progress bar |
| Real/Fake binary verdict with confidence score | This IS the product; every competitor (Deepware, Sensity) shows a clear verdict | Medium | Confidence as percentage (0-100); color-coded (green/yellow/red) |
| Visual stream analysis (frame-level) | Standard in all video deepfake detectors; ResNet-50 or similar CNN is baseline | Medium | Extract frames via FFmpeg, run through ResNet-50 backbone, aggregate |
| Audio stream analysis | The "multimodal" claim requires audio analysis; without it this is just another image detector | Medium | Wav2Vec2 for audio features; WebRTC VAD for speech detection |
| Modality breakdown display | Evaluators need to see BOTH modalities contributing; proves multimodal fusion works | Low | Show separate audio score + visual score alongside fused verdict |
| Blockchain hash registration | Core differentiator of this project; without it there is no "blockchain-enhanced" claim | Medium | Register SHA-256 hash of authentic media on Sepolia; return tx hash |
| On-chain verification lookup | Must be able to verify a previously registered file; proves blockchain is not decorative | Medium | Re-upload file or paste hash to check against on-chain record |
| Transaction confirmation with explorer link | Users need proof the blockchain interaction actually happened | Low | Link to Etherscan Sepolia with the transaction hash |
| Analysis history/results log | Evaluators will run multiple files; need to see past results without re-analyzing | Low | PostgreSQL-backed list of past analyses with timestamps |
| Processing status feedback | ML inference takes 10-30 seconds; users need to know system is not frozen | Low | Show "Extracting frames... Analyzing video... Analyzing audio... Fusing results..." |
| Error handling for unsupported formats | Must gracefully reject non-video files, corrupt files, too-large files | Low | Clear error messages, not stack traces |
| Health check endpoint | Standard API practice; evaluators and Docker healthchecks need it | Low | GET /api/health returning system status |
| Docker containerization | PRD requirement; makes demo reproducible for evaluators on any machine | Medium | docker-compose with frontend, backend, postgres services |

## Differentiators

Features that elevate this from "another student project" to "publishable academic work." Not strictly required, but significantly improve evaluation scores.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Cross-modal attention fusion | Academic novelty over simple concatenation MLP; most student projects use single-modality or naive fusion | High | Stage 2 upgrade: attention mechanism that learns audio-visual correlation. This is the key academic contribution. Provides comparison experiment (MLP vs attention). |
| Audio-visual synchronization check | Lip-sync deepfakes are a major attack vector; checking A/V sync is a strong signal | High | Compare temporal alignment of audio phonemes with lip movements. DEFER unless time permits -- very complex. |
| IPFS content storage with CID | Proves immutable storage, not just hash registration; strengthens provenance chain | Medium | Pin file metadata/report to IPFS via Pinata; store CID on-chain alongside hash |
| PDF verification report export | Professional output that can be attached to academic submissions or shared | Medium | Generate downloadable PDF with verdict, scores, blockchain proof, timestamps |
| Per-frame confidence timeline | Shows HOW the model analyzed the video, not just final score; demonstrates temporal analysis | Medium | Chart showing frame-by-frame deepfake probability over video duration |
| Silent/no-speech audio fallback | Handles edge case where video has no speech (music, ambient); shows robustness | Low | WebRTC VAD detects no speech, system falls back to visual-only with clear indication |
| Batch analysis support | Evaluators may want to test many files; batch mode saves time | Medium | Upload multiple files, queue processing, show aggregate results. Nice-to-have only. |
| Smart contract event logging | Emitting events on registration makes the contract auditable and queryable | Low | Emit `MediaRegistered(hash, timestamp, ipfsCid)` event in Solidity contract |
| Model confidence calibration display | Shows the model knows what it does not know; academically rigorous | Medium | Display whether the model's confidence is well-calibrated (e.g., "high confidence" vs "uncertain") |
| Comparison mode (two videos side-by-side) | Useful for demo: show original vs deepfake analyzed simultaneously | Medium | Split-screen UI comparing two analysis results |

## Anti-Features

Features to explicitly NOT build. Building these would waste time, add complexity, or misrepresent the project scope.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| User authentication and accounts | Academic prototype; adds weeks of work (auth flows, session management, password reset) with zero academic value | Open access; anyone can upload and analyze. Add a note in docs that auth would be added for production. |
| Real-time video stream analysis | Requires WebSocket streaming, continuous inference, GPU optimization far beyond prototype scope | File upload only. Document "real-time analysis" as future work in the thesis. |
| Model training in the application | Training ResNet-50 or Wav2Vec2 requires GPU hours, dataset management, training loops -- orthogonal to the detection+blockchain contribution | Train separately on Google Colab with DFDC/FakeAVCeleb. Export weights. Application does inference only. |
| Mainnet Ethereum deployment | Real ETH costs real money; testnet proves the concept identically | Sepolia testnet. Document that mainnet deployment is a configuration change, not an architecture change. |
| Explainability heatmaps (GradCAM) | Requires gradient computation through frozen backbone, significant implementation effort, and careful visualization -- a separate research contribution | Show per-modality scores and confidence. List GradCAM as future work. Could revisit if time permits. |
| Mobile application | React Native/Flutter port adds months of work; web works on mobile browsers adequately | Responsive web design. Test on mobile Chrome for the demo. |
| Multi-language audio support | Wav2Vec2 base is English-centric; multilingual models add complexity with minimal academic payoff | Document English-focused; note multilingual as future extension. |
| Audio-only file analysis | Requires different pipeline entry point; videos always have visual track | Require video input. If audio-only detection is needed, it is a different project. |
| Payment or subscription system | Academic prototype; no monetization | Free and open. |
| Admin dashboard | No users to administer; adds CRUD complexity for no academic value | Single-user prototype. Analysis history serves the "dashboard" need. |
| Custom model architecture design | Designing novel neural architectures is a PhD-level ML contribution, not the focus of this project | Use established architectures (ResNet-50, Wav2Vec2) with frozen weights. The fusion layer is the contribution. |
| Decentralized storage redundancy | Pinning to multiple IPFS providers, Filecoin backup, etc. -- over-engineering for prototype | Single Pinata pin is sufficient. Document redundancy as production concern. |

## Feature Dependencies

```
Video Upload --> FFmpeg Preprocessing --> [Frame Extraction, Audio Extraction]
Frame Extraction --> ResNet-50 Visual Analysis
Audio Extraction --> WebRTC VAD --> Wav2Vec2 Audio Analysis (or silent fallback)
Visual Analysis + Audio Analysis --> Fusion Layer (Stage 1: MLP)
Fusion Layer --> Detection Verdict + Confidence Score
Detection Verdict --> Results Display (modality breakdown, confidence)
Detection Verdict (REAL) --> Blockchain Registration --> Smart Contract Call
Smart Contract Call --> Transaction Hash + Explorer Link
Smart Contract Call --> IPFS Pin (metadata) --> CID stored on-chain
Blockchain Registration --> Verification Service (re-upload check)
All Results --> PostgreSQL Storage --> History Page
Detection Verdict + Blockchain Record --> PDF Report Export

Stage 1 MLP Fusion --> Stage 2 Cross-Modal Attention (upgrade path)
```

**Critical path:** Upload --> FFmpeg --> Dual-stream analysis --> Fusion --> Verdict. Everything else branches from the verdict.

**Blockchain dependency:** Registration should only happen for files classified as REAL (or user-initiated). Do not auto-register everything -- that defeats the purpose of provenance verification.

## MVP Recommendation

**Phase 1 -- Detection Pipeline (highest priority):**
1. Video upload with format validation and progress
2. FFmpeg preprocessing (frame + audio extraction)
3. ResNet-50 visual analysis
4. Wav2Vec2 audio analysis with silent fallback
5. Stage 1 fusion (concatenation MLP)
6. Results display with modality breakdown

**Phase 2 -- Blockchain Provenance:**
7. Solidity smart contract for hash registration
8. Web3.py integration with Sepolia
9. IPFS storage via Pinata
10. Verification service (re-upload check)
11. Transaction explorer links

**Phase 3 -- Polish and Academic Value:**
12. Cross-modal attention fusion (Stage 2) -- key academic differentiator
13. Per-frame confidence timeline
14. PDF report export
15. Analysis history page
16. Docker containerization

**Defer indefinitely:**
- Batch analysis: Nice but not needed for academic evaluation
- Comparison mode: Demo convenience only
- A/V sync check: Too complex for the timeline; document as future work
- GradCAM heatmaps: Separate research contribution

## Competitive Landscape Context

**Commercial products** (Sensity AI, Deepware Scanner, Reality Defender):
- Focus on API-as-a-service, enterprise dashboards, real-time monitoring
- These set user expectations but are NOT the benchmark for an academic prototype
- They have teams of 20+ and millions in funding; do not try to match their feature set

**Academic projects in this space typically offer:**
- Single-modality detection (video OR audio, rarely both)
- No blockchain integration (this is the differentiator)
- Command-line or Jupyter notebook interface (having a web UI is already above average)
- No provenance verification loop

**This project's unique positioning:**
- Multimodal (audio + visual) detection -- above most academic work
- Blockchain provenance registration -- novel combination with detection
- Full web application -- exceeds typical academic prototype polish
- Two-stage fusion comparison -- provides academic experiment/results

The combination of multimodal detection + blockchain verification + web UI is the differentiator. Each piece individually exists, but the integrated pipeline is the contribution.

## Sources

- Training data knowledge of: Sensity AI, Deepware Scanner, Microsoft Video Authenticator, Intel FakeCatcher, Resemble Detect (deepfake detection products)
- Training data knowledge of: Numbers Protocol, Starling Framework, C2PA/Content Credentials initiative (media provenance/blockchain)
- Training data knowledge of: DFDC challenge entries, FaceForensics++ benchmarks, FakeAVCeleb paper methodologies
- Project context from .planning/PROJECT.md and .planning/codebase/ analysis files
- **Confidence note:** All competitive product features are based on training data (cutoff ~mid-2025). Feature sets may have changed. Core patterns (upload, verdict, confidence score) are stable and unlikely to have shifted. MEDIUM confidence overall.
