"""
Schemas (Request/Response Models) cho Auth
- Được dùng để validate input từ client
- Được dùng để format output response
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


# ===== REQUEST SCHEMAS =====
# Dùng để validate input từ client

class UserRegister(BaseModel):
    """
    Schema cho API Register (tạo tài khoản mới)
    Client phải gửi: email, password, full_name
    """
    email: EmailStr  # EmailStr tự động validate format email
    password: str = Field(..., min_length=6)  # Password tối thiểu 6 ký tự
    full_name: str = Field(..., min_length=1, max_length=255)  # Tên từ 1-255 ký tự

    # ===== CUSTOM VALIDATORS =====
    # Validator này được gọi trước khi object được tạo
    # Dùng để kiểm tra logic phức tạp
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """
        Kiểm tra tên người dùng:
        - Tối thiểu 1 ký tự
        - Tối đa 255 ký tự
        - Không được toàn khoảng trắng
        """
        # Strip khoảng trắng 2 đầu
        v = v.strip()
        
        # Kiểm tra rỗng sau khi strip
        if not v:
            raise ValueError('Tên không được để trống')
        
        # Kiểm tra độ dài
        if len(v) < 1:
            raise ValueError('Tên tối thiểu 1 ký tự')
        
        if len(v) > 255:
            raise ValueError('Tên tối đa 255 ký tự')
        
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Kiểm tra mật khẩu phải đáp ứng các điều kiện:
        - Tối thiểu 6 ký tự
        - Có ít nhất 1 chữ hoa (A-Z)
        - Có ít nhất 1 chữ thường (a-z)
        - Có ít nhất 1 ký tự đặc biệt (!@#$%^&*...)
        
        Ý tưởng: Dùng regex để kiểm tra
        - (?=.*[A-Z]): Positive lookahead - tìm chữ hoa
        - (?=.*[a-z]): Positive lookahead - tìm chữ thường
        - (?=.*[!@#$%^&*(),.?\":{}|<>]): Positive lookahead - tìm ký tự đặc biệt
        - .{6,}: Ít nhất 6 ký tự
        """
        
        # Kiểm tra độ dài
        if len(v) < 6:
            raise ValueError('Password tối thiểu 6 ký tự')
        
        # Kiểm tra có chữ hoa
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password phải chứa ít nhất 1 chữ hoa (A-Z)')
        
        # Kiểm tra có chữ thường
        if not re.search(r'[a-z]', v):
            raise ValueError('Password phải chứa ít nhất 1 chữ thường (a-z)')
        
        # Kiểm tra có ký tự đặc biệt
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password phải chứa ít nhất 1 ký tự đặc biệt')
        
        return v



class UserLogin(BaseModel):
    """
    Schema cho API Login (đăng nhập)
    Client phải gửi: email, password
    """
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """
    Schema cho API Refresh Token
    Client phải gửi: refresh_token
    """
    refresh_token: str


# ===== RESPONSE SCHEMAS =====
# Dùng để format output response từ API

class TokenResponse(BaseModel):
    """
    Schema cho response Login/Register
    Trả về: access_token, refresh_token, token_type, user info
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional["UserResponse"] = None


class UserResponse(BaseModel):
    """
    Schema cho User response (không bao gồm password)
    Được dùng khi return user info
    """
    id: int
    email: str
    full_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Cho phép create instance từ SQLAlchemy model


class UserDetailResponse(BaseModel):
    """
    Schema chi tiết user (khi get user by id)
    """
    id: int
    email: str
    full_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== ERROR RESPONSE SCHEMAS =====

class ErrorResponse(BaseModel):
    """
    Schema cho error response
    """
    detail: str
    status_code: int
