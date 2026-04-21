from datetime import date
from typing import Optional
# ✅ Đã import thêm hàm delete để xóa trực tiếp
from sqlalchemy import select, and_, or_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models.model import Task, ProjectMember
from app.schemas.scm_task import TaskCreate, TaskUpdate

def calculate_est(mo: Optional[float], ml: Optional[float], mp: Optional[float]) -> Optional[float]:
    if mo is None or ml is None or mp is None: return None
    return round((mo + 4 * ml + mp) / 6, 2)

# ✅ HÀM TÍNH TỔNG (BUBBLE-UP)
async def update_parent_metrics(db: AsyncSession, parent_id: int):
    if not parent_id: return
    
    stmt = select(
        func.sum(Task.mo).label("mo"),
        func.sum(Task.ml).label("ml"),
        func.sum(Task.mp).label("mp"),
        func.sum(Task.cost_total).label("cost")
    ).where(Task.parent_id == parent_id)
    
    res = await db.execute(stmt)
    sums = res.mappings().one()

    parent = await db.get(Task, parent_id)
    if parent:
        parent.mo = sums["mo"] or 0.0
        parent.ml = sums["ml"] or 0.0
        parent.mp = sums["mp"] or 0.0
        parent.cost_total = sums["cost"] or 0.0
        parent.est = calculate_est(parent.mo, parent.ml, parent.mp)
        
        db.add(parent)
        await db.flush()
        
        if parent.parent_id:
            await update_parent_metrics(db, parent.parent_id)

# 🚀 CREATE
async def create_task(db: AsyncSession, project_id: int, task: TaskCreate, user_id: int) -> Task:
    est = calculate_est(task.mo, task.ml, task.mp)
    db_task = Task(
        project_id=project_id, parent_id=task.parent_id, owner_id=task.owner_id,
        name=task.name, status="TODO", mo=task.mo, ml=task.ml, mp=task.mp, est=est,
        cost_total=task.cost_total or 0.0
    )
    db.add(db_task)
    await db.flush()
    if db_task.parent_id: await update_parent_metrics(db, db_task.parent_id)
    await db.commit()
    await db.refresh(db_task)
    return db_task

# 🔍 READ
async def get_task_by_id(db: AsyncSession, task_id: int) -> Task | None:
    stmt = select(Task).options(joinedload(Task.owner)).where(Task.id == task_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def list_project_tasks(db: AsyncSession, project_id: int) -> list[Task]:
    stmt = select(Task).options(joinedload(Task.owner)).where(Task.project_id == project_id).order_by(Task.name.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

# 📝 UPDATE
# Sửa lại hàm update_task (Bỏ check PM)
async def update_task(db: AsyncSession, task_id: int, task_update: TaskUpdate, user_id: int) -> Task | None:
    task = await db.get(Task, task_id)
    if not task: return None
    
    old_parent_id = task.parent_id
    update_data = task_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    task.est = calculate_est(task.mo, task.ml, task.mp)
    await db.flush()

    if task.parent_id: await update_parent_metrics(db, task.parent_id)
    if old_parent_id and old_parent_id != task.parent_id:
        await update_parent_metrics(db, old_parent_id)
    
    await db.commit()
    stmt = select(Task).options(joinedload(Task.owner)).where(Task.id == task_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()



# ========================================================
# 🗑️ DELETE (ĐÃ TRỊ TẬN GỐC LỖI BAY MÀU CHA)
# ========================================================
async def delete_task(db: AsyncSession, task_id: int, user_id: int) -> bool:
    task = await db.get(Task, task_id)
    if not task: return False
    
    p_id = task.parent_id 
    
    # 1. Tìm toàn bộ con cháu (để xóa dọn dẹp ổ)
    all_subtasks = await get_subtasks_recursive(db, task_id)
    sub_ids = [t.id for t in all_subtasks]
    
    # 2. ÉP XÓA BẰNG SQL THUẦN (Né mọi lỗi Cascade ngược từ Model)
    if sub_ids:
        await db.execute(delete(Task).where(Task.id.in_(sub_ids)))
        
    await db.execute(delete(Task).where(Task.id == task_id))
    
    # 3. Tính toán lại cho cha (Lúc này cha vẫn an toàn 100%)
    if p_id:
        await update_parent_metrics(db, p_id)
    
    await db.commit()
    return True

async def get_subtasks_recursive(db: AsyncSession, parent_id: int) -> list[Task]:
    stmt = select(Task).where(Task.parent_id == parent_id)
    result = await db.execute(stmt)
    direct_children = result.scalars().all()
    all_subtasks = list(direct_children)
    for child in direct_children:
        grandchildren = await get_subtasks_recursive(db, child.id)
        all_subtasks.extend(grandchildren)
    return all_subtasks

# 📊 KANBAN & GANTT
async def get_tasks_by_status(db: AsyncSession, project_id: int, user_id: int) -> dict:
    result = {}
    for status in ["TODO", "DOING", "DONE"]:
        stmt = (
            select(Task)
            .options(joinedload(Task.owner))
            .where((Task.project_id == project_id) & (Task.status == status))
            .order_by(Task.name.asc()) # ✅ Đổi thành sắp xếp theo Tên A-Z
        )
        exec_result = await db.execute(stmt)
        result[status] = exec_result.scalars().all()
    return result

async def get_tasks_by_date_range(db: AsyncSession, project_id: int, start_date: date, end_date: date, user_id: int) -> list[Task]:
    stmt = select(Task).options(joinedload(Task.owner)).where((Task.project_id == project_id) & (or_(and_(Task.start_date >= start_date, Task.start_date <= end_date),and_(Task.end_date >= start_date, Task.end_date <= end_date)))).order_by(Task.start_date.asc())
    result = await db.execute(stmt)
    return result.scalars().all()