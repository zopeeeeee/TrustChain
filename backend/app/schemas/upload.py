from pydantic import BaseModel


class UploadResponse(BaseModel):
    id: str
    status: str


class UploadStatusResponse(BaseModel):
    id: str
    filename: str
    status: str
    error_message: str | None = None
    created_at: str
    verdict: str | None = None
    confidence: float | None = None
    visual_score: float | None = None
    audio_score: float | None = None
    speech_detected: bool | None = None
    audio_weight: float | None = None
    file_hash: str | None = None
    processing_time: float | None = None
    completed_at: str | None = None


class UploadListResponse(BaseModel):
    items: list[UploadStatusResponse]
    total: int
    page: int
    per_page: int
    pages: int


class StatsResponse(BaseModel):
    total: int
    real: int
    fake: int
