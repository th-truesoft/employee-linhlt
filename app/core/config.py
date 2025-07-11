import secrets
import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, validator, BaseModel

# Try to import pydantic_settings, fall back to using pydantic BaseModel if not available
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # If pydantic_settings is not available, use BaseModel as a fallback
    BaseSettings = BaseModel


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    PROJECT_NAME: str = "Employee Directory API"
    
    # Default API token for authentication
    DEFAULT_API_TOKEN: str = "employee-directory-api-token"
    
    # Rate limiting
    RATE_LIMIT: int = 100
    RATE_LIMIT_WINDOW_SIZE: int = 60
    
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # SQLite database settings
    SQLITE_DB: str = "employee_directory.db"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        # Use SQLite database
        sqlite_db = values.get("SQLITE_DB", "employee_directory.db")
        return f"sqlite:///{sqlite_db}"

    class Config:
        case_sensitive = True
        env_file = ".env"
        # Allow environment variables to be read from .env file or system environment
        extra = "allow"


settings = Settings()
