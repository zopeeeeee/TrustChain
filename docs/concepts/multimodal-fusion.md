# Multimodal Fusion

## What Does "Multimodal" Mean?

In machine learning, a **modality** is a type of input data. Common modalities include:

- **Visual**: Images, video frames
- **Audio**: Sound, speech
- **Text**: Written language
- **Sensor data**: Temperature, motion, GPS

**Multimodal** means using more than one modality at the same time. TrustChain-AV is multimodal because it analyzes both the **visual** (video frames) and **audio** (sound track) components of a video.

## Why Combine Modalities?

### The Blind Men and the Elephant

There is a classic parable about blind men touching different parts of an elephant. One touches the trunk and says "it's a snake." Another touches the leg and says "it's a tree." Each one has partial information and reaches a wrong conclusion. Only by combining all their observations can they correctly identify an elephant.

Deepfake detection faces the same challenge:

- **Visual-only analysis** might miss a video where the face looks perfect but the voice has been cloned
- **Audio-only analysis** might miss a video where the speech is real but the face has been swapped
- **Combined analysis** can catch deepfakes that attack either channel or both

### Real-World Example

Imagine someone creates a deepfake video of a politician:

**Scenario 1 -- Face swap only**: They take a real video of Person A and replace the face with Person B's face. The audio is Person A's original voice.
- Visual analysis: Detects face manipulation artifacts -- flags as FAKE
- Audio analysis: Hears real, natural speech -- says REAL
- Combined: The visual evidence outweighs the audio -- correctly flags as FAKE

**Scenario 2 -- Voice clone only**: They take a real video of Person B and replace the audio with a cloned version of Person B's voice saying something different.
- Visual analysis: Sees a real, unmanipulated face -- says REAL
- Audio analysis: Detects synthetic speech patterns -- flags as FAKE
- Combined: The audio evidence outweighs the visual -- correctly flags as FAKE

**Scenario 3 -- Both manipulated**: Face swapped and voice cloned.
- Visual analysis: Flags as FAKE
- Audio analysis: Flags as FAKE
- Combined: Both signals agree -- high confidence FAKE

Neither modality alone catches all three scenarios. Together, they cover each other's blind spots.

## How Fusion Works in TrustChain-AV

### The Input

By the time the fusion model runs, two things have happened:

1. **ResNet-50** has processed video frames and produced a **2048-dimensional visual feature vector** -- a list of 2,048 numbers summarizing the visual content
2. **Wav2Vec2** has processed the audio and produced a **768-dimensional audio feature vector** -- a list of 768 numbers summarizing the audio content

### Concatenation

The simplest and most reliable fusion method is **concatenation** -- placing the two vectors end-to-end to create one big vector:

```
Visual features:  [v1, v2, v3, ... v2048]     (2048 numbers)
Audio features:   [a1, a2, a3, ... a768]       (768 numbers)
Combined:         [v1, v2, ... v2048, a1, a2, ... a768]  (2816 numbers)
```

This 2816-dimensional vector is the input to the fusion model. It contains everything the system knows about both the visual and audio content of the video.

### The Fusion MLP

MLP stands for **Multi-Layer Perceptron** -- one of the simplest types of neural networks. Think of it as a decision-making machine with a few layers:

**Layer 1 -- Understanding**: Takes the 2816-dim combined vector and compresses it down, learning which combinations of visual and audio features are important. This is like a detective reviewing all the evidence and noting the key points.

**Layer 2 -- Reasoning**: Further processes the compressed representation, learning complex patterns. This is where the model might learn things like "if the visual blending score is high AND the audio prosody is slightly off, that is a strong indicator of a deepfake."

**Output layer -- Decision**: Produces a single number between 0 and 1:
- Close to 0 = REAL
- Close to 1 = FAKE
- The exact threshold (typically 0.5) determines the binary verdict

### Audio Weighting

Not all videos have speech. When VAD (see [Voice Activity Detection](vad-voice-activity-detection.md)) detects no speech:

- The audio feature vector is replaced with zeros
- The **audio weight** is set to 0.0

This effectively tells the fusion model: "Ignore the audio side -- there is nothing meaningful there." The decision is made entirely on visual features.

When speech is detected, the audio weight reflects how much speech was present and how reliable the audio analysis is. More speech generally means more reliable audio features.

### Weighted Fusion

The audio weight modifies the audio features before concatenation:

```
Weighted audio = audio_features * audio_weight
```

If audio_weight is 0.0 (no speech), the audio features become all zeros -- the fusion model only sees visual information. If audio_weight is 1.0 (plenty of speech), the audio features are used at full strength.

This creates a smooth spectrum:
- Pure visual-only decision (no speech)
- Mostly visual with some audio input (brief speech)
- Balanced visual and audio (sustained speech throughout)

## Types of Fusion (For Context)

TrustChain-AV uses **late fusion** with concatenation. Here is how it compares to other approaches:

### Early Fusion
Combine raw inputs before any processing. Like mixing paints before painting.
- Example: Overlay audio spectrograms on video frames and process everything with one model
- Advantage: The model can find correlations between modalities from the start
- Disadvantage: Hard to align different data types (images and waveforms have different structures)

### Late Fusion
Process each modality independently, then combine the results. Like having two experts give separate opinions, then a judge combines them.
- Example: Get a visual score and an audio score, then average them
- Advantage: Simple, each modality can use its best architecture
- Disadvantage: Misses cross-modal interactions (e.g., lip movement not matching audio)

### Mid-Level Fusion (TrustChain-AV's Approach)
Process each modality independently to extract features, then combine the features (not the raw data or final scores). Like having two detectives investigate separately, pool their clues, and then reason about the combined evidence.
- Example: Concatenate visual and audio feature vectors, then pass through an MLP
- Advantage: Captures cross-modal patterns while using specialized extractors for each modality
- This is what TrustChain-AV does

### Cross-Modal Attention (Future Enhancement)
Let each modality "look at" the other during processing. Like two detectives actively comparing notes during their investigation.
- Example: Attention mechanism that lets visual features attend to audio features and vice versa
- Advantage: Can learn things like "this lip movement does not match this audio phoneme"
- Disadvantage: More complex, needs more training data
- This is planned as a v2 enhancement for TrustChain-AV

## The Prototype vs. Trained Model

In TrustChain-AV's current prototype, the fusion MLP uses **random (untrained) weights**. This means:

- The architecture is correct (it takes 2816-dim input and outputs a verdict)
- But the weights have not been optimized on real deepfake data
- So the verdicts are not yet reliable

This is intentional for the prototype -- it demonstrates the complete pipeline works end-to-end. Training the fusion model requires a labeled dataset of real and fake videos, which is a separate step done in a training environment (Google Colab with GPUs).

Think of it like building a car and test-driving it before the engine is tuned. The car drives, the steering works, the brakes work -- but peak performance comes after tuning.

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **Modality** | A type of input data (visual, audio, text, etc.) |
| **Multimodal** | Using multiple modalities together |
| **Concatenation** | Placing two vectors end-to-end to form one longer vector |
| **MLP** | Multi-Layer Perceptron -- a simple neural network with fully connected layers |
| **Audio weight** | A scaling factor (0.0-1.0) controlling how much audio influences the verdict |
| **Late fusion** | Combining final predictions from each modality |
| **Mid-level fusion** | Combining intermediate features from each modality (TrustChain-AV's approach) |
| **Cross-modal attention** | Letting modalities interact during processing (future enhancement) |

## Further Reading

- [ResNet-50 and Fine-Tuning](resnet50-fine-tuning.md) -- Source of the 2048-dim visual features
- [Wav2Vec2](wav2vec2.md) -- Source of the 768-dim audio features
- [Voice Activity Detection](vad-voice-activity-detection.md) -- How audio weight is determined
- [Deepfake Detection](deepfake-detection.md) -- The bigger picture
