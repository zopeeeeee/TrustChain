from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class TestDetectSpeech:
    """Tests for WebRTC VAD speech detection."""

    @patch("app.ml.vad.webrtcvad")
    @patch("app.ml.vad.sf")
    def test_returns_true_when_speech_present(self, mock_sf, mock_webrtcvad):
        """detect_speech returns True when >10% of 30ms frames are voiced."""
        from app.ml.vad import detect_speech

        # 1 second of audio at 16kHz = 16000 samples
        mock_sf.read.return_value = (np.zeros(16000, dtype=np.int16), 16000)

        # Mock VAD to mark all frames as speech
        mock_vad = MagicMock()
        mock_vad.is_speech.return_value = True
        mock_webrtcvad.Vad.return_value = mock_vad

        result = detect_speech("/fake/audio.wav")

        assert result is True

    @patch("app.ml.vad.webrtcvad")
    @patch("app.ml.vad.sf")
    def test_returns_false_when_no_speech(self, mock_sf, mock_webrtcvad):
        """detect_speech returns False when audio has no speech."""
        from app.ml.vad import detect_speech

        mock_sf.read.return_value = (np.zeros(16000, dtype=np.int16), 16000)

        mock_vad = MagicMock()
        mock_vad.is_speech.return_value = False
        mock_webrtcvad.Vad.return_value = mock_vad

        result = detect_speech("/fake/audio.wav")

        assert result is False

    @patch("app.ml.vad.sf")
    def test_returns_false_on_wrong_sample_rate(self, mock_sf):
        """detect_speech returns False when audio has wrong sample rate."""
        from app.ml.vad import detect_speech

        mock_sf.read.return_value = (np.zeros(44100, dtype=np.int16), 44100)

        result = detect_speech("/fake/audio.wav")

        assert result is False

    def test_returns_false_on_missing_file(self):
        """detect_speech returns False when audio file does not exist."""
        from app.ml.vad import detect_speech

        result = detect_speech("/nonexistent/audio.wav")

        assert result is False
