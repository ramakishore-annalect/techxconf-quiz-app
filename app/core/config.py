"""Application configuration."""

import os
from typing import Any, List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # App Info
    APP_NAME: str = "Quiz Backend API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: Optional[PostgresDsn] = None
    DATABASE_TEST_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> Any:
        if isinstance(v, str):
            return v
            port_env = os.getenv("DB_PORT", "5432")
            port_int = int(port_env) if port_env is not None else None
            return PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=os.getenv("DB_USER", "quiz_user"),
                password=os.getenv("DB_PASSWORD", "quiz_password"),
                host=os.getenv("DB_HOST", "localhost"),
                port=port_int,
                path=os.getenv("DB_NAME", "quiz_db"),
            )

    # Redis
    REDIS_URL: Optional[RedisDsn] = None
    REDIS_TEST_URL: Optional[RedisDsn] = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: Optional[str]) -> Any:
        if isinstance(v, str):
            return v
            redis_port_env = os.getenv("REDIS_PORT", "6379")
            redis_port_int = int(redis_port_env) if redis_port_env is not None else None
            return RedisDsn.build(
                scheme="redis",
                host=os.getenv("REDIS_HOST", "localhost"),
                port=redis_port_int,
                path=os.getenv("REDIS_DB", "0"),
            )

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    LOGIN_RATE_LIMIT_PER_MINUTE: int = 5

    # Session Configuration
    SESSION_EXPIRE_HOURS: int = 48
    QUESTION_TIME_LIMIT_SECONDS: int = (
        20  # Each question must be answered within 20 seconds
    )

    # CORS
    CORS_ORIGINS: List[str] = ["*"]  # In production, replace with specific origins
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXCEL_EXTENSIONS: List[str] = [".xlsx", ".xls"]

    # Celery
    CELERY_BROKER_URL: Optional[RedisDsn] = None
    CELERY_RESULT_BACKEND: Optional[RedisDsn] = None

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    PROMETHEUS_METRICS_ENABLED: bool = True

    @field_validator("SENTRY_DSN", mode="before")
    @classmethod
    def validate_sentry_dsn(cls, v: Optional[str]) -> Optional[str]:
        """Validate Sentry DSN, convert empty strings to None."""
        if v is None or v == "":
            return None
        return v

    # Admin
    FIRST_ADMIN_EMAIL: str = "admin@example.com"
    FIRST_ADMIN_PASSWORD: str = "change-this-password"

    # AWS Configuration (for deployment)
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


# Create settings instance
settings = Settings()


# Convenience functions
def get_database_url() -> str:
    """Get database URL."""
    if settings.DATABASE_URL:
        return str(settings.DATABASE_URL)
    return "postgresql+asyncpg://quiz_user:quiz_password@localhost:5432/quiz_db"


def get_redis_url() -> str:
    """Get Redis URL."""
    if settings.REDIS_URL:
        return str(settings.REDIS_URL)
    return "redis://localhost:6379/0"


def is_production() -> bool:
    """Check if running in production."""
    return settings.ENVIRONMENT.lower() == "production"


def is_development() -> bool:
    """Check if running in development."""
    return settings.ENVIRONMENT.lower() == "development"


def is_testing() -> bool:
    """Check if running tests."""
    return settings.ENVIRONMENT.lower() == "testing"
