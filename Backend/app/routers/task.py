"""
Task endpoints - Các API liên quan đến công việc (tasks).
- Tạo công việc
- Xem danh sách công việc (WBS tree)
- Chi tiết công việc
- Cập nhật công việc
- Xóa công việc
- Kanban board (tasks grouped by status)
- Gantt chart (tasks in timeline)
"""

from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.core.dependencies import get_current_user, get_db
from app.crud.crud_task import (
    create_task,
    get_task_by_id,
    list_project_tasks,
    update_task,
    delete_task,
    get_tasks_by_status,
    get_tasks_by_date_range,
)
from app.models.model import User
from app.schemas.scm_task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskDetailResponse,
    TaskKanbanResponse,
    TaskGanttResponse,
    TaskListResponse,
)

# Tạo router cho task endpoints (không có prefix - paths đã đầy đủ)
router = APIRouter(tags=["Tasks"])


@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    project_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Tạo công việc mới trong project.
    User phải là member của project để tạo task.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        project_id: ID project
        task_data: TaskCreate schema
            - name (str): Tên task (3-200 ký tự)
            - parent_id (int): ID task cha (tùy chọn, dùng cho WBS)
            - mo (float): PERT Optimistic (≥0.5)
            - ml (float): PERT Most Likely (≥0.5)
            - mp (float): PERT Pessimistic (≥0.5)
            - start_date (date): Ngày bắt đầu (tùy chọn)
            - end_date (date): Ngày kết thúc (tùy chọn)
            - cost_total (float): Chi phí (≥0, tùy chọn)
    
    Returns:
        TaskResponse: Thông tin task mới được tạo (201)
        
    Raises:
        400: Parent task không tồn tại
        403: User không phải member của project
        404: Project không tồn tại
        
    Ví dụ request body:
        {
            "name": "Thiết kế database",
            "mo": 3,
            "ml": 5,
            "mp": 7,
            "start_date": "2026-05-01",
            "end_date": "2026-05-15"
        }
    """
    try:
        new_task = await create_task(
            db=db,
            project_id=project_id,
            task=task_data,
            user_id=current_user.id,
        )
        return new_task
        
    except ValueError as e:
        # User không phải member hoặc parent task lỗi
        if "member" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )


@router.get("/projects/{project_id}/tasks", response_model=TaskListResponse)
async def list_project_tasks_wbs(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lấy danh sách tất cả công việc của project (WBS).
    User phải là member của project.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        project_id: ID project
    
    Returns:
        TaskListResponse: Danh sách tasks
            - total (int): Tổng số tasks
            - tasks (list): Danh sách TaskResponse
        
    Ví dụ response:
        {
            "total": 5,
            "tasks": [
                {
                    "id": 1,
                    "name": "Project Setup",
                    "status": "DOING",
                    "est": 5.33,
                    ...
                }
            ]
        }
    """
    # Kiểm tra user có phải member không
    from app.models.model import ProjectMember
    from sqlalchemy import select
    
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
    
    # Lấy danh sách tasks
    tasks = await list_project_tasks(db, project_id)
    
    return TaskListResponse(
        total=len(tasks),
        tasks=tasks,
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_detail(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lấy chi tiết một công việc.
    User phải là member của project chứa task để xem.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        task_id: ID task
    
    Returns:
        TaskResponse: Chi tiết task
        
    Raises:
        403: User không phải member của project
        404: Task không tồn tại
        
    Ví dụ response:
        {
            "id": 1,
            "project_id": 1,
            "name": "Database Design",
            "status": "DOING",
            "mo": 3,
            "ml": 5,
            "mp": 7,
            "est": 5.0,
            "start_date": "2026-05-01",
            "end_date": "2026-05-15",
            "cost_total": 5000000,
            ...
        }
    """
    # Lấy task
    task = await get_task_by_id(db, task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Công việc không tồn tại",
        )
    
    # Kiểm tra user có phải member của project không
    from app.models.model import ProjectMember
    from sqlalchemy import select
    
    member_stmt = (
        select(ProjectMember)
        .where(
            (ProjectMember.project_id == task.project_id)
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
    
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_info(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cập nhật thông tin công việc.
    User phải là member của project để cập nhật.
    Nếu cập nhật PERT estimates → EST được recalculate tự động.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        task_id: ID task
        task_update: TaskUpdate schema
            - name (str): Tên mới (tùy chọn)
            - status (str): Trạng thái mới - TODO, DOING, DONE (tùy chọn)
            - mo, ml, mp (float): PERT estimates mới (tùy chọn)
            - start_date (date): Ngày bắt đầu mới (tùy chọn)
            - end_date (date): Ngày kết thúc mới (tùy chọn)
            - cost_total (float): Chi phí mới (tùy chọn)
    
    Returns:
        TaskResponse: Thông tin task sau cập nhật
        
    Raises:
        403: User không phải member của project
        404: Task không tồn tại
        
    Ví dụ request body:
        {
            "status": "DOING",
            "ml": 6,
            "cost_total": 5500000
        }
    """
    # Cập nhật task
    updated_task = await update_task(
        db=db,
        task_id=task_id,
        task_update=task_update,
        user_id=current_user.id,
    )
    
    if updated_task is None:
        # Kiểm tra xem là vì không tìm thấy task hay không có quyền
        task = await get_task_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Công việc không tồn tại",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không phải member của project này",
            )
    
    return updated_task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_by_id(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Xóa công việc.
    User phải là member của project để xóa.
    Cascade delete - tất cả subtasks cũng bị xóa.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        task_id: ID task
    
    Returns:
        None (204 No Content)
        
    Raises:
        403: User không phải member của project
        404: Task không tồn tại
        
    Note: Hành động này sẽ xóa task cùng tất cả subtasks!
    """
    # Xóa task
    success = await delete_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
    )
    
    if not success:
        # Kiểm tra xem là vì không tìm thấy task hay không có quyền
        task = await get_task_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Công việc không tồn tại",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không phải member của project này",
            )
    
    return None


@router.get("/projects/{project_id}/tasks/kanban", response_model=TaskKanbanResponse)
async def get_kanban_board(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lấy Kanban board - tasks grouped by status (TODO, DOING, DONE).
    User phải là member của project.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        project_id: ID project
    
    Returns:
        TaskKanbanResponse: Tasks grouped by status
            - todo (list): Tasks với status TODO
            - doing (list): Tasks với status DOING
            - done (list): Tasks với status DONE
        
    Raises:
        403: User không phải member của project
        
    Ví dụ response:
        {
            "todo": [
                {"id": 1, "name": "Task 1", "status": "TODO", ...}
            ],
            "doing": [
                {"id": 2, "name": "Task 2", "status": "DOING", ...}
            ],
            "done": [
                {"id": 3, "name": "Task 3", "status": "DONE", ...}
            ]
        }
    """
    try:
        tasks_by_status = await get_tasks_by_status(db, project_id, current_user.id)
        
        return TaskKanbanResponse(
            todo=tasks_by_status["TODO"],
            doing=tasks_by_status["DOING"],
            done=tasks_by_status["DONE"],
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/projects/{project_id}/tasks/gantt", response_model=list[TaskGanttResponse])
async def get_gantt_chart(
    project_id: int,
    start_date: date = Query(..., description="Ngày bắt đầu (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Ngày kết thúc (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lấy Gantt chart - tasks trong date range với timeline.
    User phải là member của project.
    
    **Cần authentication:** Đúng (Bearer token)
    
    Args:
        project_id: ID project
        start_date: Ngày bắt đầu (query param) - format: YYYY-MM-DD
        end_date: Ngày kết thúc (query param) - format: YYYY-MM-DD
    
    Returns:
        list[TaskGanttResponse]: Danh sách tasks trong date range
            - id (int): ID task
            - name (str): Tên task
            - start_date (date): Ngày bắt đầu
            - end_date (date): Ngày kết thúc
            - status (str): Trạng thái
            - est (float): Thời gian ước tính (ngày)
            - progress (int): % hoàn thành (0-100, DONE=100)
        
    Raises:
        403: User không phải member của project
        
    Ví dụ request:
        GET /tasks/projects/1/tasks/gantt?start_date=2026-05-01&end_date=2026-05-31
        
    Ví dụ response:
        [
            {
                "id": 1,
                "name": "Database Design",
                "start_date": "2026-05-01",
                "end_date": "2026-05-15",
                "status": "DOING",
                "est": 5.0,
                "progress": 50
            },
            {
                "id": 2,
                "name": "API Development",
                "start_date": "2026-05-15",
                "end_date": "2026-05-31",
                "status": "TODO",
                "est": 10.0,
                "progress": 0
            }
        ]
    """
    try:
        # Lấy tasks trong date range
        tasks = await get_tasks_by_date_range(
            db=db,
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
            user_id=current_user.id,
        )
        
        # Convert tasks to Gantt format
        gantt_tasks = []
        for task in tasks:
            # Tính progress dựa vào status
            if task.status == "DONE":
                progress = 100
            elif task.status == "DOING":
                progress = 50  # Có thể optimize sau
            else:  # TODO
                progress = 0
            
            gantt_task = TaskGanttResponse(
                id=task.id,
                name=task.name,
                start_date=task.start_date,
                end_date=task.end_date,
                status=task.status,
                est=task.est,
                progress=progress,
            )
            gantt_tasks.append(gantt_task)
        
        return gantt_tasks
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
