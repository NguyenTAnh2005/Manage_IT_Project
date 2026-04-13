"""
FastAPI Main Application
Entry point của backend server
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.exceptions import format_validation_errors
from app.routers import auth, user, project, task

# ===== TẠO APP INSTANCE =====
app = FastAPI(
    title=settings.APP_NAME,
    description="API backend cho IT Project Management System",
    version="1.0.0"
)

# ===== RATE LIMITER =====
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"detail": "Quá nhiều yêu cầu. Vui lòng thử lại sau."}
))

# ===== CORS MIDDLEWARE =====
# Cho phép Frontend (chạy trên domain khác) gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins (nên hạn chế trong production)
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, ...
    allow_headers=["*"],  # Cho phép tất cả headers
)

# ===== EXCEPTION HANDLERS =====
# Bắt lỗi Validation và trả tiếng Việt

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom exception handler cho lỗi validation Pydantic
    - Chuyển lỗi tiếng Anh sang tiếng Việt
    - Return response format đẹp
    """
    errors = exc.errors()
    formatted_response = format_validation_errors(errors)
    
    return JSONResponse(
        status_code=422,
        content=formatted_response
    )


# ===== INCLUDE ROUTERS =====
# Gắn các router vào app
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(project.router)
app.include_router(task.router)


# ===== ROOT ENDPOINT =====
@app.get("/")
async def root():
    """
    API thử nghiệm - Kiểm tra xem server chạy chưa
    """
    return {
        "message": "Welcome to IT Project Management System API",
        "version": "1.0.0",
        "docs": "/docs"  # Link tới Swagger API docs
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint - Dùng để kiểm tra server còn sống không
    """
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    # Chạy server trên localhost:8000
    # --reload: Tự động reload khi code thay đổi
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

