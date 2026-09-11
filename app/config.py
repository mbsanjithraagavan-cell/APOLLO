"""Validated environment configuration. No dotenv loading, I/O, or secrets in state."""
import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False, hide_input_in_errors=True)
    model_dir: Path = Path(r"C:\SLM-WORKSHOP\models\it")
    embedder_dir: Path = Path(r"C:\SLM-WORKSHOP\models\embedder")
    embedding_dimension: int = Field(default=384, gt=0)
    database_url: SecretStr | None = Field(default=None, repr=False)
    redis_url: SecretStr | None = Field(default=None, repr=False)
    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    rag_top_k: int = Field(default=3, ge=1, le=20)
    safety_confidence_threshold: float = Field(default=0.7, ge=0, le=1)
    redis_lease_seconds: int = Field(default=45, ge=1, le=300)
    max_new_tokens: int = Field(default=96, ge=8, le=256)

    @field_validator("model_dir", "embedder_dir")
    @classmethod
    def require_absolute_path(cls, value: Path) -> Path:
        if not value.is_absolute():
            raise ValueError("Model resource paths must be absolute")
        return value

    @field_validator("database_url", "redis_url")
    @classmethod
    def validate_service_url(cls, value: SecretStr | None, info):
        if value is None:
            return value
        try:
            parts = urlsplit(value.get_secret_value())
            permitted = {"postgres", "postgresql"} if info.field_name == "database_url" else {"redis", "rediss"}
            if parts.scheme not in permitted or not parts.hostname:
                raise ValueError
            _ = parts.port
        except ValueError:
            raise ValueError("Invalid service URL") from None
        return value

    @field_validator("rag_top_k", "redis_lease_seconds", "embedding_dimension", mode="before")
    @classmethod
    def reject_boolean_counts(cls, value):
        if isinstance(value, bool):
            raise ValueError("A count must be an integer, not a boolean")
        return value

    @classmethod
    def from_environment(cls) -> "Settings":
        names = {
            "model_dir": "APOLLO_MODEL_DIR", "embedder_dir": "APOLLO_EMBEDDER_DIR",
            "embedding_dimension": "APOLLO_EMBEDDING_DIMENSION",
            "database_url": "DATABASE_URL", "redis_url": "REDIS_URL",
            "environment": "APOLLO_ENV", "log_level": "APOLLO_LOG_LEVEL",
            "rag_top_k": "RAG_TOP_K",
            "safety_confidence_threshold": "SAFETY_CONFIDENCE_THRESHOLD",
            "redis_lease_seconds": "REDIS_LEASE_SECONDS",
            "max_new_tokens": "APOLLO_MAX_NEW_TOKENS",
        }
        return cls(**{field: os.environ[name] for field, name in names.items() if name in os.environ})

