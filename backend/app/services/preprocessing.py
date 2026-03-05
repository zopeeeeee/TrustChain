"""Video preprocessing service: validation, frame extraction, and audio extraction via FFmpeg."""

import asyncio
import json
import logging
import uuid
from pathlib import Path

from app.config import settings
from app.database import async_session
from app.models.upload import Upload

logger = logging.getLogger(__name__)


async def probe_video(video_path: str) -> dict:
    """Run FFprobe on a video file and return parsed JSON metadata.

    Raises RuntimeError if FFprobe exits with non-zero status.
    """
    proc = await asyncio.create_subprocess_exec(
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"FFprobe failed: {stderr.decode(errors='replace')}")

    return json.loads(stdout.decode())


async def validate_video(video_path: str) -> tuple[bool, str]:
    """Validate a video file using FFprobe metadata.

    Returns (True, "") if valid, or (False, reason) if invalid.
    """
    try:
        info = await probe_video(video_path)
        duration = float(info["format"]["duration"])

        if duration < 1.0:
            return (False, "Video must be at least 1 second long")

        return (True, "")
    except (RuntimeError, KeyError, ValueError):
        return (False, "File appears to be corrupted or not a valid video")


async def extract_frames(
    video_path: str,
    output_dir: str,
    frame_interval: int = 10,
) -> list[str]:
    """Extract frames from video at every Nth frame, resized to 224x224 JPEG.

    Returns sorted list of extracted frame file paths.
    Raises RuntimeError if FFmpeg fails.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    vf_filter = f"select=not(mod(n\\,{frame_interval})),scale=224:224"
    output_pattern = str(Path(output_dir) / "frame_%04d.jpg")

    proc = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-i", video_path,
        "-vf", vf_filter,
        "-vsync", "vfr",
        "-q:v", "2",
        output_pattern,
        "-y",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"Frame extraction failed: {stderr.decode(errors='replace')}")

    # Collect extracted frame paths
    frames = sorted(str(p) for p in Path(output_dir).glob("frame_*.jpg"))
    return frames


async def extract_audio(video_path: str, output_path: str) -> bool:
    """Extract audio as 16kHz mono WAV.

    Returns True on success, False if the video has no audio stream.
    Raises RuntimeError for other FFmpeg failures.
    """
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_path,
        "-y",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()

    if proc.returncode != 0:
        stderr_text = stderr.decode(errors="replace").lower()
        if "does not contain any stream" in stderr_text or "no audio" in stderr_text:
            return False
        raise RuntimeError(f"Audio extraction failed: {stderr.decode(errors='replace')}")

    return True


async def update_upload_status(
    session,
    upload_id: uuid.UUID,
    status: str,
    **kwargs,
) -> None:
    """Fetch an upload by ID and update its status and optional fields."""
    upload = await session.get(Upload, upload_id)
    if upload is None:
        logger.error(f"Upload {upload_id} not found during status update")
        return

    upload.status = status
    for key, value in kwargs.items():
        setattr(upload, key, value)

    await session.commit()


async def process_video(upload_id: uuid.UUID, file_path: str, models: dict | None = None) -> None:
    """Orchestrate video preprocessing and detection pipeline.

    Creates its own database session (background task, not request-scoped).
    Updates Upload.status at each stage. If models are provided, chains into
    detection after preprocessing. Otherwise falls back to "queued" status.
    """
    async with async_session() as session:
        try:
            # Step 1: Validate video
            valid, reason = await validate_video(file_path)
            if not valid:
                await update_upload_status(
                    session, upload_id, "failed", error_message=reason
                )
                return

            # Step 2: Extract frames
            await update_upload_status(session, upload_id, "extracting_frames")
            frames_dir = str(Path(file_path).parent / "frames")
            await extract_frames(
                file_path, frames_dir, frame_interval=settings.frame_interval
            )

            # Step 3: Extract audio
            await update_upload_status(session, upload_id, "extracting_audio")
            audio_path = str(Path(file_path).parent / "audio.wav")
            has_audio = await extract_audio(file_path, audio_path)

            if not has_audio:
                logger.info(f"Upload {upload_id}: no audio track")

            # Step 4: Chain into detection or fall back to queued
            if models is not None:
                from app.services.detection import run_detection
                logger.info(f"Upload {upload_id}: preprocessing complete, starting detection")
                await run_detection(upload_id, file_path, models, session)
            else:
                await update_upload_status(session, upload_id, "queued")
                logger.info(f"Upload {upload_id}: preprocessing complete, status=queued (no models)")

        except Exception as e:
            logger.error(f"Upload {upload_id}: preprocessing failed - {e}")
            await update_upload_status(
                session, upload_id, "failed", error_message=str(e)
            )
