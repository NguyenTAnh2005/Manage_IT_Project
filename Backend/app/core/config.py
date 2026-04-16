import os 
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """CÁC FILE CẤU HÌNH TỪ FILE .ENV"""

    # DATABASE 
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # CORS
    FRONTEND_URL: str = "http://localhost:5500"
    
    # --- Email / SMTP (for FastAPI-Mail) ---
    MAIL_FROM: str | None = None
    MAIL_FROM_NAME: str | None = None
    MAIL_SERVER: str | None = None
    MAIL_PORT: int | None = None
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # App Config (có giá trị mặc định, không bắt buộc trong .env)
    PROJECT_NAME: str = "Quản Lý Dự Án"  # Hiển thị trong Swagger docs
    DEBUG: bool = True  # True = hiện lỗi chi tiết (dev), False = ẩn lỗi (production)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Tạo instance duy nhất để dùng ở các file khác
settings = Settings()


