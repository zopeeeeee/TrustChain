import asyncio
import hashlib
import math
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.upload import Upload
from app.schemas.upload import (
    StatsResponse,
    UploadListResponse,
    UploadResponse,
    UploadStatusResponse,
)
from app.services.preprocessing import process_video

router = APIRouter(prefix="/uploads", tags=["uploads"])

CHUNK_SIZE = 1024 * 1024  # 1MB chunks


def _to_status_response(upload: Upload) -> UploadStatusResponse:
    """Convert an Upload model to UploadStatusResponse, computing processing_time."""
    processing_time = None
    if upload.completed_at and upload.created_at:
        try:
            delta = upload.completed_at - upload.created_at
            processing_time = delta.total_seconds()
        except (TypeError, AttributeError):
            processing_time = None

    return UploadStatusResponse(
        id=str(upload.id),
        filename=upload.filename,
        status=upload.status,
        error_message=upload.error_message,
        created_at=str(upload.created_at),
        verdict=upload.verdict,
        confidence=upload.confidence,
        visual_score=upload.visual_score,
        audio_score=upload.audio_score,
        speech_detected=upload.speech_detected,
        audio_weight=upload.audio_weight,
        file_hash=upload.file_hash,
        processing_time=processing_time,
        completed_at=str(upload.completed_at) if upload.completed_at else None,
    )


@router.post("", status_code=201, response_model=UploadResponse)
async def upload_video(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Accept a video file upload, validate, save to disk, and start background processing."""
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    extension = Path(file.filename).suffix.lower()
    if extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{extension}'. Allowed: {', '.join(settings.allowed_extensions)}",
        )

    # Validate file size via Content-Length header if available
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.max_file_size // (1024 * 1024)}MB",
        )

    # Also check file.size if available (python-multipart sets this)
    if file.size is not None and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.max_file_size // (1024 * 1024)}MB",
        )

    # Create upload record
    upload = Upload(
        id=uuid.uuid4(),
        filename=file.filename,
        status="uploading",
    )
    db.add(upload)
    await db.commit()
    await db.refresh(upload)

    # Create upload directory
    upload_dir = Path(settings.upload_dir) / str(upload.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename

    # Stream file to disk with SHA-256 hashing
    sha256_hash = hashlib.sha256()
    total_size = 0

    async with aiofiles.open(file_path, "wb") as out_file:
        while chunk := await file.read(CHUNK_SIZE):
            sha256_hash.update(chunk)
            total_size += len(chunk)
            await out_file.write(chunk)

    # Verify actual file size
    if total_size > settings.max_file_size:
        file_path.unlink(missing_ok=True)
        upload.status = "failed"
        upload.error_message = "File too large after upload"
        await db.commit()
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.max_file_size // (1024 * 1024)}MB",
        )

    # Update record with file path and hash
    upload.file_path = str(file_path)
    upload.file_hash = sha256_hash.hexdigest()
    await db.commit()

    # Fire background preprocessing task with ML models
    models = {
        "visual_model": request.app.state.visual_model,
        "audio_processor": request.app.state.audio_processor,
        "audio_model": request.app.state.audio_model,
        "fusion_model": request.app.state.fusion_model,
    }
    asyncio.create_task(process_video(upload.id, str(file_path), models))

    return UploadResponse(id=str(upload.id), status=upload.status)


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get aggregate upload statistics."""
    total_result = await db.execute(select(func.count()).select_from(Upload))
    total = total_result.scalar() or 0

    real_result = await db.execute(
        select(func.count()).select_from(Upload).where(Upload.verdict == "REAL")
    )
    real = real_result.scalar() or 0

    fake_result = await db.execute(
        select(func.count()).select_from(Upload).where(Upload.verdict == "FAKE")
    )
    fake = fake_result.scalar() or 0

    return StatsResponse(total=total, real=real, fake=fake)


@router.get("", response_model=UploadListResponse)
async def list_uploads(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    verdict: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List uploads with pagination, search, and filter support."""
    # Base query
    base_query = select(Upload)
    count_query = select(func.count()).select_from(Upload)

    # Apply filters
    if search:
        base_query = base_query.where(Upload.filename.ilike(f"%{search}%"))
        count_query = count_query.where(Upload.filename.ilike(f"%{search}%"))

    if verdict:
        if verdict.lower() == "failed":
            base_query = base_query.where(Upload.status == "failed")
            count_query = count_query.where(Upload.status == "failed")
        else:
            base_query = base_query.where(Upload.verdict == verdict.upper())
            count_query = count_query.where(Upload.verdict == verdict.upper())

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    offset = (page - 1) * per_page
    data_query = base_query.order_by(Upload.created_at.desc()).offset(offset).limit(per_page)

    result = await db.execute(data_query)
    uploads = result.scalars().all()

    pages = math.ceil(total / per_page) if total > 0 else 1

    items = [_to_status_response(u) for u in uploads]

    return UploadListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/{upload_id}/status", response_model=UploadStatusResponse)
async def get_upload_status(
    upload_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get the current processing status for an upload."""
    upload = await db.get(Upload, upload_id)
    if upload is None:
        raise HTTPException(status_code=404, detail="Upload not found")

    return _to_status_response(upload)
