# TrustChain-AV: Project Report

**Date:** April 8, 2026
**Project Phase:** Phase 4 completed; Transitioning to Phase 5 (Blockchain Layer)
**Institution:** IIIT Pune, Computer Engineering

## 1. Executive Summary
**TrustChain-AV** is a final year project prototype providing a blockchain-enhanced audiovisual deepfake detection system. The application allows users to upload video files, which are analyzed through a multimodal artificial intelligence pipeline (combining visual and audio streams) to determine authenticity. Authentic media is ultimately intended to be cryptographically hashed and registered on the Ethereum Sepolia testnet via IPFS, providing a tamper-proof provenance record.

## 2. Core Architecture
The system employs a modern, loosely-coupled architecture partitioned across independent microservices:

* **Frontend:** Built with React, TailwindCSS v4, and Shadcn UI. Features include drag-and-drop file staging, a multi-card results dashboard, and a paginated history table.
* **Backend:** A FastAPI engine structured around background async jobs.
* **Database:** PostgreSQL storing video metadata, analysis tasks, and blockchain records securely.
* **Orchestration:** Managed via Docker and Docker Compose for deterministic environments and easy deployment.

## 3. The Multimodal Intelligence Pipeline
TrustChain-AV executes concurrent analyses to produce an accurate determination:
1. **Visual Stream (ResNet-50):** The video stream undergoes frame extraction. A pre-trained, frozen ResNet-50 model mathematically translates visual traits into a 2048-dimensional feature vector.
2. **Audio Stream (Wav2Vec 2.0):** Simultaneously, the audio stream is parsed using a Hugging Face `Wav2Vec2` backbone, generating a 768-dimensional feature vector. WebRTC VAD (Voice Activity Detection) handles instances of absent or silent speech.
3. **The Fusion Layer:** The outputs are concatenated (2816 dimensions) and fed into a custom Multi-Layer Perceptron (FusionMLP) mapping the data natively to a binary probability (`Real` vs `Fake`).

### Custom Offline Training Strategy
To avoid inflating the application image with terabytes of raw datasets, the FusionMLP layer utilizes an explicit cloud extraction strategy:
* We leverage cloud platforms (e.g., Kaggle/Colab) parsing large-scale datasets (like FakeAVCeleb or DFDC) natively.
* The extracted lightweight `.pt` tensors are moved locally to our training rig (RTX 5070 Ti, 64GB RAM).
* Fast local PyTorch DataLoaders orchestrate Binary Cross-Entropy and AdamW gradient descent iterations, outputting optimized `fusion_weights.pth` which seamlessly attach to our live API.

## 4. Current Progress & Metrics
The project workflow is strictly governed by a 5-phase delivery cycle.

**Completed Phases:**
* **Phase 1: Foundation** (FastAPI, React routing, DB schemas)
* **Phase 2: Preprocessing** (Video/Audio extraction, FFmpeg)
* **Phase 3: Detection** (ResNet50 + Wav2Vec2 + FusionMLP Async Inference)
* **Phase 4: Results UI** (History dashboard & PDF Report Generator)

**Velocity Trends:**
* Work distribution shows exceptionally rapid velocity. A total of 10 structural plans correctly executed. 
* Average phase components are implemented rapidly (~6-10 minute implementation averages during execution sessions).

## 5. Next Steps (Phase 5: Blockchain Layer)
The forthcoming phase is the integration of the immutable transaction layer:
1. **Solidity Smart Contract:** Designing and compiling a secure mechanism for IPFS media registration.
2. **Sepolia Deployment:** Testnet deployment via Hardhat.
3. **Web3.py Connection:** The background FastAPI workers will directly interop with the contract to confirm hashes upon user request.
4. **Blockchain UI Update:** Modifying the History table components and Results outputs to display direct Etherscan linkage for validated uploads.
