from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app, lifespan


def _make_mock_models():
    """Create lightweight mock models for testing (no real weights)."""
    return {
        "visual_model": MagicMock(name="mock_visual_model"),
        "audio_processor": MagicMock(name="mock_audio_processor"),
        "audio_model": MagicMock(name="mock_audio_model"),
        "fusion_model": MagicMock(name="mock_fusion_model"),
    }


@pytest.fixture
async def async_client():
    """Provide an async HTTP client for testing the FastAPI app with lifespan."""
    with patch("app.main.load_models", return_value=_make_mock_models()):
        async with lifespan(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                yield client
