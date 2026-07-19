from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env", ".env.local"),
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

    # API Keys - DO NOT strip dots, they are part of the key format
    qwen_api_key: str | None = None
    dashscope_api_key: str | None = None
    qwen_base_url: str = "https://ws-r0izv5baffzpmfae.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"

    @field_validator("qwen_api_key", "dashscope_api_key", mode="before")
    @classmethod
    def strip_whitespace_only(cls, v: str | None) -> str | None:
        """Only strip whitespace, NOT dots. Dots are part of sk-ws- keys."""
        if v is None:
            return None
        return v.strip()

    @property
    def effective_dashscope_key(self) -> str | None:
        """Return whichever key is configured (qwen_api_key wins over dashscope_api_key)."""
        return self.qwen_api_key or self.dashscope_api_key

    fal_api_key: str | None = None

    backend_cors_origins: str = Field(default="http://localhost:3000")
    redis_url: str = "redis://localhost:6379/0"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    def log_startup_info(self) -> None:
        """Log configuration status for debugging (without exposing full keys)."""
        if self.qwen_api_key:
            key_prefix = self.qwen_api_key[:10] if len(self.qwen_api_key) > 10 else self.qwen_api_key
            key_suffix = self.qwen_api_key[-4:] if len(self.qwen_api_key) > 4 else ""
            logger.info(f"✓ Qwen API Key loaded: {key_prefix}...{key_suffix} (len={len(self.qwen_api_key)})")
            logger.info(f"✓ Qwen Base URL: {self.qwen_base_url}")
            
            # Warn if using workspace key with generic URL or vice versa
            if self.qwen_api_key.startswith("sk-ws-") and "ws-" not in self.qwen_base_url:
                logger.warning("⚠️  WARNING: Workspace key (sk-ws-) detected but base URL is not workspace-specific!")
                logger.warning(f"   Expected URL format: https://ws-*.maas.aliyuncs.com/compatible-mode/v1")
                logger.warning(f"   Current URL: {self.qwen_base_url}")
            elif not self.qwen_api_key.startswith("sk-ws-") and "ws-" in self.qwen_base_url:
                logger.warning("⚠️  WARNING: Workspace URL detected but key doesn't start with sk-ws-!")
        else:
            logger.error("❌ CRITICAL: QWEN_API_KEY is not set!")
            logger.error("   Please set QWEN_API_KEY in your .env file")

@lru_cache(maxsize=None)
def get_settings() -> Settings:
    settings = Settings()
    settings.log_startup_info()
    return settings

def clear_settings_cache():
    """Clear the settings cache - call this when reloading configuration."""
    get_settings.cache_clear()