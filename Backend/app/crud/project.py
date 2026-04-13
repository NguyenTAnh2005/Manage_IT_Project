"""
CRUD operations cho Project model
CRUD = Create, Read, Update, Delete
"""

import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Project, ProjectMember, RoleEnum

logger = logging.getLogger(__name__)


# ===== CREATE =====

async def create_project(
    db: AsyncSession, 
    user_id: int, 
    project_code: str,
    project_name: str, 
    description: str = None
) -> Project:
    """
    Tạo project mới trong database
    - Input: database session, user_id, project_code, project_name, description
    - Output: Project object vừa tạo
    - Tự động thêm creator vào project_members với role PM
    """
    db_project = Project(
        project_code=project_code,
        name=project_name,
        description=description
    )
    
    db.add(db_project)
    await db.flush()  # Flush để lấy project.id trước khi commit
    
    # Thêm user vào project với role PM
    project_member = ProjectMember(
        user_id=user_id,
        project_id=db_project.id,
        role=RoleEnum.PM
    )
    db.add(project_member)
    
    await db.commit()
    await db.refresh(db_project)
    
    logger.info(f"Created project: {db_project.id} - {db_project.name} by user {user_id}")
    
    return db_project


# ===== READ =====

async def get_project_by_id(db: AsyncSession, project_id: int) -> Project | None:
    """
    Lấy project từ database theo id
    - Input: database session, project_id (integer)
    - Output: Project object nếu tìm thấy, None nếu không
    """
    return await db.get(Project, project_id)


async def get_projects_by_user(db: AsyncSession, user_id: int) -> List[Project]:
    """
    Lấy tất cả projects mà user là member/PM
    - Input: database session, user_id (integer)
    - Output: List of Project objects
    """
    query = select(Project).join(
        ProjectMember, Project.id == ProjectMember.project_id
    ).where(ProjectMember.user_id == user_id)
    
    result = await db.execute(query)
    return result.scalars().all()


# ===== UPDATE =====

async def update_project(
    db: AsyncSession, 
    project_id: int, 
    **kwargs
) -> Project | None:
    """
    Update thông tin project
    - Input: database session, project_id, các trường cần update (name, description, ...)
    - Output: Project object đã update, None nếu project không tồn tại
    """
    db_project = await get_project_by_id(db, project_id)
    
    if not db_project:
        return None
    
    # Update các trường được pass vào (bỏ qua project_code vì nó là unique identifier)
    for key, value in kwargs.items():
        if hasattr(db_project, key) and key != "project_code":
            setattr(db_project, key, value)
    
    await db.commit()
    await db.refresh(db_project)
    
    logger.info(f"Updated project: {project_id}")
    
    return db_project


# ===== DELETE =====

async def delete_project(db: AsyncSession, project_id: int) -> bool:
    """
    Xóa project khỏi database
    - Input: database session, project_id
    - Output: True nếu xóa thành công, False nếu project không tồn tại
    - Cascade: tự động xóa tasks, project_members liên quan
    """
    db_project = await get_project_by_id(db, project_id)
    
    if not db_project:
        return False
    
    await db.delete(db_project)
    await db.commit()
    
    logger.info(f"Deleted project: {project_id}")
    
    return True


# ===== PERMISSION CHECK =====

async def check_project_permission(
    db: AsyncSession, 
    project_id: int, 
    user_id: int, 
    require_pm: bool = False
) -> bool:
    """
    Kiểm tra user có quyền truy cập project hay không
    - Input: database session, project_id, user_id, require_pm (chỉ PM mới được)
    - Output: True nếu có quyền, False nếu không
    """
    query = select(ProjectMember).where(
        (ProjectMember.project_id == project_id) & 
        (ProjectMember.user_id == user_id)
    )
    
    result = await db.execute(query)
    member = result.scalars().first()
    
    if not member:
        return False
    
    if require_pm:
        return member.role == RoleEnum.PM
    
    return True


async def check_project_ownership(
    db: AsyncSession,
    project_id: int,
    user_id: int
) -> bool:
    """
    Kiểm tra user có phải owner (PM) của project hay không
    - Input: database session, project_id, user_id
    - Output: True nếu là owner, False nếu không
    """
    return await check_project_permission(db, project_id, user_id, require_pm=True)
