from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.scm_user import UserResponse

class TaskCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    parent_id: Optional[int] = Field(default=None)
    owner_id: Optional[int] = Field(default=None)
    mo: Optional[float] = Field(default=None)
    ml: Optional[float] = Field(default=None)
    mp: Optional[float] = Field(default=None)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    cost_total: Optional[float] = Field(default=0, ge=0)

class TaskUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None, pattern="^(TODO|DOING|DONE)$")
    owner_id: Optional[int] = Field(default=None)
    parent_id: Optional[int] = Field(default=None)
    mo: Optional[float] = Field(default=None)
    ml: Optional[float] = Field(default=None)
    mp: Optional[float] = Field(default=None)
    cost_total: Optional[float] = Field(default=None)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)

class TaskResponse(BaseModel):
    id: int
    project_id: int
    parent_id: Optional[int]
    owner_id: Optional[int]
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
    total: int
    tasks: list[TaskResponse]

class TaskKanbanResponse(BaseModel):
    todo: list[TaskResponse]
    doing: list[TaskResponse]
    done: list[TaskResponse]

class TaskGanttResponse(BaseModel):
    id: int
    name: str
    start_date: Optional[date]
    end_date: Optional[date]
    status: str
    est: float
    progress: int