from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # App settings
    APP_ENV: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=True, env="DEBUG")
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Database
    DATABASE_URL: str = Field(default="", env="DATABASE_URL")
    
    # Supabase
    SUPABASE_URL: str = Field(default="", env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(default="", env="SUPABASE_KEY")
    SUPABASE_JWT_SECRET: str = Field(default="", env="SUPABASE_JWT_SECRET")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(","),
        description="Comma-separated list of allowed CORS origins"
    )
    ALLOW_CREDENTIALS: bool = Field(
        default=os.getenv("ALLOW_CREDENTIALS", "true").lower() == "true",
        description="Whether to allow credentials in CORS requests"
    )
    ALLOWED_METHODS: List[str] = Field(
        default=os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(","),
        description="List of allowed HTTP methods"
    )
    ALLOWED_HEADERS: List[str] = Field(
        default=os.getenv("ALLOWED_HEADERS", "*,Authorization,Content-Type").split(","),
        description="List of allowed HTTP headers"
    )
    
    # Pydantic v2 config
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Create settings instance
settings = get_settings()
