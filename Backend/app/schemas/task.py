"""
Schemas (Request/Response Models) cho Task
- Được dùng để validate input từ client
- Được dùng để format output response
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# ===== ENUMS CHO VALIDATION =====

class TaskStatusEnum(str):
    """Giá trị trạng thái công việc"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TaskPriorityEnum(str):
    """Giá trị mức độ ưu tiên công việc"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ===== REQUEST SCHEMAS =====

class TaskCreate(BaseModel):
    """
    Schema cho API tạo công việc mới
    Client phải gửi: title, description (optional), status, priority, assigned_to (optional)
    """
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: str = Field(default="pending")  # pending, in_progress, completed, blocked
    priority: str = Field(default="medium")  # low, medium, high, critical
    assigned_to: Optional[int] = Field(None)
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """
        Kiểm tra tiêu đề công việc:
        - Tối thiểu 1 ký tự
        - Tối đa 255 ký tự
        - Không được toàn khoảng trắng
        """
        v = v.strip()
        
        if not v:
            raise ValueError('Tiêu đề công việc không được để trống')
        
        if len(v) < 1:
            raise ValueError('Tiêu đề công việc tối thiểu 1 ký tự')
        
        if len(v) > 255:
            raise ValueError('Tiêu đề công việc tối đa 255 ký tự')
        
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """
        Kiểm tra mô tả:
        - Tối đa 2000 ký tự
        """
        if v is None:
            return v
        
        if len(v) > 2000:
            raise ValueError('Mô tả công việc tối đa 2000 ký tự')
        
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """
        Kiểm tra trạng thái:
        - Phải là một trong: pending, in_progress, completed, blocked
        """
        valid_statuses = ["pending", "in_progress", "completed", "blocked"]
        if v not in valid_statuses:
            raise ValueError(f'Trạng thái phải là một trong: {", ".join(valid_statuses)}')
        return v
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """
        Kiểm tra mức độ ưu tiên:
        - Phải là một trong: low, medium, high, critical
        """
        valid_priorities = ["low", "medium", "high", "critical"]
        if v not in valid_priorities:
            raise ValueError(f'Mức độ ưu tiên phải là một trong: {", ".join(valid_priorities)}')
        return v


class TaskUpdate(BaseModel):
    """
    Schema cho API sửa công việc
    Client có thể gửi: title, description, status, priority, assigned_to (cả hai optional)
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """
        Kiểm tra tiêu đề công việc:
        - Tối thiểu 1 ký tự
        - Tối đa 255 ký tự
        - Không được toàn khoảng trắng
        """
        if v is None:
            return v
        
        v = v.strip()
        
        if not v:
            raise ValueError('Tiêu đề công việc không được để trống')
        
        if len(v) < 1:
            raise ValueError('Tiêu đề công việc tối thiểu 1 ký tự')
        
        if len(v) > 255:
            raise ValueError('Tiêu đề công việc tối đa 255 ký tự')
        
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """
        Kiểm tra mô tả:
        - Tối đa 2000 ký tự
        """
        if v is None:
            return v
        
        if len(v) > 2000:
            raise ValueError('Mô tả công việc tối đa 2000 ký tự')
        
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """
        Kiểm tra trạng thái:
        - Phải là một trong: pending, in_progress, completed, blocked
        """
        if v is None:
            return v
        
        valid_statuses = ["pending", "in_progress", "completed", "blocked"]
        if v not in valid_statuses:
            raise ValueError(f'Trạng thái phải là một trong: {", ".join(valid_statuses)}')
        return v
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str | None) -> str | None:
        """
        Kiểm tra mức độ ưu tiên:
        - Phải là một trong: low, medium, high, critical
        """
        if v is None:
            return v
        
        valid_priorities = ["low", "medium", "high", "critical"]
        if v not in valid_priorities:
            raise ValueError(f'Mức độ ưu tiên phải là một trong: {", ".join(valid_priorities)}')
        return v


# ===== RESPONSE SCHEMAS =====

class TaskResponse(BaseModel):
    """
    Schema cho task response (không bao gồm chi tiết mở rộng)
    Được dùng khi return thông tin công việc
    """
    id: int
    project_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    created_by: Optional[int] = None
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Cho phép tạo instance từ SQLAlchemy model


class TaskDetailResponse(BaseModel):
    """
    Schema chi tiết công việc (khi get task by id)
    """
    id: int
    project_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    created_by: Optional[int] = None
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== ERROR RESPONSE SCHEMAS =====

class ErrorResponse(BaseModel):
    """
    Schema cho error response
    """
    detail: str
    status_code: int
