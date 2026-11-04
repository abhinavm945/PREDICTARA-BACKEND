import os
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Predictara AI Academic Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    
    # Database URL: Supports SQLite out-of-the-box or PostgreSQL via env
    # e.g., postgresql://user:password@localhost:5432/predictara_db
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./predictara.db")
    
    # Mathpix OCR credentials (set via env or fallback mock/free endpoint)
    MATHPIX_APP_ID: str = os.getenv("MATHPIX_APP_ID", "")
    MATHPIX_APP_KEY: str = os.getenv("MATHPIX_APP_KEY", "")
    
    # Google Gemini Flash & Token Safeguards
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    GEMINI_MAX_CALLS_PER_MINUTE: int = int(os.getenv("GEMINI_MAX_CALLS_PER_MINUTE", "10"))
    GEMINI_MAX_CALLS_PER_DAY: int = int(os.getenv("GEMINI_MAX_CALLS_PER_DAY", "150"))
    GEMINI_MAX_OUTPUT_TOKENS: int = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "2048"))
    GEMINI_CACHE_ENABLED: bool = os.getenv("GEMINI_CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
    
    # Moderator Default Configuration (PRD Section 5)
    DEFAULT_MODERATOR_ENABLED: bool = True
    MODERATOR_SLA_DAYS: int = 3

    class Config:
        env_file = (ENV_PATH, ".env")
        extra = "allow"

settings = Settings()
