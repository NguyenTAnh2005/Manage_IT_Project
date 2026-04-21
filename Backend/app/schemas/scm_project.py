"""
Pydantic schemas cho Project - Request/Response models.
Dùng để validate dữ liệu input và format dữ liệu output.
"""

from datetime import datetime
from pydantic import BaseModel, Field


# ========== CREATE REQUEST ==========
class ProjectCreate(BaseModel):
    """
    Schema để tạo project mới.
    
    Fields:
        - project_code (str): Mã project - dùng để join project (unique, 6-10 ký tự)
        - name (str): Tên project (min 3, max 100 ký tự)
        - description (str): Mô tả project (min 5, max 500 ký tự, tùy chọn)
    
    Ví dụ:
        {
            "project_code": "PRJMNG001",
            "name": "Quản Lý Dự Án IT",
            "description": "Dự án quản lý dự án CNTT sử dụng FastAPI"
        }
    """
    project_code: str = Field(
        ...,
        min_length=6,
        max_length=10,
        pattern="^[A-Z0-9_]+$",
        description="Mã project (6-10 ký tự, A-Z, 0-9, _)"
    )
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Tên project (3-100 ký tự)"
    )
    description: str = Field(
        default="",
        min_length=0,
        max_length=500,
        description="Mô tả project (0-500 ký tự, tùy chọn)"
    )


# ========== UPDATE REQUEST ==========
class ProjectUpdate(BaseModel):
    """
    Schema để cập nhật project.
    Tất cả fields đều tùy chọn - chỉ cập nhật những field được gửi.
    
    Fields:
        - name (str): Tên project mới (tùy chọn)
        - description (str): Mô tả mới (tùy chọn)
    
    Note: project_code không thể sửa sau khi tạo (dùng để join project)
    
    Ví dụ:
        {
            "name": "Quản Lý Dự Án IT - Phiên Bản 2.0",
            "description": "Cập nhật mô tả mới"
        }
    """
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
        description="Tên project mới (tùy chọn)"
    )
    description: str | None = Field(
        default=None,
        min_length=0,
        max_length=500,
        description="Mô tả mới (tùy chọn)"
    )


# ========== RESPONSE ==========
class ProjectResponse(BaseModel):
    id: int = Field(..., description="ID project")
    project_code: str = Field(..., description="Mã project (unique)")
    name: str = Field(..., description="Tên project")
    description: str | None = Field(default=None, description="Mô tả project") 
    created_at: datetime = Field(..., description="Thời gian tạo")
    updated_at: datetime = Field(..., description="Thời gian cập nhật cuối")
    
    class Config:
        from_attributes = True


# ========== PROJECT WITH MEMBERS COUNT ==========
class ProjectWithMembersCount(ProjectResponse):
    """
    Schema project kèm số lượng thành viên.
    Dùng cho list projects endpoint.
    
    Fields:
        - (tất cả fields của ProjectResponse)
        - members_count (int): Số lượng thành viên trong project
    
    Ví dụ:
        {
            "id": 1,
            "project_code": "PRJMNG001",
            "name": "Quản Lý Dự Án IT",
            "description": "...",
            "created_at": "2026-04-16T10:30:00",
            "updated_at": "2026-04-16T10:30:00",
            "members_count": 5
        }
    """
    members_count: int = Field(default=0, description="Số lượng thành viên")


# ========== JOIN PROJECT REQUEST ==========
class ProjectJoinRequest(BaseModel):
    """
    Schema để join project bằng project_code.
    
    Fields:
        - project_code (str): Mã project để join
    
    Ví dụ:
        {
            "project_code": "PRJMNG001"
        }
    """
    project_code: str = Field(
        ...,
        min_length=6,
        max_length=10,
        description="Mã project để join"
    )


# ========== PROJECT LIST RESPONSE ==========
class ProjectListResponse(BaseModel):
    """
    Schema để trả về danh sách projects.
    
    Fields:
        - total (int): Tổng số project
        - projects (list): Danh sách projects
    
    Ví dụ:
        {
            "total": 2,
            "projects": [
                {
                    "id": 1,
                    "project_code": "PRJMNG001",
                    "name": "Quản Lý Dự Án IT",
                    ...
                }
            ]
        }
    """
    total: int = Field(..., description="Tổng số project")
    projects: list[ProjectWithMembersCount] = Field(..., description="Danh sách projects")
