import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.ml.loader import load_models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle: load models on startup, cleanup on shutdown."""
    logger.info("Starting TrustChain-AV backend...")

    # Load ML models at startup
    models = load_models()
    app.state.visual_model = models["visual_model"]
    app.state.audio_processor = models["audio_processor"]
    app.state.audio_model = models["audio_model"]
    app.state.fusion_model = models["fusion_model"]

    logger.info("TrustChain-AV backend ready")
    yield

    # Cleanup on shutdown
    app.state.visual_model = None
    app.state.audio_processor = None
    app.state.audio_model = None
    app.state.fusion_model = None
    logger.info("TrustChain-AV backend shutdown complete")


app = FastAPI(
    title="TrustChain-AV",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
