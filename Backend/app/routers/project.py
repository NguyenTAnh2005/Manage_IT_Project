# Backend\app\routers\project.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_current_user, get_db, get_current_pm, get_current_project_member
from app.crud.crud_project import (
    create_project, get_project_by_id, get_project_by_code,
    list_user_projects, update_project, delete_project, get_project_members_count,
)
from app.schemas.scm_project import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectWithMembersCount, ProjectListResponse, ProjectJoinRequest,
)
from app.models.model import User, ProjectMember, RoleEnum

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Tạo dự án mới. User tạo sẽ tự động trở thành PM của dự án.
    
    Request Body:
    - project_code: Mã dự án (6-10 ký tự, A-Z, 0-9, _)
    - name: Tên dự án (3-100 ký tự)
    - description: Mô tả (0-500 ký tự, tùy chọn)
    
    Errors:
    - 400: Mã dự án đã tồn tại
    - 422: Validation error
    """
    try:
        return await create_project(db, project_data, current_user.id)
    except Exception as e:
        # Catch IntegrityError từ create_project
        if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã dự án '{project_data.project_code}' đã tồn tại. Vui lòng chọn mã khác!"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi máy chủ khi tạo dự án."
        )

@router.get("", response_model=ProjectListResponse)
async def list_my_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    projects = await list_user_projects(db, current_user.id)
    res = []
    for p in projects:
        count = await get_project_members_count(db, p.id)
        pd = ProjectWithMembersCount.model_validate(p)
        pd.members_count = count
        res.append(pd)
    return ProjectListResponse(total=len(res), projects=res)

# Join dự án bằng mã dự án
@router.post("/join", response_model=ProjectResponse)
async def join_existing_project(
    join_data: ProjectJoinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Join dự án bằng mã dự án. Nếu chưa join thì tự động thêm user vào project với role MEMBER.
    
    Request Body:
    - project_code: Mã dự án để join
    
    Response: Trả về thông tin project
    
    Errors:
    - 404: Mã dự án không tồn tại
    - 422: Validation error
    """
    # Tìm project theo code
    project = await get_project_by_code(db, join_data.project_code)
    if not project:
        raise HTTPException(status_code=404, detail="Mã dự án không tồn tại")
    
    # Kiểm tra xem đã là member chưa
    stmt = select(ProjectMember).where(
        (ProjectMember.project_id == project.id) & (ProjectMember.user_id == current_user.id)
    )
    is_member = (await db.execute(stmt)).scalar_one_or_none()
    
    # Nếu chưa join, tự động thêm vào với role MEMBER
    if not is_member:
        new_member = ProjectMember(user_id=current_user.id, project_id=project.id, role=RoleEnum.MEMBER)
        db.add(new_member)
        await db.commit()
    
    return project

@router.get("/{project_id}/my-role")
async def get_my_role_in_project(
    member: ProjectMember = Depends(get_current_project_member),
):
    """
    Lấy role của user hiện tại trong project.
    
    Response: {"role": "PM" | "MEMBER"}
    """
    role_val = member.role.value if hasattr(member.role, 'value') else str(member.role)
    return {"role": role_val}

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_info(
    project_id: int,
    project_update: ProjectUpdate,
    current_pm: ProjectMember = Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    """⚠️ NOT USED BY FRONTEND. Update project name/description (PM only)."""
    return await update_project(db, project_id, project_update, current_pm.user_id)

@router.delete("/{project_id}", status_code=204)
async def delete_project_by_id(
    project_id: int,
    current_pm: ProjectMember = Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    """⚠️ NOT USED BY FRONTEND. Delete project (PM only)."""
    await delete_project(db, project_id, current_pm.user_id)
    return None



from app.schemas.scm_project import MemberResponse, ChangeRoleRequest
from app.crud.crud_project import get_project_members, change_member_role, remove_project_member

# Project member list
@router.get("/{project_id}/members", response_model=list[MemberResponse])
async def list_project_members(
    project_id: int,
    member: ProjectMember = Depends(get_current_project_member),
    db: AsyncSession = Depends(get_db)
):
    """Get all members in project. Any member can view."""
    return await get_project_members(db, project_id)

# Change member role (PM only) - NOT USED BY FRONTEND
@router.put("/{project_id}/members/{target_user_id}/role", response_model=MemberResponse)
async def update_member_role(
    project_id: int,
    target_user_id: int,
    role_data: ChangeRoleRequest,
    current_pm: ProjectMember = Depends(get_current_pm),
    db: AsyncSession = Depends(get_db)
):
    """⚠️ NOT USED BY FRONTEND. Change member role (PM only). PM cannot demote self."""
    if current_pm.user_id == target_user_id and role_data.role == "MEMBER":
        raise HTTPException(status_code=400, detail="PM cannot demote self!")
    updated_member = await change_member_role(db, project_id, target_user_id, role_data.role)
    if not updated_member:
        raise HTTPException(status_code=404, detail="Member not found in project")
    return updated_member

# Remove member from project (PM only) - NOT USED BY FRONTEND
@router.delete("/{project_id}/members/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def kick_member(
    project_id: int,
    target_user_id: int,
    current_pm: ProjectMember = Depends(get_current_pm),
    db: AsyncSession = Depends(get_db)
):
    """⚠️ NOT USED BY FRONTEND. Remove member from project (PM only). PM cannot kick self."""
    if current_pm.user_id == target_user_id:
        raise HTTPException(status_code=400, detail="Cannot kick yourself from project!")
    success = await remove_project_member(db, project_id, target_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found in project")
    return None