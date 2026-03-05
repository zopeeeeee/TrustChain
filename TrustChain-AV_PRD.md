# Product Requirements Document
# TrustChain-AV: Blockchain-Enhanced Audiovisual Deepfake Detection System

**Version:** 1.0  
**Date:** March 2026  
**Team:** Vedant Zope, Siddhant Borude, Atharv Bodhane, Ninad Waskar  
**Guide:** Dr. Poonam Deokar  
**Institution:** International Institute of Information Technology, Pune  
**Department:** Computer Engineering

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Goals & Success Metrics](#3-goals--success-metrics)
4. [System Architecture Overview](#4-system-architecture-overview)
5. [Technology Stack](#5-technology-stack)
6. [Detailed Module Specifications](#6-detailed-module-specifications)
   - 6.1 Frontend UI
   - 6.2 Backend API
   - 6.3 Preprocessing Pipeline
   - 6.4 Audio Detection — Wav2Vec2
   - 6.5 Visual Detection — ResNet-50
   - 6.6 Voice Activity Detection (Fallback)
   - 6.7 Fusion Layer
   - 6.8 Blockchain Layer
   - 6.9 IPFS Storage
   - 6.10 Verification Service
7. [Build Phases](#7-build-phases)
   - Phase 1: Core Detection Pipeline
   - Phase 2: Fusion Layer Upgrade + Blockchain Integration
8. [Fusion Layer — Detailed Design](#8-fusion-layer--detailed-design)
   - Stage 1: Concatenation MLP
   - Stage 2: Cross-Modal Attention
9. [Training Strategy](#9-training-strategy)
10. [Dataset Plan](#10-dataset-plan)
11. [API Specifications](#11-api-specifications)
12. [Database Schema](#12-database-schema)
13. [UI Screens & User Flows](#13-ui-screens--user-flows)
14. [Non-Functional Requirements](#14-non-functional-requirements)
15. [Risks & Mitigations](#15-risks--mitigations)
16. [Out of Scope](#16-out-of-scope)
17. [Glossary](#17-glossary)

---

## 1. Project Overview

TrustChain-AV is a functional prototype that detects whether any video file is AI-generated or manipulated (deepfake) and cryptographically proves the authenticity of genuine media using blockchain technology. The system is content-agnostic — it works on any video regardless of whether it contains human faces, speech, or any specific type of content.

The system operates in two sequential phases:

- **Detection Phase:** A multimodal AI pipeline extracts features from both the audio and visual streams of a video and fuses them to produce a REAL/FAKE classification with a confidence score.
- **Verification Phase:** A blockchain-anchored provenance system generates a SHA-256 hash of the file, stores it on the Ethereum Sepolia testnet via a smart contract, and provides tamper-proof proof of authenticity on demand.

---

## 2. Problem Statement

Modern deepfake technology can manipulate both audio and video streams simultaneously, easily bypassing detectors that analyze only one modality. At the same time, traditional media verification methods like metadata and watermarks are trivially altered or removed.

There is a need for a unified system that can:

- Detect forgeries across both audio and visual signals simultaneously
- Operate on any video content, not just face-centric media
- Gracefully handle videos with no speech or poor audio quality
- Provide cryptographic, tamper-proof proof of a file's authenticity
- Present results in a clear, accessible interface for non-expert users

---

## 3. Goals & Success Metrics

### Primary Goals

| Goal | Metric | Target |
|---|---|---|
| Deepfake detection accuracy | Accuracy on test set | ≥ 90% |
| Blockchain registration time | Time from upload to on-chain record | ≤ 15 seconds |
| Inference latency | Time from upload to result | ≤ 30 seconds |
| Tamper detection | Flag any altered file | 100% |
| UI accessibility | Non-expert user can complete a verification flow | Without documentation |

### Secondary Goals

- Clear UI communication of which modalities were used in analysis
- Adaptive audio weighting based on speech presence
- Exportable verification report per media file
- Audit trail of all past verifications

---

## 4. System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND UI                               │
│                  React + TailwindCSS                             │
│           Upload Dashboard | Results | Verify | History          │
└─────────────────────────────┬────────────────────────────────────┘
                               │ HTTP / REST
┌─────────────────────────────▼────────────────────────────────────┐
│                      BACKEND API                                  │
│                   FastAPI (Python)                                │
│              File handling | Job routing | DB writes             │
└──────┬──────────────────────┬───────────────────────────────────┘
       │                       │
┌──────▼──────┐     ┌──────────▼──────────────────────────────────┐
│  PostgreSQL  │     │            AI DETECTION PIPELINE             │
│  Database    │     │                                              │
│  - uploads   │     │  ┌──────────────┐     ┌──────────────────┐  │
│  - results   │     │  │ Preprocessing │────►│   VAD Check      │  │
│  - tx hashes │     │  │ FFmpeg        │     │  (WebRTC VAD)    │  │
│  - ipfs cids │     │  │ Frames+Audio  │     └────────┬─────────┘  │
└─────────────┘     │  └──────┬───────┘              │             │
                    │         │              ┌─────────┴──────────┐ │
                    │   ┌─────┴──────┐       │  Speech Detected?  │ │
                    │   │            │       └─────────┬──────────┘ │
                    │   ▼            ▼            YES  │  NO        │
                    │ ResNet-50   Wav2Vec2          │   │           │
                    │ (frames)    (audio)      Wav2Vec2 Zero[768]  │
                    │   │            │              │   │           │
                    │   └─────┬──────┘              └───┘           │
                    │   [2048] │ [768]                               │
                    │         ▼                                      │
                    │   Layer Normalization                          │
                    │         │                                      │
                    │   Fusion Layer (MLP)                           │
                    │         │                                      │
                    │   REAL / FAKE + Confidence                     │
                    └─────────┬───────────────────────────────────┘
                               │
┌─────────────────────────────▼────────────────────────────────────┐
│                    BLOCKCHAIN + STORAGE LAYER                     │
│                                                                   │
│   SHA-256 Hash ──► Merkle Root ──► Ethereum Smart Contract        │
│                                    (Sepolia Testnet)              │
│                                                                   │
│   Video + Metadata ──► IPFS (via Pinata API)                      │
└──────────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────▼────────────────────────────────────┐
│                    VERIFICATION SERVICE                           │
│         Recompute Hash → Compare On-Chain → Proof Output          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + TailwindCSS | User interface |
| Backend | FastAPI (Python) | API server, job orchestration |
| Database | PostgreSQL | Persistent storage |
| Frame Extraction | FFmpeg + OpenCV | Video preprocessing |
| Audio Extraction | FFmpeg | Audio preprocessing |
| Speech Detection | WebRTC VAD (`webrtcvad`) | Fallback gate before Wav2Vec2 |
| Audio Model | Wav2Vec2 (HuggingFace `facebook/wav2vec2-base`) | Audio feature extraction |
| Visual Model | ResNet-50 (`torchvision.models`) | Visual feature extraction |
| Fusion Layer | Custom PyTorch MLP | Final REAL/FAKE classification |
| Deep Learning | PyTorch + HuggingFace Transformers | Model inference |
| Smart Contract | Solidity | On-chain hash registration |
| Blockchain Dev | Hardhat | Local testing + Sepolia deployment |
| Python ↔ Ethereum | Web3.py | Backend blockchain interaction |
| Decentralized Storage | IPFS via Pinata API | Video + metadata storage |
| Blockchain Network | Ethereum Sepolia Testnet | Free testnet, real blockchain behavior |
| Containerization | Docker + Docker Compose | Consistent environment |

---

## 6. Detailed Module Specifications

### 6.1 Frontend UI

**Technology:** React + TailwindCSS

**Screens:**
- **Upload Dashboard** — drag-and-drop video upload, file size/format validation, upload progress bar
- **Detection Results** — REAL/FAKE verdict, confidence score, modalities used, breakdown of audio vs visual signal
- **Blockchain Registration** — SHA-256 hash display, transaction hash, IPFS CID, Sepolia explorer link
- **Verification Page** — re-upload or enter hash to verify against blockchain record
- **History Page** — paginated table of all past analyses with status, date, and result

**Key UI Behaviors:**
- Show "Audio analyzed: Yes/No" on every result card
- Show "Decision based on: Visual + Audio / Visual only" depending on VAD result
- Display confidence as a percentage with a color-coded bar (green = real, red = fake)
- Show blockchain transaction status as a live progress indicator (Pending → Confirmed)

---

### 6.2 Backend API

**Technology:** FastAPI (Python)

**Responsibilities:**
- Accept video file uploads (multipart/form-data)
- Validate file format (MP4, AVI, MOV, MKV) and size (max 500MB)
- Spawn detection pipeline as a background job
- Write results to PostgreSQL
- Interact with Web3.py for blockchain registration
- Interact with Pinata API for IPFS upload
- Return job status and results to frontend via polling or WebSocket

**Key Design Decisions:**
- Detection runs asynchronously — frontend polls for job completion
- All model inference runs in a single Python process to avoid loading models multiple times
- Models are loaded once at server startup, not per request

---

### 6.3 Preprocessing Pipeline

**Technology:** FFmpeg + OpenCV

**Video Processing:**
- Extract one frame every N frames (N configurable, default = 10)
- Resize each frame to 224×224 pixels
- Normalize pixel values to ImageNet mean/std
- Output: tensor of shape `[num_frames, 3, 224, 224]`

**Audio Processing:**
- Extract audio track from video container
- Resample to 16kHz mono WAV (required by Wav2Vec2)
- Output: raw waveform tensor `[num_samples]`

**Edge Cases:**
- Video with no audio track → skip audio pipeline entirely, set `audio_weight = 0.0`
- Video shorter than 1 second → process all frames, no sampling
- Corrupted file → return error before reaching models

---

### 6.4 Audio Detection — Wav2Vec2

**Model:** `facebook/wav2vec2-base` from HuggingFace

**How it works:**
- Wav2Vec2 is a transformer pretrained on 960 hours of speech
- The final classification head is removed
- Raw waveform is passed through the model
- The hidden states from the last transformer layer are averaged across time
- Output: `[768-dim feature vector]` — a rich mathematical summary of the audio

**What it captures:**
- Unnatural speech rhythm and cadence
- Synthetic voice artifacts from TTS/voice-cloning models
- Temporal inconsistencies in the waveform

**Implementation Notes:**
- Model is loaded once at startup: `Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")`
- Backbone weights are **frozen** — no gradient updates
- Only the fusion layer is trained
- Audio must be exactly 16kHz mono before being passed in

---

### 6.5 Visual Detection — ResNet-50

**Model:** `torchvision.models.resnet50(pretrained=True)`

**How it works:**
- ResNet-50 is pretrained on ImageNet (1.2M images, 1000 classes)
- The final fully-connected classification layer (`fc`) is removed
- Each video frame is passed through the model independently
- The output of the global average pooling layer is used as the feature vector
- Per-frame vectors `[2048]` are averaged across all sampled frames
- Output: `[2048-dim feature vector]` — a visual summary of the entire video

**What it captures:**
- GAN grid artifacts and generation fingerprints
- Temporal inconsistency between frames
- Unnatural compression patterns from AI generation pipelines
- Frequency domain anomalies invisible to the human eye

**Implementation Notes:**
- Model loaded once: `resnet50 = torchvision.models.resnet50(pretrained=True)`
- Remove final layer: `resnet50.fc = nn.Identity()`
- Backbone weights are **frozen** — no gradient updates
- No face detection step — works on full frames for any content type

---

### 6.6 Voice Activity Detection (Fallback)

**Library:** `webrtcvad` (Python wrapper for Google's WebRTC VAD)

**Purpose:** Determine whether the audio track contains human speech before running the expensive Wav2Vec2 model.

**How it works:**
- Audio is split into 30ms frames
- VAD model classifies each frame as speech or non-speech
- If >20% of frames contain speech → `speech_detected = True`
- If ≤20% → `speech_detected = False`

**Fallback Behavior:**

| Condition | Wav2Vec2 | audio_weight | visual_weight |
|---|---|---|---|
| Speech detected | Run normally | 0.5 | 0.5 |
| No speech / silence | Skip, use zero vector | 0.0 | 1.0 |
| No audio track | Skip entirely | 0.0 | 1.0 |

**UI Communication:**
- Always show the user which modality was used and why
- "No speech detected — analysis based on visual signals only"

---

### 6.7 Fusion Layer

See Section 8 for full design details.

**Summary:**
- Input: concatenated `[2816-dim]` vector (visual 2048 + audio 768, weighted)
- Layer Normalization applied to each branch before concatenation
- Small MLP with ReLU activations and Dropout
- Output: single scalar score `[0.0 → 1.0]`
- Threshold at 0.5 → REAL (below) / FAKE (above)

---

### 6.8 Blockchain Layer

**Network:** Ethereum Sepolia Testnet  
**Language:** Solidity  
**Dev Tool:** Hardhat  
**Python Interface:** Web3.py

**Smart Contract Responsibilities:**
- Accept a file hash (bytes32) and store it with a timestamp
- Accept a Merkle root derived from the file hash and metadata
- Provide a lookup function: given a hash, return whether it exists and when it was registered

**Minimal Smart Contract (Solidity):**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TrustChainAV {
    struct MediaRecord {
        bytes32 merkleRoot;
        uint256 timestamp;
        string ipfsCID;
        bool exists;
    }

    mapping(bytes32 => MediaRecord) public records;

    event MediaRegistered(bytes32 indexed fileHash, uint256 timestamp);

    function registerMedia(
        bytes32 fileHash,
        bytes32 merkleRoot,
        string memory ipfsCID
    ) public {
        require(!records[fileHash].exists, "Already registered");
        records[fileHash] = MediaRecord(merkleRoot, block.timestamp, ipfsCID, true);
        emit MediaRegistered(fileHash, block.timestamp);
    }

    function verifyMedia(bytes32 fileHash) public view returns (bool, uint256, string memory) {
        MediaRecord memory r = records[fileHash];
        return (r.exists, r.timestamp, r.ipfsCID);
    }
}
```

**Deployment Flow:**
1. Write contract in Hardhat project
2. Test locally on Hardhat node
3. Deploy to Sepolia using Hardhat deploy script
4. Store deployed contract address in backend `.env`

**Registration Flow (per upload):**
1. Backend computes SHA-256 hash of the video file
2. Backend constructs JSON metadata (filename, timestamp, detection score, IPFS CID)
3. Backend builds Merkle tree from `[file_hash, metadata_hash]` → Merkle root
4. Backend calls `registerMedia()` on smart contract via Web3.py
5. Transaction hash stored in PostgreSQL

---

### 6.9 IPFS Storage

**Service:** Pinata API (free tier)

**What gets stored:**
- Original video file
- JSON metadata file containing:
  - Original filename
  - Upload timestamp
  - SHA-256 hash
  - Detection result (REAL/FAKE)
  - Confidence score
  - Modalities used
  - Blockchain transaction hash

**Flow:**
1. Upload video to Pinata → receive `videoCID`
2. Upload metadata JSON to Pinata → receive `metadataCID`
3. Store both CIDs in PostgreSQL
4. Register `metadataCID` on blockchain alongside file hash

---

### 6.10 Verification Service

**Purpose:** Allow anyone to re-verify a video's authenticity at any future point.

**Flow:**
1. User uploads video (or provides SHA-256 hash manually)
2. Backend recomputes SHA-256 hash of the file
3. Backend calls `verifyMedia(hash)` on smart contract
4. If hash exists on-chain:
   - Retrieve original registration timestamp
   - Retrieve IPFS CID → fetch original metadata
   - Compare current hash with registered hash
   - **Match → AUTHENTIC, display proof certificate**
   - **Mismatch → TAMPERED, display alert**
5. If hash not found on chain → **UNREGISTERED**, no proof available

---

## 7. Build Phases

### Phase 1 — Core Detection Pipeline (Weeks 1–4)

**Goal:** Get a working end-to-end detection pipeline with a simple fusion layer. No blockchain yet.

**Deliverables:**

- [ ] FFmpeg preprocessing pipeline (frame + audio extraction)
- [ ] ResNet-50 feature extractor (frozen backbone, remove final layer)
- [ ] Wav2Vec2 feature extractor (frozen backbone, remove final layer)
- [ ] WebRTC VAD integration with fallback logic
- [ ] Stage 1 Fusion Layer — Concatenation MLP (see Section 8)
- [ ] Train fusion layer on DFDC dataset (Google Colab)
- [ ] FastAPI backend with `/analyze` endpoint
- [ ] Basic React frontend (upload + result display)
- [ ] PostgreSQL schema setup

**Success Criteria for Phase 1:**
- System correctly classifies videos from test set with ≥85% accuracy
- Pipeline runs end-to-end in under 60 seconds
- VAD fallback correctly routes speech vs non-speech videos

---

### Phase 2 — Fusion Upgrade + Blockchain Integration (Weeks 5–8)

**Goal:** Upgrade fusion layer to cross-modal attention, integrate full blockchain + IPFS pipeline, polish UI.

**Deliverables:**

- [ ] Stage 2 Fusion Layer — Cross-Modal Attention (see Section 8)
- [ ] Compare Stage 1 vs Stage 2 accuracy — document improvement
- [ ] Fine-tune ResNet-50 last 2 layers on DFDC (optional, if GPU available)
- [ ] Solidity smart contract written and tested locally (Hardhat)
- [ ] Deploy smart contract to Sepolia testnet
- [ ] Web3.py integration in FastAPI backend
- [ ] Pinata IPFS upload integration
- [ ] Verification service endpoint `/verify`
- [ ] Blockchain registration endpoint `/register`
- [ ] Full UI — Results, Verify, History screens
- [ ] Verification report export (PDF)

**Success Criteria for Phase 2:**
- Detection accuracy ≥ 90% on test set
- Blockchain registration completes in ≤ 15 seconds
- Tamper detection rate = 100% (any byte change triggers mismatch)
- Full user flow works without errors on 10 diverse test videos

---

## 8. Fusion Layer — Detailed Design

### Stage 1: Concatenation MLP (Build First)

**Architecture:**

```
Visual Features [2048]          Audio Features [768]
        │                               │
  Layer Norm [2048]             Layer Norm [768]
        │                               │
        │           × audio_weight (0.0 or 0.5)
        │                               │
        └──────────── Concat ───────────┘
                          │
                     [2816-dim]
                          │
              Linear(2816 → 512)
                       ReLU
                   Dropout(0.3)
              Linear(512 → 128)
                       ReLU
               Linear(128 → 1)
                    Sigmoid
                          │
                    Score [0.0–1.0]
                          │
              ┌───────────┴───────────┐
           < 0.5                   ≥ 0.5
           REAL                    FAKE
```

**PyTorch Implementation:**

```python
class FusionMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.visual_norm = nn.LayerNorm(2048)
        self.audio_norm = nn.LayerNorm(768)
        self.mlp = nn.Sequential(
            nn.Linear(2816, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

    def forward(self, visual_feat, audio_feat, audio_weight=0.5):
        v = self.visual_norm(visual_feat)
        a = self.audio_norm(audio_feat) * audio_weight
        combined = torch.cat([v, a], dim=-1)  # [2816]
        return self.mlp(combined)
```

**Why Stage 1 first:**
- Fastest to implement and debug
- Gets the full pipeline running end-to-end quickly
- Provides a performance baseline to compare against Stage 2
- If time is limited, Stage 1 alone is a defensible submission

---

### Stage 2: Cross-Modal Attention (Upgrade in Phase 2)

**Core Idea:** Instead of blindly concatenating features, let the audio features "attend to" the most relevant parts of the visual features and vice versa. This explicitly models the relationship between what is seen and what is heard.

**Architecture:**

```
Visual Features [2048]          Audio Features [768]
        │                               │
Project to [512]               Project to [512]
        │                               │
        └──── Cross-Attention ──────────┘
               (V attends to A,
                A attends to V)
                       │
              Attended Features [512]
                       │
              Linear(512 → 128)
                     ReLU
               Linear(128 → 1)
                   Sigmoid
                       │
                Score [0.0–1.0]
```

**What Cross-Modal Attention Does:**

The attention mechanism learns to ask: *"Which audio features are most relevant given these visual features, and vice versa?"*

For example:
- Sees: mouth moving → attends to: speech audio features
- Hears: synthetic voice → attends to: lip-sync visual features
- Detects mismatch between the two → flags as FAKE

**PyTorch Implementation:**

```python
class CrossModalAttentionFusion(nn.Module):
    def __init__(self):
        super().__init__()
        self.visual_proj = nn.Linear(2048, 512)
        self.audio_proj = nn.Linear(768, 512)
        self.attention = nn.MultiheadAttention(embed_dim=512, num_heads=8, batch_first=True)
        self.classifier = nn.Sequential(
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

    def forward(self, visual_feat, audio_feat, audio_weight=0.5):
        v = self.visual_proj(visual_feat).unsqueeze(1)    # [B, 1, 512]
        a = self.audio_proj(audio_feat).unsqueeze(1) * audio_weight  # [B, 1, 512]
        attended, _ = self.attention(query=v, key=a, value=a)
        return self.classifier(attended.squeeze(1))
```

**Academic Value:** Comparing Stage 1 vs Stage 2 accuracy is a concrete experiment to include in your report — it demonstrates that cross-modal attention provides measurable improvement over naive concatenation.

---

## 9. Training Strategy

### What Gets Trained

| Component | Phase 1 | Phase 2 |
|---|---|---|
| ResNet-50 backbone | ❌ Frozen | ❌ Frozen (optionally unfreeze last 2 layers) |
| Wav2Vec2 backbone | ❌ Frozen | ❌ Frozen |
| Stage 1 Fusion MLP | ✅ Train | — |
| Stage 2 Attention Fusion | — | ✅ Train |

### Training Setup

**Environment:** Google Colab (free T4 GPU) or local GPU if available

**Loss Function:** Binary Cross Entropy (BCELoss) — suitable for binary REAL/FAKE classification

**Optimizer:** Adam with learning rate 1e-3

**Batch Size:** 32

**Epochs:** 20–30 (early stopping on validation loss)

**Train/Val/Test Split:** 70% / 15% / 15%

### Training Loop Summary

```
For each epoch:
  For each batch (visual_feats, audio_feats, audio_weights, labels):
    1. Forward pass through frozen ResNet → visual_feats
    2. Run VAD → determine audio_weight
    3. Forward pass through frozen Wav2Vec2 (if speech) → audio_feats
    4. Forward pass through Fusion Layer → prediction
    5. Compute BCELoss(prediction, label)
    6. Backpropagate → update only Fusion Layer weights
    7. Log loss + accuracy
  Evaluate on validation set
  Save best model checkpoint
```

### Phase 2 Optional Fine-Tuning

After Stage 2 fusion converges:
1. Unfreeze last 2 ResNet layers (`layer4`)
2. Use a much lower learning rate: 1e-5
3. Train for 5 more epochs
4. Compare accuracy before/after — document in report

---

## 10. Dataset Plan

| Dataset | Used For | Size | Free? |
|---|---|---|---|
| **DFDC (Facebook Deepfake Detection Challenge)** | Primary training — general visual manipulation | ~100k videos | ✅ |
| **FakeAVCeleb** | Audio-visual sync training, strengthens audio branch | ~20k clips | ✅ |
| **ASVspoof 2019 LA** | Audio-only fine-tuning reference (optional) | ~100k clips | ✅ |
| **WildDeepfake** | Out-of-distribution test set evaluation | ~7k clips | ✅ |

**Recommended Training Strategy:**
- Train primarily on DFDC (covers general manipulation)
- Supplement with FakeAVCeleb (strengthens audio-visual fusion)
- Evaluate on WildDeepfake as a held-out test (tests generalization)

---

## 11. API Specifications

### POST /upload
Upload a video for analysis.

**Request:** `multipart/form-data` with `file` field  
**Response:**
```json
{
  "job_id": "abc123",
  "status": "processing",
  "message": "Video received. Analysis in progress."
}
```

---

### GET /status/{job_id}
Poll for job completion.

**Response:**
```json
{
  "job_id": "abc123",
  "status": "complete",
  "result": {
    "verdict": "FAKE",
    "confidence": 0.87,
    "visual_score": 0.91,
    "audio_score": 0.82,
    "audio_analyzed": true,
    "speech_detected": true,
    "audio_weight_used": 0.5
  }
}
```

---

### POST /register/{job_id}
Register the analyzed file on the blockchain.

**Response:**
```json
{
  "file_hash": "sha256:abc...",
  "merkle_root": "0xdef...",
  "tx_hash": "0x123...",
  "ipfs_cid": "QmXyz...",
  "block_number": 5842910,
  "timestamp": "2026-03-05T10:30:00Z"
}
```

---

### POST /verify
Verify a file against the blockchain record.

**Request:** `multipart/form-data` with `file` field OR `{ "hash": "sha256:abc..." }`  
**Response:**
```json
{
  "status": "AUTHENTIC",
  "registered_at": "2026-03-05T10:30:00Z",
  "ipfs_cid": "QmXyz...",
  "tx_hash": "0x123...",
  "message": "File matches on-chain record. Not tampered."
}
```

---

### GET /history
Retrieve past analysis records.

**Response:**
```json
{
  "records": [
    {
      "job_id": "abc123",
      "filename": "video.mp4",
      "verdict": "FAKE",
      "confidence": 0.87,
      "registered": true,
      "created_at": "2026-03-05T10:30:00Z"
    }
  ]
}
```

---

## 12. Database Schema

### Table: `uploads`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| filename | VARCHAR | Original filename |
| file_path | VARCHAR | Server storage path |
| file_hash | VARCHAR(64) | SHA-256 hex hash |
| status | ENUM | `processing`, `complete`, `failed` |
| created_at | TIMESTAMP | Upload time |

### Table: `results`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| upload_id | UUID | FK → uploads.id |
| verdict | ENUM | `REAL`, `FAKE` |
| confidence | FLOAT | 0.0–1.0 |
| visual_score | FLOAT | ResNet branch score |
| audio_score | FLOAT | Wav2Vec2 branch score |
| speech_detected | BOOLEAN | VAD result |
| audio_weight | FLOAT | Weight used in fusion |
| created_at | TIMESTAMP | Analysis completion time |

### Table: `blockchain_records`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| upload_id | UUID | FK → uploads.id |
| file_hash | VARCHAR(64) | SHA-256 hash |
| merkle_root | VARCHAR(66) | Merkle root hex |
| tx_hash | VARCHAR(66) | Ethereum tx hash |
| ipfs_cid | VARCHAR | IPFS content ID |
| block_number | INTEGER | Block number on Sepolia |
| registered_at | TIMESTAMP | On-chain timestamp |

---

## 13. UI Screens & User Flows

### Primary User Flow — Upload & Detect

```
Landing Page
    │
    ▼
Upload Dashboard
  - Drag & drop or browse
  - Shows: accepted formats, max size
    │
    ▼
Processing Screen
  - Animated progress indicator
  - Steps shown: "Extracting frames... Extracting audio...
                  Running visual analysis... Running audio analysis...
                  Computing fusion score..."
    │
    ▼
Results Screen
  ┌────────────────────────────────────┐
  │  VERDICT: FAKE                     │
  │  Confidence: 87%  ████████░░        │
  │                                    │
  │  Visual Score:  91%                │
  │  Audio Score:   82%                │
  │  Speech Detected: Yes              │
  │  Analysis Mode: Audio + Visual     │
  │                                    │
  │  [Register on Blockchain]          │
  └────────────────────────────────────┘
    │
    ▼
Blockchain Registration Screen
  - SHA-256 hash
  - Transaction hash (link to Sepolia explorer)
  - IPFS CID
  - Registration timestamp
  - [Download Verification Certificate]
```

### Secondary User Flow — Verify Existing File

```
Verify Page
  - Upload file OR paste hash manually
    │
    ▼
Verification Result
  ┌─────────────────────────────────┐
  │  STATUS: AUTHENTIC ✓            │
  │  Registered: 2026-03-05 10:30  │
  │  TX Hash: 0x123...             │
  │  IPFS CID: QmXyz...            │
  │  No tampering detected.        │
  └─────────────────────────────────┘
```

---

## 14. Non-Functional Requirements

| Requirement | Specification |
|---|---|
| Max file size | 500MB |
| Supported formats | MP4, AVI, MOV, MKV |
| Max inference time | 30 seconds for a 5-minute video |
| Blockchain registration time | ≤ 15 seconds |
| Concurrent users (prototype) | 3–5 simultaneous uploads |
| Browser support | Chrome, Firefox, Edge (latest) |
| Model loading time | ≤ 10 seconds at server startup |
| Database backup | Daily (development environment) |

---

## 15. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| GPU not available for training | Medium | High | Use Google Colab free T4 GPU |
| Wav2Vec2 poor on non-speech audio | High | Medium | VAD fallback handles this — visual takes full weight |
| Sepolia testnet slow/congested | Low | Medium | Increase gas price in Web3.py transaction config |
| Large video files slow inference | Medium | Medium | Sample frames (every 10th), cap max frames at 50 |
| DFDC dataset download slow/large | Medium | Low | Use a 10% stratified subset for initial training |
| Smart contract deployment fails | Low | High | Test thoroughly on local Hardhat node first |
| Pinata API rate limits | Low | Low | Cache IPFS uploads, don't re-upload same file twice |

---

## 16. Out of Scope

The following are explicitly out of scope for this prototype and are noted as future work:

- Live video stream analysis
- Mobile application
- Real Ethereum mainnet deployment (uses testnet only)
- Fine-tuning Wav2Vec2 backbone (frozen in this version)
- Multi-language speech support
- User authentication and accounts
- Paid tier or SLA guarantees
- Explainability heatmaps (GradCAM visualization)
- Support for audio-only files (video required)

---

## 17. Glossary

| Term | Definition |
|---|---|
| **Deepfake** | AI-generated or manipulated media where audio/video has been synthetically altered |
| **Feature Vector / Embedding** | A list of numbers that mathematically encodes what a model learned about an input |
| **Fusion Layer** | The neural network component that combines audio and visual features to make the final REAL/FAKE decision |
| **VAD (Voice Activity Detection)** | A lightweight algorithm that determines whether audio contains human speech |
| **SHA-256** | A cryptographic hash function that produces a unique 64-character fingerprint for any file |
| **Merkle Tree** | A tree data structure where each node is a hash of its children, used to efficiently verify data integrity |
| **Smart Contract** | A self-executing program stored on the blockchain that cannot be altered once deployed |
| **Sepolia** | Ethereum's recommended test network — behaves like mainnet but uses free test ETH |
| **IPFS** | InterPlanetary File System — a decentralized, content-addressed file storage network |
| **CID** | Content Identifier — a unique hash-based address for content stored on IPFS |
| **Hardhat** | A local Ethereum development environment for writing, testing, and deploying smart contracts |
| **Web3.py** | A Python library for interacting with Ethereum nodes and smart contracts |
| **Cross-Modal Attention** | An attention mechanism that learns relationships between features from different modalities (audio + visual) |
| **Layer Normalization** | A technique that rescales feature vectors to a consistent range before combining them |
| **Testnet** | A test blockchain network that mirrors mainnet behavior but uses worthless test currency |
| **Pinata** | A service that provides a simple API for uploading and pinning files to IPFS |
