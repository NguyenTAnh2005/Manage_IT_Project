"""
CRUD operations cho Task - Tương tác với database.
Sử dụng SQLAlchemy async ORM để thực hiện các thao tác database.

Task model hỗ trợ:
- WBS (Work Breakdown Structure): parent_id cho task hierarchy
- PERT: mo, ml, mp → est = (mo + 4*ml + mp) / 6
- Kanban: status (TODO, DOING, DONE)
- Gantt: start_date, end_date
- Cost: cost_total
"""

from datetime import date
from typing import Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model import Task, ProjectMember
from app.schemas.scm_task import TaskCreate, TaskUpdate


def calculate_est(mo: float, ml: float, mp: float) -> float:
    """
    Tính thời gian ước tính PERT.
    Formula: EST = (Optimistic + 4 * Most Likely + Pessimistic) / 6
    
    Args:
        mo (float): Optimistic time (ngày)
        ml (float): Most Likely time (ngày)
        mp (float): Pessimistic time (ngày)
    
    Returns:
        float: Estimated time (ngày)
        
    Ví dụ:
        mo=3, ml=5, mp=7 → EST = (3 + 4*5 + 7) / 6 = 30/6 = 5.0
    """
    return round((mo + 4 * ml + mp) / 6, 2)


async def create_task(
    db: AsyncSession,
    project_id: int,
    task: TaskCreate,
    user_id: int,
) -> Task:
    """
    Tạo task mới.
    User phải là member của project để tạo task.
    
    Args:
        db: Database session
        project_id: ID project
        task: TaskCreate schema
        user_id: ID user tạo task (phải là member)
    
    Returns:
        Task: Object task mới được tạo
        
    Raises:
        ValueError: User không phải member của project
        ValueError: Parent task không tồn tại hoặc thuộc project khác
    
    Logic:
        1. Kiểm tra user có phải member của project không
        2. Kiểm tra parent_id có hợp lệ không (nếu có)
        3. Tính EST từ mo, ml, mp
        4. Tạo object Task
        5. Flush + Commit
        6. Refresh
    """
    # Kiểm tra user có phải member của project không
    member_stmt = (
        select(ProjectMember)
        .where(
            (ProjectMember.project_id == project_id)
            & (ProjectMember.user_id == user_id)
        )
    )
    member_result = await db.execute(member_stmt)
    is_member = member_result.scalar_one_or_none() is not None
    
    if not is_member:
        raise ValueError("User không phải member của project này")
    
    # Kiểm tra parent_id nếu có
    if task.parent_id:
        parent_task = await get_task_by_id(db, task.parent_id)
        if not parent_task or parent_task.project_id != project_id:
            raise ValueError("Parent task không tồn tại hoặc thuộc project khác")
    
    # Tính EST
    est = calculate_est(task.mo, task.ml, task.mp)
    
    # Tạo object Task
    db_task = Task(
        project_id=project_id,
        parent_id=task.parent_id,
        name=task.name,
        status="TODO",  # Default status
        mo=task.mo,
        ml=task.ml,
        mp=task.mp,
        est=est,
        start_date=task.start_date,
        end_date=task.end_date,
        cost_total=task.cost_total,
    )
    
    db.add(db_task)
    await db.flush()
    await db.commit()
    await db.refresh(db_task)
    
    return db_task


async def get_task_by_id(
    db: AsyncSession,
    task_id: int,
) -> Task | None:
    """
    Lấy task theo ID.
    
    Args:
        db: Database session
        task_id: ID task
    
    Returns:
        Task | None: Object task hoặc None nếu không tìm thấy
    """
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_project_tasks(
    db: AsyncSession,
    project_id: int,
) -> list[Task]:
    """
    Lấy danh sách tất cả tasks của project.
    Trả về danh sách flat (không phải tree).
    
    Args:
        db: Database session
        project_id: ID project
    
    Returns:
        list[Task]: Danh sách tasks sắp xếp theo:
            1. parent_id (null/root tasks trước)
            2. created_at (task cũ trước)
    """
    stmt = (
        select(Task)
        .where(Task.project_id == project_id)
        .order_by(
            Task.parent_id.asc(),  # Root tasks (parent_id=null) trước
            Task.created_at.asc()  # Theo thứ tự tạo
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_subtasks_recursive(
    db: AsyncSession,
    parent_id: int,
) -> list[Task]:
    """
    Lấy tất cả subtasks (con cháu) của một task.
    Recursive - lấy cả subtasks của subtasks.
    
    Args:
        db: Database session
        parent_id: ID task cha
    
    Returns:
        list[Task]: Danh sách tất cả subtasks
    """
    stmt = select(Task).where(Task.parent_id == parent_id)
    result = await db.execute(stmt)
    direct_children = result.scalars().all()
    
    # Lấy recursive
    all_subtasks = list(direct_children)
    for child in direct_children:
        grandchildren = await get_subtasks_recursive(db, child.id)
        all_subtasks.extend(grandchildren)
    
    return all_subtasks


async def update_task(
    db: AsyncSession,
    task_id: int,
    task_update: TaskUpdate,
    user_id: int,
) -> Task | None:
    """
    Cập nhật task.
    User phải là member của project chứa task để cập nhật.
    Nếu cập nhật mo, ml, hoặc mp thì recalculate est.
    
    Args:
        db: Database session
        task_id: ID task
        task_update: TaskUpdate schema
        user_id: ID user thực hiện update (phải là member)
    
    Returns:
        Task | None: Task sau cập nhật, hoặc None nếu không có quyền
        
    Logic:
        1. Lấy task
        2. Kiểm tra user có phải member của project không
        3. Cập nhật những field được gửi
        4. Nếu cập nhật PERT → recalculate est
        5. Commit + Refresh
    """
    # Lấy task
    task = await get_task_by_id(db, task_id)
    if not task:
        return None
    
    # Kiểm tra user có phải member của project không
    member_stmt = (
        select(ProjectMember)
        .where(
            (ProjectMember.project_id == task.project_id)
            & (ProjectMember.user_id == user_id)
        )
    )
    member_result = await db.execute(member_stmt)
    is_member = member_result.scalar_one_or_none() is not None
    
    if not is_member:
        return None
    
    # Cập nhật những field được gửi
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Kiểm tra xem có PERT field nào được cập nhật không
    has_pert_update = any(field in update_data for field in ["mo", "ml", "mp"])
    
    for field, value in update_data.items():
        if value is not None:
            setattr(task, field, value)
    
    # Nếu cập nhật PERT → recalculate est
    if has_pert_update:
        task.est = calculate_est(task.mo, task.ml, task.mp)
    
    # Commit
    await db.commit()
    await db.refresh(task)
    
    return task


async def delete_task(
    db: AsyncSession,
    task_id: int,
    user_id: int,
) -> bool:
    """
    Xóa task.
    User phải là member của project để xóa task.
    Cascade delete - tất cả subtasks cũng bị xóa.
    
    Args:
        db: Database session
        task_id: ID task
        user_id: ID user thực hiện delete (phải là member)
    
    Returns:
        bool: True nếu xóa thành công, False nếu không có quyền
    """
    # Lấy task
    task = await get_task_by_id(db, task_id)
    if not task:
        return False
    
    # Kiểm tra user có phải member của project không
    member_stmt = (
        select(ProjectMember)
        .where(
            (ProjectMember.project_id == task.project_id)
            & (ProjectMember.user_id == user_id)
        )
    )
    member_result = await db.execute(member_stmt)
    is_member = member_result.scalar_one_or_none() is not None
    
    if not is_member:
        return False
    
    # Lấy tất cả subtasks (cascade delete)
    all_subtasks = await get_subtasks_recursive(db, task_id)
    
    # Xóa tất cả subtasks
    for subtask in all_subtasks:
        await db.delete(subtask)
    
    # Xóa task chính
    await db.delete(task)
    
    # Commit
    await db.commit()
    
    return True


async def get_tasks_by_status(
    db: AsyncSession,
    project_id: int,
    user_id: int,
) -> dict:
    """
    Lấy tasks grouped by status (Kanban Board).
    User phải là member của project.
    
    Args:
        db: Database session
        project_id: ID project
        user_id: ID user (phải là member)
    
    Returns:
        dict: {
            "todo": list[Task],
            "doing": list[Task],
            "done": list[Task]
        }
        
    Raises:
        ValueError: User không phải member của project
    """
    # Kiểm tra user có phải member của project không
    member_stmt = (
        select(ProjectMember)
        .where(
            (ProjectMember.project_id == project_id)
            & (ProjectMember.user_id == user_id)
        )
    )
    member_result = await db.execute(member_stmt)
    is_member = member_result.scalar_one_or_none() is not None
    
    if not is_member:
        raise ValueError("User không phải member của project này")
    
    # Lấy tasks grouped by status
    result = {}
    for status in ["TODO", "DOING", "DONE"]:
        stmt = (
            select(Task)
            .where(
                (Task.project_id == project_id)
                & (Task.status == status)
            )
            .order_by(Task.created_at.asc())
        )
        exec_result = await db.execute(stmt)
        result[status] = exec_result.scalars().all()
    
    return result


async def get_tasks_by_date_range(
    db: AsyncSession,
    project_id: int,
    start_date: date,
    end_date: date,
    user_id: int,
) -> list[Task]:
    """
    Lấy tasks trong date range (Gantt Chart).
    User phải là member của project.
    
    Args:
        db: Database session
        project_id: ID project
        start_date: Ngày bắt đầu
        end_date: Ngày kết thúc
        user_id: ID user (phải là member)
    
    Returns:
        list[Task]: Danh sách tasks có start_date hoặc end_date trong range
        
    Raises:
        ValueError: User không phải member của project
    """
    # Kiểm tra user có phải member của project không
    member_stmt = (
        select(ProjectMember)
        .where(
            (ProjectMember.project_id == project_id)
            & (ProjectMember.user_id == user_id)
        )
    )
    member_result = await db.execute(member_stmt)
    is_member = member_result.scalar_one_or_none() is not None
    
    if not is_member:
        raise ValueError("User không phải member của project này")
    
    # Lấy tasks có dates trong range
    stmt = (
        select(Task)
        .where(
            (Task.project_id == project_id)
            & (
                or_(
                    and_(
                        Task.start_date >= start_date,
                        Task.start_date <= end_date
                    ),
                    and_(
                        Task.end_date >= start_date,
                        Task.end_date <= end_date
                    ),
                )
            )
        )
        .order_by(Task.start_date.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()
