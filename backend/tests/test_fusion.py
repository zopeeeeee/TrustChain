import pytest
import torch


class TestFusionMLP:
    """Tests for the Fusion MLP classifier."""

    def test_forward_produces_scalar_in_0_1(self):
        """FusionMLP forward pass with (2048,) visual + (768,) audio produces scalar in [0, 1]."""
        from app.ml.fusion import FusionMLP

        model = FusionMLP()
        model.eval()

        visual_feat = torch.randn(2048)
        audio_feat = torch.randn(768)

        with torch.no_grad():
            result = model(visual_feat, audio_feat)

        assert isinstance(result, torch.Tensor)
        assert result.dim() == 0 or result.numel() == 1  # scalar
        assert 0.0 <= result.item() <= 1.0

    def test_audio_weight_zero_removes_audio(self):
        """FusionMLP with audio_weight=0.0 zeros out audio features."""
        from app.ml.fusion import FusionMLP

        model = FusionMLP()
        model.eval()

        visual_feat = torch.randn(2048)
        audio_feat = torch.randn(768)

        with torch.no_grad():
            result_with_audio = model(visual_feat, audio_feat, audio_weight=1.0)
            result_without_audio = model(visual_feat, audio_feat, audio_weight=0.0)
            result_zero_audio = model(visual_feat, torch.zeros(768), audio_weight=1.0)

        # With audio_weight=0.0, result should match using zero audio features
        assert torch.allclose(result_without_audio, result_zero_audio, atol=1e-6)
