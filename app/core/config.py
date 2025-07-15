"""
Configuration settings for the Employee Directory API.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Employee Directory API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    DEFAULT_API_TOKEN: str = "employee-directory-api-token"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Production hardening
    ENVIRONMENT: str = "development"  # development, staging, production
    ENABLE_SECURITY_HEADERS: bool = True
    MAX_REQUEST_SIZE: int = 1024 * 1024  # 1MB

    # CORS settings
    BACKEND_CORS_ORIGINS: str = '["http://localhost", "http://localhost:8000"]'

    # Database settings
    SQLITE_DB: str = "employee_directory.db"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    ASYNC_SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Rate limiting settings
    RATE_LIMIT: int = 100
    RATE_LIMIT_WINDOW_SIZE: int = 60

    # Redis settings for distributed rate limiting
    REDIS_URL: Optional[str] = None
    REDIS_RATE_LIMITING: bool = False
    REDIS_CONNECTION_TIMEOUT: int = 5
    REDIS_MAX_CONNECTIONS: int = 20
    REDIS_RETRY_ON_TIMEOUT: bool = True

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str) and not v.startswith("["):
            return v
        elif isinstance(v, str):
            return v
        raise ValueError(v)

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> Optional[str]:
        if isinstance(v, str):
            return v

        # Try PostgreSQL first
        db_host = values.get("DB_HOST")
        if db_host and db_host != "localhost":
            return f"postgresql://{values.get('DB_USER')}:{values.get('DB_PASSWORD')}@{db_host}:{values.get('DB_PORT')}/{values.get('DB_NAME')}"

        # Fallback to SQLite for local development
        sqlite_db = values.get("SQLITE_DB", "employee_directory.db")
        return f"sqlite:///{sqlite_db}"

    @validator("ASYNC_SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_async_db_connection(
        cls, v: Optional[str], values: dict
    ) -> Optional[str]:
        if isinstance(v, str):
            return v

        # Try PostgreSQL async first
        db_host = values.get("DB_HOST")
        if db_host and db_host != "localhost":
            return f"postgresql+asyncpg://{values.get('DB_USER')}:{values.get('DB_PASSWORD')}@{db_host}:{values.get('DB_PORT')}/{values.get('DB_NAME')}"

        # Fallback to SQLite async for local development
        sqlite_db = values.get("SQLITE_DB", "employee_directory.db")
        return f"sqlite+aiosqlite:///{sqlite_db}"

    @validator("SECRET_KEY")
    def validate_secret_key_production(cls, v: str, values: dict) -> str:
        """Validate secret key for production environment."""
        environment = values.get("ENVIRONMENT", "development")

        if environment == "production":
            if v == "your-secret-key-here-change-in-production":
                raise ValueError(
                    "SECRET_KEY must be changed from default value in production! "
                    "Use a secure random string."
                )
            if len(v) < 32:
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters long in production"
                )

        return v

    @validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        """Validate environment setting."""
        allowed_environments = {"development", "staging", "production"}
        if v not in allowed_environments:
            raise ValueError(f"ENVIRONMENT must be one of: {allowed_environments}")
        return v

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    class Config:
        case_sensitive = True
        env_file = ".env"
        # Allow environment variables to be read from .env file or system environment
        extra = "allow"


settings = Settings()
