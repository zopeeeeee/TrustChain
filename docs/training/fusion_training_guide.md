# Guide: Training the TrustChain-AV Fusion Layer

Currently, the `FusionMLP` layer in `backend/app/ml/fusion.py` is initialized with random weights. This means it's effectively guessing if a video is a deepfake or not blindly. To make the system work reliably, we need to train this specific component.

Here is a comprehensive breakdown of the process.

## 1. The Analogy: The Experts and The Judge

To truly understand what we're training, imagine a courtroom setup for a forgery case:

* **The Visual Expert (ResNet-50):** An investigator who only looks at the facial features frame-by-frame. They output a 2048-page report of raw observations but don't give a final "fake or real" verdict.
* **The Audio Expert (Wav2Vec 2.0):** An audio engineer who strictly listens to the voice and produces a 768-page report of acoustic anomalies.
* **The Reports (Feature Vectors):** These 2048 and 768 numbers are what the models produce.
* **The Judge (FusionMLP):** The final decision-maker. The judge doesn't re-examine the video or audio; they only read the **2816 pages of combined reports** and must issue a final binary verdict: **0 (Real)** or **1 (Fake)**.

### The Cloud Extraction Analogy (Avoiding Gigabyte Downloads)
Downloading gigabytes of videos locally is inefficient since we only need the ResNet and Wav2Vec "Reports". Because pre-extracted datasets for our *exact* models may not be packaged natively online, we use the **"Remote Deposition"** strategy:
1. Instead of transporting thousands of suspects (gigabytes of raw videos) locally to your courthouse (your computer) for the Experts to interview, we **send the Experts to the remote prison** (e.g., executing a Kaggle or Google Colab Notebook where the dataset is natively hosted).
2. The Experts do their interviews in the remote environment and write their tiny text reports (`.pt` tensors).
3. We mail just the lightweight stack of papers (a few megabytes of tensors) back to your local courthouse.
4. Your fast Judge (your RTX GPU) quickly reads the papers and trains locally without needing to download the actual massive videos!

## 2. Hardware and Software Requirements

**Hardware Requirements:**
* **Local Machine (Your Peer's):** Minimum 16GB RAM, modern GPU (e.g., RTX 5070 Ti). This is exceptionally powerful and will chew through the MLP training loop easily.
* **Cloud (Kaggle/Colab):** Free P100/T4 instances to ingest the raw dataset and extract the features.

**Software Requirements:**
* Python Ecosystem: `torch`, `torchvision`, `torchaudio`
* ML Utilities: `scikit-learn`, `pandas`, `tqdm`

## 3. The Remote Training Architecture Roadmap

### Step 1: The Cloud Extractor (`kaggle_extract_features.py`)
We write a script configured to run on a cloud platform like Kaggle, which natively hosts massive datasets like the **Deepfake Detection Challenge (DFDC)** for free so you don't have to download anything. The script loops over the videos in the cloud, runs ResNet and Wav2Vec, and outputs a Zip drive containing the 2816-dimensional vectors.

### Step 2: Download the Small Features Cache
Download the generated `.zip` array to your local machine. It will be orders of magnitude smaller than the raw videos.

### Step 3: Local PyTorch DataLoader (`dataset.py`)
We write a PyTorch `Dataset` on the local machine that loads these tiny `.pt` files directly into RAM. 

### Step 4: Local Blazing-Fast Training Loop (`train.py`)
We run multiple "Epochs" over the loaded memory array on the RTX GPU:
1. Feed the 2816-dim tensor into `FusionMLP`
2. Compare prediction to actual label -> Calculate Binary Cross Entropy Loss
3. Nudge the Judge's weights to be slightly better after every batch using AdamW.

### Step 5: Integration into TrustChain-AV
Once validation accuracy peaks, the script saves `fusion_weights.pth`. We update `backend/app/ml/loader.py` to seamlessly load this newly trained "Judge" profile, transforming the generic UI into a genuinely intelligent system capable of high-accuracy deepfake detection.
