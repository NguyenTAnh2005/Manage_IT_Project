"""
Dependencies cho FastAPI
Dùng để inject database session, authenticate user, etc. vào các endpoint
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.crud.user import get_user_by_id
from app.models import User
from app.core.exceptions import InvalidTokenException

# ===== SECURITY SCHEME =====
# HTTPBearer: Để FastAPI biết rằng API này dùng Bearer token authentication
# auto_error=False: Không tự động raise exception nếu không có token
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency để xác thực user từ JWT token
    
    Cách dùng:
        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    
    Quá trình:
    1. Client gửi request kèm Header: Authorization: Bearer <token>
    2. FastAPI/HTTPBearer tự động extract token từ Authorization header
    3. Hàm này verify token có hợp lệ không
    4. Lấy user_id từ token payload
    5. Query database để lấy User object
    6. Return User object cho endpoint
    
    Nếu token không hợp lệ → Raise InvalidTokenException (401)
    """
    
    # Lấy token từ credentials (HTTPBearer tự động parse từ Authorization header)
    token = credentials.credentials if credentials else None
    
    if not token:
        raise InvalidTokenException()
    
    # Verify token có hợp lệ không
    payload = verify_token(token)
    
    if not payload:
        # Token hết hạn hoặc không hợp lệ
        raise InvalidTokenException()
    
    # Lấy user_id từ payload (field "sub" = subject)
    user_id_str = payload.get("sub")
    
    if not user_id_str:
        raise InvalidTokenException()
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise InvalidTokenException()
    
    # Query database để lấy User object
    user = await get_user_by_id(db, user_id)
    
    if not user:
        # User bị xóa sau khi token được tạo
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    
    # Return User object - sẽ được pass vào endpoint
    return user


async def get_current_user_optional(
    credentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User | None:
    """
    Dependency để lấy current user nếu có token, nhưng không bắt buộc
    
    Cách dùng khi API là optional auth (dùng token nếu có, không dùng nếu không có):
        @router.get("/posts")
        async def get_posts(current_user: User | None = Depends(get_current_user_optional)):
            if current_user:
                # User đã login - trả nội dung đầy đủ
                return posts_full
            else:
                # User chưa login - trả nội dung public thôi
                return posts_public
    """
    
    # Nếu client không gửi token thì credentials sẽ None
    if not credentials:
        return None
    
    token = credentials.credentials
    
    if not token:
        return None
    
    payload = verify_token(token)
    
    if not payload:
        return None
    
    user_id_str = payload.get("sub")
    
    if not user_id_str:
        return None
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        return None
    
    # Query database
    user = await get_user_by_id(db, user_id)
    return user
