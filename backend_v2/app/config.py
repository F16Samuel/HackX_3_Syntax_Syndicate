# backend_v2/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Loads environment variables from .env file.
    Uses pydantic-settings for validation.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # MongoDB
    MONGO_URI: str
    MONGO_DB_NAME: str = "backend_v2"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # App
    DEFAULT_PROMPT_BUDGET: int = 15
    FRONTEND_URL: str = "http://localhost:5173"


settings = Settings()