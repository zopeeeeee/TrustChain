import pytest


@pytest.mark.asyncio
async def test_health_returns_200(async_client):
    """Health endpoint should return 200 status code."""
    response = await async_client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_has_model_status(async_client):
    """Health response should include model status fields."""
    response = await async_client.get("/api/health")
    data = response.json()
    assert "models" in data
    assert "visual" in data["models"]
    assert "audio" in data["models"]
    assert "fusion" in data["models"]


@pytest.mark.asyncio
async def test_models_loaded_at_startup(async_client):
    """Models should show 'loaded' status after lifespan startup."""
    response = await async_client.get("/api/health")
    data = response.json()
    assert data["models"]["visual"] == "loaded"
    assert data["models"]["audio"] == "loaded"
    assert data["models"]["fusion"] == "loaded"
