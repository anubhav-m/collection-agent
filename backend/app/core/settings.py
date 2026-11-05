"""Typed application settings loaded from the project-root .env file."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "collections-agent"
    log_level: str = "INFO"

    gemini_model: str = "gemini-model-not-set"
    gemini_api_key_1: SecretStr | None = None
    gemini_api_key_2: SecretStr | None = None
    gemini_api_key_3: SecretStr | None = None
    llm_requests_per_minute: int = Field(default=10, ge=1)
    llm_timeout_seconds: float = Field(default=30.0, gt=0)
    llm_max_retries: int = Field(default=4, ge=0)
    llm_cache_enabled: bool = False
    llm_cache_dir: Path = BACKEND_ROOT / ".llm_cache"

    lender_policy_dir: Path = BACKEND_ROOT / "data" / "lenders"

    policy_docs_dir: Path = BACKEND_ROOT / "data" / "policies"
    vector_store_dir: Path = BACKEND_ROOT / "data" / "vector_store"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_cache_dir: Path = BACKEND_ROOT / ".fastembed_cache"
    # Calibrated on this corpus; see SESSION_LOG.md Session 3 for the measured scores.
    rag_score_threshold: float = Field(default=0.40, ge=0, le=1)
    rag_top_k: int = Field(default=3, ge=1, le=10)

    # Required, no local fallback: a missing MONGODB_URI must fail loudly.
    mongodb_uri: SecretStr
    mongodb_db: str = "collections_agent"
    mongodb_timeout_ms: int = Field(default=5000, ge=100)

    @property
    def gemini_api_keys(self) -> list[str]:
        """Keys in fallback order; blank slots are skipped."""
        slots = (self.gemini_api_key_1, self.gemini_api_key_2, self.gemini_api_key_3)
        return [s.get_secret_value() for s in slots if s and s.get_secret_value().strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
