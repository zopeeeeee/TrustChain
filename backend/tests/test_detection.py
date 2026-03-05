"""Tests for the detection orchestrator service."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import torch

from app.services.detection import run_detection


@pytest.fixture
def mock_models():
    """Create mock ML models dict matching app.state structure."""
    visual_model = MagicMock(name="visual_model")
    audio_processor = MagicMock(name="audio_processor")
    audio_model = MagicMock(name="audio_model")
    fusion_model = MagicMock(name="fusion_model")
    return {
        "visual_model": visual_model,
        "audio_processor": audio_processor,
        "audio_model": audio_model,
        "fusion_model": fusion_model,
    }


@pytest.fixture
def mock_session():
    """Create a mock async database session."""
    session = AsyncMock()
    return session


@pytest.fixture
def upload_id():
    return uuid.uuid4()


@pytest.mark.asyncio
@patch("app.services.detection.extract_visual_features")
@patch("app.services.detection.extract_audio_features")
@patch("app.services.detection.detect_speech")
@patch("app.services.detection.update_upload_status")
async def test_run_detection_status_transitions(
    mock_update_status,
    mock_detect_speech,
    mock_extract_audio,
    mock_extract_visual,
    mock_models,
    mock_session,
    upload_id,
    tmp_path,
):
    """run_detection cycles status through visual_analysis -> audio_analysis -> computing_fusion -> completed."""
    # Setup mocks
    mock_extract_visual.return_value = torch.randn(2048)
    mock_detect_speech.return_value = True
    mock_extract_audio.return_value = torch.randn(768)
    mock_models["fusion_model"].return_value = torch.tensor(0.7)

    job_dir = tmp_path / "job"
    job_dir.mkdir()
    frames_dir = job_dir / "frames"
    frames_dir.mkdir()
    audio_path = job_dir / "audio.wav"
    audio_path.write_text("fake")

    file_path = str(job_dir / "video.mp4")

    await run_detection(upload_id, file_path, mock_models, mock_session)

    # Collect all status updates
    status_calls = [
        call.kwargs.get("status", call.args[2] if len(call.args) > 2 else None)
        for call in mock_update_status.call_args_list
    ]

    assert "visual_analysis" in status_calls
    assert "audio_analysis" in status_calls
    assert "computing_fusion" in status_calls
    assert "completed" in status_calls

    # Verify order
    va_idx = status_calls.index("visual_analysis")
    aa_idx = status_calls.index("audio_analysis")
    cf_idx = status_calls.index("computing_fusion")
    co_idx = status_calls.index("completed")
    assert va_idx < aa_idx < cf_idx < co_idx


@pytest.mark.asyncio
@patch("app.services.detection.extract_visual_features")
@patch("app.services.detection.extract_audio_features")
@patch("app.services.detection.detect_speech")
@patch("app.services.detection.update_upload_status")
async def test_run_detection_stores_results(
    mock_update_status,
    mock_detect_speech,
    mock_extract_audio,
    mock_extract_visual,
    mock_models,
    mock_session,
    upload_id,
    tmp_path,
):
    """run_detection stores verdict, confidence, visual_score, audio_score in database."""
    mock_extract_visual.return_value = torch.randn(2048)
    mock_detect_speech.return_value = True
    mock_extract_audio.return_value = torch.randn(768)
    mock_models["fusion_model"].return_value = torch.tensor(0.7)

    job_dir = tmp_path / "job"
    job_dir.mkdir()
    (job_dir / "frames").mkdir()
    (job_dir / "audio.wav").write_text("fake")

    await run_detection(upload_id, str(job_dir / "video.mp4"), mock_models, mock_session)

    # Find the final "completed" status call
    final_call = mock_update_status.call_args_list[-1]
    kwargs = final_call.kwargs if final_call.kwargs else {}

    # Should have verdict and confidence
    assert "verdict" in kwargs
    assert kwargs["verdict"] in ("REAL", "FAKE")
    assert "confidence" in kwargs
    assert 0.0 <= kwargs["confidence"] <= 1.0
    assert "visual_score" in kwargs
    assert "audio_score" in kwargs
    assert "completed_at" in kwargs


@pytest.mark.asyncio
@patch("app.services.detection.extract_visual_features")
@patch("app.services.detection.detect_speech")
@patch("app.services.detection.update_upload_status")
async def test_run_detection_no_speech(
    mock_update_status,
    mock_detect_speech,
    mock_extract_visual,
    mock_models,
    mock_session,
    upload_id,
    tmp_path,
):
    """run_detection with no speech sets audio_weight=0.0, speech_detected=False, uses zero audio vector."""
    mock_extract_visual.return_value = torch.randn(2048)
    mock_detect_speech.return_value = False
    mock_models["fusion_model"].return_value = torch.tensor(0.3)

    job_dir = tmp_path / "job"
    job_dir.mkdir()
    (job_dir / "frames").mkdir()
    (job_dir / "audio.wav").write_text("fake")

    await run_detection(upload_id, str(job_dir / "video.mp4"), mock_models, mock_session)

    # Find the final "completed" status call
    final_call = mock_update_status.call_args_list[-1]
    kwargs = final_call.kwargs if final_call.kwargs else {}

    assert kwargs.get("speech_detected") is False
    assert kwargs.get("audio_weight") == 0.0


@pytest.mark.asyncio
@patch("app.services.detection.extract_visual_features")
@patch("app.services.detection.detect_speech")
@patch("app.services.detection.update_upload_status")
async def test_run_detection_sets_completed_at(
    mock_update_status,
    mock_detect_speech,
    mock_extract_visual,
    mock_models,
    mock_session,
    upload_id,
    tmp_path,
):
    """run_detection sets completed_at timestamp on success."""
    mock_extract_visual.return_value = torch.randn(2048)
    mock_detect_speech.return_value = False
    mock_models["fusion_model"].return_value = torch.tensor(0.4)

    job_dir = tmp_path / "job"
    job_dir.mkdir()
    (job_dir / "frames").mkdir()
    (job_dir / "audio.wav").write_text("fake")

    await run_detection(upload_id, str(job_dir / "video.mp4"), mock_models, mock_session)

    final_call = mock_update_status.call_args_list[-1]
    kwargs = final_call.kwargs if final_call.kwargs else {}

    assert "completed_at" in kwargs
    assert isinstance(kwargs["completed_at"], datetime)


@pytest.mark.asyncio
@patch("app.services.detection.extract_visual_features")
@patch("app.services.detection.update_upload_status")
async def test_run_detection_error_handling(
    mock_update_status,
    mock_extract_visual,
    mock_models,
    mock_session,
    upload_id,
    tmp_path,
):
    """run_detection catches exceptions and sets status=failed with error_message."""
    mock_extract_visual.side_effect = RuntimeError("GPU out of memory")

    job_dir = tmp_path / "job"
    job_dir.mkdir()
    (job_dir / "frames").mkdir()

    await run_detection(upload_id, str(job_dir / "video.mp4"), mock_models, mock_session)

    # Should have a "failed" status call
    final_call = mock_update_status.call_args_list[-1]
    args = final_call.args if final_call.args else ()
    kwargs = final_call.kwargs if final_call.kwargs else {}

    assert args[2] == "failed" if len(args) > 2 else kwargs.get("status") == "failed"
    assert "error_message" in kwargs
    assert "GPU out of memory" in kwargs["error_message"]


@pytest.mark.asyncio
@patch("app.services.detection.run_detection")
@patch("app.services.preprocessing.validate_video", return_value=(True, ""))
@patch("app.services.preprocessing.extract_frames", return_value=["frame_0001.jpg"])
@patch("app.services.preprocessing.extract_audio", return_value=True)
async def test_process_video_chains_detection(
    mock_extract_audio,
    mock_extract_frames,
    mock_validate,
    mock_run_detection,
    tmp_path,
):
    """process_video now chains into run_detection instead of stopping at 'queued'."""
    from app.services.preprocessing import process_video

    upload_id = uuid.uuid4()
    file_path = str(tmp_path / "video.mp4")
    models = {"visual_model": MagicMock()}

    with patch("app.services.preprocessing.async_session") as mock_session_ctx:
        mock_session = AsyncMock()
        mock_session_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        # Mock update_upload_status
        with patch("app.services.preprocessing.update_upload_status", new_callable=AsyncMock):
            await process_video(upload_id, file_path, models)

    # run_detection should have been called
    mock_run_detection.assert_called_once()
    call_args = mock_run_detection.call_args
    assert call_args.args[0] == upload_id or call_args.kwargs.get("upload_id") == upload_id
