"""
Pydantic schemas cho Task - Request/Response models.
Dùng để validate dữ liệu input và format dữ liệu output.

Task là unit của WBS, PERT, Kanban, Gantt Chart.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


# ========== CREATE REQUEST ==========
class TaskCreate(BaseModel):
    """
    Schema để tạo task mới.
    
    Fields:
        - name (str): Tên công việc (3-200 ký tự)
        - parent_id (int): ID task cha (tùy chọn, dùng cho WBS tree)
        - mo (float): PERT Optimistic - thời gian tối ưu (ngày) - ≥ 0.5
        - ml (float): PERT Most Likely - thời gian có khả năng nhất (ngày) - ≥ 0.5
        - mp (float): PERT Pessimistic - thời gian tối đa (ngày) - ≥ 0.5
        - start_date (date): Ngày bắt đầu (Gantt Chart) - tùy chọn
        - end_date (date): Ngày kết thúc dự kiến (Gantt Chart) - tùy chọn
        - cost_total (float): Chi phí dự kiến (VND) - ≥ 0 - tùy chọn
    
    Ví dụ:
        {
            "name": "Thiết kế database",
            "parent_id": null,
            "mo": 3,
            "ml": 5,
            "mp": 7,
            "start_date": "2026-05-01",
            "end_date": "2026-05-15",
            "cost_total": 5000000
        }
    """
    name: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Tên công việc (3-200 ký tự)"
    )
    parent_id: Optional[int] = Field(
        default=None,
        description="ID task cha (tùy chọn, dùng cho WBS tree)"
    )
    mo: float = Field(
        ...,
        ge=0.5,
        description="PERT Optimistic - thời gian tối ưu (ngày, ≥0.5)"
    )
    ml: float = Field(
        ...,
        ge=0.5,
        description="PERT Most Likely - thời gian có khả năng nhất (ngày, ≥0.5)"
    )
    mp: float = Field(
        ...,
        ge=0.5,
        description="PERT Pessimistic - thời gian tối đa (ngày, ≥0.5)"
    )
    start_date: Optional[date] = Field(
        default=None,
        description="Ngày bắt đầu (Gantt Chart, tùy chọn)"
    )
    end_date: Optional[date] = Field(
        default=None,
        description="Ngày kết thúc dự kiến (Gantt Chart, tùy chọn)"
    )
    cost_total: float = Field(
        default=0,
        ge=0,
        description="Chi phí dự kiến (VND, ≥0, tùy chọn)"
    )


# ========== UPDATE REQUEST ==========
class TaskUpdate(BaseModel):
    """
    Schema để cập nhật task.
    Tất cả fields đều tùy chọn - chỉ cập nhật những field được gửi.
    
    Fields:
        - name (str): Tên công việc mới (tùy chọn)
        - status (str): Trạng thái (TODO, DOING, DONE) - tùy chọn
        - mo, ml, mp (float): PERT estimates mới (tùy chọn)
        - start_date (date): Ngày bắt đầu mới (tùy chọn)
        - end_date (date): Ngày kết thúc mới (tùy chọn)
        - cost_total (float): Chi phí mới (tùy chọn)
    
    Note: est (estimated duration) được tính tự động: (mo + 4*ml + mp) / 6
    
    Ví dụ:
        {
            "status": "DOING",
            "ml": 6,
            "cost_total": 5500000
        }
    """
    name: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=200,
        description="Tên công việc mới (tùy chọn)"
    )
    status: Optional[str] = Field(
        default=None,
        pattern="^(TODO|DOING|DONE)$",
        description="Trạng thái (TODO, DOING, DONE) - tùy chọn"
    )
    mo: Optional[float] = Field(
        default=None,
        ge=0.5,
        description="PERT Optimistic mới (tùy chọn)"
    )
    ml: Optional[float] = Field(
        default=None,
        ge=0.5,
        description="PERT Most Likely mới (tùy chọn)"
    )
    mp: Optional[float] = Field(
        default=None,
        ge=0.5,
        description="PERT Pessimistic mới (tùy chọn)"
    )
    start_date: Optional[date] = Field(
        default=None,
        description="Ngày bắt đầu mới (tùy chọn)"
    )
    end_date: Optional[date] = Field(
        default=None,
        description="Ngày kết thúc mới (tùy chọn)"
    )
    cost_total: Optional[float] = Field(
        default=None,
        ge=0,
        description="Chi phí mới (tùy chọn)"
    )


# ========== RESPONSE ==========
class TaskResponse(BaseModel):
    """
    Schema để trả về thông tin task cơ bản.
    
    Fields:
        - id (int): ID task
        - project_id (int): ID project
        - parent_id (int): ID task cha (null nếu là root)
        - name (str): Tên task
        - status (str): Trạng thái (TODO, DOING, DONE)
        - mo, ml, mp (float): PERT estimates
        - est (float): PERT Estimated duration (tính tự động)
        - start_date (date): Ngày bắt đầu
        - end_date (date): Ngày kết thúc
        - cost_total (float): Chi phí
        - created_at (datetime): Thời gian tạo
        - updated_at (datetime): Thời gian cập nhật
    """
    id: int = Field(..., description="ID task")
    project_id: int = Field(..., description="ID project")
    parent_id: Optional[int] = Field(..., description="ID task cha (null nếu root)")
    name: str = Field(..., description="Tên task")
    status: str = Field(..., description="Trạng thái (TODO, DOING, DONE)")
    mo: float = Field(..., description="PERT Optimistic (ngày)")
    ml: float = Field(..., description="PERT Most Likely (ngày)")
    mp: float = Field(..., description="PERT Pessimistic (ngày)")
    est: float = Field(..., description="Estimated duration = (mo + 4*ml + mp)/6")
    start_date: Optional[date] = Field(..., description="Ngày bắt đầu")
    end_date: Optional[date] = Field(..., description="Ngày kết thúc")
    cost_total: float = Field(..., description="Chi phí (VND)")
    created_at: datetime = Field(..., description="Thời gian tạo")
    updated_at: datetime = Field(..., description="Thời gian cập nhật")
    
    class Config:
        from_attributes = True


# ========== RESPONSE WITH SUBTASKS (WBS TREE) ==========
class TaskDetailResponse(TaskResponse):
    """
    Schema để trả về task kèm subtasks (WBS tree).
    
    Fields:
        - (tất cả fields của TaskResponse)
        - subtasks (list): Danh sách subtasks (recursive)
    
    Ví dụ:
        {
            "id": 1,
            "name": "Project Setup",
            "status": "DOING",
            "est": 5.33,
            "subtasks": [
                {
                    "id": 2,
                    "name": "Database Design",
                    "status": "DONE",
                    "subtasks": []
                }
            ]
        }
    """
    subtasks: list["TaskDetailResponse"] = Field(
        default_factory=list,
        description="Danh sách subtasks (WBS tree)"
    )


# ========== KANBAN RESPONSE (Group by Status) ==========
class TaskKanbanResponse(BaseModel):
    """
    Schema để trả về tasks grouped by status (Kanban Board).
    
    Fields:
        - todo (list): Tasks với status TODO
        - doing (list): Tasks với status DOING
        - done (list): Tasks với status DONE
    """
    todo: list[TaskResponse] = Field(default_factory=list, description="Tasks TODO")
    doing: list[TaskResponse] = Field(default_factory=list, description="Tasks DOING")
    done: list[TaskResponse] = Field(default_factory=list, description="Tasks DONE")


# ========== GANTT RESPONSE ==========
class TaskGanttResponse(BaseModel):
    """
    Schema để trả về tasks grouped by timeline (Gantt Chart).
    
    Fields:
        - id (int): ID task
        - name (str): Tên task
        - start_date (date): Ngày bắt đầu
        - end_date (date): Ngày kết thúc
        - status (str): Trạng thái
        - est (float): Thời gian ước tính
        - progress (float): % hoàn thành (0-100)
    """
    id: int = Field(..., description="ID task")
    name: str = Field(..., description="Tên task")
    start_date: Optional[date] = Field(..., description="Ngày bắt đầu")
    end_date: Optional[date] = Field(..., description="Ngày kết thúc")
    status: str = Field(..., description="Trạng thái (TODO, DOING, DONE)")
    est: float = Field(..., description="Thời gian ước tính (ngày)")
    progress: int = Field(
        ...,
        ge=0,
        le=100,
        description="% hoàn thành (0-100, DONE=100)"
    )


# ========== TASK LIST RESPONSE ==========
class TaskListResponse(BaseModel):
    """
    Schema để trả về danh sách tasks.
    
    Fields:
        - total (int): Tổng số tasks
        - tasks (list): Danh sách tasks
    """
    total: int = Field(..., description="Tổng số tasks")
    tasks: list[TaskResponse] = Field(..., description="Danh sách tasks")


# Update forward reference cho recursive TaskDetailResponse
TaskDetailResponse.model_rebuild()
