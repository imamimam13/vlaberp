import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve repository root directory to ensure absolute database persistence
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = ROOT_DIR / "vlaberp.db"

class Settings(BaseSettings):
    PROJECT_NAME: str = "VLab-ERP: Virtual Lab & Business Simulation Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "vlab-erp-super-secret-key-for-university-simulation-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

    class Config:
        case_sensitive = True

settings = Settings()
