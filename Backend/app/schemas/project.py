"""
Schemas (Request/Response Models) cho Project
- Được dùng để validate input từ client
- Được dùng để format output response
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# ===== REQUEST SCHEMAS =====

class ProjectCreate(BaseModel):
    """
    Schema cho API tạo project mới
    Client phải gửi: project_code, name, description (optional)
    """
    project_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Kiểm tra tên project:
        - Tối thiểu 1 ký tự
        - Tối đa 255 ký tự
        - Không được toàn khoảng trắng
        """
        v = v.strip()
        
        if not v:
            raise ValueError('Tên dự án không được để trống')
        
        if len(v) < 1:
            raise ValueError('Tên dự án tối thiểu 1 ký tự')
        
        if len(v) > 255:
            raise ValueError('Tên dự án tối đa 255 ký tự')
        
        return v
    
    @field_validator('project_code')
    @classmethod
    def validate_project_code(cls, v: str) -> str:
        """
        Kiểm tra mã dự án:
        - Tối thiểu 1 ký tự
        - Tối đa 50 ký tự
        - Không được toàn khoảng trắng
        """
        v = v.strip()
        
        if not v:
            raise ValueError('Mã dự án không được để trống')
        
        if len(v) < 1:
            raise ValueError('Mã dự án tối thiểu 1 ký tự')
        
        if len(v) > 50:
            raise ValueError('Mã dự án tối đa 50 ký tự')
        
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """
        Kiểm tra mô tả:
        - Tối đa 1000 ký tự
        """
        if v is None:
            return v
        
        if len(v) > 1000:
            raise ValueError('Mô tả tối đa 1000 ký tự')
        
        return v


class ProjectUpdate(BaseModel):
    """
    Schema cho API update project
    Client có thể gửi: name, description (cả hai optional)
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """
        Kiểm tra tên project:
        - Tối thiểu 1 ký tự
        - Tối đa 255 ký tự
        - Không được toàn khoảng trắng
        """
        if v is None:
            return v
        
        v = v.strip()
        
        if not v:
            raise ValueError('Tên dự án không được để trống')
        
        if len(v) < 1:
            raise ValueError('Tên dự án tối thiểu 1 ký tự')
        
        if len(v) > 255:
            raise ValueError('Tên dự án tối đa 255 ký tự')
        
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """
        Kiểm tra mô tả:
        - Tối đa 1000 ký tự
        """
        if v is None:
            return v
        
        if len(v) > 1000:
            raise ValueError('Mô tả tối đa 1000 ký tự')
        
        return v


# ===== RESPONSE SCHEMAS =====

class ProjectResponse(BaseModel):
    """
    Schema cho Project response (không bao gồm tasks, members chi tiết)
    Được dùng khi return project info
    """
    id: int
    project_code: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Cho phép create instance từ SQLAlchemy model


class ProjectDetailResponse(BaseModel):
    """
    Schema chi tiết project (khi get project by id)
    Có thể bao gồm thêm thông tin members, tasks, etc.
    """
    id: int
    project_code: str
    name: str
    description: Optional[str] = None
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
