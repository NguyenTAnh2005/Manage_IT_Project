"""
Application Configuration
Load từ .env file (environment variables)
"""

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load biến từ .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Cấu hình ứng dụng
    Tất cả giá trị được load từ .env file hoặc environment variables
    
    Priority: Environment Variables > .env file > Default values
    
    Note: Dùng postgresql+asyncpg cho cả app và migrations
    - App sử dụng async driver
    - Migrations dùng sync driver nhưng cấu hình string tương tự
    """
    
    # ===== DATABASE =====
    # Async driver cho FastAPI app
    # Format: postgresql+asyncpg://username:password@host:port/database_name
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:password@localhost:5432/QTDA"
    )
    
    # ===== JWT & SECURITY =====
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    # ===== APPLICATION =====
    APP_NAME: str = os.getenv("APP_NAME", "IT Project Management System")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Tạo instance settings global
settings = Settings()
