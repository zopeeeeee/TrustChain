# Phase 3: Detection Pipeline - Research

**Researched:** 2026-03-06
**Domain:** ML inference pipeline (PyTorch, Hugging Face Transformers, WebRTC VAD, fusion MLP)
**Confidence:** HIGH

## Summary

Phase 3 transforms the preprocessed frames and audio from Phase 2 into a REAL/FAKE verdict. The pipeline has four stages: (1) ResNet-50 frozen backbone extracts 2048-dim visual features from sampled frames, (2) Wav2Vec2 frozen backbone extracts 768-dim audio features from the WAV file, (3) WebRTC VAD determines speech presence to gate audio weight, and (4) a simple fusion MLP concatenates visual + weighted audio features and outputs a binary classification with confidence.

This is an academic prototype with frozen backbones (no fine-tuning). The models download pretrained weights on first run (~100MB for ResNet-50, ~360MB for Wav2Vec2 base). All inference runs on CPU. The fusion MLP is untrained and will use random weights -- producing essentially random verdicts -- which is acceptable for an end-to-end prototype. Training the MLP on real data (e.g., DFDC dataset) is a separate concern done outside this system.

**Primary recommendation:** Use torchvision's ResNet-50 with `weights=IMAGENET1K_V1` for visual features, Hugging Face `transformers` Wav2Vec2Model for audio features, `webrtcvad` for VAD, and a simple `nn.Sequential` MLP for fusion. Load all models once at startup via the existing lifespan pattern. Extend `process_video` to chain detection after preprocessing.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DETC-01 | ResNet-50 frozen backbone extracts 2048-dim visual feature vector averaged across sampled frames | torchvision ResNet-50 with final FC layer removed, AdaptiveAvgPool2d produces 2048-dim per frame, mean across frames |
| DETC-02 | Wav2Vec2 frozen backbone extracts 768-dim audio feature vector averaged across time | HuggingFace Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h"), last_hidden_state mean over time axis |
| DETC-03 | WebRTC VAD determines speech presence; if no speech, audio_weight=0.0 and zero vector used | webrtcvad library with aggressiveness=2, process 30ms frames of 16kHz PCM, threshold on % voiced frames |
| DETC-04 | Stage 1 Fusion MLP concatenates visual (2048) + weighted audio (768) features, outputs REAL/FAKE with confidence | nn.Sequential MLP: Linear(2816, 512) -> ReLU -> Dropout -> Linear(512, 1) -> Sigmoid |
| DETC-05 | Frontend shows multi-stage processing status | Extend status field values: visual_analysis, audio_analysis, computing_fusion, completed; update ResultsPage STATUS_LABELS and TERMINAL_STATES |
| DETC-06 | System computes SHA-256 hash of uploaded video file | Already implemented in upload endpoint (sha256 computed during streaming, stored in file_hash column) -- verify and confirm |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| torch | 2.3.x (CPU) | Tensor ops, neural network inference | Industry standard for ML inference |
| torchvision | 0.18.x | ResNet-50 pretrained weights and model | Official PyTorch vision models |
| torchaudio | 2.3.x | Audio loading utilities | Pairs with torch for audio processing |
| transformers | 4.44+ | Wav2Vec2Model, Wav2Vec2Processor | HuggingFace standard for NLP/audio models |
| webrtcvad | 2.0.10 | Voice Activity Detection | Google WebRTC VAD, lightweight, battle-tested |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| soundfile | 0.12+ | WAV file reading for Wav2Vec2 | Loading 16kHz WAV files produced by FFmpeg |
| numpy | (already installed) | Array operations | Feature vector manipulation |
| Pillow | (already installed) | JPEG frame loading | Loading extracted 224x224 frames |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| torchvision ResNet-50 | timm ResNet-50 | timm more flexible but adds dependency; torchvision already paired with torch |
| HuggingFace Wav2Vec2 | torchaudio Wav2Vec2 bundle | HuggingFace has simpler API, better docs for feature extraction |
| webrtcvad | silero-vad | Silero is more accurate but heavier; webrtcvad is C-based, fast, minimal |

**Installation (add to backend/requirements.txt):**
```
torch --index-url https://download.pytorch.org/whl/cpu
torchvision --index-url https://download.pytorch.org/whl/cpu
torchaudio --index-url https://download.pytorch.org/whl/cpu
transformers
webrtcvad-wheels
soundfile
```

**CRITICAL: Use CPU-only torch.** The `--index-url https://download.pytorch.org/whl/cpu` flag is essential. Without it, pip installs the CUDA variant (~2.5GB). CPU-only torch is ~250MB. For Docker pip install, use `--extra-index-url` or a separate pip install line.

## Architecture Patterns

### Recommended Project Structure
```
backend/app/
├── ml/
│   ├── loader.py          # Replace stubs with real model loading
│   ├── visual.py          # ResNet-50 feature extraction
│   ├── audio.py           # Wav2Vec2 feature extraction
│   ├── vad.py             # WebRTC VAD speech detection
│   └── fusion.py          # Fusion MLP classifier
├── services/
│   ├── preprocessing.py   # (existing) FFmpeg extraction
│   └── detection.py       # NEW: orchestrates ML pipeline
```

### Pattern 1: Model Loading at Startup (Lifespan)
**What:** All ML models load once in the FastAPI lifespan, stored on `app.state`
**When to use:** Always -- models are large, loading per-request would be 10+ seconds
**Example:**
```python
# backend/app/ml/loader.py
import torch
import torchvision.models as models
from transformers import Wav2Vec2Model, Wav2Vec2Processor

def load_models() -> dict:
    # Visual: ResNet-50 without final FC layer
    resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    resnet.eval()
    # Remove the final classification layer, keep avgpool output (2048-dim)
    visual_model = torch.nn.Sequential(*list(resnet.children())[:-1])
    visual_model.eval()

    # Audio: Wav2Vec2
    audio_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    audio_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
    audio_model.eval()

    return {
        "visual_model": visual_model,
        "audio_processor": audio_processor,
        "audio_model": audio_model,
    }
```

### Pattern 2: Feature Extraction Functions (Stateless)
**What:** Each extraction function takes model + data, returns feature vector. No side effects.
**When to use:** For testability -- mock the model, test the extraction logic independently

```python
# backend/app/ml/visual.py
import torch
from PIL import Image
from torchvision import transforms
from pathlib import Path

# ImageNet normalization (MUST match training preprocessing)
IMAGENET_TRANSFORM = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def extract_visual_features(model, frames_dir: str) -> torch.Tensor:
    """Extract 2048-dim visual feature vector averaged across frames."""
    frame_paths = sorted(Path(frames_dir).glob("frame_*.jpg"))
    if not frame_paths:
        raise ValueError("No frames found in directory")

    features_list = []
    with torch.no_grad():
        for path in frame_paths:
            img = Image.open(path).convert("RGB")
            tensor = IMAGENET_TRANSFORM(img).unsqueeze(0)  # (1, 3, 224, 224)
            feat = model(tensor)  # (1, 2048, 1, 1)
            feat = feat.squeeze()  # (2048,)
            features_list.append(feat)

    # Average across all frames
    avg_features = torch.stack(features_list).mean(dim=0)  # (2048,)
    return avg_features
```

### Pattern 3: Detection Orchestrator (Background Task)
**What:** A service function that chains preprocessing status -> visual -> audio -> VAD -> fusion
**When to use:** Called from the existing `process_video` after preprocessing completes

```python
# backend/app/services/detection.py
async def run_detection(upload_id, file_path, models):
    """Run full ML detection pipeline. Called after preprocessing."""
    job_dir = Path(file_path).parent
    frames_dir = str(job_dir / "frames")
    audio_path = str(job_dir / "audio.wav")

    # Stage 1: Visual analysis
    await update_status(upload_id, "visual_analysis")
    visual_features = extract_visual_features(models["visual_model"], frames_dir)
    visual_score = visual_features  # raw features for fusion

    # Stage 2: Audio analysis + VAD
    await update_status(upload_id, "audio_analysis")
    has_speech = detect_speech(audio_path)  # WebRTC VAD
    if has_speech and Path(audio_path).exists():
        audio_features = extract_audio_features(
            models["audio_model"], models["audio_processor"], audio_path
        )
        audio_weight = 1.0
    else:
        audio_features = torch.zeros(768)
        audio_weight = 0.0

    # Stage 3: Fusion
    await update_status(upload_id, "computing_fusion")
    verdict, confidence, v_score, a_score = run_fusion(
        models["fusion_model"], visual_features, audio_features, audio_weight
    )

    # Store results
    await update_results(upload_id, verdict, confidence, v_score, a_score,
                         has_speech, audio_weight)
```

### Pattern 4: Passing Models to Background Tasks
**What:** The background task needs access to `app.state` models but runs outside request context
**When to use:** The detection task is spawned via `asyncio.create_task` from the upload endpoint

```python
# In uploads.py - pass models from request.app.state to background task
models = {
    "visual_model": request.app.state.visual_model,
    "audio_processor": request.app.state.audio_processor,
    "audio_model": request.app.state.audio_model,
    "fusion_model": request.app.state.fusion_model,
}
asyncio.create_task(process_video(upload.id, str(file_path), models))
```

### Anti-Patterns to Avoid
- **Loading models inside the detection function:** Each call would take 10+ seconds. Use lifespan.
- **Running inference in async context without wrapping:** PyTorch operations are CPU-bound and block the event loop. Use `asyncio.to_thread()` or `loop.run_in_executor()` for heavy computation.
- **Not calling model.eval():** Without eval mode, BatchNorm and Dropout behave differently. Always set eval mode for frozen backbones.
- **Forgetting torch.no_grad():** Without it, PyTorch builds computation graphs, wasting memory. Always use `with torch.no_grad():` for inference.
- **ImageNet normalization mismatch:** Frames must be normalized with ImageNet mean/std (already done in FFmpeg? No -- FFmpeg just resizes to 224x224 JPEG. Normalization must happen in Python before inference).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Visual feature extraction | Custom CNN | torchvision ResNet-50 pretrained | Pretrained on ImageNet, well-tested 2048-dim features |
| Audio feature extraction | Custom audio encoder | Wav2Vec2 from HuggingFace | State-of-art speech representations, 768-dim |
| Voice activity detection | Energy thresholding | webrtcvad | Google's production VAD, handles edge cases |
| Image preprocessing | Manual numpy transforms | torchvision.transforms | Handles normalization, tensor conversion correctly |
| WAV file loading | Manual wave module | soundfile or torchaudio.load | Handles sample rate, channels, bit depth |

**Key insight:** For an academic prototype with frozen backbones, the entire ML pipeline is essentially glue code around pretrained models. The only custom piece is the fusion MLP, which is a trivial 2-layer network.

## Common Pitfalls

### Pitfall 1: Event Loop Blocking
**What goes wrong:** PyTorch inference (especially ResNet-50 forward passes on many frames) blocks the asyncio event loop, causing all concurrent requests and status polling to hang.
**Why it happens:** PyTorch operations are synchronous CPU-bound work.
**How to avoid:** Wrap all inference calls in `await asyncio.to_thread(sync_function, *args)` to run them in a thread pool.
**Warning signs:** Frontend polling freezes during analysis, health endpoint stops responding.

### Pitfall 2: Docker Image Size Explosion
**What goes wrong:** Docker image grows to 5GB+ because pip installs GPU-enabled PyTorch.
**Why it happens:** Default `pip install torch` pulls CUDA variant.
**How to avoid:** Use `--index-url https://download.pytorch.org/whl/cpu` for CPU-only builds. Consider a separate pip install line for torch packages with the CPU index URL.
**Warning signs:** Docker build takes 20+ minutes, image size > 3GB.

### Pitfall 3: Model Download on Every Container Restart
**What goes wrong:** Wav2Vec2 downloads ~360MB from HuggingFace every time the container starts.
**Why it happens:** Model cache is inside the container's ephemeral filesystem.
**How to avoid:** Mount a Docker volume for the HuggingFace cache directory (`/root/.cache/huggingface`). Or set `TRANSFORMERS_CACHE` env var to a volume-mounted path.
**Warning signs:** Startup takes 2+ minutes, high bandwidth usage.

### Pitfall 4: WAV File Format Mismatch
**What goes wrong:** Wav2Vec2 expects raw 16kHz float waveform but gets integer samples or wrong sample rate.
**Why it happens:** FFmpeg extracts PCM 16-bit signed integer WAV. Need to convert to float32 normalized to [-1, 1].
**How to avoid:** Use `soundfile.read()` which returns float32 by default, or `torchaudio.load()` which normalizes automatically. Verify sample rate matches 16000.
**Warning signs:** Model outputs garbage, NaN values in features.

### Pitfall 5: Empty Frames Directory
**What goes wrong:** Visual extraction crashes because no frames were extracted.
**Why it happens:** Very short video (just over 1 second) with high frame interval may yield 0 frames.
**How to avoid:** Check frame count after extraction. If zero frames, either reduce interval or mark as error. The extraction function should raise a clear error.
**Warning signs:** IndexError or empty tensor errors.

### Pitfall 6: WebRTC VAD Input Requirements
**What goes wrong:** WebRTC VAD silently returns wrong results or crashes.
**Why it happens:** VAD requires exactly 10ms, 20ms, or 30ms frames of 16-bit PCM at 8/16/32/48 kHz. Feeding arbitrary-length audio fails.
**How to avoid:** Read the WAV file, chunk into exactly 30ms frames (480 samples at 16kHz), feed each frame to `vad.is_speech()`. Count voiced frames as percentage.
**Warning signs:** VAD always returns True or always False.

### Pitfall 7: Fusion MLP Random Weights
**What goes wrong:** Untrained MLP produces random 50/50 verdicts with ~0.5 confidence.
**Why it happens:** This is expected for a prototype without training data.
**How to avoid:** This is acceptable for the academic prototype. Document it. In future, train on DFDC or similar dataset. Alternatively, initialize with slightly biased weights for demo purposes.
**Warning signs:** Not a bug -- expected behavior for untrained fusion.

## Code Examples

### ResNet-50 Feature Extraction (2048-dim)
```python
# Source: torchvision official docs + PyTorch forums
import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image
from pathlib import Path

def build_visual_model():
    """Build ResNet-50 feature extractor (no final FC layer)."""
    resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    # Remove final FC layer. Children: conv1, bn1, relu, maxpool, layer1-4, avgpool, fc
    # Keep up to avgpool -> output is (batch, 2048, 1, 1)
    feature_extractor = torch.nn.Sequential(*list(resnet.children())[:-1])
    feature_extractor.eval()
    for param in feature_extractor.parameters():
        param.requires_grad = False
    return feature_extractor

TRANSFORM = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def extract_visual_features(model, frames_dir: str) -> tuple[torch.Tensor, float]:
    """Returns (2048-dim avg feature vector, visual_score)."""
    frame_paths = sorted(Path(frames_dir).glob("frame_*.jpg"))
    if not frame_paths:
        raise ValueError("No frames found")

    all_features = []
    with torch.no_grad():
        for p in frame_paths:
            img = Image.open(p).convert("RGB")
            x = TRANSFORM(img).unsqueeze(0)     # (1, 3, 224, 224)
            feat = model(x).squeeze()            # (2048,)
            all_features.append(feat)

    avg = torch.stack(all_features).mean(dim=0)  # (2048,)
    return avg
```

### Wav2Vec2 Feature Extraction (768-dim)
```python
# Source: HuggingFace transformers Wav2Vec2 docs
import torch
import soundfile as sf
from transformers import Wav2Vec2Model, Wav2Vec2Processor

def build_audio_model():
    """Load Wav2Vec2 for feature extraction."""
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
    model.eval()
    for param in model.parameters():
        param.requires_grad = False
    return processor, model

def extract_audio_features(processor, model, audio_path: str) -> torch.Tensor:
    """Returns 768-dim avg feature vector from audio."""
    speech, sr = sf.read(audio_path)  # float32, shape (samples,)
    assert sr == 16000, f"Expected 16kHz, got {sr}"

    inputs = processor(speech, sampling_rate=16000, return_tensors="pt", padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        hidden_states = outputs.last_hidden_state  # (1, time_steps, 768)

    avg = hidden_states.squeeze(0).mean(dim=0)  # (768,)
    return avg
```

### WebRTC VAD Speech Detection
```python
# Source: py-webrtcvad GitHub
import webrtcvad
import struct
import soundfile as sf

def detect_speech(audio_path: str, aggressiveness: int = 2, threshold: float = 0.1) -> bool:
    """Return True if speech is detected in audio file.

    Uses WebRTC VAD on 30ms frames. If >threshold fraction of frames
    contain speech, returns True.
    """
    speech, sr = sf.read(audio_path, dtype="int16")
    if sr != 16000:
        return False  # Unsupported sample rate

    vad = webrtcvad.Vad(aggressiveness)

    frame_duration_ms = 30
    frame_size = int(sr * frame_duration_ms / 1000)  # 480 samples at 16kHz

    num_voiced = 0
    num_frames = 0

    for i in range(0, len(speech) - frame_size, frame_size):
        frame = speech[i:i + frame_size]
        frame_bytes = frame.tobytes()
        if vad.is_speech(frame_bytes, sr):
            num_voiced += 1
        num_frames += 1

    if num_frames == 0:
        return False

    return (num_voiced / num_frames) > threshold
```

### Fusion MLP
```python
# Simple concatenation fusion
import torch
import torch.nn as nn

class FusionMLP(nn.Module):
    """Stage 1 fusion: concatenate visual + audio features, classify."""

    def __init__(self, visual_dim=2048, audio_dim=768, hidden_dim=512):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(visual_dim + audio_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid(),
        )

    def forward(self, visual_feat, audio_feat, audio_weight=1.0):
        """
        Args:
            visual_feat: (2048,) tensor
            audio_feat: (768,) tensor (zeros if no speech)
            audio_weight: 0.0 or 1.0
        Returns:
            confidence: float in [0, 1] where >0.5 means FAKE
        """
        weighted_audio = audio_feat * audio_weight
        combined = torch.cat([visual_feat, weighted_audio], dim=0)  # (2816,)
        combined = combined.unsqueeze(0)  # (1, 2816)
        confidence = self.net(combined).squeeze()
        return confidence
```

### Async Inference Wrapper
```python
# Prevent event loop blocking
import asyncio

async def run_visual_inference(model, frames_dir):
    """Run visual inference in thread pool to avoid blocking event loop."""
    return await asyncio.to_thread(extract_visual_features, model, frames_dir)

async def run_audio_inference(processor, model, audio_path):
    """Run audio inference in thread pool."""
    return await asyncio.to_thread(extract_audio_features, processor, model, audio_path)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `models.resnet50(pretrained=True)` | `models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)` | torchvision 0.13 (2022) | `pretrained=True` deprecated, use weights enum |
| `from_pretrained` without eval | Always call `.eval()` after loading | Best practice | Critical for correct BatchNorm behavior |
| Manual WAV parsing | soundfile.read() / torchaudio.load() | Standard | Handles format edge cases |
| webrtcvad (original) | webrtcvad-wheels | 2023+ | Provides prebuilt wheels, avoids C compilation on Windows |

**Deprecated/outdated:**
- `torchvision.models.resnet50(pretrained=True)`: Use `weights=` parameter instead
- `Wav2Vec2FeatureExtractor`: Replaced by `Wav2Vec2Processor` which combines feature extraction + tokenization

## Integration Points with Existing Code

### What Already Exists (Phase 2 Output)
1. **Preprocessing pipeline** (`backend/app/services/preprocessing.py`): `process_video()` extracts frames to `/data/{id}/frames/` and audio to `/data/{id}/audio.wav`, then sets status to `queued`
2. **Upload model** (`backend/app/models/upload.py`): Already has `verdict`, `confidence`, `visual_score`, `audio_score`, `speech_detected`, `audio_weight`, `completed_at` columns -- ready for detection results
3. **SHA-256 hashing** (`backend/app/api/uploads.py`): Already computed during upload stream, stored in `file_hash` -- DETC-06 is satisfied
4. **Model stubs** (`backend/app/ml/loader.py`): `load_model_stubs()` returns dicts -- replace with real model loading
5. **Frontend polling** (`frontend/src/hooks/useJobStatus.ts`): Polls every 2s, stops on terminal states `["queued", "completed", "failed"]`
6. **ResultsPage status labels**: Has labels for `extracting_frames`, `extracting_audio`, `queued`, `completed`, `failed`

### What Needs to Change
1. **`process_video()`**: After preprocessing, instead of stopping at `queued`, chain into detection pipeline
2. **`load_model_stubs()`**: Replace with real model loading (ResNet-50, Wav2Vec2, fusion MLP)
3. **`main.py` lifespan**: Update to load real models, store on `app.state`
4. **`uploads.py`**: Pass models reference to background task
5. **Frontend `TERMINAL_STATES`**: Change from `["queued", "completed", "failed"]` to `["completed", "failed"]` -- `queued` is no longer terminal
6. **Frontend `STATUS_LABELS`**: Add `visual_analysis`, `audio_analysis`, `computing_fusion` labels
7. **Alembic migration**: May not need new columns (model already has all detection fields) but need to widen `status` column if it's VARCHAR(20) -- new statuses like `computing_fusion` are 16 chars, fits in 20
8. **Upload status response schema**: May need to include verdict/confidence fields for completed jobs

### Flow After Phase 3
```
Upload -> extracting_frames -> extracting_audio -> visual_analysis -> audio_analysis -> computing_fusion -> completed
```
The `queued` status becomes unnecessary -- detection runs immediately after preprocessing.

## Docker Considerations

### PyTorch CPU Installation in Dockerfile
```dockerfile
# Install CPU-only PyTorch BEFORE other requirements
RUN pip install --no-cache-dir \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# Then install remaining requirements (excluding torch packages)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

### Model Cache Volume
Add a volume mount for HuggingFace model cache to avoid re-downloading:
```yaml
# docker-compose.yml
backend:
  volumes:
    - ./backend:/app
    - upload_data:/data
    - model_cache:/root/.cache  # Cache torch and HF models
```

### Build Time Warning
- PyTorch CPU: ~250MB download
- Wav2Vec2 model: ~360MB download on first startup
- ResNet-50 weights: ~100MB download on first startup
- Total Docker image: expect ~2-3GB with all dependencies
- First startup: 30-60 seconds for model downloads (cached after)

### webrtcvad Build Dependency
`webrtcvad` requires C compilation. Use `webrtcvad-wheels` instead which provides prebuilt wheels. If that fails in Docker, ensure `gcc` is in the apt-get install list (already present in current Dockerfile).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio (already installed) |
| Config file | None (uses pytest defaults, conftest.py for fixtures) |
| Quick run command | `docker compose exec backend pytest tests/ -x -q` |
| Full suite command | `docker compose exec backend pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DETC-01 | ResNet-50 extracts 2048-dim features from frames | unit | `pytest tests/test_visual.py -x` | No -- Wave 0 |
| DETC-02 | Wav2Vec2 extracts 768-dim features from audio | unit | `pytest tests/test_audio.py -x` | No -- Wave 0 |
| DETC-03 | VAD detects speech/no-speech, zero vector on no speech | unit | `pytest tests/test_vad.py -x` | No -- Wave 0 |
| DETC-04 | Fusion MLP produces verdict + confidence from features | unit | `pytest tests/test_fusion.py -x` | No -- Wave 0 |
| DETC-05 | Frontend shows multi-stage status | manual | Visual inspection of ResultsPage | N/A -- manual |
| DETC-06 | SHA-256 hash computed and stored | unit | `pytest tests/test_uploads.py -x` | Yes -- partially covered |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q` (quick, stop on first failure)
- **Per wave merge:** `docker compose exec backend pytest tests/ -v` (full suite in Docker)
- **Phase gate:** Full suite green before verification

### Wave 0 Gaps
- [ ] `tests/test_visual.py` -- covers DETC-01 (mock ResNet-50, verify 2048-dim output shape)
- [ ] `tests/test_audio.py` -- covers DETC-02 (mock Wav2Vec2, verify 768-dim output shape)
- [ ] `tests/test_vad.py` -- covers DETC-03 (mock webrtcvad, verify speech/no-speech logic)
- [ ] `tests/test_fusion.py` -- covers DETC-04 (test MLP forward pass, verify output range 0-1)
- [ ] `tests/test_detection.py` -- covers integration of full detection pipeline with mocked models

**Testing strategy:** All ML model tests should use mocked models (not real weights) to keep tests fast and avoid downloading 500MB+ in CI. Test the shape/type contracts, not the model accuracy.

## Open Questions

1. **Fusion MLP initialization**
   - What we know: The MLP will have random weights (untrained)
   - What's unclear: Should we initialize with specific weights for demo consistency, or leave random?
   - Recommendation: Leave random. Document that training is a separate step. The pipeline correctness is what matters for the prototype.

2. **Inference time budget**
   - What we know: STATE.md mentions "30s for 5-min video on CPU needs profiling"
   - What's unclear: Actual time for ResNet-50 on ~30 frames + Wav2Vec2 on 5 min audio
   - Recommendation: Profile during implementation. ResNet-50 per frame is ~50ms on CPU, so 30 frames = ~1.5s. Wav2Vec2 on 5 min audio may be 5-10s. Should be under 30s total.

3. **Remove `queued` status or keep it?**
   - What we know: Currently `process_video` stops at `queued`. Phase 3 continues to detection.
   - What's unclear: Whether to keep `queued` as a brief intermediate or skip directly to `visual_analysis`
   - Recommendation: Remove `queued` from the flow. After `extracting_audio`, go straight to `visual_analysis`. Update frontend accordingly.

## Sources

### Primary (HIGH confidence)
- [torchvision ResNet-50 docs](https://docs.pytorch.org/vision/main/models/generated/torchvision.models.resnet50.html) - weights API, model architecture
- [HuggingFace Wav2Vec2 docs](https://huggingface.co/docs/transformers/model_doc/wav2vec2) - model loading, feature extraction, processor API
- [py-webrtcvad GitHub](https://github.com/wiseman/py-webrtcvad) - VAD API, frame requirements, aggressiveness modes

### Secondary (MEDIUM confidence)
- [PyTorch Forums](https://discuss.pytorch.org/t/resnet-as-backbone-feature-extractor-undesired-output-dimensions/133903) - ResNet-50 feature extraction patterns
- [webrtcvad-wheels PyPI](https://pypi.org/project/webrtcvad-wheels/) - prebuilt wheels for easier installation
- [PyTorch CPU install guide](https://pytorch.org/get-started/locally/) - CPU-only installation with index URL

### Tertiary (LOW confidence)
- None -- all findings verified against official sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all libraries are well-documented, stable, widely used
- Architecture: HIGH - pattern follows existing codebase conventions (lifespan loading, background tasks, status updates)
- Pitfalls: HIGH - event loop blocking and Docker image size are well-known issues with documented solutions
- Integration: HIGH - existing code reviewed in detail, all integration points identified

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable libraries, slow-moving domain)
