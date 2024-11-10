import os
import sys
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


class Settings(BaseSettings):
    PROJECT_NAME: str = "MTGA AI Deck Builder"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database settings
    POSTGRES_SERVER: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_PORT: str = ""

    # Additional settings that were causing validation errors
    API_VERSION: Optional[str] = "v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    ANTHROPIC_API_KEY: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def get_database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = "backend\\.env"
        case_sensitive = True
        extra = "allow"  # This allows extra fields from the environment


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
print(settings.get_database_url)