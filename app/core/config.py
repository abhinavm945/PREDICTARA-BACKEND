import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Predictara AI Academic Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    
    # Mathpix OCR credentials (set via env or fallback mock/free endpoint)
    MATHPIX_APP_ID: str = os.getenv("MATHPIX_APP_ID", "")
    MATHPIX_APP_KEY: str = os.getenv("MATHPIX_APP_KEY", "")
    
    # Google Gemini Flash
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Moderator Default Configuration (PRD Section 5)
    DEFAULT_MODERATOR_ENABLED: bool = True
    MODERATOR_SLA_DAYS: int = 3

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
