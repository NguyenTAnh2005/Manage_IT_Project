"""
API Routes cho Task (CRUD operations)
Endpoints:
  GET /projects/{project_id}/tasks       - Lấy tất cả công việc của dự án
  POST /projects/{project_id}/tasks      - Tạo công việc mới
  GET /tasks/{task_id}                   - Lấy chi tiết công việc (cần quyền)
  PUT /tasks/{task_id}                   - Sửa công việc (cần quyền PM)
  DELETE /tasks/{task_id}                - Xóa công việc (cần quyền PM)
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.crud.task import (
    create_task,
    get_task_by_id,
    get_tasks_by_project,
    update_task,
    delete_task,
    check_task_permission,
    check_task_project_permission,
    check_task_pm_permission
)
from app.crud.project import check_project_permission

logger = logging.getLogger(__name__)

# Prefix rỗng vì endpoints đã có đường dẫn đầy đủ
router = APIRouter(tags=["Tasks"])


# ===== GET - Lấy danh sách công việc của dự án =====

@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def list_project_tasks(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TaskResponse]:
    """
    API Lấy tất cả công việc của dự án
    
    Yêu cầu: Token hợp lệ + User phải là thành viên của dự án
    
    Request:
        Headers:
            Authorization: Bearer <access_token>
        
        Path:
            project_id: ID của dự án
    
    Response (200 - OK):
        [
            {
                "id": 1,
                "project_id": 1,
                "title": "Công việc A",
                "description": "Mô tả...",
                "status": "pending",
                "priority": "high",
                "created_by": 1,
                "assigned_to": 2,
                "created_at": "2026-04-13T...",
                "updated_at": null
            },
            ...
        ]
    
    Lỗi có thể xảy ra:
    - 401 Unauthorized: Token không hợp lệ hoặc hết hạn
    - 403 Forbidden: User không phải là thành viên của dự án
    - 404 Not Found: Dự án không tồn tại
    - 500 Internal Server Error: Lỗi database
    """
    try:
        # Kiểm tra user có quyền truy cập dự án không (phải là thành viên)
        has_permission = await check_project_permission(db, project_id, current_user.id)
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập công việc của dự án này"
            )
        
        # Lấy danh sách công việc
        tasks = await get_tasks_by_project(db, project_id)
        
        logger.info(f"Lấy danh sách công việc của dự án {project_id} - {len(tasks)} công việc")
        return [TaskResponse.from_orm(t) for t in tasks]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lấy danh sách công việc - Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )


# ===== POST - Tạo công việc mới =====

@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    project_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """
    API Tạo công việc mới
    
    Yêu cầu: Token hợp lệ + User phải là PM của dự án
    
    Request:
        Headers:
            Authorization: Bearer <access_token>
        
        Path:
            project_id: ID của dự án
        
        Body:
            {
                "title": "Công việc A",
                "description": "Mô tả công việc",
                "status": "pending",
                "priority": "high",
                "assigned_to": 2
            }
    
    Response (201 - Created):
        {
            "id": 1,
            "project_id": 1,
            "title": "Công việc A",
            "description": "Mô tả công việc",
            "status": "pending",
            "priority": "high",
            "created_by": 1,
            "assigned_to": 2,
            "created_at": "2026-04-13T...",
            "updated_at": null
        }
    
    Lỗi có thể xảy ra:
    - 401 Unauthorized: Token không hợp lệ hoặc hết hạn
    - 403 Forbidden: User không phải là PM của dự án (chỉ PM mới được tạo công việc)
    - 404 Not Found: Dự án không tồn tại
    - 422 Unprocessable Entity: Dữ liệu không hợp lệ
    - 500 Internal Server Error: Lỗi database
    """
    try:
        # Kiểm tra user có quyền tạo công việc không (phải là PM hoặc thành viên dự án)
        has_access = await check_task_project_permission(db, current_user.id, project_id)
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền tạo công việc trong dự án này"
            )
        
        # Tạo công việc
        db_task = await create_task(
            db,
            project_id=project_id,
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            created_by=current_user.id,
            assigned_to=task_data.assigned_to
        )
        
        logger.info(f"Tạo công việc {db_task.id} bởi user {current_user.id}")
        return TaskResponse.from_orm(db_task)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Tạo công việc - Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )


# ===== GET - Lấy chi tiết công việc =====

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """
    API Lấy chi tiết công việc
    
    Yêu cầu: Token hợp lệ + User phải có quyền truy cập (thành viên dự án hoặc được gán công việc)
    
    Request:
        Headers:
            Authorization: Bearer <access_token>
        
        Path:
            task_id: ID của công việc
    
    Response (200 - OK):
        {
            "id": 1,
            "project_id": 1,
            "title": "Công việc A",
            "description": "Mô tả công việc",
            "status": "pending",
            "priority": "high",
            "created_by": 1,
            "assigned_to": 2,
            "created_at": "2026-04-13T...",
            "updated_at": null
        }
    
    Lỗi có thể xảy ra:
    - 401 Unauthorized: Token không hợp lệ hoặc hết hạn
    - 403 Forbidden: User không có quyền truy cập công việc này
    - 404 Not Found: Công việc không tồn tại
    - 500 Internal Server Error: Lỗi database
    """
    try:
        # Kiểm tra công việc có tồn tại không
        db_task = await get_task_by_id(db, task_id)
        
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Công việc không tồn tại"
            )
        
        # Kiểm tra user có quyền truy cập không
        has_permission = await check_task_permission(db, current_user.id, task_id)
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập công việc này"
            )
        
        logger.info(f"Lấy chi tiết công việc {task_id} bởi user {current_user.id}")
        return TaskResponse.from_orm(db_task)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lấy chi tiết công việc - Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )


# ===== PUT - Sửa công việc =====

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """
    API Sửa công việc
    
    Yêu cầu: Token hợp lệ + User phải là PM của dự án chứa công việc
    
    Request:
        Headers:
            Authorization: Bearer <access_token>
        
        Path:
            task_id: ID của công việc
        
        Body:
            {
                "title": "Công việc A (đã sửa)",
                "description": "Mô tả mới",
                "status": "in_progress",
                "priority": "critical",
                "assigned_to": 3
            }
    
    Response (200 - OK):
        {
            "id": 1,
            "project_id": 1,
            "title": "Công việc A (đã sửa)",
            "description": "Mô tả mới",
            "status": "in_progress",
            "priority": "critical",
            "created_by": 1,
            "assigned_to": 3,
            "created_at": "2026-04-13T...",
            "updated_at": "2026-04-14T..."
        }
    
    Lỗi có thể xảy ra:
    - 401 Unauthorized: Token không hợp lệ hoặc hết hạn
    - 403 Forbidden: User không phải là PM của dự án (chỉ PM mới được sửa công việc)
    - 404 Not Found: Công việc không tồn tại
    - 422 Unprocessable Entity: Dữ liệu không hợp lệ
    - 500 Internal Server Error: Lỗi database
    """
    try:
        # Kiểm tra công việc có tồn tại không
        db_task = await get_task_by_id(db, task_id)
        
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Công việc không tồn tại"
            )
        
        # Kiểm tra user có quyền sửa không (phải là PM)
        is_pm = await check_task_pm_permission(db, current_user.id, task_id)
        
        if not is_pm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ Project Manager mới có quyền sửa công việc"
            )
        
        # Chuẩn bị dữ liệu update (bỏ qua các trường None)
        update_data = {k: v for k, v in task_data.dict().items() if v is not None}
        
        # Sửa công việc
        db_task = await update_task(db, task_id, **update_data)
        
        logger.info(f"Sửa công việc {task_id} bởi user {current_user.id}")
        return TaskResponse.from_orm(db_task)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Sửa công việc - Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )


# ===== DELETE - Xóa công việc =====

@router.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task_endpoint(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    API Xóa công việc
    
    Yêu cầu: Token hợp lệ + User phải là PM của dự án chứa công việc
    
    Request:
        Headers:
            Authorization: Bearer <access_token>
        
        Path:
            task_id: ID của công việc
    
    Response (200 - OK):
        {
            "message": "Công việc đã được xóa"
        }
    
    Lỗi có thể xảy ra:
    - 401 Unauthorized: Token không hợp lệ hoặc hết hạn
    - 403 Forbidden: User không phải là PM của dự án (chỉ PM mới được xóa công việc)
    - 404 Not Found: Công việc không tồn tại
    - 500 Internal Server Error: Lỗi database
    """
    try:
        # Kiểm tra công việc có tồn tại không
        db_task = await get_task_by_id(db, task_id)
        
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Công việc không tồn tại"
            )
        
        # Kiểm tra user có quyền xóa không (phải là PM)
        is_pm = await check_task_pm_permission(db, current_user.id, task_id)
        
        if not is_pm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ Project Manager mới có quyền xóa công việc"
            )
        
        # Xóa công việc
        success = await delete_task(db, task_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Công việc không tồn tại"
            )
        
        logger.info(f"Xóa công việc {task_id} bởi user {current_user.id}")
        return {"message": "Công việc đã được xóa"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Xóa công việc - Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )
