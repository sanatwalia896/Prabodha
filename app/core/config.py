from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Prabodha"
    app_version: str = "0.1.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./prabodha.db"
    media_root: str = "./data/media"
    redis_url: str = "redis://localhost:6379/0"
    ai_engine_url: str = "http://localhost:11434"
    jwt_secret: str = "change-me-in-production"
    access_token_minutes: int = 120

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
