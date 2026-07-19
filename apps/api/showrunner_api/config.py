from functools import lru_cache
import logging

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            ".env",
            "../../.env",
            ".env.local",
            "../../.env.local",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "development"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    database_url: str | None = None
    alembic_database_url: str | None = None

    neo4j_uri: str | None = None
    neo4j_username: str = "neo4j"
    neo4j_password: str | None = None
    neo4j_database: str = "neo4j"
    neo4j_tier: str = "AuraDB Free"

    clerk_secret_key: str | None = None
    clerk_webhook_signing_secret: str | None = None
    clerk_issuer: str | None = None
    clerk_jwks_url: str | None = None
    clerk_jwt_audience: str | None = None

    qwen_api_key: str | None = None
    dashscope_api_key: str | None = None
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    fal_api_key: str | None = None

    backend_cors_origins: str = Field(default="http://localhost:3000")
    redis_url: str = "redis://localhost:6379/0"

    @field_validator("qwen_api_key", "dashscope_api_key", mode="before")
    @classmethod
    def strip_dots_from_keys(cls, v: str | None) -> str | None:
        """Remove any dots from API keys - they are visual separators only."""
        if v is None:
            return None
        # Remove all dots from the key string
        cleaned = v.replace(".", "")
        if cleaned != v:
            logger.warning(f"API key had dots removed: {v[:10]}... → {cleaned[:10]}...")
        return cleaned

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Debug: Log what's actually loaded (with masked keys)
        self._log_startup_info()

    def _log_startup_info(self):
        """Log configuration status without exposing sensitive data."""
        logger.info("=== QWEN/DASHSCOPE CONFIGURATION ===")
        logger.info(f"QWEN_API_KEY present: {bool(self.qwen_api_key)}")
        logger.info(f"DASHSCOPE_API_KEY present: {bool(self.dashscope_api_key)}")
        logger.info(f"Effective key present: {bool(self.effective_dashscope_key)}")
        logger.info(f"QWEN_BASE_URL: {self.qwen_base_url}")
        
        if self.qwen_api_key:
            key_prefix = self.qwen_api_key[:8] if len(self.qwen_api_key) >= 8 else self.qwen_api_key
            key_suffix = self.qwen_api_key[-4:] if len(self.qwen_api_key) >= 4 else ""
            logger.info(f"QWEN_API_KEY format: {key_prefix}...{key_suffix} (len={len(self.qwen_api_key)})")
            
            # Validate workspace key + URL combo
            if self.qwen_api_key.startswith("sk-ws-"):
                if "ws-" not in self.qwen_base_url:
                    logger.error(
                        "⚠️  MISMATCH: Workspace key (sk-ws-) requires workspace-specific base_url "
                        f"(e.g., https://ws-XXXXX.maas.aliyuncs.com/compatible-mode/v1). "
                        f"Current: {self.qwen_base_url}"
                    )
                else:
                    logger.info("✓ Workspace key and URL appear correctly matched")
            elif self.qwen_api_key.startswith("sk-"):
                if "dashscope.aliyuncs.com" not in self.qwen_base_url:
                    logger.warning(
                        f"Standard key (sk-) typically uses https://dashscope.aliyuncs.com/compatible-mode/v1, "
                        f"but using: {self.qwen_base_url}"
                    )
        
        if self.dashscope_api_key:
            key_prefix = self.dashscope_api_key[:8] if len(self.dashscope_api_key) >= 8 else self.dashscope_api_key
            key_suffix = self.dashscope_api_key[-4:] if len(self.dashscope_api_key) >= 4 else ""
            logger.info(f"DASHSCOPE_API_KEY format: {key_prefix}...{key_suffix} (len={len(self.dashscope_api_key)})")
        
        logger.info("====================================")

    @property
    def effective_dashscope_key(self) -> str | None:
        """Return whichever key is configured (QWEN_API_KEY wins over DASHSCOPE_API_KEY)."""
        return self.qwen_api_key or self.dashscope_api_key

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


# Cache that can be cleared on reload
_settings_cache = None


def get_settings(clear_cache: bool = False) -> Settings:
    """Get settings instance, optionally clearing cache for reload scenarios."""
    global _settings_cache
    if clear_cache or _settings_cache is None:
        _settings_cache = Settings()
    return _settings_cache
