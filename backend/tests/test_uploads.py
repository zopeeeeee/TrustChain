import math
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.main import app, lifespan
from app.models.upload import Upload


def make_mock_upload(**overrides):
    """Create a mock Upload object with sensible defaults."""
    obj = MagicMock(spec=Upload)
    obj.id = overrides.get("id", uuid.uuid4())
    obj.filename = overrides.get("filename", "test.mp4")
    obj.status = overrides.get("status", "uploading")
    obj.error_message = overrides.get("error_message", None)
    obj.created_at = overrides.get("created_at", datetime(2026, 1, 1))
    obj.file_path = overrides.get("file_path", None)
    obj.file_hash = overrides.get("file_hash", None)
    obj.verdict = overrides.get("verdict", None)
    obj.confidence = overrides.get("confidence", None)
    obj.visual_score = overrides.get("visual_score", None)
    obj.audio_score = overrides.get("audio_score", None)
    obj.speech_detected = overrides.get("speech_detected", None)
    obj.audio_weight = overrides.get("audio_weight", None)
    obj.completed_at = overrides.get("completed_at", None)
    return obj


@pytest.fixture
async def upload_client(tmp_path):
    """Provide an async HTTP client with mocked DB and file I/O for upload tests."""
    mock_session = AsyncMock()
    mock_upload = make_mock_upload()

    mock_session.get = AsyncMock(return_value=mock_upload)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    with (
        patch("app.api.uploads.settings") as mock_settings,
        patch("app.api.uploads.process_video", new_callable=AsyncMock) as mock_pv,
    ):
        mock_settings.upload_dir = str(tmp_path)
        mock_settings.max_file_size = 500 * 1024 * 1024
        mock_settings.allowed_extensions = [".mp4", ".avi", ".mov", ".mkv"]
        mock_settings.frame_interval = 10

        async with lifespan(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                yield client, mock_session, mock_upload, mock_pv

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_valid_mp4_returns_201(upload_client):
    """POST /api/uploads with valid .mp4 file returns 201 with id and status."""
    client, mock_session, mock_upload, _ = upload_client

    file_content = b"\x00" * 1024  # 1KB dummy content
    response = await client.post(
        "/api/uploads",
        files={"file": ("test_video.mp4", BytesIO(file_content), "video/mp4")},
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "uploading"


@pytest.mark.asyncio
async def test_upload_invalid_extension_returns_400(upload_client):
    """POST /api/uploads with .txt file returns 400 with error about unsupported format."""
    client, _, _, _ = upload_client

    file_content = b"not a video"
    response = await client.post(
        "/api/uploads",
        files={"file": ("document.txt", BytesIO(file_content), "text/plain")},
    )

    assert response.status_code == 400
    data = response.json()
    assert "unsupported" in data["detail"].lower() or "format" in data["detail"].lower()


@pytest.mark.asyncio
async def test_upload_oversized_file_returns_400(upload_client):
    """POST /api/uploads with file exceeding max size returns 400."""
    client, _, _, _ = upload_client

    # Create a small file but mock the size header to simulate oversized
    file_content = b"\x00" * 100
    response = await client.post(
        "/api/uploads",
        files={"file": ("big_video.mp4", BytesIO(file_content), "video/mp4")},
        headers={"Content-Length": str(600 * 1024 * 1024)},  # 600MB
    )

    assert response.status_code == 400
    data = response.json()
    assert "size" in data["detail"].lower() or "large" in data["detail"].lower()


@pytest.fixture
async def status_client():
    """Provide an async HTTP client for status endpoint tests."""
    test_upload_id = uuid.uuid4()

    mock_upload = make_mock_upload(
        id=test_upload_id,
        status="extracting_frames",
    )

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_upload)

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, test_upload_id, mock_session

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_status_returns_upload_info(status_client):
    """GET /api/uploads/{valid_id}/status returns upload status info."""
    client, upload_id, _ = status_client

    response = await client.get(f"/api/uploads/{upload_id}/status")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(upload_id)
    assert data["filename"] == "test.mp4"
    assert data["status"] == "extracting_frames"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_status_nonexistent_returns_404(status_client):
    """GET /api/uploads/{random_uuid}/status returns 404."""
    client, _, mock_session = status_client

    # Make session.get return None for unknown ID
    mock_session.get = AsyncMock(return_value=None)

    random_id = uuid.uuid4()
    response = await client.get(f"/api/uploads/{random_id}/status")

    assert response.status_code == 404


# ---------- List / Stats / processing_time tests ----------


def _make_scalars_result(items):
    """Create a mock result whose .scalars().all() returns items."""
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = items
    mock_result.scalars.return_value = mock_scalars
    return mock_result


def _make_scalar_result(value):
    """Create a mock result whose .scalar() returns value."""
    mock_result = MagicMock()
    mock_result.scalar.return_value = value
    return mock_result


@pytest.fixture
async def list_client():
    """Provide an async HTTP client for list endpoint tests."""
    uploads = [
        make_mock_upload(
            id=uuid.uuid4(),
            filename="video1.mp4",
            status="completed",
            verdict="REAL",
            confidence=0.85,
            completed_at=datetime(2026, 1, 1, 0, 5, 0),
        ),
        make_mock_upload(
            id=uuid.uuid4(),
            filename="test_clip.mp4",
            status="completed",
            verdict="FAKE",
            confidence=0.92,
            completed_at=datetime(2026, 1, 1, 0, 3, 0),
        ),
        make_mock_upload(
            id=uuid.uuid4(),
            filename="sample.avi",
            status="failed",
            error_message="Processing error",
        ),
    ]

    mock_session = AsyncMock()

    # db.execute() returns different results based on the query
    call_count = {"n": 0}

    async def mock_execute(stmt, *args, **kwargs):
        call_count["n"] += 1
        # First call is the count query, second is the data query
        if call_count["n"] % 2 == 1:
            return _make_scalar_result(len(uploads))
        else:
            return _make_scalars_result(uploads)

    mock_session.execute = mock_execute

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, mock_session, uploads

    app.dependency_overrides.clear()


@pytest.fixture
async def stats_client():
    """Provide an async HTTP client for stats endpoint tests."""
    mock_session = AsyncMock()

    call_count = {"n": 0}

    async def mock_execute(stmt, *args, **kwargs):
        call_count["n"] += 1
        # total=10, real=6, fake=4
        values = [10, 6, 4]
        idx = min(call_count["n"] - 1, 2)
        return _make_scalar_result(values[idx])

    mock_session.execute = mock_execute

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, mock_session

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_uploads_returns_paginated(list_client):
    """GET /api/uploads returns 200 with items array, total, page, per_page, pages."""
    client, _, uploads = list_client
    response = await client.get("/api/uploads")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert "pages" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_list_uploads_pagination_params(list_client):
    """GET /api/uploads?page=1&per_page=10 returns correct pagination."""
    client, _, _ = list_client
    response = await client.get("/api/uploads?page=1&per_page=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["per_page"] == 10


@pytest.mark.asyncio
async def test_list_uploads_search_filter(list_client):
    """GET /api/uploads?search=test returns filtered results."""
    client, mock_session, uploads = list_client

    # Override execute to return only matching uploads
    filtered = [u for u in uploads if "test" in u.filename.lower()]
    call_count = {"n": 0}

    async def mock_execute(stmt, *args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] % 2 == 1:
            return _make_scalar_result(len(filtered))
        else:
            return _make_scalars_result(filtered)

    mock_session.execute = mock_execute

    response = await client.get("/api/uploads?search=test")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    for item in data["items"]:
        assert "test" in item["filename"].lower()


@pytest.mark.asyncio
async def test_list_uploads_verdict_filter(list_client):
    """GET /api/uploads?verdict=REAL returns only REAL uploads."""
    client, mock_session, uploads = list_client

    filtered = [u for u in uploads if u.verdict == "REAL"]
    call_count = {"n": 0}

    async def mock_execute(stmt, *args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] % 2 == 1:
            return _make_scalar_result(len(filtered))
        else:
            return _make_scalars_result(filtered)

    mock_session.execute = mock_execute

    response = await client.get("/api/uploads?verdict=REAL")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["verdict"] == "REAL"


@pytest.mark.asyncio
async def test_list_uploads_failed_filter(list_client):
    """GET /api/uploads?verdict=failed returns only failed uploads."""
    client, mock_session, uploads = list_client

    filtered = [u for u in uploads if u.status == "failed"]
    call_count = {"n": 0}

    async def mock_execute(stmt, *args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] % 2 == 1:
            return _make_scalar_result(len(filtered))
        else:
            return _make_scalars_result(filtered)

    mock_session.execute = mock_execute

    response = await client.get("/api/uploads?verdict=failed")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["status"] == "failed"


@pytest.mark.asyncio
async def test_stats_returns_counts(stats_client):
    """GET /api/uploads/stats returns 200 with total, real, fake counts."""
    client, _ = stats_client
    response = await client.get("/api/uploads/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert data["real"] == 6
    assert data["fake"] == 4


@pytest.mark.asyncio
async def test_status_includes_processing_time():
    """GET /api/uploads/{id}/status includes processing_time field."""
    test_id = uuid.uuid4()
    created = datetime(2026, 1, 1, 0, 0, 0)
    completed = datetime(2026, 1, 1, 0, 0, 15)

    mock_upload = make_mock_upload(
        id=test_id,
        status="completed",
        created_at=created,
        completed_at=completed,
        verdict="REAL",
        confidence=0.9,
    )

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_upload)

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/uploads/{test_id}/status")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert "processing_time" in data
    assert data["processing_time"] == 15.0
