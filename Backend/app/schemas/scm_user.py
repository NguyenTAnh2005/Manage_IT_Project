from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from app.utils.validators import is_strong_password, get_password_error_message, is_valid_email

# ============= CREATE =============
class UserCreate(BaseModel):
    """Schema khi user ĐĂNG KÝ"""
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6)  # Mật khẩu chưa mã hóa
    full_name: str = Field(..., min_length=3, max_length=255)

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v):
        """Validate định dạng email phải hợp lệ"""
        if not is_valid_email(v):
            raise ValueError("Email không hợp lệ.")
        return v

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate mật khẩu phải mạnh"""
        if not is_strong_password(v):
            raise ValueError(get_password_error_message())
        return v

    class Config:
        # JSON schema examples
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "Pass!",
                "full_name": "Nguyễn Tuấn Anh"
            }
        }


# ============= RESPONSE =============
class UserResponse(BaseModel):
    """Schema khi API trả về user info"""
    id: int
    email: str
    full_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ✅ Pydantic v2 - đọc từ SQLAlchemy models


# ============= UPDATE =============
class UserUpdate(BaseModel):
    """Schema khi user CẬP NHẬT PROFILE"""
    email: Optional[str] = Field(None, min_length=5, max_length=255)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=6)

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v):
        """Validate định dạng email phải hợp lệ (nếu có)"""
        if v is not None and not is_valid_email(v):
            raise ValueError("Email không hợp lệ. Ví dụ: user@example.com")
        return v

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate mật khẩu phải mạnh (nếu có)"""
        if v is not None and not is_strong_password(v):
            raise ValueError(get_password_error_message())
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "full_name": "Tên Mới",
                "password": "New!"
            }
        }


# ============= LOGIN =============
class UserLogin(BaseModel):
    """Schema khi user ĐĂNG NHẬP"""
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "Pass!"
            }
        }


# ============= TOKEN RESPONSE =============
class TokenResponse(BaseModel):
    """Schema khi API trả về token sau đăng nhập"""
    access_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


# ============= LOGIN RESPONSE =============
class LoginResponse(BaseModel):
    """Schema khi user ĐĂNG NHẬP THÀNH CÔNG"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "full_name": "Nguyễn Tuấn Anh",
                    "created_at": "2026-04-16T10:30:00",
                    "updated_at": "2026-04-16T10:30:00"
                }
            }
        }

