"""
CRUD operations cho Task model - Quản lý WBS, PERT, Cost, Kanban, Gantt.
Tự động tính toán metrics của task cha từ các con (bubble-up aggregation).
"""

from datetime import date
from typing import Optional
from sqlalchemy import select, and_, or_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models.model import Task, ProjectMember
from app.schemas.scm_task import TaskCreate, TaskUpdate


def calculate_est(mo: Optional[float], ml: Optional[float], mp: Optional[float]) -> Optional[float]:
    """Tính EST theo công thức PERT: (O + 4M + P) / 6"""
    if mo is None or ml is None or mp is None: 
        return None
    return round((mo + 4 * ml + mp) / 6, 2)


async def update_parent_metrics(db: AsyncSession, parent_id: int):
    """
    Cộng dồn metrics từ task con lên task cha.
    Giúp task cha (nhóm việc) tự động tính tổng PERT và chi phí từ các con.
    """
    if not parent_id: 
        return
    
    # Tính tổng metrics từ tất cả task con trực tiếp
    stmt = select(
        func.sum(Task.mo).label("mo"),
        func.sum(Task.ml).label("ml"),
        func.sum(Task.mp).label("mp"),
        func.sum(Task.cost_total).label("cost")
    ).where(Task.parent_id == parent_id)
    
    res = await db.execute(stmt)
    sums = res.mappings().one()

    # Cập nhật task cha với giá trị cộng dồn
    parent = await db.get(Task, parent_id)
    if parent:
        parent.mo = sums["mo"] or 0.0
        parent.ml = sums["ml"] or 0.0
        parent.mp = sums["mp"] or 0.0
        parent.cost_total = sums["cost"] or 0.0
        parent.est = calculate_est(parent.mo, parent.ml, parent.mp)
        
        db.add(parent)
        await db.flush()
        
        # Cập nhật task ông một cách đệ quy
        if parent.parent_id:
            await update_parent_metrics(db, parent.parent_id)


async def create_task(db: AsyncSession, project_id: int, task: TaskCreate, user_id: int) -> Task:
    """Tạo task mới với EST tự động tính toán. Cập nhật metrics của task cha nếu là task con."""
    est = calculate_est(task.mo, task.ml, task.mp)
    db_task = Task(
        project_id=project_id, 
        parent_id=task.parent_id, 
        owner_id=task.owner_id,
        name=task.name, 
        status="TODO", 
        mo=task.mo, 
        ml=task.ml, 
        mp=task.mp, 
        est=est,
        cost_total=task.cost_total or 0.0
    )
    db.add(db_task)
    await db.flush()
    
    # Cập nhật metrics task cha nếu đây là task con
    if db_task.parent_id: 
        await update_parent_metrics(db, db_task.parent_id)
        
    await db.commit()
    
    # Lấy lại task kèm thông tin owner
    stmt = select(Task).options(joinedload(Task.owner)).where(Task.id == db_task.id)
    res = await db.execute(stmt)
    return res.scalar_one()


async def get_task_by_id(db: AsyncSession, task_id: int) -> Task | None:
    """Lấy task kèm thông tin owner."""
    stmt = select(Task).options(joinedload(Task.owner)).where(Task.id == task_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_project_tasks(db: AsyncSession, project_id: int) -> list[Task]:
    """Lấy tất cả tasks của dự án kèm thông tin owner."""
    stmt = (
        select(Task)
        .options(joinedload(Task.owner))
        .where(Task.project_id == project_id)
        .order_by(Task.name.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_task(db: AsyncSession, task_id: int, task_update: TaskUpdate, user_id: int) -> Task | None:
    """Cập nhật task với tính toán lại EST và bubble-up metrics của task cha."""
    task = await db.get(Task, task_id)
    if not task: 
        return None
    
    old_parent_id = task.parent_id
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Áp dụng cập nhật lên task
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # Tính lại EST
    task.est = calculate_est(task.mo, task.ml, task.mp)
    await db.flush()

    # Cập nhật metrics task cha (cả task cha cũ và mới nếu parent thay đổi)
    if task.parent_id: 
        await update_parent_metrics(db, task.parent_id)
    if old_parent_id and old_parent_id != task.parent_id:
        await update_parent_metrics(db, old_parent_id)
    
    await db.commit()
    
    # Lấy lại task kèm thông tin owner
    stmt = select(Task).options(joinedload(Task.owner)).where(Task.id == task_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def delete_task(db: AsyncSession, task_id: int, user_id: int) -> bool:
    """
    Xóa task cùng tất cả task con của nó (xóa đệ quy).
    Cập nhật metrics task cha sau khi xóa.
    """
    task = await db.get(Task, task_id)
    if not task: 
        return False
    
    parent_id = task.parent_id 
    
    # Tìm tất cả task con/cháu
    all_subtasks = await get_subtasks_recursive(db, task_id)
    subtask_ids = [t.id for t in all_subtasks]
    
    # Xóa tất cả task con trước
    if subtask_ids:
        await db.execute(delete(Task).where(Task.id.in_(subtask_ids)))
        
    # Xóa task chính
    await db.execute(delete(Task).where(Task.id == task_id))
    
    # Tính lại metrics task cha sau xóa
    if parent_id:
        await update_parent_metrics(db, parent_id)
    
    await db.commit()
    return True


async def get_subtasks_recursive(db: AsyncSession, parent_id: int) -> list[Task]:
    """Lấy tất cả task con/cháu của một task (đệ quy)."""
    stmt = select(Task).where(Task.parent_id == parent_id)
    result = await db.execute(stmt)
    direct_children = result.scalars().all()
    
    all_subtasks = list(direct_children)
    for child in direct_children:
        grandchildren = await get_subtasks_recursive(db, child.id)
        all_subtasks.extend(grandchildren)
    
    return all_subtasks


async def get_tasks_by_status(db: AsyncSession, project_id: int, user_id: int) -> dict:
    """Lấy tasks được nhóm theo trạng thái cho bảng Kanban."""
    result = {}
    for status in ["TODO", "DOING", "DONE"]:
        stmt = (
            select(Task)
            .options(joinedload(Task.owner))
            .where((Task.project_id == project_id) & (Task.status == status))
            .order_by(Task.name.asc())
        )
        exec_result = await db.execute(stmt)
        result[status] = exec_result.scalars().all()
    return result


async def get_tasks_by_date_range(
    db: AsyncSession, 
    project_id: int, 
    start_date: date, 
    end_date: date, 
    user_id: int
) -> list[Task]:
    """Lấy tasks trong khoảng thời gian cho biểu đồ Gantt."""
    stmt = (
        select(Task)
        .options(joinedload(Task.owner))
        .where(
            (Task.project_id == project_id) & 
            (or_(
                and_(Task.start_date >= start_date, Task.start_date <= end_date),
                and_(Task.end_date >= start_date, Task.end_date <= end_date)
            ))
        )
        .order_by(Task.start_date.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()