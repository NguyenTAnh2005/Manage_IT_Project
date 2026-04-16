"""
Hàm dependency injection cho FastAPI routes.
Dùng để lấy thông tin user từ JWT token, validate quyền truy cập, v.v.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import decode_access_token
from app.crud.crud_user import get_user_by_id
from app.models.model import User

# Scheme bảo mật HTTP Bearer (để Swagger docs hiển thị)
security = HTTPBearer()


async def get_db() -> AsyncSession:
    """
    Dependency cung cấp session database.
    Dùng để thực hiện các thao tác database.
    
    Yields:
        AsyncSession: Session database async
    """
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Lấy thông tin user hiện tại từ JWT token.
    Đây là dependency cho protected routes - sẽ raise 401 nếu token không hợp lệ.
    
    Args:
        credentials: HTTPAuthCredentials từ header Authorization (Bearer token)
        db: Session database
        
    Returns:
        User: Object user từ database
        
    Raises:
        HTTPException: 401 nếu token không hợp lệ/bị mất/hết hạn
        HTTPException: 404 nếu user không tìm thấy trong database
        
    Ví dụ:
        @router.get("/users/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    """
    token = credentials.credentials
    
    # Giải mã JWT token
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Lấy user_id từ token payload
    user_id_str = payload.get("sub")
    
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không chứa thông tin người dùng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID trong token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Lấy user từ database
    user = await get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại",
        )
    
    return user


async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Optional["User"]:
    """
    Lấy thông tin user từ JWT token (tùy chọn).
    Trả về None nếu token không được cung cấp hoặc không hợp lệ.
    
    Args:
        request: FastAPI Request object
        db: Session database
        
    Returns:
        User | None: Object user hoặc None nếu chưa đăng nhập
        
    Ví dụ:
        @router.get("/posts")
        async def list_posts(current_user: Optional[User] = Depends(get_current_user_optional)):
            # Public endpoint, nhưng ưu tiên hiển thị bài viết của user nếu đã login
            if current_user:
                # User đã đăng nhập
                pass
            else:
                # User chưa đăng nhập
                pass
    """
    # Lấy Authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    # Extract token từ header
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    
    if payload is None:
        return None
    
    user_id_str = payload.get("sub")
    
    if not user_id_str:
        return None
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        return None
    
    user = await get_user_by_id(db, user_id)
    return user
