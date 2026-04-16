# ========================================
# CRUD OPERATIONS FOR USER MODEL
# ========================================
# Tất cả operations liên quan đến User model
# Async/await pattern cho database

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.model import User
from app.schemas.scm_user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password


# ========================================
# CREATE - Tạo user mới
# ========================================
async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """
    Tạo user mới trong database.
    
    Args:
        db: Database session (async)
        user: UserCreate schema chứa email, password, full_name
        
    Returns:
        User object vừa tạo (có id từ DB)
        
    Raises:
        IntegrityError: Nếu email đã tồn tại (unique constraint)
    """
    # Hash password trước khi lưu vào DB
    hashed_password = hash_password(user.password)
    
    # Tạo User object (chưa save vào DB)
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        full_name=user.full_name
    )
    
    # Thêm vào session
    db.add(db_user)
    
    # Commit thay đổi vào database
    await db.commit()
    
    # Refresh để lấy id từ database (auto-increment)
    await db.refresh(db_user)
    
    return db_user


# ========================================
# READ - Lấy user
# ========================================
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Tìm user theo email (dùng cho login).
    
    Args:
        db: Database session (async)
        email: Email cần tìm
        
    Returns:
        User object nếu tìm thấy, None nếu không
    """
    # Viết SQL: SELECT * FROM users WHERE email = :email
    query = select(User).where(User.email == email)
    
    # Execute query
    result = await db.execute(query)
    
    # Lấy kết quả đầu tiên (hoặc None nếu không có)
    user = result.scalars().first()
    
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """
    Tìm user theo id (dùng cho get current user).
    
    Args:
        db: Database session (async)
        user_id: ID của user
        
    Returns:
        User object nếu tìm thấy, None nếu không
    """
    # Tương tự, nhưng WHERE id = :id
    query = select(User).where(User.id == user_id)
    
    result = await db.execute(query)
    
    user = result.scalars().first()
    
    return user


# ========================================
# VERIFY - Kiểm tra password
# ========================================
async def verify_user_password(db: AsyncSession, email: str, password: str) -> User | None:
    """
    Verify email + password khi login.
    
    Args:
        db: Database session (async)
        email: Email người dùng nhập
        password: Password người dùng nhập (plain text, chưa hash)
        
    Returns:
        User object nếu email tồn tại và password khớp
        None nếu email không tồn tại hoặc password sai
    """
    # Bước 1: Lấy user theo email
    user = await get_user_by_email(db, email)
    
    # Nếu email không tồn tại
    if not user:
        return None
    
    # Bước 2: Verify password
    # Gọi verify_password từ security.py để so sánh plain password với hashed password
    if not verify_password(password, user.password_hash):
        return None
    
    # Cả email và password đều đúng
    return user


# ========================================
# UPDATE - Cập nhật user
# ========================================
async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> User | None:
    """
    Cập nhật thông tin user (profile).
    
    Args:
        db: Database session (async)
        user_id: ID của user cần update
        user_update: UserUpdate schema chứa các field cần update
        
    Returns:
        User object đã update, None nếu user không tồn tại
    """
    # Lấy user từ DB
    user = await get_user_by_id(db, user_id)
    
    if not user:
        return None
    
    # Update các field không null
    if user_update.email is not None:
        user.email = user_update.email
    
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    
    if user_update.password is not None:
        user.password_hash = hash_password(user_update.password)
    
    # Commit thay đổi
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


# ========================================
# DELETE - Xóa user
# ========================================
async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Xóa user khỏi database.
    
    Args:
        db: Database session (async)
        user_id: ID của user cần xóa
        
    Returns:
        True nếu xóa thành công, False nếu user không tồn tại
    """
    # Lấy user
    user = await get_user_by_id(db, user_id)
    
    if not user:
        return False
    
    # Xóa khỏi session
    await db.delete(user)
    
    # Commit thay đổi
    await db.commit()
    
    return True
