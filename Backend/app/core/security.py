from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Context để hash password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    """
    Mã hóa password bằng bcrypt
    
    Args:
        password: Mật khẩu gốc
        
    Returns:
        Mật khẩu đã hash
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra password có khớp với hash không
    
    Args:
        plain_password: Mật khẩu người dùng nhập
        hashed_password: Mật khẩu đã hash trong DB
        
    Returns:
        True nếu khớp, False nếu sai
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT access token
    
    Args:
        data: Dữ liệu muốn lưu trong token (thường là {"sub": user_id})
        expires_delta: Thời gian hết hạn (mặc định từ settings)
        
    Returns:
        str: JWT token string đã mã hóa
    """
    to_encode = data.copy()
    
    # Tính thời gian hết hạn
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Mặc định: lấy từ settings (VD: 1440 phút = 24 giờ)
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Đưa exp vào payload của token
    # Token payload sẽ gồm: {"sub": "1", "exp": 1739...}
    to_encode.update({"exp": expire})
    
    # Mã hóa token bằng SECRET_KEY và thuật toán HS256
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Giải mã JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Dict chứa data trong token, hoặc None nếu token không hợp lệ
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
