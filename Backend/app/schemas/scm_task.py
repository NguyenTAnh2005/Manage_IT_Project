"""Task schemas for WBS, PERT, Cost, Kanban, and Gantt modules."""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.scm_user import UserResponse


class TaskCreate(BaseModel):
    """Schema for creating a new task (WBS)."""
    name: str = Field(..., min_length=3, max_length=200, description="Tên công việc")
    parent_id: Optional[int] = Field(default=None, description="ID task cha (nếu là task con)")
    owner_id: Optional[int] = Field(default=None, description="ID người phụ trách")
    mo: Optional[float] = Field(default=None, ge=0, description="Lạc quan (Optimistic) - PERT")
    ml: Optional[float] = Field(default=None, ge=0, description="Khả dĩ (Most Likely) - PERT")
    mp: Optional[float] = Field(default=None, ge=0, description="Bi quan (Pessimistic) - PERT")
    start_date: Optional[date] = Field(default=None, description="Ngày bắt đầu")
    end_date: Optional[date] = Field(default=None, description="Ngày kết thúc")
    cost_total: Optional[float] = Field(default=0, ge=0, description="Tổng chi phí")


class TaskUpdate(BaseModel):
    """Schema for updating task. All fields are optional."""
    name: Optional[str] = Field(default=None, min_length=3, max_length=200, description="Tên công việc mới")
    status: Optional[str] = Field(default=None, pattern="^(TODO|DOING|DONE)$", description="Trạng thái task")
    owner_id: Optional[int] = Field(default=None, description="ID người phụ trách")
    parent_id: Optional[int] = Field(default=None, description="ID task cha")
    mo: Optional[float] = Field(default=None, ge=0, description="Lạc quan (O)")
    ml: Optional[float] = Field(default=None, ge=0, description="Khả dĩ (M)")
    mp: Optional[float] = Field(default=None, ge=0, description="Bi quan (P)")
    cost_total: Optional[float] = Field(default=None, ge=0, description="Chi phí")
    start_date: Optional[date] = Field(default=None, description="Ngày bắt đầu")
    end_date: Optional[date] = Field(default=None, description="Ngày kết thúc")


class TaskResponse(BaseModel):
    """Complete task response with owner info."""
    id: int
    project_id: int
    parent_id: Optional[int] = None
    owner_id: Optional[int] = None
    owner: Optional[UserResponse] = None
    name: str
    status: str
    mo: Optional[float] = None
    ml: Optional[float] = None
    mp: Optional[float] = None
    est: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    cost_total: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Response for listing tasks (WBS)."""
    total: int = Field(..., description="Tổng số task")
    tasks: list[TaskResponse] = Field(..., description="Danh sách tasks")


class TaskKanbanResponse(BaseModel):
    """Response for Kanban board with tasks grouped by status."""
    todo: list[TaskResponse] = Field(..., description="Tasks in TODO status")
    doing: list[TaskResponse] = Field(..., description="Tasks in DOING status")
    done: list[TaskResponse] = Field(..., description="Tasks in DONE status")


class TaskGanttResponse(BaseModel):
    """Simplified task response for Gantt chart."""
    id: int
    name: str
    start_date: Optional[date]
    end_date: Optional[date]
    status: str
    est: float
    progress: int