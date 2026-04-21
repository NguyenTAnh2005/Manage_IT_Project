# Backend\app\routers\task.py

from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select # ✅ THÊM DÒNG NÀY

from app.core.dependencies import get_current_user, get_db, get_current_pm, get_current_project_member
from app.crud.crud_task import (
    create_task, get_task_by_id, list_project_tasks,
    update_task, delete_task, get_tasks_by_status, get_tasks_by_date_range
)
from app.models.model import User, ProjectMember, Task # ✅ THÊM 'Task' Ở ĐÂY
from app.schemas.scm_task import (
    TaskCreate, TaskUpdate, TaskResponse,
    TaskKanbanResponse, TaskGanttResponse, TaskListResponse,
)

router = APIRouter(tags=["Tasks"])

@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    project_id: int,
    task_data: TaskCreate,
    current_pm: ProjectMember = Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await create_task(db, project_id, task_data, current_pm.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects/{project_id}/tasks", response_model=TaskListResponse)
async def list_project_tasks_wbs(
    project_id: int,
    member: ProjectMember = Depends(get_current_project_member), 
    db: AsyncSession = Depends(get_db),
):
    tasks = await list_project_tasks(db, project_id)
    return TaskListResponse(total=len(tasks), tasks=tasks)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_info(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Công việc không tồn tại")
    
    member_stmt = select(ProjectMember).where(
        (ProjectMember.project_id == task.project_id) & (ProjectMember.user_id == current_user.id)
    )
    member = (await db.execute(member_stmt)).scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=403, detail="Bạn không thuộc dự án này")

    update_dict = task_update.model_dump(exclude_unset=True)
    
    # ✅ LOGIC BÌNH ĐẲNG: Kéo thẻ (đổi status) thì phải là việc của chính mình
    if 'status' in update_dict:
        # Nếu task có người phụ trách, mà người đó KHÔNG PHẢI là người đang thao tác -> Chặn!
        if task.owner_id is not None and task.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Chỉ người phụ trách mới được kéo thẻ chuyển trạng thái!")

    # Nếu sửa các thông tin KHÁC (Tên, Tiền, Ngày...), thì bắt buộc phải là PM
    is_only_updating_status = list(update_dict.keys()) == ['status']
    if not is_only_updating_status and member.role.name != "PM":
        raise HTTPException(status_code=403, detail="Chỉ Trưởng dự án (PM) mới được sửa thông tin chi tiết!")

    # Chống sửa số liệu trên task cha
    check_child_stmt = select(Task).where(Task.parent_id == task_id)
    child_result = await db.execute(check_child_stmt)
    if child_result.scalars().first() and any(k in update_dict for k in ["mo", "ml", "mp", "cost_total"]):
         raise HTTPException(status_code=400, detail="Không thể sửa số liệu trực tiếp trên nhóm việc cha")

    return await update_task(db, task_id, task_update, current_user.id)


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task_by_id(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Công việc không tồn tại")
    
    from app.core.dependencies import get_current_pm_by_project_id
    await get_current_pm_by_project_id(task.project_id, current_user, db)

    await delete_task(db, task_id, current_user.id)
    return None

# 2. API LẤY DỮ LIỆU KANBAN (Chia sẵn 3 cột cho Frontend)
@router.get("/projects/{project_id}/tasks/kanban", response_model=TaskKanbanResponse)
async def get_kanban_board(
    project_id: int,
    member: ProjectMember = Depends(get_current_project_member),
    db: AsyncSession = Depends(get_db),
):
    tasks_by_status = await get_tasks_by_status(db, project_id, member.user_id)
    return TaskKanbanResponse(
        todo=tasks_by_status["TODO"],
        doing=tasks_by_status["DOING"],
        done=tasks_by_status["DONE"],
    )