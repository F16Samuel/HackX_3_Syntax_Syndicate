"""
Configuration management using Pydantic BaseSettings.
All secrets and config loaded from .env file.
"""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB
    MONGODB_URI: str
    MONGODB_DB: str = "programming_pathshala"
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    # CORS
    BACKEND_CORS_ORIGINS: str = "[]"  # JSON array as string
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_OAUTH_REDIRECT_URI: str
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from JSON string."""
        try:
            return json.loads(self.BACKEND_CORS_ORIGINS)
        except json.JSONDecodeError:
            return []
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()