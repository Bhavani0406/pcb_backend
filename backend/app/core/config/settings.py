import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    LLM_PROVIDER: str = Field(default="groq")
    LLM_MODEL: str = Field(default="llama-3.3-70b-versatile")
    LLM_API_KEY: str = Field(default="")
    LLM_API_URL: str = Field(default="")
    LLM_TIMEOUT_SECONDS: float = Field(default=6.0)
    LLM_VOICE_TIMEOUT_SECONDS: float = Field(default=3.5)
    LLM_VALIDATION_TIMEOUT_SECONDS: float = Field(default=4.0)
    LLM_MAX_COMPLETION_TOKENS: int = Field(default=4096)
    ENABLE_SERVER_TTS: bool = Field(default=False)

    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    DEBUG: bool = Field(default=True)
    CORS_ORIGINS: List[str] = Field(default=["*"])

settings = Settings()
