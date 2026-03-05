# Domain Pitfalls

**Domain:** Blockchain-enhanced audiovisual deepfake detection system
**Project:** TrustChain-AV
**Researched:** 2026-03-05

---

## Critical Pitfalls

Mistakes that cause rewrites, demo failures, or fundamentally broken systems.

### Pitfall 1: Audio-Visual Temporal Misalignment

**What goes wrong:** Frame extraction and audio extraction happen independently, producing feature sequences that are not temporally aligned. The fusion layer receives visual features from frame 0-N and audio features from chunk 0-M where the time boundaries do not match. The model learns spurious correlations instead of genuine cross-modal signals.

**Why it happens:** FFmpeg frame extraction at a fixed FPS (e.g., 1 frame/sec) and Wav2Vec2 processing audio in 20ms windows produce outputs on completely different timescales. Teams concatenate these features without aligning their temporal positions, treating them as independent signals rather than synchronized streams.

**Consequences:** The fusion layer cannot learn lip-sync inconsistencies or audio-visual mismatches -- the exact signals that distinguish deepfakes. Detection accuracy drops to near-random on sophisticated fakes that only exhibit cross-modal artifacts.

**Warning signs:**
- Model performs well on visual-only deepfakes but poorly on lip-sync or voice-swap fakes
- Removing the audio branch does not change accuracy (audio features are being ignored)
- Cross-modal attention weights are uniform (not attending to specific temporal positions)

**Prevention:**
- Use a consistent temporal reference: extract frames at known timestamps, segment audio at the same timestamps
- For the concatenation MLP (Stage 1), this matters less since you average-pool both modalities. But for cross-modal attention (Stage 2), you MUST align frame-level features with corresponding audio segments
- Store timestamps alongside features throughout the pipeline

**Detection:** Compare model accuracy with and without the audio branch. If removing audio changes accuracy by less than 2%, temporal alignment is likely broken.

**Phase relevance:** Phase covering FFmpeg preprocessing and feature extraction. Must be correct before fusion layer training.

---

### Pitfall 2: Dataset Distribution Mismatch Leading to Overfit Metrics

**What goes wrong:** The model achieves 95%+ accuracy on DFDC/FakeAVCeleb test splits but fails badly on real-world uploads. The team reports the high test accuracy in the demo, then the system misclassifies obvious deepfakes (or flags real videos as fake) during live testing.

**Why it happens:** DFDC and FakeAVCeleb have specific generation methods (face-swap, lip-sync, reenactment), compression artifacts, and demographic distributions. A model trained on these datasets learns dataset-specific artifacts (compression fingerprints, specific GAN signatures, background patterns) rather than generalizable deepfake features. The test split comes from the same distribution, so it looks good on paper.

**Consequences:** The core value proposition -- "detect deepfakes" -- fails on any video not matching the training distribution. For a demo/evaluation, this can be career-ending if evaluators bring their own test videos.

**Warning signs:**
- Accuracy above 95% with a simple concatenation MLP (suspiciously high for a hard problem)
- Model is very confident (>0.95) on almost all predictions
- Performance drops dramatically when testing with videos from YouTube or other sources
- ResNet-50 features alone (without audio) achieve nearly the same accuracy

**Prevention:**
- Test on held-out datasets NOT used during training (e.g., train on DFDC, test on FakeAVCeleb and vice versa)
- Include a "wild test set" of 20-30 manually collected real and fake videos from diverse sources
- Use cross-dataset evaluation in the academic report -- this is what reviewers look for
- Set realistic accuracy expectations: 85-90% cross-dataset is excellent for this architecture

**Detection:** Run inference on 10 random YouTube videos of real people and 10 obvious deepfakes from social media. If accuracy drops below 70%, the model has overfit to training distribution.

**Phase relevance:** Phase covering model training (on Colab) and integration testing. Must validate before demo preparation.

---

### Pitfall 3: Blockchain Registration of Fake Media

**What goes wrong:** The system registers ANY video on the blockchain -- both real and fake. A user uploads a deepfake, gets a "FAKE" verdict, but can still register it on-chain. Now there is a blockchain record for a deepfake, which defeats the entire purpose of provenance verification.

**Why it happens:** The detection pipeline and blockchain registration are built as independent features without enforcing the logical constraint: only REAL-classified media should be eligible for blockchain registration. Teams build both features in parallel and forget to wire the conditional logic.

**Consequences:** The blockchain becomes a registry of all uploaded media, not a trust anchor for authentic media. The verification feature becomes meaningless -- "verified on blockchain" no longer implies "verified as authentic."

**Warning signs:**
- No conditional check between detection verdict and blockchain registration API call
- UI shows "Register on Blockchain" button regardless of detection result
- Smart contract accepts any hash without an associated verdict

**Prevention:**
- Enforce at the API level: the blockchain registration endpoint must reject requests for videos classified as FAKE
- Store the detection verdict alongside the hash in the smart contract (not just the hash)
- UI must disable/hide blockchain registration for FAKE verdicts
- Smart contract should store: `hash -> {verdict, confidence, timestamp, registrant}`

**Detection:** Try registering a FAKE-classified video on the blockchain. If it succeeds, this pitfall is present.

**Phase relevance:** Phase covering blockchain integration. Must be enforced at smart contract level AND API level (defense in depth).

---

### Pitfall 4: Sepolia Testnet Instability Killing Demos

**What goes wrong:** The demo is scheduled. Sepolia is congested or down. Blockchain transactions hang for 5+ minutes or fail entirely. The blockchain verification feature -- half the project's value proposition -- is non-functional during the evaluation.

**Why it happens:** Sepolia is a free testnet. It has no SLA, experiences periodic congestion, and sometimes undergoes network upgrades or resets. Teams build their entire blockchain flow assuming reliable testnet availability and discover during the demo that transactions take 60+ seconds or fail outright.

**Consequences:** Half the project cannot be demonstrated. Evaluators see a loading spinner for the blockchain section.

**Warning signs:**
- Blockchain transactions occasionally take >30 seconds during development
- Sepolia faucets are frequently dry (can not get test ETH)
- No fallback behavior when blockchain is unavailable

**Prevention:**
- Implement a mock/fallback mode: if the blockchain transaction fails after 15 seconds, show a "pending" state with the transaction details rather than blocking the UI
- Pre-register 5-10 sample videos on the blockchain BEFORE the demo so verification lookups work even if new registrations are slow
- Cache blockchain transaction results in PostgreSQL so the UI can show historical registrations without hitting the chain
- Have a local Hardhat node as a backup: `npx hardhat node` runs a local chain with instant confirmations
- Test with Hardhat local node during development; only use Sepolia for final integration testing

**Detection:** Run 10 blockchain registrations in a row. If any take >15 seconds or fail, you need a fallback.

**Phase relevance:** Phase covering blockchain integration and demo preparation. Fallback mode must be built alongside the primary blockchain flow, not as an afterthought.

---

### Pitfall 5: Model File Size Crashing Deployment

**What goes wrong:** ResNet-50 is ~100MB. Wav2Vec2-base is ~360MB. Combined with PyTorch itself (~800MB), the Docker image balloons to 3-5GB. Container builds take forever, Docker Compose startup times out, and the system runs out of memory on modest hardware.

**Why it happens:** ML frameworks and pretrained weights are enormous. Teams add `torch`, `torchvision`, `torchaudio`, and `transformers` to `requirements.txt` without considering the deployment footprint. GPU-enabled PyTorch wheels are even larger (~2GB for CUDA builds).

**Consequences:** Docker builds take 20+ minutes. Container images are 5GB+. Starting all containers via Docker Compose requires 8GB+ RAM. The team's laptops struggle to run the full stack.

**Warning signs:**
- `docker build` takes >10 minutes
- Docker image size exceeds 3GB
- Container OOM-kills during model loading
- Team members with 8GB RAM laptops cannot run the full stack

**Prevention:**
- Use CPU-only PyTorch: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu` (saves ~1.5GB)
- Use multi-stage Docker builds: build stage installs dependencies, runtime stage copies only what is needed
- Download model weights at build time and cache them in the Docker image (do not download at runtime)
- Set PyTorch memory limits: `torch.set_num_threads(2)` to prevent CPU thread explosion
- Consider ONNX export of both models to eliminate the PyTorch runtime dependency entirely (inference only needs `onnxruntime` at ~50MB)
- Allocate specific memory limits in `docker-compose.yml`: `mem_limit: 4g` for the ML service

**Detection:** Build the Docker image and check its size with `docker images`. If >3GB, optimization is needed.

**Phase relevance:** Phase covering Docker containerization. Must be addressed before the team tries to run the full stack locally.

---

## Moderate Pitfalls

### Pitfall 6: Wav2Vec2 Failing Silently on Non-Speech Audio

**What goes wrong:** Many videos have background music, silence, or ambient noise instead of speech. Wav2Vec2 is trained on speech data and produces meaningless features for non-speech audio. The model makes predictions based on garbage audio features but reports high confidence.

**Why it happens:** Wav2Vec2 does not refuse non-speech input -- it produces a feature vector regardless. Without explicit speech detection (VAD), the pipeline treats music or silence as if it were speech and feeds those features to the fusion layer.

**Consequences:** Incorrect predictions for any video without clear speech. Confidence scores are misleading because the model does not know its audio features are meaningless.

**Prevention:**
- Implement WebRTC VAD (already in the PRD) BEFORE Wav2Vec2 feature extraction
- If VAD detects <2 seconds of speech in the video, flag the result as "visual-only analysis" and zero out or exclude audio features
- Report to the user: "Audio analysis unavailable -- insufficient speech detected"
- Train the fusion layer with both audio-present and audio-absent examples (randomly zero out audio features during training with 20% probability)

**Detection:** Upload a video with only music (no speech). If the system reports audio-based confidence without a warning, this pitfall is present.

**Phase relevance:** Phase covering audio pipeline (FFmpeg extraction + Wav2Vec2). VAD must be implemented first.

---

### Pitfall 7: IPFS Pinata Free Tier Limits

**What goes wrong:** Pinata free tier allows 500 uploads and 1GB storage. During development and testing, the team exhausts the quota before the demo. IPFS uploads fail silently or return 429 errors.

**Why it happens:** Each test upload pins a file to IPFS. With a team of 4 testing regularly, 500 pins are consumed quickly. Nobody monitors the quota until uploads start failing.

**Consequences:** IPFS storage feature stops working mid-development or during the demo.

**Prevention:**
- Track Pinata API usage: log remaining quota after each upload
- Use Pinata only for final integration testing and demos -- mock the IPFS upload during development
- Create an IPFS service abstraction that can switch between real Pinata and a mock that returns a fake CID
- Consider storing only the metadata (hash, verdict, timestamp) on IPFS rather than the full video file -- dramatically reduces storage consumption
- Unpin test uploads after testing: `pinata.unpin(cid)` frees quota

**Detection:** Check Pinata dashboard for remaining storage and pin count weekly.

**Phase relevance:** Phase covering IPFS integration. Mock-first approach from day one.

---

### Pitfall 8: Smart Contract Gas Costs and Optimization

**What goes wrong:** The smart contract stores too much data on-chain (full metadata, strings, arrays). Each registration costs excessive gas. On Sepolia this does not matter (free ETH), but the contract architecture is academically indefensible because it would be unusable on mainnet. Evaluators may question this.

**Why it happens:** Solidity beginners store everything on-chain because storage is "free" on testnets. The contract ends up with string fields, dynamic arrays, and mappings of mappings that would cost $50+ per transaction on mainnet.

**Consequences:** Academically weak architecture. Contract is not a credible prototype because it ignores real-world cost constraints.

**Prevention:**
- Store only the minimum on-chain: `bytes32 contentHash`, `bytes32 ipfsCidHash`, `uint256 timestamp`, `address registrant`, `uint8 verdict`
- Store detailed metadata (filename, confidence scores, analysis details) on IPFS -- reference the CID on-chain
- Document the gas cost per registration in the report (use Hardhat gas reporter)
- Compare with a naive approach in the academic write-up to demonstrate optimization awareness

**Detection:** Run `npx hardhat test --gas` and check gas costs per function call. If `registerMedia` costs >100,000 gas, the contract is storing too much on-chain.

**Phase relevance:** Phase covering smart contract development. Design the data split (on-chain vs. IPFS) before writing the contract.

---

### Pitfall 9: FFmpeg Preprocessing Becoming the Bottleneck

**What goes wrong:** For a 5-minute video, FFmpeg frame extraction at 1 FPS produces 300 frames. Processing each through ResNet-50 takes ~50ms, totaling 15 seconds just for visual features. Audio extraction and Wav2Vec2 processing adds more. The 30-second inference target is exceeded before the fusion layer even runs.

**Why it happens:** Teams extract too many frames or process them sequentially. FFmpeg itself is fast, but feeding hundreds of frames through ResNet-50 one at a time is slow.

**Consequences:** The 30-second performance target is missed. Users wait 60+ seconds for results.

**Prevention:**
- Extract frames at 0.5 FPS or lower (150 frames for 5 min is plenty)
- Batch ResNet-50 inference: process 16-32 frames at once (batch dimension)
- Run audio and visual extraction in parallel (async with `asyncio` or `concurrent.futures`)
- For the fusion layer, average-pool frame-level features into a single 2048-dim vector -- do not pass all 300 frame features individually
- Profile the pipeline early: measure time per stage (extraction, visual inference, audio inference, fusion, blockchain) and optimize the slowest stage
- Consider extracting only keyframes (`-vf "select=eq(pict_type\\,I)"`) instead of uniform sampling

**Detection:** Time each pipeline stage separately. If any stage takes >10 seconds for a 5-minute video, it needs optimization.

**Phase relevance:** Phase covering FFmpeg preprocessing and ML inference pipeline.

---

### Pitfall 10: Web3.py Async Incompatibility with FastAPI

**What goes wrong:** Web3.py's default synchronous HTTP provider blocks the FastAPI event loop. When a blockchain transaction is pending (10-30 seconds on Sepolia), ALL other API requests are blocked. The entire backend becomes unresponsive.

**Why it happens:** FastAPI is async (built on ASGI), but Web3.py's default provider is synchronous. Calling `w3.eth.send_transaction()` in an async route handler blocks the event loop without yielding.

**Consequences:** During blockchain registration, the backend cannot process new upload requests, health checks fail, and the frontend appears frozen.

**Prevention:**
- Use `Web3.AsyncHTTPProvider` with `AsyncWeb3` (available in Web3.py v6+)
- Alternatively, run synchronous Web3 calls in a thread pool: `await asyncio.to_thread(w3.eth.send_transaction, tx)`
- Better yet: make blockchain registration a background task (FastAPI `BackgroundTasks` or Celery) -- return immediately with a "pending" status and let the client poll for completion
- Never await a blockchain transaction in the request-response cycle

**Detection:** Start a blockchain registration, then immediately try to upload another video. If the upload hangs until the registration completes, the event loop is blocked.

**Phase relevance:** Phase covering FastAPI backend and blockchain integration. Architecture decision must be made before implementation.

---

### Pitfall 11: Fusion Layer Training Data Leakage

**What goes wrong:** The fusion layer is trained on Colab using DFDC + FakeAVCeleb. The team splits by video clip, but multiple clips come from the same source identity or the same manipulation method. The model memorizes identity-specific or method-specific features rather than learning general deepfake artifacts.

**Why it happens:** DFDC contains multiple fake versions of the same source video (different manipulation methods applied to the same person). Splitting randomly by clip puts different manipulations of the same person in both train and test sets. The model learns to recognize specific faces rather than deepfake artifacts.

**Consequences:** Inflated test accuracy. Model fails on new identities not seen during training.

**Prevention:**
- Split by source identity, not by clip: all clips of person X must be in the same split (train OR test, not both)
- For FakeAVCeleb, split by celebrity identity
- For DFDC, split by the original video ID (not the manipulated clip ID)
- Document the split strategy in the academic report -- reviewers specifically look for this

**Detection:** Check if the same person appears in both train and test sets. If yes, re-split.

**Phase relevance:** Phase covering model training (Colab). Must be correct before training begins.

---

## Minor Pitfalls

### Pitfall 12: SHA-256 Collision Between Formats

**What goes wrong:** The same video content re-encoded in a different container (MP4 vs MKV) produces a different SHA-256 hash. A user registers an MP4 on the blockchain, then verifies with the same content in MKV format -- verification fails even though the content is identical.

**Prevention:** Document this limitation explicitly in the UI. Consider hashing decoded frame/audio data rather than raw file bytes (computationally expensive but format-independent). For the prototype, file-level hashing is acceptable if the limitation is documented.

**Phase relevance:** Verification feature implementation.

---

### Pitfall 13: Frontend Upload Progress Misleading Users

**What goes wrong:** The upload progress bar reaches 100% when the file transfer completes, but the actual analysis takes another 20-30 seconds. Users think the process is stuck.

**Prevention:** Implement a multi-stage progress indicator: "Uploading... -> Extracting frames... -> Analyzing video... -> Analyzing audio... -> Running detection... -> Registering on blockchain..." Use server-sent events (SSE) or WebSocket to push stage updates from the backend.

**Phase relevance:** Phase covering frontend upload dashboard and backend job processing.

---

### Pitfall 14: Hardhat + Web3.py Version Mismatch

**What goes wrong:** Hardhat generates ABI and contract artifacts in its own format. Web3.py expects the ABI as a JSON list. Teams manually copy-paste the ABI or use incompatible artifact formats, causing silent type errors in contract interactions.

**Prevention:**
- Use Hardhat's compilation output directly: `artifacts/contracts/MediaRegistry.sol/MediaRegistry.json` contains the ABI
- Write a script that extracts the ABI from Hardhat artifacts and writes it to a location the Python backend can read
- Pin specific versions: Hardhat 2.19+, Web3.py 6.x+, Solidity 0.8.19+
- Test the full flow (compile -> deploy -> interact) in a single integration test using Hardhat's local node

**Phase relevance:** Phase covering smart contract development and Web3.py integration.

---

### Pitfall 15: PostgreSQL Schema Migration Nightmares

**What goes wrong:** The database schema changes during development (adding columns, changing types). Without a migration tool, the team drops and recreates tables, losing test data. Or worse, each team member has a different schema version.

**Prevention:**
- Use Alembic (SQLAlchemy's migration tool) from day one -- do not create tables with raw SQL
- Define models with SQLAlchemy ORM, generate migrations with `alembic revision --autogenerate`
- Include migration in Docker Compose startup: `alembic upgrade head` before starting FastAPI
- Never manually modify the database schema

**Phase relevance:** Phase covering database setup. Alembic must be configured alongside the initial schema.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| FFmpeg preprocessing | Temporal misalignment (Pitfall 1), Performance bottleneck (Pitfall 9) | Align timestamps, batch processing, parallel extraction |
| Audio pipeline (Wav2Vec2) | Silent failure on non-speech (Pitfall 6) | Implement VAD first, handle audio-absent gracefully |
| ML fusion layer training | Data leakage (Pitfall 11), Distribution mismatch (Pitfall 2) | Identity-based splits, cross-dataset evaluation |
| Smart contract development | Excessive on-chain storage (Pitfall 8), Registering fakes (Pitfall 3) | Minimal on-chain data, verdict-gated registration |
| Blockchain integration | Testnet instability (Pitfall 4), Event loop blocking (Pitfall 10) | Local Hardhat fallback, async/background tasks |
| IPFS integration | Free tier limits (Pitfall 7) | Mock-first, metadata-only storage, quota monitoring |
| Docker containerization | Image size explosion (Pitfall 5) | CPU-only PyTorch, multi-stage builds, ONNX consideration |
| Database setup | Schema migration (Pitfall 15) | Alembic from day one |
| Frontend dashboard | Misleading progress (Pitfall 13) | Multi-stage SSE progress updates |
| Verification feature | Hash format sensitivity (Pitfall 12) | Document limitation, file-level hashing is acceptable for prototype |
| Demo preparation | Testnet failure (Pitfall 4), Model overfit exposed (Pitfall 2) | Pre-register samples, prepare diverse test videos, Hardhat local fallback |

## Sources

- Project context: `.planning/PROJECT.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/ARCHITECTURE.md`
- Domain knowledge: PyTorch model deployment patterns, Ethereum smart contract best practices, DFDC/FakeAVCeleb dataset documentation, Web3.py async patterns, Pinata API tier limits
- Confidence: MEDIUM overall -- pitfalls are drawn from established domain knowledge and the specific project constraints documented in PROJECT.md. WebSearch was unavailable for verification against 2026-specific community reports.

---

*Pitfalls research: 2026-03-05*
