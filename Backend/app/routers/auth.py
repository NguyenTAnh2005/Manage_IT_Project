"""
API Routes cho Authentication (Đăng ký, Đăng nhập)
Endpoints:
  POST /auth/register - Đăng ký tài khoản mới
  POST /auth/login    - Đăng nhập
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse
from app.crud.user import create_user, get_user_by_email
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.exceptions import EmailAlreadyExistsException, InvalidCredentialsException

# Khởi tạo logger để ghi lỗi
logger = logging.getLogger(__name__)

# Tạo limiter instance
limiter = Limiter(key_func=get_remote_address)

# Tạo router cho auth (sẽ được gắn vào main app với prefix="/auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    API Đăng ký tài khoản mới
    
    Request:
        {
            "email": "user@example.com",
            "password": "Password@123",
            "full_name": "Nguyễn Văn A"
        }
    
    Response:
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "Nguyễn Văn A",
                "created_at": "2026-04-13T..."
            }
        }
    """
    try:
        # Tạo user mới trong database
        new_user = await create_user(db, user_data)
        
        # Tạo JWT tokens
        access_token = create_access_token({"sub": str(new_user.id)})
        refresh_token = create_refresh_token({"sub": str(new_user.id)})
        
        logger.info(f"Register - Tạo tài khoản thành công: {user_data.email}")
        
        # Return response
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.from_orm(new_user)
        )
    
    except IntegrityError as e:
        # Nếu email đã tồn tại (unique constraint violation)
        await db.rollback()
        logger.warning(f"Register - Email đã tồn tại: {user_data.email}")
        raise EmailAlreadyExistsException()
    
    except HTTPException:
        # Re-raise HTTPException (từ Pydantic validation)
        raise
    
    except Exception as e:
        await db.rollback()
        # Ghi lỗi vào log để debug (full error)
        logger.error(f"Register - Lỗi bất ngờ: {str(e)}", exc_info=True)
        # Trả lỗi generic cho client (không expose chi tiết)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login(
    request: Request,
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    API Đăng nhập
    
    Request:
        {
            "email": "user@example.com",
            "password": "Password@123"
        }
    
    Response:
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "bearer",
            "user": {...}
        }
    
    Note: Chỉ trả lỗi generic để không lộ thông tin về user (security best practice)
    """
    try:
        # Tìm user theo email
        user = await get_user_by_email(db, login_data.email)
        
        # Nếu không tìm thấy user
        if not user:
            logger.warning(f"Login - User không tồn tại: {login_data.email}")
            raise InvalidCredentialsException()
        
        # Nếu password sai
        if not verify_password(login_data.password, user.password_hash):
            logger.warning(f"Login - Password sai cho user: {login_data.email}")
            raise InvalidCredentialsException()
        
        # Tạo JWT tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        logger.info(f"Login - Đăng nhập thành công: {login_data.email}")
        
        # Return response
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.from_orm(user)
        )
    
    except HTTPException:
        # Re-raise HTTPException (custom exceptions - chỉ trả generic message)
        raise
    
    except Exception as e:
        # Ghi lỗi vào log để debug (full error)
        logger.error(f"Login - Lỗi bất ngờ: {str(e)}", exc_info=True)
        # Trả lỗi generic cho client (bảo mật - không nên lộ chi tiết)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )
