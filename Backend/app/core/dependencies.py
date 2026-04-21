"""
Hàm dependency injection cho FastAPI routes.
Dùng để lấy thông tin user từ JWT token, validate quyền truy cập, v.v.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import decode_access_token, oauth_scheme 
from app.crud.crud_user import get_user_by_id
from app.models.model import User, ProjectMember, RoleEnum

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# 2. Sửa lại hàm get_current_user:
async def get_current_user(
    token: str = Depends(oauth_scheme), # Đổi chỗ này! OAuth2 trả thẳng về token (kiểu string)
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Lấy thông tin user hiện tại từ JWT token.
    """
    # XÓA dòng: token = credentials.credentials đi, vì biến token ở trên đã là string rồi.
    
    # Giải mã JWT token
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Lấy user_id từ token payload
    user_id_str = payload.get("data")
    
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


# ✅ 1. Dependency lấy thông tin Member trong dự án cụ thể
async def get_current_project_member(
    project_id: int, # FastAPI sẽ tự động bóc project_id từ URL path
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProjectMember:
    stmt = select(ProjectMember).where(
        (ProjectMember.project_id == project_id) & 
        (ProjectMember.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của dự án này"
        )
    return member

# ✅ 2. Dependency CHECK QUYỀN PM (Sếp dùng cái này cho CRUD)
async def get_current_pm(
    member: ProjectMember = Depends(get_current_project_member)
) -> ProjectMember:
    # Kiểm tra xem role có phải PM không
    if member.role != RoleEnum.PM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Trưởng dự án (PM) mới có quyền thực hiện hành động này"
        )
    return member

# Thêm vào dependencies.py
async def get_current_pm_by_project_id(
    project_id: int, 
    current_user: User, 
    db: AsyncSession
) -> ProjectMember:
    stmt = select(ProjectMember).where(
        (ProjectMember.project_id == project_id) & 
        (ProjectMember.user_id == current_user.id) &
        (ProjectMember.role == RoleEnum.PM)
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=403, detail="Chỉ Trưởng dự án (PM) mới có quyền này")
    return member