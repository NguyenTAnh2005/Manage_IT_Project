"""
Module bảo mật: Xử lý mã hóa password và JWT tokens
"""

from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
from app.core.config import settings

# ===== PASSWORD HASHING =====
# Sử dụng bcrypt để hash password (an toàn nhất hiện nay)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hàm mã hóa password
    - Input: password thường (plaintext)
    - Output: password đã hash (không thể đảo ngược)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Hàm kiểm tra password
    - Input: password người dùng nhập, password đã hash từ DB
    - Output: True nếu khớp, False nếu sai
    """
    return pwd_context.verify(plain_password, hashed_password)


# ===== JWT TOKEN =====
# JWT là một cách an toàn để xác thực người dùng qua token

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT access token (dùng để xác thực request API)
    - Input: dict chứa user_id, email, ...
    - Output: token string
    - Thời hạn mặc định: ACCESS_TOKEN_EXPIRE_MINUTES (30 phút)
    """
    to_encode = data.copy()
    
    # Tính thời gian hết hạn
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    # Mã hóa token bằng SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT refresh token (dùng để lấy access token mới)
    - Input: dict chứa user_id, email, ...
    - Output: token string
    - Thời hạn mặc định: REFRESH_TOKEN_EXPIRE_DAYS (7 ngày)
    """
    to_encode = data.copy()
    
    # Tính thời gian hết hạn
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    # Mã hóa token bằng SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, expected_type: Optional[str] = None) -> Optional[dict]:
    """
    Kiểm tra xem token có hợp lệ không
    - Input: JWT token string, expected_type (optional: "access" or "refresh")
    - Output: payload dict nếu hợp lệ, None nếu token hết hạn hoặc sai
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Validate token type if expected_type is provided
        if expected_type:
            token_type = payload.get("type")
            if token_type != expected_type:
                return None
        
        return payload
    except JWTError:
        return None
