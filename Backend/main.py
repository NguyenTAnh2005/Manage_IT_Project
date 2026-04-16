from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError  # Import exception type
from app.routers import auth, user, project, task  # Import routers
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

# Include user router → tất cả endpoints trong user.py sẽ có prefix /users
app.include_router(user.router)

# Include project router → tất cả endpoints trong project.py sẽ có prefix /projects
app.include_router(project.router)

# Include task router → tất cả endpoints trong task.py sẽ có prefix /tasks
app.include_router(task.router)


@app.get("/", tags=["Health Check"])
async def Home():
    return {"message":"Server đang chạy ngon lành"}

