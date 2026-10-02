from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "OrderGuard AI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    USE_SQLITE: bool = True
    DATABASE_URL: Optional[str] = None
    
    # Supabase Cloud
    SUPABASE_URL: Optional[str] = None
    SUPABASE_PUBLISHABLE_KEY: Optional[str] = None
    SUPABASE_SECRET_KEY: Optional[str] = None
    SUPABASE_JWKS_URL: Optional[str] = None
    
    # Postgres
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "orderguard"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "orderguard_db"
    POSTGRES_PORT: str = "5432"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.USE_SQLITE:
            # Create data directory if using SQLite
            os.makedirs("data", exist_ok=True)
            return "sqlite:///./data/orderguard.db"
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION_SUPER_SECRET_KEY_123")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    BACKEND_CORS_ORIGINS: list[str] | str = ["*"]

    # ML
    MODEL_PATH: str = os.getenv("MODEL_PATH", "../ml/models/best_model_RandomForest.joblib")
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }

settings = Settings()
