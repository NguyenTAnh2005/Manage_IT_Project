"""
CRUD operations cho Task model
CRUD = Tạo, Đọc, Sửa, Xóa
"""

import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Task, ProjectMember, RoleEnum, TaskStatus, TaskPriority

logger = logging.getLogger(__name__)


# ===== TẠO =====

async def create_task(
    db: AsyncSession,
    project_id: int,
    title: str,
    description: str,
    status: str,
    priority: str,
    created_by: int,
    assigned_to: int = None
) -> Task:
    """
    Tạo công việc mới trong dự án
    - Input: database session, project_id, title, description, status, priority, created_by, assigned_to (optional)
    - Output: Task object vừa tạo
    """
    # Convert string sang Enum
    status_enum = TaskStatus(status)
    priority_enum = TaskPriority(priority)
    
    db_task = Task(
        project_id=project_id,
        name=title,  # Model yêu cầu field 'name'
        title=title,
        description=description,
        status=status_enum,
        priority=priority_enum,
        created_by=created_by,
        assigned_to=assigned_to
    )
    
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    
    logger.info(f"Tạo công việc: {db_task.id} - {db_task.title} trong dự án {project_id} bởi user {created_by}")
    
    return db_task


# ===== ĐỌC =====

async def get_task_by_id(db: AsyncSession, task_id: int) -> Task | None:
    """
    Lấy công việc từ database theo id
    - Input: database session, task_id (integer)
    - Output: Task object nếu tìm thấy, None nếu không
    """
    return await db.get(Task, task_id)


async def get_tasks_by_project(db: AsyncSession, project_id: int) -> List[Task]:
    """
    Lấy tất cả công việc của một dự án
    - Input: database session, project_id (integer)
    - Output: List of Task objects
    """
    query = select(Task).where(Task.project_id == project_id).order_by(Task.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_tasks_assigned_to_user(db: AsyncSession, user_id: int) -> List[Task]:
    """
    Lấy tất cả công việc được gán cho một user
    - Input: database session, user_id (integer)
    - Output: List of Task objects
    """
    query = select(Task).where(Task.assigned_to == user_id).order_by(Task.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


# ===== SỬA =====

async def update_task(
    db: AsyncSession,
    task_id: int,
    **kwargs
) -> Task | None:
    """
    Sửa thông tin công việc
    - Input: database session, task_id, các trường cần update (title, description, status, priority, assigned_to)
    - Output: Task object đã sửa, None nếu công việc không tồn tại
    """
    db_task = await get_task_by_id(db, task_id)
    
    if not db_task:
        return None
    
    # Sửa các trường được phép
    allowed_fields = {"title", "description", "status", "priority", "assigned_to"}
    for key, value in kwargs.items():
        if key in allowed_fields and hasattr(db_task, key):
            setattr(db_task, key, value)
    
    await db.commit()
    await db.refresh(db_task)
    
    logger.info(f"Sửa công việc: {task_id}")
    
    return db_task


# ===== XÓA =====

async def delete_task(db: AsyncSession, task_id: int) -> bool:
    """
    Xóa công việc khỏi database
    - Input: database session, task_id
    - Output: True nếu xóa thành công, False nếu công việc không tồn tại
    """
    db_task = await get_task_by_id(db, task_id)
    
    if not db_task:
        return False
    
    await db.delete(db_task)
    await db.commit()
    
    logger.info(f"Xóa công việc: {task_id}")
    
    return True


# ===== KIỂM QUYỀN =====

async def check_task_permission(
    db: AsyncSession,
    user_id: int,
    task_id: int
) -> bool:
    """
    Kiểm tra user có quyền truy cập công việc hay không
    - User phải là thành viên dự án HOẶC được gán công việc này
    - Input: database session, user_id, task_id
    - Output: True nếu có quyền, False nếu không
    """
    db_task = await get_task_by_id(db, task_id)
    
    if not db_task:
        return False
    
    # Kiểm tra nếu user được gán công việc này
    if db_task.assigned_to == user_id:
        return True
    
    # Kiểm tra nếu user là thành viên dự án
    is_member = await check_task_project_permission(db, user_id, db_task.project_id)
    
    return is_member


async def check_task_project_permission(
    db: AsyncSession,
    user_id: int,
    project_id: int
) -> bool:
    """
    Kiểm tra user có phải là thành viên của dự án hay không
    - Input: database session, user_id, project_id
    - Output: True nếu là thành viên, False nếu không
    """
    query = select(ProjectMember).where(
        (ProjectMember.project_id == project_id) & 
        (ProjectMember.user_id == user_id)
    )
    
    result = await db.execute(query)
    member = result.scalars().first()
    
    return member is not None


async def check_task_pm_permission(
    db: AsyncSession,
    user_id: int,
    task_id: int
) -> bool:
    """
    Kiểm tra user có phải là PM của dự án chứa công việc hay không
    - Input: database session, user_id, task_id
    - Output: True nếu là PM, False nếu không
    """
    db_task = await get_task_by_id(db, task_id)
    
    if not db_task:
        return False
    
    query = select(ProjectMember).where(
        (ProjectMember.project_id == db_task.project_id) & 
        (ProjectMember.user_id == user_id) &
        (ProjectMember.role == RoleEnum.PM)
    )
    
    result = await db.execute(query)
    member = result.scalars().first()
    
    return member is not None
