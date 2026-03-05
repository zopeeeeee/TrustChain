from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import torch


class TestExtractAudioFeatures:
    """Tests for audio feature extraction using Wav2Vec2."""

    @patch("app.ml.audio.sf")
    def test_returns_768_dim_tensor(self, mock_sf):
        """extract_audio_features with a mock processor/model returns a tensor of shape (768,)."""
        from app.ml.audio import extract_audio_features

        # Mock soundfile.read
        mock_sf.read.return_value = (np.random.randn(16000).astype(np.float32), 16000)

        # Mock processor
        processor = MagicMock()
        processor.return_value = {"input_values": torch.randn(1, 16000)}

        # Mock model
        model = MagicMock()
        mock_output = MagicMock()
        mock_output.last_hidden_state = torch.randn(1, 50, 768)
        model.return_value = mock_output

        result = extract_audio_features(processor, model, "/fake/audio.wav")

        assert isinstance(result, torch.Tensor)
        assert result.shape == (768,)
