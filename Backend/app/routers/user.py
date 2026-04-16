"""
User endpoints - Các API liên quan đến người dùng.
- Lấy thông tin user hiện tại
- Cập nhật profile user
- Xóa tài khoản user
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.crud.crud_user import update_user, delete_user
from app.models.model import User
from app.schemas.scm_user import UserResponse, UserUpdate

# Tạo router cho user endpoints
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Lấy thông tin của user hiện tại.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Returns:
        UserResponse: Thông tin user (id, email, full_name, created_at, updated_at)
        
    Raises:
        401: Token không hợp lệ hoặc đã hết hạn
        
    Ví dụ response:
        {
            "id": 1,
            "email": "user@example.com",
            "full_name": "Tên người dùng",
            "created_at": "2026-04-16T10:30:00",
            "updated_at": "2026-04-16T10:30:00"
        }
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cập nhật thông tin của user hiện tại.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        user_update: Dữ liệu cập nhật
            - email (tùy chọn): Email mới (phải unique, validate format)
            - full_name (tùy chọn): Tên mới (min 3 ký tự)
            - password (tùy chọn): Mật khẩu mới (min 6 ký tự + 1 uppercase + 1 special char)
    
    Returns:
        UserResponse: Thông tin user sau cập nhật
        
    Raises:
        400: Email đã tồn tại hoặc dữ liệu không hợp lệ
        401: Token không hợp lệ hoặc đã hết hạn
        404: User không tồn tại
        
    Ví dụ request body:
        {
            "email": "newemail@example.com",
            "full_name": "Tên mới",
            "password": "NewPass123!"
        }
    
    Note: Chỉ cần cập nhật những field nào cần thiết, các field khác có thể bỏ trống
    """
    # Gọi hàm update_user từ CRUD
    updated_user = await update_user(db, current_user.id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại",
        )
    
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Xóa tài khoản của user hiện tại.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Returns:
        None (204 No Content)
        
    Raises:
        401: Token không hợp lệ hoặc đã hết hạn
        404: User không tồn tại
        
    Note: Hành động này không thể hoàn tác! Tài khoản sẽ bị xóa vĩnh viễn.
    """
    # Gọi hàm delete_user từ CRUD
    success = await delete_user(db, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại",
        )
    
    # Trả về 204 No Content
    return None
