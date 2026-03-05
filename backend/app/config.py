from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://trustchain:trustchain@db:5432/trustchain_db"
    debug: bool = False
    api_prefix: str = "/api"
    cors_origins: list[str] = ["http://localhost:5173"]

    # Upload settings
    upload_dir: str = "/data"
    max_file_size: int = 500 * 1024 * 1024  # 500MB
    allowed_extensions: list[str] = [".mp4", ".avi", ".mov", ".mkv"]
    frame_interval: int = 10  # Extract every Nth frame

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
