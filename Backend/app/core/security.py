import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Context để hash password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> Tuple[str, str, datetime]:
    """
    Tạo JWT access token có jti (JWT ID) unique
    
    Args:
        data: Dữ liệu muốn lưu trong token (thường là {"sub": user_id})
        expires_delta: Thời gian hết hạn (mặc định từ settings)
        
    Returns:
        Tuple gồm:
        - encoded_jwt (str): JWT token string đã mã hóa
        - jti (str): JWT ID unique (UUID) → lưu vào bảng user_sessions
        - expire (datetime): Thời điểm token hết hạn → lưu vào user_sessions.expires_at
    """
    to_encode = data.copy()
    
    # Tạo JTI (JWT ID) - mỗi token có 1 ID unique
    # Dùng uuid4() tạo ra chuỗi ngẫu nhiên kiểu: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    # JTI này sẽ được lưu vào bảng user_sessions để theo dõi token nào đang active
    jti = str(uuid.uuid4())
    
    # Tính thời gian hết hạn
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Mặc định: lấy từ settings (VD: 1440 phút = 24 giờ)
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Đưa jti và exp vào payload của token
    # Token payload sẽ gồm: {"sub": "1", "jti": "uuid-xxx", "exp": 1739...}
    to_encode.update({"exp": expire, "jti": jti})
    
    # Mã hóa token bằng SECRET_KEY và thuật toán HS256
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # Trả về 3 giá trị: token, jti, thời gian hết hạn
    # - token: gửi cho client lưu ở localStorage/cookie
    # - jti: lưu vào DB để kiểm tra token còn hợp lệ không
    # - expire: lưu vào DB để biết khi nào session hết hạn
    return encoded_jwt, jti, expire


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
