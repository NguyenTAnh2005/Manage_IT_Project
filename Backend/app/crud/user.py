"""
CRUD operations cho User model
CRUD = Create, Read, Update, Delete
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.schemas.user import UserRegister
from app.core.security import hash_password


# ===== CREATE =====

async def create_user(db: AsyncSession, user_data: UserRegister) -> User:
    """
    Tạo user mới trong database
    - Input: database session, UserRegister schema (email, password, full_name)
    - Output: User object vừa tạo
    - Xảy ra lỗi nếu email đã tồn tại
    """
    # Hash password trước khi lưu vào DB
    hashed_password = hash_password(user_data.password)
    
    # Tạo user object mới
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name
    )
    
    # Thêm vào database
    db.add(db_user)
    await db.commit()  # Commit để lưu vào DB
    await db.refresh(db_user)  # Refresh để lấy id và thông tin từ DB
    
    return db_user


# ===== READ =====

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Lấy user từ database theo email
    - Input: database session, email string
    - Output: User object nếu tìm thấy, None nếu không
    """
    # Tạo query: SELECT * FROM users WHERE email = ?
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """
    Lấy user từ database theo id
    - Input: database session, user_id (integer)
    - Output: User object nếu tìm thấy, None nếu không
    """
    # Dùng session.get() là cách nhanh nhất để lấy by primary key
    return await db.get(User, user_id)


# ===== UPDATE =====

async def update_user(db: AsyncSession, user_id: int, **kwargs) -> User | None:
    """
    Update thông tin user
    - Input: database session, user_id, các trường cần update (email, full_name, ...)
    - Output: User object đã update, None nếu user không tồn tại
    """
    # Lấy user từ DB
    db_user = await get_user_by_id(db, user_id)
    
    if not db_user:
        return None
    
    # Update các trường được pass vào
    for key, value in kwargs.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    # Lưu vào DB
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


# ===== DELETE =====

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Xóa user khỏi database
    - Input: database session, user_id
    - Output: True nếu xóa thành công, False nếu user không tồn tại
    """
    # Lấy user từ DB
    db_user = await get_user_by_id(db, user_id)
    
    if not db_user:
        return False
    
    # Xóa từ DB
    await db.delete(db_user)
    await db.commit()
    
    return True
