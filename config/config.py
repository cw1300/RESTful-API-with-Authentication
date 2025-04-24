"""
Configuration settings for the Task Management API.
Handles environment variables, database connections, and security settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Using Pydantic's BaseSettings allows for easy validation and type checking.
    """
    # Database settings
    DATABASE_URL: str = "sqlite:///./tasks.db"  # Default to SQLite for development

    # JWT settings
    SECRET_KEY: str = "your-secret-key-here"  # In production, use a secure random key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application settings
    APP_NAME: str = "Task Management API"
    DEBUG: bool = True

    # Rate limiting settings
    RATE_LIMIT: str = "100/hour"

    class Config:
        env_file = ".env"  # Load settings from .env file if it exists

@lru_cache()
def get_settings():
    """
    Get cached settings instance.
    Using lru_cache ensures we only create one instance of Settings.
    """
    return Settings()

# Database setup
settings = get_settings()
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Dependency function to get database session.
    This ensures each request gets its own database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()