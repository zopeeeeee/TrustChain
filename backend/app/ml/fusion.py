"""Fusion MLP classifier for combining visual and audio features."""

import logging

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


class FusionMLP(nn.Module):
    """Multi-layer perceptron that fuses visual and audio features.

    Concatenates visual (2048-dim) and audio (768-dim) feature vectors,
    passes through a hidden layer, and outputs a confidence score in [0, 1].
    """

    def __init__(
        self,
        visual_dim: int = 2048,
        audio_dim: int = 768,
        hidden_dim: int = 512,
    ):
        super().__init__()
        input_dim = visual_dim + audio_dim  # 2816
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid(),
        )

    def forward(
        self,
        visual_feat: torch.Tensor,
        audio_feat: torch.Tensor,
        audio_weight: float = 1.0,
    ) -> torch.Tensor:
        """Forward pass: fuse features and produce confidence score.

        Args:
            visual_feat: Tensor of shape (2048,).
            audio_feat: Tensor of shape (768,).
            audio_weight: Scaling factor for audio features (0.0 to 1.0).

        Returns:
            Scalar tensor with confidence score in [0, 1].
        """
        weighted_audio = audio_feat * audio_weight
        combined = torch.cat([visual_feat, weighted_audio], dim=0)  # (2816,)
        combined = combined.unsqueeze(0)  # (1, 2816)
        out = self.net(combined)  # (1, 1)
        return out.squeeze()  # scalar
