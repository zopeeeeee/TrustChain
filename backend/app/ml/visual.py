"""ResNet-50 visual feature extraction module."""

import glob
import logging
import os

import torch
from PIL import Image
from torchvision import transforms

logger = logging.getLogger(__name__)

IMAGENET_TRANSFORM = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


def extract_visual_features(model, frames_dir: str) -> torch.Tensor:
    """Extract visual features from a directory of frame images.

    Loads sorted frame_*.jpg files, applies ImageNet normalization,
    forwards through the model, and returns the mean feature vector.

    Args:
        model: ResNet-50 feature extractor (without final FC layer).
        frames_dir: Path to directory containing frame_*.jpg files (224x224).

    Returns:
        Tensor of shape (2048,) -- mean feature vector across all frames.

    Raises:
        ValueError: If no frame files are found in the directory.
    """
    frame_paths = sorted(glob.glob(os.path.join(frames_dir, "frame_*.jpg")))
    if not frame_paths:
        raise ValueError(f"No frame files found in {frames_dir}")

    features = []
    with torch.no_grad():
        for path in frame_paths:
            img = Image.open(path).convert("RGB")
            tensor = IMAGENET_TRANSFORM(img).unsqueeze(0)  # (1, 3, 224, 224)
            out = model(tensor)  # (1, 2048, 1, 1)
            feat = out.squeeze()  # (2048,)
            features.append(feat)

    stacked = torch.stack(features)  # (N, 2048)
    mean_feat = stacked.mean(dim=0)  # (2048,)

    logger.info("Extracted visual features from %d frames", len(frame_paths))
    return mean_feat
