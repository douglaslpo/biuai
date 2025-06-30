import os
import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True, 
        extra="ignore"
    )
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    
    # Security
    ALGORITHM: str = "HS256"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080", 
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Project Configuration
    PROJECT_NAME: str = "BIUAI Financial System"
    PROJECT_VERSION: str = "2.0.0"
    PROJECT_DESCRIPTION: str = "Sistema Financeiro Inteligente com BI e ML"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    @field_validator("DEBUG", mode="before")
    @classmethod
    def set_debug_from_env(cls, v: str, info: ValidationInfo) -> bool:
        if info.data.get("ENVIRONMENT") == "production":
            return False
        return v if isinstance(v, bool) else v.lower() in ("true", "1", "yes")

    # Database Configuration
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "biuai"
    POSTGRES_PASSWORD: str = "biuai123"
    POSTGRES_DB: str = "biuai"
    POSTGRES_PORT: int = 5432
    
    DATABASE_URL: Optional[str] = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_SERVER"),
            port=info.data.get("POSTGRES_PORT"),
            path=f"{info.data.get('POSTGRES_DB') or ''}",
        ))

    # Redis Configuration
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL: int = 300  # 5 minutes
    
    # Email Configuration (SMTP)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Superuser
    FIRST_SUPERUSER: str = "admin@biuai.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    
    # Security Headers
    SECURE_HEADERS: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf", "text/csv", "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/app.log"
    
    # Monitoring & Observability
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    METRICS_PREFIX: str = "biuai"
    
    # Machine Learning
    ML_MODEL_PATH: str = "models/"
    ML_PREDICTION_CACHE_TTL: int = 3600  # 1 hour
    
    # Business Rules
    DEFAULT_CURRENCY: str = "BRL"
    DEFAULT_TIMEZONE: str = "America/Sao_Paulo"
    FISCAL_YEAR_START_MONTH: int = 1  # Janeiro
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000
    
    # API Documentation
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"
    OPENAPI_URL: Optional[str] = "/openapi.json"
    
    @field_validator("DOCS_URL", "REDOC_URL", "OPENAPI_URL", mode="before")
    @classmethod
    def hide_docs_in_production(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if info.data.get("ENVIRONMENT") == "production":
            return None
        return v

    # Health Check
    HEALTH_CHECK_INTERVAL: int = 30  # seconds
    
    # MCP Memory Service Configuration
    MCP_MEMORY_SERVICE_URL: str = "http://mcp-memory-server:8001"
    MCP_MEMORY_SERVICE_TIMEOUT: int = 30  # seconds
    
    # MCP Chatbot Service Configuration
    MCP_CHATBOT_SERVICE_URL: str = "http://mcp-chatbot-service:8002"
    MCP_CHATBOT_SERVICE_TIMEOUT: int = 60  # seconds
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    BOT_NAME: str = "Bi UAI Bot Administrador"
    
    # Backup Configuration
    BACKUP_ENABLED: bool = True
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM


@lru_cache()
def get_settings() -> Settings:
    """Get application settings with caching"""
    return Settings()


# Global settings instance
settings = get_settings() 