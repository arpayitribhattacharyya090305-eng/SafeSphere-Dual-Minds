import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # App Settings
    ENVIRONMENT: str = "development"
    BACKEND_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = "sqlite:///./disaster_response.db"

    # API Keys (External Integrations)
    GEMINI_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    TAVILY_API_KEY: str = ""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings
settings = Settings()
