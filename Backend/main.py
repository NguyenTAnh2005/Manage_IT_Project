from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError  # Import exception type
from app.routers import auth  # Import router auth
from app.core.exceptions import validation_exception_handler  # Import custom handler


app = FastAPI(
    title="API Quản Trị Dự Án CNTT",
    description="API quản lí dự án",
    version="1.0.0"     
)

# ========================================
# REGISTER CUSTOM EXCEPTION HANDLERS
# ========================================
# Register custom handler cho Pydantic validation errors → trả message tiếng Việt
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# ========================================
# INCLUDE ROUTERS
# ========================================
# Include auth router → tất cả endpoints trong auth.py sẽ có prefix /auth
app.include_router(auth.router)


@app.get("/", tags=["Health Check"])
async def Home():
    return {"message":"Server đang chạy ngon lành"}

