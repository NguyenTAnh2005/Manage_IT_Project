"""
API Routes cho Project (CRUD operations)
Endpoints:
  GET /projects          - Lấy tất cả projects của user hiện tại
  POST /projects         - Tạo project mới
  GET /projects/{id}     - Lấy chi tiết project (cần quyền)
  PUT /projects/{id}     - Update project (cần quyền PM)
  DELETE /projects/{id}  - Xóa project (cần quyền PM)
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.crud.project import (
    create_project,
    get_project_by_id,
    get_projects_by_user,
    update_project,
    delete_project,
    check_project_permission,
    check_project_ownership
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ProjectResponse]:
    """
    API Lấy tất cả projects của user hiện tại
    
    Yêu cầu: Token hợp lệ trong Authorization header
    
    Request:
        Headers:
            Authorization: Bearer <access_token>
    
    Response (200 - OK):
        [
            {
                "id": 1,
                "project_code": "PRJ001",
                "name": "Project A",
                "description": "Description...",
                "created_at": "2026-04-13T...",
                "updated_at": null
            },
            ...
        ]
    
    Lỗi có thể xảy ra:
    - 401 Unauthorized: Token không hợp lệ hoặc hết hạn
    - 500 Internal Server Error: Lỗi database
    """
    try:
        projects = await get_projects_by_user(db, current_user.id)
        logger.info(f"Listed {len(projects)} projects for user {current_user.id}")
        return [ProjectResponse.from_orm(p) for p in projects]
    except Exception as e:
        logger.error(f"List projects - Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """
    API Tạo project mới
    
    Yêu cầu: Token hợp lệ trong Authorization header
    
    Request:
        Headers:
            Authorization: Bearer <access_token>
        
        Body:
            {
                "project_code": "PRJ001",
                "name": "Project A",
                "description": "Description..."
            }
    
    Response (201 - Created):
        {
            "id": 1,
            "project_code": "PRJ001",
            "name": "Project A",
            "description": "Description...",
            "created_at": "2026-04-13T...",
            "updated_at": null
        }
    
    Lỗi có thể xảy ra:
    - 401 Unauthorized: Token không hợp lệ hoặc hết hạn
    - 409 Conflict: Project code đã tồn tại
    - 422 Unprocessable Entity: Dữ liệu không hợp lệ
    - 500 Internal Server Error: Lỗi database
    """
    try:
        db_project = await create_project(
            db,
            user_id=current_user.id,
            project_code=project_data.project_code,
            project_name=project_data.name,
            description=project_data.description
        )
        logger.info(f"Created project {db_project.id} by user {current_user.id}")
        return ProjectResponse.from_orm(db_project)
    
    except IntegrityError as e:
        await db.rollback()
        logger.warning(f"Create project - Duplicate project_code: {project_data.project_code}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mã dự án đã tồn tại"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Create project - Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """
    API Lấy chi tiết project
    
    Yêu cầu: Token hợp lệ + User phải là member hoặc PM của project
    
    Request:
        Headers:
            Authorization: Bearer <access_token>
        
        Path:
            project_id: ID của project
    
    Response (200 - OK):
        {
            "id": 1,
            "project_code": "PRJ001",
            "name": "Project A",
            "description": "Description...",
            "created_at": "2026-04-13T...",
            "updated_at": null
        }
    
    Lỗi có thể xảy ra:
    - 401 Unauthorized: Token không hợp lệ hoặc hết hạn
    - 403 Forbidden: User không có quyền truy cập project này
    - 404 Not Found: Project không tồn tại
    - 500 Internal Server Error: Lỗi database
    """
    try:
        # Kiểm tra project có tồn tại không
        db_project = await get_project_by_id(db, project_id)
        
        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dự án không tồn tại"
            )
        
        # Kiểm tra user có quyền truy cập không
        has_permission = await check_project_permission(db, project_id, current_user.id)
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập dự án này"
            )
        
        logger.info(f"Get project {project_id} by user {current_user.id}")
        return ProjectResponse.from_orm(db_project)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project - Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_endpoint(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """
    API Update project
    
    Yêu cầu: Token hợp lệ + User phải là PM của project
    
    Request:
        Headers:
            Authorization: Bearer <access_token>
        
        Path:
            project_id: ID của project
        
        Body:
            {
                "name": "Project A (Updated)",
                "description": "New description..."
            }
    
    Response (200 - OK):
        {
            "id": 1,
            "project_code": "PRJ001",
            "name": "Project A (Updated)",
            "description": "New description...",
            "created_at": "2026-04-13T...",
            "updated_at": "2026-04-14T..."
        }
    
    Lỗi có thể xảy ra:
    - 401 Unauthorized: Token không hợp lệ hoặc hết hạn
    - 403 Forbidden: User không có quyền sửa project này (chỉ PM)
    - 404 Not Found: Project không tồn tại
    - 422 Unprocessable Entity: Dữ liệu không hợp lệ
    - 500 Internal Server Error: Lỗi database
    """
    try:
        # Kiểm tra project có tồn tại không
        db_project = await get_project_by_id(db, project_id)
        
        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dự án không tồn tại"
            )
        
        # Kiểm tra user có quyền sửa không (chỉ PM)
        is_owner = await check_project_ownership(db, project_id, current_user.id)
        
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền sửa dự án này"
            )
        
        # Chuẩn bị dữ liệu update (bỏ qua các trường None)
        update_data = {k: v for k, v in project_data.dict().items() if v is not None}
        
        # Nếu có field 'name' thì đổi thành đúng field của model
        if 'name' in update_data:
            update_data['name'] = update_data.pop('name')
        
        # Update project
        db_project = await update_project(db, project_id, **update_data)
        
        logger.info(f"Updated project {project_id} by user {current_user.id}")
        return ProjectResponse.from_orm(db_project)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Update project - Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )


@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project_endpoint(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    API Xóa project
    
    Yêu cầu: Token hợp lệ + User phải là PM của project
    
    Request:
        Headers:
            Authorization: Bearer <access_token>
        
        Path:
            project_id: ID của project
    
    Response (200 - OK):
        {
            "message": "Dự án đã được xóa"
        }
    
    Lỗi có thể xảy ra:
    - 401 Unauthorized: Token không hợp lệ hoặc hết hạn
    - 403 Forbidden: User không có quyền xóa project này (chỉ PM)
    - 404 Not Found: Project không tồn tại
    - 500 Internal Server Error: Lỗi database
    """
    try:
        # Kiểm tra project có tồn tại không
        db_project = await get_project_by_id(db, project_id)
        
        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dự án không tồn tại"
            )
        
        # Kiểm tra user có quyền xóa không (chỉ PM)
        is_owner = await check_project_ownership(db, project_id, current_user.id)
        
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền xóa dự án này"
            )
        
        # Xóa project
        success = await delete_project(db, project_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dự án không tồn tại"
            )
        
        logger.info(f"Deleted project {project_id} by user {current_user.id}")
        return {"message": "Dự án đã được xóa"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Delete project - Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra, vui lòng thử lại"
        )
