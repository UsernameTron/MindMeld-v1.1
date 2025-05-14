"""Application configuration and environment settings."""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        LOG_LEVEL (str): Logging level.
        DEFAULT_MODEL_NAME (str): Default ML model name.
        INFERENCE_DEVICE (str): Device for inference (e.g., 'cpu', 'mps').
        OPENAI_API_KEY (str): OpenAI API key.
        OPENAI_MODEL (str): OpenAI model name.
        REDIS_URL (str): Redis connection URL.
        JWT_SECRET_KEY (str): JWT secret key.
        JWT_REFRESH_SECRET_KEY (str): JWT refresh secret key.
        JWT_ALGORITHM (str): JWT algorithm.
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES (int): JWT access token expiry in minutes.
        HUGGINGFACE_KEY (Optional[str]): Hugging Face API key.
        AUTH_ENABLED (bool): Feature flag to enable/disable authentication.
        AUDIO_STORAGE_PATH (str): Path to store audio files.
        API_BASE_URL (str): Base URL for the API.
    """

    # Application
    app_name: str = "MindMeld API"
    debug: bool = Field(False, env="DEBUG")

    # Logging
    LOG_LEVEL: str = "INFO"
    # Model settings
    DEFAULT_MODEL_NAME: str = "distilbert-base-uncased-finetuned-sst-2-english"
    EMOTION_MODEL_NAME: str = "j-hartmann/emotion-english-distilroberta-base"
    INFERENCE_DEVICE: str = "cpu"  # or "mps" for Apple Silicon GPU
    # OpenAI settings
    openai_api_key: str = Field("", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4"
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    # JWT settings
    JWT_SECRET_KEY: str = "changeme"
    JWT_REFRESH_SECRET_KEY: str = "refreshchangeme"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Hugging Face settings
    HUGGINGFACE_KEY: Optional[str] = None

    # Feature flags
    AUTH_ENABLED: bool = Field(
        True, description="Set to False to disable authentication"
    )

    # Audio storage settings
    audio_storage_path: str = Field("./storage/audio", env="AUDIO_STORAGE_PATH")
    # API settings
    api_base_url: str = Field("http://localhost:8000", env="API_BASE_URL")

    class Config:
        """
        Pydantic settings configuration.

        Attributes:
            env_file (str): Path to the .env file.
            env_file_encoding (str): Encoding for the .env file.
            case_sensitive (bool): Whether environment variable names are case-sensitive.
        """

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# Redis connection (async)
import redis.asyncio as redis_async

try:
    redis = redis_async.from_url(settings.REDIS_URL, decode_responses=True)
except Exception:
    redis = None
