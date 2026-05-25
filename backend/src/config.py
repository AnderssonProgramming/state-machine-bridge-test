"""Application configuration loaded from environment variables."""

from enum import Enum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class RepositoryBackend(str, Enum):
    """Available persistence backends."""

    MEMORY = "memory"
    DYNAMODB = "dynamodb"


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    repository_backend: RepositoryBackend = RepositoryBackend.MEMORY
    dynamodb_table_name: str = "orders"
    dynamodb_tickets_table_name: str = "support-tickets"
    aws_region: str = "us-east-1"
    anthropic_api_key: str = ""
    environment: str = "local"
    log_level: str = "INFO"
    powertools_service_name: str = "order-state-machine"
    allowed_origins: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
