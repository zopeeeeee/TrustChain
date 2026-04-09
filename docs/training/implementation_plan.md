# Fusion Model Training Plan

This document outlines the concrete steps and module designs established to train the custom `FusionMLP` multi-modal AI layer without needing to download massive gigabyte video datasets to the local training machine.

## Module Architecture

The training functionality is contained entirely inside `backend/app/ml/training/`. It is detached from the live REST API to ensure no overhead during endpoint ingestion.

### 1. Cloud Pre-Extractor (`kaggle_extract_features.py`)
This standalone script is intended to be copied out of the codebase and executed directly on cloud GPU environments (Kaggle or Google Colab) where huge datasets like **FakeAVCeleb** or **DFDC** are provided natively to use for free without having to download or persist the raw video payloads to your hard drive. 

- **Input:** Iterates over the raw Kaggle/Colab `.mp4` video dataset paths.
- **Process:** Initializes PyTorch with your pre-trained `models.resnet50` and `Wav2Vec2` model from Hugging Face.
- **Output:** Extracts visual (2048-dim) and audio (768-dim) features, and writes a `.zip` archive containing highly optimized lightweight `.pt` tensors.

### 2. Fast Local DataLoader (`dataset.py`)
Once the tiny extracted tensors `.zip` is downloaded to the local training machine, the custom PyTorch `Dataset` loads these tensors directly into RAM. Utilizing an RTX GPU and massive 64GB RAM footprint ensures zero data-fetching bottlenecks, as all mathematical numbers are kept on memory ready to be blasted to the GPU cores.

### 3. Deep Learning Loop (`train.py`)
The primary training entrypoint to be executed on the target peer machine (RTX 5070 Ti).

- Bootstraps the TrustChain `FusionMLP` layer locally identically to how it gets generated in production.
- Initializes the **AdamW Optimizer** and **Binary Cross-Entropy Loss** criterion.
- Executes batch backpropagation over datasets, dynamically evaluating Validation accuracy split.
- **Output:** Saves an optimized `fusion_weights.pth` file containing the finished algorithmic bias logic.

## Production API Bridge

### 4. Zero-Friction Weight Bootstrapping (`backend/app/ml/loader.py`)
The centralized ML models bootstrapper has been updated to dynamically sniff for `fusion_weights.pth` stored inside its directory. 

By running `python -m app.main`, or `docker-compose up`:
1. If the FastAPI logic finds a locally trained `fusion_weights.pth` file, it maps those weights precisely over the prototype array.
2. If the user hasn't trained it yet, it gracefully falls back to generating random proto weights so as not to break compilation.
