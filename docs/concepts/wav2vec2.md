# Wav2Vec2

## What is Wav2Vec2?

Wav2Vec2 is a deep learning model developed by Meta (Facebook) AI Research for understanding speech and audio. While it was originally designed for **automatic speech recognition** (converting spoken words into text), TrustChain-AV repurposes it for a different task: detecting whether audio has been synthetically generated or manipulated.

The name breaks down as:
- **Wav**: It works directly on raw audio waveforms (WAV files)
- **Vec**: It converts audio into numerical vectors (lists of numbers)
- **2**: It is the second version, improving on the original Wav2Vec

## How Humans Hear vs. How Wav2Vec2 "Hears"

When you listen to someone speak, your ear converts sound waves into electrical signals, and your brain processes those signals to understand words, tone, and emotion. You can also tell when something sounds "off" -- a robot voice, an unnatural pause, or a voice that does not match the person you see.

Wav2Vec2 does something analogous:

1. **Raw audio in**: It takes the raw waveform -- the actual pressure changes over time that make up sound
2. **Feature extraction**: It converts small chunks of audio into numerical representations
3. **Contextual understanding**: It looks at how these chunks relate to each other over time (like understanding a sentence, not just individual words)
4. **Output**: A rich numerical representation of the audio content

## Self-Supervised Learning: Learning from Unlabeled Data

What makes Wav2Vec2 special is how it was trained. Most AI models need millions of labeled examples ("this audio clip says 'hello'"). Labeling that much audio is extremely expensive.

Wav2Vec2 uses **self-supervised learning** -- it learns from unlabeled audio by playing a game with itself:

1. Take a piece of audio
2. Mask (hide) some parts of it -- like covering words in a sentence with black boxes
3. Try to predict what the masked parts should sound like, based on the surrounding audio
4. Check the prediction against the actual audio and learn from mistakes

This is similar to how you might fill in a missing word in a sentence: "The cat sat on the ___." You know it is probably "mat" or "chair" because of the context. Wav2Vec2 does the same thing, but with audio segments.

By training this way on 53,000 hours of unlabeled speech, Wav2Vec2 develops a deep understanding of what natural speech sounds like -- its rhythms, patterns, and characteristics -- without anyone telling it what specific words are being said.

## Why Wav2Vec2 for Deepfake Audio Detection

### What It Learns About Natural Speech

Through its self-supervised training, Wav2Vec2 develops an implicit understanding of:

- **Natural speech patterns**: How consonants connect to vowels, how pitch changes during a question, how speakers pause between sentences
- **Acoustic properties**: Room reverb, breathing sounds, lip smacks, background noise consistency
- **Temporal coherence**: How speech flows over time -- natural speech has a rhythm that synthetic speech often subtly violates
- **Speaker characteristics**: Vocal tract shape, speaking style, accent patterns

### What Synthetic Speech Gets Wrong

AI-generated speech, no matter how good, tends to have subtle differences from real speech:

- **Prosody artifacts**: The rhythm and emphasis might be slightly mechanical. Real speech has micro-variations in timing that are very hard to replicate.
- **Spectral smoothness**: Synthetic speech often has unnaturally smooth frequency patterns. Real speech is "messier" in the frequency domain because it comes from a physical vocal tract.
- **Breathing and micro-sounds**: Real speakers breathe, swallow, and make tiny lip and tongue sounds. Voice cloning systems often produce "too clean" audio.
- **Transition artifacts**: The way one sound flows into the next (coarticulation) is extremely complex in real speech. Synthetic systems sometimes produce subtle glitches at these boundaries.

Wav2Vec2's deep understanding of natural speech makes it sensitive to these differences, even when they are inaudible to human listeners.

## How TrustChain-AV Uses Wav2Vec2

### The Audio Pipeline

1. **Audio extraction**: FFmpeg extracts the audio track from the uploaded video and converts it to 16kHz mono WAV format (the format Wav2Vec2 expects)

2. **Voice Activity Detection**: Before running Wav2Vec2, a separate system (WebRTC VAD -- see [Voice Activity Detection](vad-voice-activity-detection.md)) checks whether the audio actually contains speech. If there is no speech (e.g., background music only, or silence), audio analysis is skipped entirely.

3. **Feature extraction**: The audio waveform is fed into Wav2Vec2, which processes it and outputs a **768-dimensional feature vector** for each time step

4. **Temporal averaging**: These time-step vectors are averaged into a single 768-dimensional vector that represents the entire audio clip. This is like summarizing a whole conversation into a single numerical fingerprint.

5. **Fusion**: This 768-dim audio vector is sent to the fusion model along with the 2048-dim visual vector from ResNet-50 (see [Multimodal Fusion](multimodal-fusion.md))

### Why 768 Dimensions?

Similar to ResNet-50's 2048-dimensional visual features, Wav2Vec2's 768 dimensions each capture a different aspect of the audio:

- Some dimensions might be sensitive to pitch patterns
- Others might capture the texture of the voice
- Others might respond to timing and rhythm

Together, they form a comprehensive numerical description of what the audio sounds like. The fusion model learns which combinations of these dimensions are indicative of real vs. synthetic audio.

### Frozen vs. Fine-Tuned

In TrustChain-AV's prototype, Wav2Vec2 is used as a **frozen feature extractor** -- it is not retrained on deepfake audio. This is the same approach used with ResNet-50:

- **Frozen (current)**: Use Wav2Vec2 as-is to extract general audio features. The fusion model learns to interpret these features for deepfake detection.
- **Fine-tuned (future)**: Partially retrain Wav2Vec2 on labeled real/fake audio data so it directly learns to detect synthetic speech.

The frozen approach works as a proof of concept because Wav2Vec2's understanding of natural speech is already valuable for distinguishing real from fake audio.

## The Relationship Between Audio and Visual Analysis

| Aspect | Visual (ResNet-50) | Audio (Wav2Vec2) |
|--------|-------------------|-----------------|
| Input | Video frames (images) | Audio waveform (sound) |
| Output | 2048-dim feature vector | 768-dim feature vector |
| Pre-trained on | ImageNet (1.2M images) | LibriSpeech (53K hours audio) |
| Looks for | Visual artifacts, texture anomalies | Speech artifacts, prosody issues |
| Architecture | Convolutional Neural Network | Transformer-based |

These two models complement each other. A sophisticated deepfake might have perfect visual manipulation but synthetic audio, or vice versa. By analyzing both independently and then combining the results, TrustChain-AV is more robust than either analysis alone.

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **Waveform** | The raw audio signal -- pressure changes over time |
| **Self-supervised learning** | Training a model using unlabeled data by creating prediction tasks |
| **Masking** | Hiding parts of the input and training the model to predict them |
| **Feature vector** | A list of numbers representing the content of an audio clip |
| **16kHz mono** | Audio format: 16,000 samples per second, single channel |
| **Temporal averaging** | Combining time-step features into a single summary vector |
| **Prosody** | The rhythm, stress, and intonation of speech |
| **Coarticulation** | How adjacent speech sounds influence each other in natural speech |
| **Frozen backbone** | Using the model as-is without retraining its weights |

## Further Reading

- [Voice Activity Detection](vad-voice-activity-detection.md) -- How the system decides whether to run audio analysis
- [ResNet-50 and Fine-Tuning](resnet50-fine-tuning.md) -- The visual counterpart to Wav2Vec2
- [Multimodal Fusion](multimodal-fusion.md) -- How audio and visual features are combined
