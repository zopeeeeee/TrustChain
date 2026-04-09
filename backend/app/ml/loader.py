"""ML model loader -- loads real PyTorch models at server startup."""

import logging

import torch
import torchvision.models as models
from transformers import Wav2Vec2Model, Wav2Vec2Processor

from app.ml.fusion import FusionMLP

logger = logging.getLogger(__name__)


def load_models() -> dict:
    """Load all ML models for inference.

    Loads ResNet-50 (visual), Wav2Vec2 (audio), and FusionMLP (classifier).
    All models are set to eval mode with gradients disabled.

    Returns:
        Dictionary with keys: visual_model, audio_processor, audio_model, fusion_model.
    """
    logger.info("Loading ML models...")

    # Visual: ResNet-50 without final FC layer
    logger.info("Loading ResNet-50 feature extractor...")
    resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    feature_extractor = torch.nn.Sequential(*list(resnet.children())[:-1])
    feature_extractor.eval()
    for p in feature_extractor.parameters():
        p.requires_grad = False
    logger.info("ResNet-50 feature extractor loaded")

    # Audio: Wav2Vec2
    logger.info("Loading Wav2Vec2 processor and model...")
    audio_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    audio_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
    audio_model.eval()
    for p in audio_model.parameters():
        p.requires_grad = False
    logger.info("Wav2Vec2 model loaded")

    import os
    
    # Fusion MLP (conditionally load trained weights if available)
    fusion_model = FusionMLP()
    weights_path = os.path.join(os.path.dirname(__file__), "training", "fusion_weights.pth")
    if os.path.exists(weights_path):
        logger.info(f"Loading trained Fusion MLP weights from {weights_path}...")
        fusion_model.load_state_dict(torch.load(weights_path, map_location="cpu", weights_only=True))
        logger.info("Trained Fusion MLP loaded successfully.")
    else:
        logger.info("Loading untrained random weights for Fusion MLP (prototype mode)...")
        
    fusion_model.eval()

    logger.info("All ML models loaded successfully")
    return {
        "visual_model": feature_extractor,
        "audio_processor": audio_processor,
        "audio_model": audio_model,
        "fusion_model": fusion_model,
    }
