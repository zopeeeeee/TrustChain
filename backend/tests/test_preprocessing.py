import json
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# --- Mock subprocess helpers ---

def make_mock_process(returncode=0, stdout=b"", stderr=b""):
    """Create a mock async subprocess process."""
    proc = AsyncMock()
    proc.returncode = returncode
    proc.communicate = AsyncMock(return_value=(stdout, stderr))
    return proc


# --- probe_video tests ---

@pytest.mark.asyncio
async def test_probe_video_returns_parsed_json():
    """probe_video returns parsed JSON with duration from FFprobe."""
    from app.services.preprocessing import probe_video

    probe_output = json.dumps({
        "format": {"duration": "10.5", "filename": "test.mp4"},
        "streams": [{"codec_type": "video"}],
    }).encode()

    mock_proc = make_mock_process(returncode=0, stdout=probe_output)

    with patch("app.services.preprocessing.asyncio") as mock_asyncio:
        mock_asyncio.create_subprocess_exec = AsyncMock(return_value=mock_proc)
        result = await probe_video("/fake/test.mp4")

    assert result["format"]["duration"] == "10.5"


# --- extract_frames tests ---

@pytest.mark.asyncio
async def test_extract_frames_produces_jpg_files(tmp_path):
    """extract_frames produces .jpg files in output dir when FFmpeg succeeds."""
    from app.services.preprocessing import extract_frames

    # Create fake frame files to simulate FFmpeg output
    output_dir = tmp_path / "frames"
    output_dir.mkdir()
    for i in range(1, 4):
        (output_dir / f"frame_{i:04d}.jpg").write_bytes(b"\xff\xd8\xff")

    mock_proc = make_mock_process(returncode=0)

    with patch("app.services.preprocessing.asyncio") as mock_asyncio:
        mock_asyncio.create_subprocess_exec = AsyncMock(return_value=mock_proc)
        frames = await extract_frames("/fake/video.mp4", str(output_dir), frame_interval=10)

    assert len(frames) == 3
    assert all(f.endswith(".jpg") for f in frames)


# --- extract_audio tests ---

@pytest.mark.asyncio
async def test_extract_audio_produces_wav_file():
    """extract_audio returns True when FFmpeg succeeds."""
    from app.services.preprocessing import extract_audio

    mock_proc = make_mock_process(returncode=0)

    with patch("app.services.preprocessing.asyncio") as mock_asyncio:
        mock_asyncio.create_subprocess_exec = AsyncMock(return_value=mock_proc)
        result = await extract_audio("/fake/video.mp4", "/fake/audio.wav")

    assert result is True


@pytest.mark.asyncio
async def test_extract_audio_returns_false_for_no_audio_stream():
    """extract_audio returns False when FFmpeg stderr says no audio stream."""
    from app.services.preprocessing import extract_audio

    mock_proc = make_mock_process(
        returncode=1,
        stderr=b"Output file #0 does not contain any stream",
    )

    with patch("app.services.preprocessing.asyncio") as mock_asyncio:
        mock_asyncio.create_subprocess_exec = AsyncMock(return_value=mock_proc)
        result = await extract_audio("/fake/video.mp4", "/fake/audio.wav")

    assert result is False


# --- validate_video tests ---

@pytest.mark.asyncio
async def test_validate_video_rejects_short_video():
    """validate_video rejects video with duration < 1.0 second."""
    from app.services.preprocessing import validate_video

    probe_output = json.dumps({
        "format": {"duration": "0.5"},
        "streams": [],
    }).encode()

    mock_proc = make_mock_process(returncode=0, stdout=probe_output)

    with patch("app.services.preprocessing.asyncio") as mock_asyncio:
        mock_asyncio.create_subprocess_exec = AsyncMock(return_value=mock_proc)
        valid, reason = await validate_video("/fake/short.mp4")

    assert valid is False
    assert "1 second" in reason.lower()


@pytest.mark.asyncio
async def test_validate_video_rejects_corrupted_file():
    """validate_video rejects corrupted file when FFprobe returns non-zero."""
    from app.services.preprocessing import validate_video

    mock_proc = make_mock_process(returncode=1, stderr=b"Invalid data found")

    with patch("app.services.preprocessing.asyncio") as mock_asyncio:
        mock_asyncio.create_subprocess_exec = AsyncMock(return_value=mock_proc)
        valid, reason = await validate_video("/fake/corrupted.mp4")

    assert valid is False
    assert "corrupt" in reason.lower() or "valid" in reason.lower()


# --- process_video tests ---

@pytest.mark.asyncio
async def test_process_video_orchestrates_stages():
    """process_video updates status through stages: extracting_frames -> extracting_audio -> queued."""
    from app.services.preprocessing import process_video

    upload_id = uuid.uuid4()

    # Track all status values set on the upload object
    status_history = []

    class FakeUpload:
        def __init__(self):
            self.id = upload_id
            self._status = "uploading"
            self.error_message = None
            self.audio_weight = None

        @property
        def status(self):
            return self._status

        @status.setter
        def status(self, value):
            status_history.append(value)
            self._status = value

    mock_upload = FakeUpload()

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_upload)
    mock_session.commit = AsyncMock()

    mock_session_factory = MagicMock()
    mock_session_factory.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_factory.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("app.services.preprocessing.async_session", return_value=mock_session_factory),
        patch("app.services.preprocessing.validate_video", new_callable=AsyncMock, return_value=(True, "")),
        patch("app.services.preprocessing.extract_frames", new_callable=AsyncMock, return_value=["/fake/frame_0001.jpg"]),
        patch("app.services.preprocessing.extract_audio", new_callable=AsyncMock, return_value=True),
    ):
        await process_video(upload_id, "/fake/video.mp4")

    assert "extracting_frames" in status_history
    assert "extracting_audio" in status_history
    assert "queued" in status_history


@pytest.mark.asyncio
async def test_process_video_sets_failed_on_error():
    """process_video sets status=failed and error_message when FFmpeg fails."""
    from app.services.preprocessing import process_video

    upload_id = uuid.uuid4()
    mock_upload = MagicMock()
    mock_upload.id = upload_id

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_upload)
    mock_session.commit = AsyncMock()

    mock_session_factory = MagicMock()
    mock_session_factory.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_factory.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("app.services.preprocessing.async_session", return_value=mock_session_factory),
        patch("app.services.preprocessing.validate_video", new_callable=AsyncMock, return_value=(True, "")),
        patch("app.services.preprocessing.extract_frames", new_callable=AsyncMock, side_effect=RuntimeError("FFmpeg failed")),
    ):
        await process_video(upload_id, "/fake/video.mp4")

    # Check that status was set to failed
    assert mock_upload.status == "failed"
    assert mock_upload.error_message is not None
    assert "FFmpeg failed" in str(mock_upload.error_message)
