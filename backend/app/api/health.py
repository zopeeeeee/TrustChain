import logging

from fastapi import APIRouter, Request
from sqlalchemy import text

from app.database import async_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(request: Request) -> dict:
    """Check system health: database connectivity and model loading status."""
    # Check database
    db_status = "healthy"
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("Database health check failed: %s", exc)
        db_status = "unhealthy"

    # Check models
    visual_model = getattr(request.app.state, "visual_model", None)
    audio_model = getattr(request.app.state, "audio_model", None)
    fusion_model = getattr(request.app.state, "fusion_model", None)

    visual_status = "loaded" if visual_model is not None else "not_loaded"
    audio_status = "loaded" if audio_model is not None else "not_loaded"
    fusion_status = "loaded" if fusion_model is not None else "not_loaded"

    overall = "healthy" if db_status == "healthy" else "degraded"

    return {
        "status": overall,
        "database": db_status,
        "models": {
            "visual": visual_status,
            "audio": audio_status,
            "fusion": fusion_status,
        },
        "version": "0.1.0",
    }
