from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPOSITORY_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    app_env: Literal["development", "production"] = Field(validation_alias="APP_ENV")
    api_host: str = Field(validation_alias="API_HOST")
    api_port: int = Field(validation_alias="API_PORT", ge=1, le=65535)
    database_url: SecretStr = Field(validation_alias="DATABASE_URL")
    allowed_hosts: list[str] = Field(validation_alias="ALLOWED_HOSTS", min_length=1)
    allowed_origins: list[str] = Field(validation_alias="ALLOWED_ORIGINS", min_length=1)
    db_pool_size: int = Field(validation_alias="DB_POOL_SIZE", ge=1)
    db_max_overflow: int = Field(validation_alias="DB_MAX_OVERFLOW", ge=0)
    db_pool_timeout_seconds: int = Field(validation_alias="DB_POOL_TIMEOUT_SECONDS", ge=1)
    db_pool_recycle_seconds: int = Field(validation_alias="DB_POOL_RECYCLE_SECONDS", ge=1)
    db_connect_timeout_seconds: int = Field(validation_alias="DB_CONNECT_TIMEOUT_SECONDS", ge=1)
    db_read_timeout_seconds: int = Field(validation_alias="DB_READ_TIMEOUT_SECONDS", ge=1)
    db_write_timeout_seconds: int = Field(validation_alias="DB_WRITE_TIMEOUT_SECONDS", ge=1)
    db_lock_wait_timeout_seconds: int = Field(
        validation_alias="DB_LOCK_WAIT_TIMEOUT_SECONDS",
        ge=1,
    )

    @field_validator("api_host")
    @classmethod
    def require_development_loopback_host(cls, value: str, info: ValidationInfo) -> str:
        if info.data.get("app_env") == "development" and value != "127.0.0.1":
            raise ValueError("development API_HOST must be 127.0.0.1")
        return value


@lru_cache
def get_settings() -> Settings:
    # BaseSettings supplies required fields from environment sources at runtime.
    return Settings()  # type: ignore[call-arg, unused-ignore]
