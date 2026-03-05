"""Detection pipeline orchestrator: visual analysis, audio analysis, fusion verdict."""

import asyncio
import logging
import uuid
from datetime import datetime
from pathlib import Path

import torch

from app.ml.audio import extract_audio_features
from app.ml.fusion import FusionMLP
from app.ml.vad import detect_speech
from app.ml.visual import extract_visual_features
from app.services.preprocessing import update_upload_status

logger = logging.getLogger(__name__)


async def run_detection(
    upload_id: uuid.UUID,
    file_path: str,
    models: dict,
    session,
) -> None:
    """Run the full detection pipeline: visual, audio, fusion.

    Derives frames_dir and audio_path from file_path's parent directory.
    Updates upload status at each stage and stores final results.

    Args:
        upload_id: UUID of the upload record.
        file_path: Path to the original video file.
        models: Dict with visual_model, audio_processor, audio_model, fusion_model.
        session: Async database session.
    """
    job_dir = Path(file_path).parent
    frames_dir = str(job_dir / "frames")
    audio_path = str(job_dir / "audio.wav")

    try:
        # Stage 1: Visual analysis
        await update_upload_status(session, upload_id, "visual_analysis")
        visual_features = await asyncio.to_thread(
            extract_visual_features, models["visual_model"], frames_dir
        )

        # Stage 2: Audio analysis
        await update_upload_status(session, upload_id, "audio_analysis")
        audio_file_exists = Path(audio_path).exists()
        has_speech = detect_speech(audio_path) if audio_file_exists else False

        if has_speech and audio_file_exists:
            audio_features = await asyncio.to_thread(
                extract_audio_features,
                models["audio_processor"],
                models["audio_model"],
                audio_path,
            )
            audio_weight = 1.0
            speech_detected = True
        else:
            audio_features = torch.zeros(768)
            audio_weight = 0.0
            speech_detected = False

        # Stage 3: Fusion
        await update_upload_status(session, upload_id, "computing_fusion")
        fusion_model = models["fusion_model"]
        confidence_tensor = await asyncio.to_thread(
            fusion_model, visual_features, audio_features, audio_weight
        )
        confidence = float(confidence_tensor)
        verdict = "FAKE" if confidence > 0.5 else "REAL"

        # Compute scores
        visual_score = confidence  # prototype: use fusion confidence as visual score
        audio_score = confidence if speech_detected else 0.0

        # Stage 4: Store results
        await update_upload_status(
            session,
            upload_id,
            "completed",
            verdict=verdict,
            confidence=confidence,
            visual_score=visual_score,
            audio_score=audio_score,
            speech_detected=speech_detected,
            audio_weight=audio_weight,
            completed_at=datetime.utcnow(),
        )

        logger.info(
            "Upload %s: detection complete - verdict=%s confidence=%.3f",
            upload_id, verdict, confidence,
        )

    except Exception as e:
        logger.error("Upload %s: detection failed - %s", upload_id, e)
        await update_upload_status(
            session, upload_id, "failed", error_message=str(e)
        )
