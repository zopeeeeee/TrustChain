"""Test fixtures for video processing integration tests.

NOTE: Generating a real test MP4 requires FFmpeg to be installed.
These fixtures are for future integration tests that run in Docker
where FFmpeg is available.
"""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def test_video(tmp_path) -> Path:
    """Generate a small synthetic MP4 test video (~10KB) using FFmpeg.

    Requires FFmpeg to be installed. Skips if not available.
    Creates a 2-second video with a test pattern and silent audio.
    """
    output_path = tmp_path / "test_video.mp4"

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-f", "lavfi",
                "-i", "testsrc=duration=2:size=224x224:rate=10",
                "-f", "lavfi",
                "-i", "anullsrc=r=16000:cl=mono",
                "-t", "2",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-c:a", "aac",
                "-shortest",
                str(output_path),
                "-y",
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        pytest.skip("FFmpeg not available for integration test fixture")

    return output_path


@pytest.fixture
def test_video_no_audio(tmp_path) -> Path:
    """Generate a small synthetic MP4 test video without audio."""
    output_path = tmp_path / "test_video_no_audio.mp4"

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-f", "lavfi",
                "-i", "testsrc=duration=2:size=224x224:rate=10",
                "-t", "2",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-an",
                str(output_path),
                "-y",
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        pytest.skip("FFmpeg not available for integration test fixture")

    return output_path
