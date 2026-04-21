"""
Project endpoints - Các API liên quan đến dự án.
- Tạo dự án
- Xem danh sách dự án của user
- Chi tiết dự án
- Cập nhật dự án
- Xóa dự án
- Join dự án by code
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_db
from app.crud.crud_project import (
    create_project,
    get_project_by_id,
    get_project_by_code,
    list_user_projects,
    update_project,
    delete_project,
    get_project_members_count,
)
from app.models.model import User, ProjectMember
from app.schemas.scm_project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithMembersCount,
    ProjectListResponse,
    ProjectJoinRequest,
)
from sqlalchemy import select

# Tạo router cho project endpoints
router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Tạo dự án mới.
    User tạo project sẽ tự động trở thành PM (Project Manager).
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        project_data: ProjectCreate schema
            - project_code (str): Mã project (6-10 ký tự, A-Z, 0-9, _) - UNIQUE
            - name (str): Tên project (3-100 ký tự)
            - description (str): Mô tả (0-500 ký tự, tùy chọn)
    
    Returns:
        ProjectResponse: Thông tin project mới được tạo (201)
        
    Raises:
        400: project_code đã tồn tại
        401: Token không hợp lệ
        
    Ví dụ request body:
        {
            "project_code": "PRJMNG001",
            "name": "Quản Lý Dự Án IT",
            "description": "Dự án quản lý dự án CNTT"
        }
    """
    try:
        # Tạo project mới (creator sẽ là PM)
        new_project = await create_project(
            db=db,
            project=project_data,
            user_id=current_user.id,
        )
        return new_project
        
    except IntegrityError:
        # project_code đã tồn tại
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã project đã tồn tại",
        )


@router.get("", response_model=ProjectListResponse)
async def list_my_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lấy danh sách tất cả dự án mà user là member.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Returns:
        ProjectListResponse: Danh sách projects
            - total (int): Tổng số project
            - projects (list): Danh sách ProjectWithMembersCount
        
    Ví dụ response:
        {
            "total": 2,
            "projects": [
                {
                    "id": 1,
                    "project_code": "PRJMNG001",
                    "name": "Quản Lý Dự Án IT",
                    "description": "...",
                    "created_at": "2026-04-16T10:30:00",
                    "updated_at": "2026-04-16T10:30:00",
                    "members_count": 5
                }
            ]
        }
    """
    # Lấy danh sách projects của user
    projects = await list_user_projects(db, current_user.id)
    
    # Lấy members_count cho mỗi project
    projects_with_count = []
    for project in projects:
        members_count = await get_project_members_count(db, project.id)
        project_with_count = ProjectWithMembersCount(
            **project.__dict__,
            members_count=members_count,
        )
        projects_with_count.append(project_with_count)
    
    return ProjectListResponse(
        total=len(projects_with_count),
        projects=projects_with_count,
    )


@router.get("/{project_id}", response_model=ProjectWithMembersCount)
async def get_project_detail(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lấy chi tiết một dự án.
    User phải là member của project để xem.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        project_id: ID project
    
    Returns:
        ProjectWithMembersCount: Chi tiết project kèm số lượng members
        
    Raises:
        403: User không phải member của project
        404: Project không tồn tại
        
    Ví dụ response:
        {
            "id": 1,
            "project_code": "PRJMNG001",
            "name": "Quản Lý Dự Án IT",
            "description": "...",
            "created_at": "2026-04-16T10:30:00",
            "updated_at": "2026-04-16T10:30:00",
            "members_count": 5
        }
    """
    # Kiểm tra user có phải member không
    member_stmt = (
        select(ProjectMember)
        .where(
            (ProjectMember.project_id == project_id)
            & (ProjectMember.user_id == current_user.id)
        )
    )
    member_result = await db.execute(member_stmt)
    is_member = member_result.scalar_one_or_none() is not None
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải member của project này",
        )
    
    # Lấy project
    project = await get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project không tồn tại",
        )
    
    # Lấy members count
    members_count = await get_project_members_count(db, project_id)
    
    return ProjectWithMembersCount(
        **project.__dict__,
        members_count=members_count,
    )


@router.get("/{project_id}/my-role", status_code=status.HTTP_200_OK)
async def get_my_role_in_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lấy chức vụ (role) của user hiện tại trong project.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        project_id: ID project
    
    Returns:
        {
            "role": "PM" | "MEMBER"
        }
        
    Raises:
        403: User không phải member của project
        404: Project không tồn tại
        
    Ví dụ response:
        {
            "role": "PM"
        }
    """
    # Kiểm tra project tồn tại
    project = await get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project không tồn tại",
        )
    
    # Lấy membership của user
    member_stmt = (
        select(ProjectMember)
        .where(
            (ProjectMember.project_id == project_id)
            & (ProjectMember.user_id == current_user.id)
        )
    )
    member_result = await db.execute(member_stmt)
    member = member_result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải member của project này",
        )
    
    return {
        "role": member.role.value if hasattr(member.role, 'value') else str(member.role)
    }


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_info(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cập nhật thông tin dự án.
    Chỉ PM (người tạo project) mới có quyền cập nhật.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        project_id: ID project
        project_update: ProjectUpdate schema
            - name (str): Tên mới (tùy chọn)
            - description (str): Mô tả mới (tùy chọn)
    
    Returns:
        ProjectResponse: Thông tin project sau cập nhật
        
    Raises:
        403: User không phải PM (không có quyền)
        404: Project không tồn tại
        401: Token không hợp lệ
        
    Ví dụ request body:
        {
            "name": "Quản Lý Dự Án IT v2.0",
            "description": "Mô tả mới"
        }
    """
    # Cập nhật project (hàm CRUD sẽ check permission)
    updated_project = await update_project(
        db=db,
        project_id=project_id,
        project_update=project_update,
        user_id=current_user.id,
    )
    
    if updated_project is None:
        # Kiểm tra xem là vì không tìm thấy project hay không có quyền
        project = await get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project không tồn tại",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ PM mới có quyền cập nhật project",
            )
    
    return updated_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_by_id(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Xóa dự án.
    Chỉ PM (người tạo project) mới có quyền xóa.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        project_id: ID project
    
    Returns:
        None (204 No Content)
        
    Raises:
        403: User không phải PM (không có quyền)
        404: Project không tồn tại
        401: Token không hợp lệ
        
    Note: Hành động này sẽ xóa project cùng tất cả tasks trong project!
    """
    # Xóa project (hàm CRUD sẽ check permission)
    success = await delete_project(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )
    
    if not success:
        # Kiểm tra xem là vì không tìm thấy project hay không có quyền
        project = await get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project không tồn tại",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ PM mới có quyền xóa project",
            )
    
    return None


@router.post("/join", response_model=ProjectResponse)
async def join_project(
    join_data: ProjectJoinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Join dự án bằng mã project code.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        join_data: ProjectJoinRequest schema
            - project_code (str): Mã project
    
    Returns:
        ProjectResponse: Thông tin project đã join (200)
        
    Raises:
        400: User đã là member của project này
        404: Project không tìm thấy
        401: Token không hợp lệ
        
    Ví dụ request body:
        {
            "project_code": "PRJMNG001"
        }
    """
    # Tìm project by code
    project = await get_project_by_code(db, join_data.project_code)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project với mã này không tồn tại",
        )
    
    # Kiểm tra user đã là member chưa
    member_stmt = (
        select(ProjectMember)
        .where(
            (ProjectMember.project_id == project.id)
            & (ProjectMember.user_id == current_user.id)
        )
    )
    member_result = await db.execute(member_stmt)
    is_already_member = member_result.scalar_one_or_none() is not None
    
    if is_already_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn đã là member của project này",
        )
    
    # Thêm user vào project với role MEMBER
    new_member = ProjectMember(
        user_id=current_user.id,
        project_id=project.id,
        role="MEMBER",
    )
    db.add(new_member)
    
    # Commit
    await db.commit()
    
    return project
