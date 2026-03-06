# Deepfake Detection

## What is a Deepfake?

A deepfake is a piece of media -- usually a video or audio clip -- where a person's face, voice, or both have been artificially generated or manipulated using artificial intelligence. The word itself is a combination of "deep learning" (a branch of AI) and "fake."

Think of it like a very convincing mask. In old movies, actors wore rubber masks to look like someone else. Deepfakes are the digital equivalent, but so realistic that the human eye often cannot tell the difference.

### How Deepfakes are Made

Most deepfakes are created using a type of neural network called a Generative Adversarial Network (GAN) or more recently, diffusion models. Here is the simplified idea:

1. **The Generator** creates a fake image or video frame. At first, it produces garbage -- random noise that looks nothing like a real face.
2. **The Discriminator** looks at both real images and the generator's fakes and tries to tell them apart.
3. They compete against each other. The generator keeps improving its fakes to fool the discriminator, and the discriminator keeps getting better at spotting fakes.
4. After thousands of rounds, the generator produces outputs that are nearly indistinguishable from real media.

This adversarial training process is what makes deepfakes so convincing -- the AI literally trains itself to fool a detector.

### Common Types of Deepfakes

- **Face Swap**: Replacing one person's face with another's in a video (e.g., putting a celebrity's face on someone else's body)
- **Face Reenactment**: Making a real person appear to say or do something they never did by driving their face with another person's expressions
- **Lip Sync**: Altering mouth movements to match different audio
- **Voice Cloning**: Generating synthetic speech that sounds like a specific person
- **Full Synthesis**: Generating an entirely fictional person who never existed

## Why Deepfake Detection Matters

### The Threat Landscape

Deepfakes pose serious risks across multiple domains:

- **Misinformation**: Fake videos of politicians saying things they never said can influence elections and public opinion
- **Fraud**: Voice clones of CEOs have been used to authorize fraudulent wire transfers worth millions
- **Harassment**: Non-consensual deepfake content targeting individuals
- **Evidence Tampering**: Fabricated video evidence in legal proceedings
- **Erosion of Trust**: When anything can be faked, people start doubting everything -- even real footage. This is called the "liar's dividend"

### The Arms Race

Deepfake detection is fundamentally an arms race. As detection methods improve, generation methods evolve to evade them. This is why modern detection systems need to:

1. Look at multiple signals simultaneously (not just visual -- audio too)
2. Provide confidence scores rather than binary yes/no answers
3. Create tamper-proof records of their analysis (which is where blockchain comes in)

## How TrustChain-AV Detects Deepfakes

TrustChain-AV uses a **multimodal approach** -- it analyzes both the visual and audio components of a video independently, then combines the results. This is more robust than looking at either signal alone.

### Visual Analysis

When a human face is deepfaked, the AI generation process often leaves subtle artifacts that are invisible to the naked eye but detectable by another AI:

- **Blending boundaries**: Where the fake face meets the real background, there are often slight inconsistencies in lighting, color, or texture
- **Temporal inconsistencies**: Frame-to-frame, a real face moves smoothly. Deepfakes sometimes have tiny flickers or inconsistent movements
- **Texture anomalies**: Skin texture, hair details, and reflections in eyes are hard for generators to get perfectly right
- **Compression artifacts**: Deepfakes are often re-compressed, creating double-compression patterns

TrustChain-AV uses **ResNet-50** (see [ResNet-50 and Fine-Tuning](resnet50-fine-tuning.md)) to extract visual features from sampled frames and learn to recognize these subtle patterns.

### Audio Analysis

Synthetic or cloned speech also carries telltale signs:

- **Unnatural prosody**: The rhythm and intonation of speech may be slightly off
- **Spectral artifacts**: The frequency distribution of synthetic speech differs from natural speech in ways that are hard for humans to hear but easy for models to detect
- **Breathing patterns**: Real speech includes natural breathing sounds that synthetic speech often lacks or gets wrong
- **Background consistency**: The acoustic environment (room echo, background noise) should remain consistent throughout a clip

TrustChain-AV uses **Wav2Vec2** (see [Wav2Vec2](wav2vec2.md)) to extract audio features and detect these anomalies.

### Why Both Together?

A sophisticated deepfake might swap someone's face but keep the original audio, or clone someone's voice but use a real video. By analyzing both modalities, TrustChain-AV can catch attacks that only target one channel. The **fusion model** (see [Multimodal Fusion](multimodal-fusion.md)) weighs both signals and produces a combined verdict.

## Detection is Not Perfect

It is important to understand the limitations:

- **No detector is 100% accurate.** There will always be false positives (real videos flagged as fake) and false negatives (deepfakes that slip through).
- **Confidence scores matter.** A 95% confidence verdict is very different from a 55% confidence verdict. TrustChain-AV always shows the confidence level.
- **New generation techniques** can temporarily bypass existing detectors until the detector is updated or retrained.
- **Quality matters.** Heavily compressed, low-resolution videos lose the subtle artifacts that detectors rely on.

This is why TrustChain-AV pairs detection with **blockchain registration** -- even if detection is not perfect, having a tamper-proof record of when a piece of media was first analyzed and what the result was adds an extra layer of accountability.

## Key Terminology

| Term | Meaning |
|------|---------|
| **Deepfake** | AI-generated or manipulated media designed to look real |
| **GAN** | Generative Adversarial Network -- the AI architecture behind most deepfakes |
| **Multimodal** | Using multiple types of input (visual + audio) together |
| **Confidence Score** | A percentage indicating how certain the detector is about its verdict |
| **False Positive** | A real video incorrectly flagged as fake |
| **False Negative** | A fake video incorrectly classified as real |
| **Liar's Dividend** | The phenomenon where the existence of deepfakes causes people to doubt real media |

## Further Reading

- [ResNet-50 and Fine-Tuning](resnet50-fine-tuning.md) -- How the visual analysis model works
- [Wav2Vec2](wav2vec2.md) -- How the audio analysis model works
- [Multimodal Fusion](multimodal-fusion.md) -- How visual and audio verdicts are combined
- [Blockchain and Smart Contracts](blockchain-and-smart-contracts.md) -- How analysis results are permanently recorded
