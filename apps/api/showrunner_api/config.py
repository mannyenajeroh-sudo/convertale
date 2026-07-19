from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
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

    @property
    def effective_dashscope_key(self) -> str | None:
        """Return whichever key is configured (QWEN_API_KEY wins over DASHSCOPE_API_KEY)."""
        return self.qwen_api_key or self.dashscope_api_key

    fal_api_key: str | None = None

    backend_cors_origins: str = Field(default="http://localhost:3000")
    redis_url: str = "redis://localhost:6379/0"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
