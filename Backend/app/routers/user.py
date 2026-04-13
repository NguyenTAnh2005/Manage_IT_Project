"""
API Routes cho User (Xem thông tin, Logout, Refresh Token)
Endpoints:
  GET /users/me           - Lấy thông tin user hiện tại (cần auth)
  POST /users/logout      - Đăng xuất (cần auth)
  POST /users/refresh     - Lấy access token mới từ refresh token
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional
from app.models import User
from app.schemas.user import UserResponse, TokenResponse, RefreshTokenRequest
from app.core.security import create_access_token, verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["User"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    API Lấy thông tin user hiện tại
    
    Yêu cầu: Token hợp lệ trong Authorization header
    
    Request:
        Headers:
            Authorization: Bearer <access_token>
    
    Response (200 - OK):
        {
            "id": 1,
            "email": "user@example.com",
            "full_name": "Nguyễn Văn A",
            "created_at": "2026-04-13T...",
            "updated_at": null
        }
    
    Lỗi có thể xảy ra:
    - 401 Unauthorized: Token không hợp lệ hoặc hết hạn
    - 404 Not Found: User không tồn tại
    """
    return UserResponse.from_orm(current_user)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    API Đăng xuất
    
    Yêu cầu: Token hợp lệ trong Authorization header
    
    Lưu ý: 
    - Backend không lưu blacklist token (vì JWT là stateless)
    - Frontend nên xóa token khỏi localStorage
    - Trong production nên dùng token blacklist list hoặc short expiration time
    
    Request:
        Headers:
            Authorization: Bearer <access_token>
    
    Response (200 - OK):
        {
            "message": "Đăng xuất thành công",
            "user_email": "user@example.com"
        }
    """
    logger.info(f"Logout - User: {current_user.email}")
    
    return {
        "message": "Đăng xuất thành công",
        "user_email": current_user.email
    }


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    API Lấy access token mới từ refresh token
    
    Refresh token có thời hạn dài hơn (7 ngày)
    Access token có thời hạn ngắn hơn (30 phút)
    
    Khi access token hết hạn, dùng refresh token để lấy access token mới
    
    Request:
        {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    
    Response (200 - OK):
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user": {...}
        }
    
    Lỗi có thể xảy ra:
    - 401 Unauthorized: Refresh token không hợp lệ hoặc hết hạn
    - 404 Not Found: User không tồn tại
    """
    try:
        refresh_token_str = token_data.refresh_token
        
        # Verify refresh token with type validation
        payload = verify_token(refresh_token_str, expected_type="refresh")
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token không hợp lệ hoặc đã hết hạn"
            )
        
        # Lấy user_id từ payload
        user_id_str = payload.get("sub")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token không hợp lệ"
            )
        
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token không hợp lệ"
            )
        
        # Query database để lấy user
        from app.crud.user import get_user_by_id
        user = await get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User không tồn tại"
            )
        
        # Tạo access token mới
        new_access_token = create_access_token({"sub": str(user.id)})
        
        logger.info(f"Refresh Token - User: {user.email}")
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token_str,
            user=UserResponse.from_orm(user)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refresh Token - Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )
