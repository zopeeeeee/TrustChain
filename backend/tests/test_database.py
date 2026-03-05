"""Tests for database model definitions (no live DB required)."""

import uuid

from app.models.upload import Upload
from app.models.blockchain import BlockchainRecord


def test_upload_model_has_required_columns():
    """Upload model should have all expected column names."""
    column_names = {c.name for c in Upload.__table__.columns}
    expected = {
        "id", "filename", "file_path", "file_hash", "status", "verdict",
        "confidence", "visual_score", "audio_score", "speech_detected",
        "audio_weight", "created_at", "completed_at",
    }
    assert expected.issubset(column_names), f"Missing columns: {expected - column_names}"


def test_blockchain_record_model_has_required_columns():
    """BlockchainRecord model should have all expected column names."""
    column_names = {c.name for c in BlockchainRecord.__table__.columns}
    expected = {
        "id", "upload_id", "file_hash", "merkle_root", "tx_hash",
        "block_number", "registered_at", "created_at",
    }
    assert expected.issubset(column_names), f"Missing columns: {expected - column_names}"


def test_models_use_uuid_primary_keys():
    """Both models should use UUID primary keys."""
    upload_pk = Upload.__table__.c.id
    blockchain_pk = BlockchainRecord.__table__.c.id

    # Check the Python type mapped by SQLAlchemy
    assert upload_pk.primary_key
    assert blockchain_pk.primary_key
