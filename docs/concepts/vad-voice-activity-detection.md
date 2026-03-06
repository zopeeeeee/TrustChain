# Voice Activity Detection (VAD)

## What is VAD?

Voice Activity Detection is the task of determining whether a segment of audio contains human speech or not. It answers a simple yes/no question: "Is someone talking right now?"

This might sound trivial -- you can usually tell if someone is speaking when you listen to audio. But for a computer processing raw audio data (just a stream of numbers representing sound pressure), distinguishing speech from background noise, music, wind, or silence is a real challenge.

## Why TrustChain-AV Needs VAD

Not every video has speech. Consider these scenarios:

- A nature documentary with background music but no narration
- A surveillance camera video with ambient sounds
- A silent screen recording
- A music video with singing but no spoken dialogue

TrustChain-AV's audio analysis model (Wav2Vec2) is designed to analyze **speech**. If you feed it background noise or music, it will still produce a feature vector, but that vector will be meaningless for deepfake detection -- it would be like asking a handwriting expert to analyze a printed barcode.

VAD acts as a **gatekeeper**:

- **Speech detected**: Run audio analysis with Wav2Vec2, include audio score in the fusion
- **No speech detected**: Skip audio analysis, set audio weight to zero, rely on visual analysis only

This prevents the system from making bad decisions based on irrelevant audio data.

## How WebRTC VAD Works

TrustChain-AV uses **WebRTC VAD**, a lightweight voice activity detector originally developed by Google for real-time communication (like Google Meet and Chrome's echo cancellation).

### The Approach

WebRTC VAD analyzes audio in very short chunks (10-30 milliseconds at a time) and uses statistical signal processing to determine if each chunk contains speech:

1. **Frequency analysis**: Speech has a characteristic frequency distribution. Human voice typically falls in the 85-8000 Hz range, with most energy between 300-3000 Hz. The VAD checks if the audio energy in these "speech bands" is significantly higher than the background.

2. **Energy detection**: Speech segments are generally louder than silence or background noise. The VAD compares the energy of each chunk against a dynamically estimated noise floor.

3. **Temporal patterns**: Speech has a rhythm -- alternating between voiced sounds (vowels), unvoiced sounds (consonants like "s" and "f"), and short pauses. The VAD looks for these patterns.

### Aggressiveness Levels

WebRTC VAD has an aggressiveness parameter (0 to 3):

- **Level 0**: Least aggressive -- classifies more audio as speech (fewer false negatives, more false positives). Good when you do not want to miss any speech.
- **Level 3**: Most aggressive -- only classifies audio as speech when very confident (fewer false positives, more false negatives). Good when you want to be sure it is really speech.

TrustChain-AV uses an appropriate aggressiveness level to balance between missing speech and falsely detecting speech in non-speech audio.

### The Decision Process

The VAD does not just look at one chunk. TrustChain-AV processes the entire audio track and counts how many chunks contain speech:

1. Split the audio into 30ms frames
2. Run VAD on each frame: speech or not speech?
3. Count the ratio of speech frames to total frames
4. If enough speech is detected (above a threshold), declare "speech present"

This approach is robust because it does not get fooled by a single cough or door slam that might momentarily sound like speech.

## What Happens Without Speech

When VAD determines there is no speech in the video:

1. **Audio score is set to zero** -- not because the audio is fake, but because there is no speech to analyze
2. **Audio weight is set to zero** -- the fusion model ignores the audio component entirely
3. **A zero vector replaces audio features** -- instead of a meaningful 768-dimensional vector from Wav2Vec2, a vector of all zeros is used
4. **The verdict relies entirely on visual analysis** -- ResNet-50's visual features determine the outcome alone

This is the correct behavior. If someone uploads a silent screen recording, it would be wrong to penalize it or flag it as suspicious just because there is no speech.

## Why Not Just Always Run Audio Analysis?

You might wonder: why not always run Wav2Vec2 and let the fusion model figure it out? There are several reasons:

- **Garbage in, garbage out**: Wav2Vec2 was trained on speech. Feeding it music or noise produces feature vectors that do not represent anything meaningful. The fusion model cannot reliably interpret these nonsensical features.

- **Efficiency**: Wav2Vec2 is computationally expensive. Skipping it when there is no speech saves processing time.

- **Cleaner signals**: By explicitly detecting speech absence and zeroing out the audio contribution, the fusion model gets a clear signal: "audio analysis was not applicable." This is much better than passing confusing, noisy audio features.

## Real-World Analogy

Think of a doctor examining a patient. If the patient comes in with a sore throat:

- The doctor examines the throat (visual analysis)
- The doctor asks the patient to say "ahh" and listens (audio analysis)

But if the patient has lost their voice completely (no speech), the doctor does not try to diagnose a throat problem from silence. They rely on the visual examination alone and note "patient could not vocalize."

VAD is the step where the system checks: "Can this patient vocalize?" If not, it adjusts its diagnostic approach accordingly.

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **VAD** | Voice Activity Detection -- determining if audio contains speech |
| **WebRTC** | Web Real-Time Communication -- Google's framework for audio/video calls |
| **Frame** | A small chunk of audio (typically 10-30 ms) analyzed individually |
| **Aggressiveness** | How strict the VAD is about classifying audio as speech (0=lenient, 3=strict) |
| **Speech ratio** | The percentage of audio frames containing speech |
| **Zero vector** | A placeholder vector of all zeros used when audio analysis is skipped |
| **Audio weight** | The importance given to audio features in the fusion model (0.0 when no speech) |

## Further Reading

- [Wav2Vec2](wav2vec2.md) -- The model that runs when VAD detects speech
- [Multimodal Fusion](multimodal-fusion.md) -- How audio weight affects the final verdict
- [Deepfake Detection](deepfake-detection.md) -- The broader detection pipeline
