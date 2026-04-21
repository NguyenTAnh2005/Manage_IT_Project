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
    return await create_project(db, project_data, current_user.id)

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

# ✅ Endpoint Join dự án (Rất quan trọng)
@router.post("/join", response_model=ProjectResponse)
async def join_existing_project(
    join_data: ProjectJoinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project_by_code(db, join_data.project_code)
    if not project:
        raise HTTPException(status_code=404, detail="Mã dự án không tồn tại")
    
    # Kiểm tra xem đã là member chưa
    stmt = select(ProjectMember).where(
        (ProjectMember.project_id == project.id) & (ProjectMember.user_id == current_user.id)
    )
    is_member = (await db.execute(stmt)).scalar_one_or_none()
    
    if not is_member:
        new_member = ProjectMember(user_id=current_user.id, project_id=project.id, role=RoleEnum.MEMBER)
        db.add(new_member)
        await db.commit()
    
    return project

@router.get("/{project_id}/my-role")
async def get_my_role_in_project(
    member: ProjectMember = Depends(get_current_project_member),
):
    # Trả về value của Enum (ví dụ "PM" hoặc "MEMBER")
    role_val = member.role.value if hasattr(member.role, 'value') else str(member.role)
    return {"role": role_val}

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_info(
    project_id: int,
    project_update: ProjectUpdate,
    current_pm: ProjectMember = Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    return await update_project(db, project_id, project_update, current_pm.user_id)

@router.delete("/{project_id}", status_code=204)
async def delete_project_by_id(
    project_id: int,
    current_pm: ProjectMember = Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    await delete_project(db, project_id, current_pm.user_id)
    return None