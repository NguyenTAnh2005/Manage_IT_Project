# ========================================
# AUTH ROUTER - AUTHENTICATION ENDPOINTS
# ========================================
# Endpoints: Register, Login
# Trả về JWT token + user info

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.database import AsyncSessionLocal
from app.schemas.scm_user import UserCreate, UserLogin, UserResponse, TokenResponse, LoginResponse, Token
from app.crud.crud_user import (
    create_user,
    verify_user_password,
    get_user_by_email
)
from app.core.security import create_access_token

# Import OAuth2RequestForm 
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from app.models import model

# Tạo router với prefix "/auth"
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ========================================
# DEPENDENCY - Get Database Session
# ========================================
async def get_db() -> AsyncSession:
    """
    Dependency để inject database session vào endpoint.
    Tự động close connection sau khi endpoint xử lý xong.
    """
    async with AsyncSessionLocal() as session:
        yield session


# ========================================
# ENDPOINT 1: REGISTER
# ========================================
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint để USER ĐĂNG KÝ tài khoản mới.
    
    Request Body:
    ```json
    {
        "email": "user@example.com",
        "password": "SecurePass!",
        "full_name": "Nguyễn Tuấn Anh"
    }
    ```
    
    Response (201):
    ```json
    {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Nguyễn Tuấn Anh",
        "created_at": "2026-04-16T10:30:00",
        "updated_at": "2026-04-16T10:30:00"
    }
    ```
    
    Errors:
    - 400: Email đã tồn tại (duplicate)
    - 422: Validation error (email, password, full_name không hợp lệ)
    
    Args:
        user_data: UserCreate schema (email, password, full_name)
        db: Database session (injected)
        
    Returns:
        UserResponse: Thông tin user vừa tạo
        
    Raises:
        HTTPException 400: Email đã tồn tại
    """
    try:
        # Gọi hàm create_user từ crud_user.py
        # Hàm này tự động hash password
        db_user = await create_user(db, user_data)
        
        # Trả về UserResponse
        return db_user
    
    except IntegrityError:
        # Email đã tồn tại (unique constraint violated)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email này đã tồn tại, vui lòng dùng email khác"
        )
    
    except Exception as e:
        # Lỗi khác (database error, etc)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server: {str(e)}"
        )


# ========================================
# ENDPOINT 2: LOGIN
# ========================================
# @router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
# async def login(
#     login_data: UserLogin,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Endpoint để USER ĐĂNG NHẬP.
    
#     Request Body:
#     ```json
#     {
#         "email": "user@example.com",
#         "password": "Pass!"
#     }
#     ```
    
#     Response (200):
#     ```json
#     {
#         "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#         "token_type": "bearer",
#         "user": {
#             "id": 1,
#             "email": "user@example.com",
#             "full_name": "Nguyễn Tuấn Anh",
#             "created_at": "2026-04-16T10:30:00",
#             "updated_at": "2026-04-16T10:30:00"
#         }
#     }
#     ```
    
#     Errors:
#     - 401: Email không tồn tại hoặc password sai
#     - 422: Validation error (email, password không hợp lệ)
    
#     Args:
#         login_data: UserLogin schema (email, password)
#         db: Database session (injected)
        
#     Returns:
#         LoginResponse: JWT token + user info
        
#     Raises:
#         HTTPException 401: Credentials không đúng
#     """
#     try:
#         # Verify email + password
#         user = await verify_user_password(db, login_data.email, login_data.password)
        
#         if not user:
#             # Email không tồn tại hoặc password sai
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Email hoặc mật khẩu không đúng"
#             )
        
#         # Tạo JWT token
#         access_token = create_access_token(
#             data={"sub": str(user.id)}
#         )
        
#         # Trả về LoginResponse (token + user info)
#         return {
#             "access_token": access_token,
#             "token_type": "bearer",
#             "user": user
#         }
    
#     except HTTPException:
#         # Re-raise HTTPException (401 từ credential check)
#         raise
    
#     except Exception as e:
#         # Lỗi khác (database error, etc)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Lỗi server: {str(e)}"
#         )


# Backend\app\routers\auth.py

@router.post("/login", response_model=Token) # Chốt trả về chỉ Token theo ý sếp
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Verify user
    user = await verify_user_password(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu chưa chính xác!",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Tạo Token đúng cấu hình sếp chọn
    access_token = create_access_token(
        data = {
            "data" : str(user.id),  # ID để backend truy vấn
            "sub": str(user.email)  # Email để định danh OAuth2
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
