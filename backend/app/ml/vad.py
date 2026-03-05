"""WebRTC VAD speech detection module."""

import logging

import numpy as np
import soundfile as sf
import webrtcvad

logger = logging.getLogger(__name__)


def detect_speech(
    audio_path: str,
    aggressiveness: int = 2,
    threshold: float = 0.1,
) -> bool:
    """Detect whether speech is present in an audio file.

    Uses WebRTC VAD to analyze 30ms frames and returns True if the
    proportion of voiced frames exceeds the threshold.

    Args:
        audio_path: Path to a 16kHz mono WAV file.
        aggressiveness: VAD aggressiveness (0-3). Higher = more aggressive filtering.
        threshold: Minimum fraction of voiced frames to consider speech present.

    Returns:
        True if speech is detected, False otherwise.
        Returns False if file doesn't exist, has wrong sample rate, or on error.
    """
    try:
        audio_data, sr = sf.read(audio_path, dtype="int16")
    except Exception:
        logger.warning("Could not read audio file: %s", audio_path)
        return False

    if sr != 16000:
        logger.warning("Expected 16kHz sample rate, got %d", sr)
        return False

    vad = webrtcvad.Vad(aggressiveness)

    # 30ms frames at 16kHz = 480 samples per frame
    frame_size = 480
    num_frames = len(audio_data) // frame_size

    if num_frames == 0:
        return False

    num_voiced = 0
    for i in range(num_frames):
        start = i * frame_size
        end = start + frame_size
        frame = audio_data[start:end]
        if vad.is_speech(frame.tobytes(), sr):
            num_voiced += 1

    ratio = num_voiced / num_frames
    logger.info(
        "VAD: %d/%d frames voiced (%.1f%%), threshold=%.1f%%",
        num_voiced, num_frames, ratio * 100, threshold * 100,
    )
    return ratio > threshold
