"""Wav2Vec2 audio feature extraction module."""

import logging

import soundfile as sf
import torch

logger = logging.getLogger(__name__)


def extract_audio_features(processor, model, audio_path: str) -> torch.Tensor:
    """Extract audio features from a WAV file using Wav2Vec2.

    Args:
        processor: Wav2Vec2Processor instance.
        model: Wav2Vec2Model instance.
        audio_path: Path to a 16kHz mono WAV file.

    Returns:
        Tensor of shape (768,) -- mean hidden state across time dimension.

    Raises:
        AssertionError: If sample rate is not 16000.
    """
    audio_data, sample_rate = sf.read(audio_path)
    assert sample_rate == 16000, f"Expected 16kHz audio, got {sample_rate}Hz"

    inputs = processor(
        audio_data,
        sampling_rate=16000,
        return_tensors="pt",
    )

    with torch.no_grad():
        outputs = model(**inputs)

    # outputs.last_hidden_state shape: (1, time_steps, 768)
    hidden_states = outputs.last_hidden_state.squeeze(0)  # (time_steps, 768)
    mean_feat = hidden_states.mean(dim=0)  # (768,)

    logger.info("Extracted audio features from %s", audio_path)
    return mean_feat
