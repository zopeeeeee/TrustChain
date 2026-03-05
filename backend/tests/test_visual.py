import os
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import torch


class TestExtractVisualFeatures:
    """Tests for visual feature extraction using ResNet-50."""

    def _make_mock_model(self):
        """Create a mock model that returns a (1, 2048, 1, 1) tensor."""
        model = MagicMock()
        model.return_value = torch.randn(1, 2048, 1, 1)
        return model

    @patch("app.ml.visual.IMAGENET_TRANSFORM")
    @patch("app.ml.visual.Image")
    def test_returns_2048_dim_tensor(self, mock_image_mod, mock_transform, tmp_path):
        """extract_visual_features with a mock model returns a tensor of shape (2048,)."""
        from app.ml.visual import extract_visual_features

        # Create fake frame files
        for i in range(3):
            (tmp_path / f"frame_{i:04d}.jpg").write_bytes(b"\xff\xd8dummy")

        # Mock PIL Image.open to return a fake image
        fake_img = MagicMock()
        fake_img.convert.return_value = fake_img
        mock_image_mod.open.return_value = fake_img

        # Mock transform to return a tensor of correct shape
        mock_transform.return_value = torch.randn(3, 224, 224)

        model = self._make_mock_model()

        result = extract_visual_features(model, str(tmp_path))

        assert isinstance(result, torch.Tensor)
        assert result.shape == (2048,)

    def test_raises_on_empty_directory(self, tmp_path):
        """extract_visual_features raises ValueError when frames directory is empty."""
        from app.ml.visual import extract_visual_features

        model = self._make_mock_model()

        with pytest.raises(ValueError, match="No frame"):
            extract_visual_features(model, str(tmp_path))
