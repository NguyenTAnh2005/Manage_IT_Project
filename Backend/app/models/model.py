# ========================================
# SQLALCHEMY MODELS - DATABASE SCHEMA
# ========================================
# ORM Models để SQLAlchemy tự động tạo/quản lý database tables
# Async support: Dùng sqlalchemy 2.0+ với asyncpg

from datetime import datetime
from typing import Optional
import enum
from sqlalchemy import (
    Column, DateTime, Integer, 
    String, ForeignKey, Float, Date, Enum, Text
)
from sqlalchemy.orm import relationship

# Import Base từ database.py (không tạo Base mới!)
from app.core.database import Base


# ========================================
# ENUM - Kiểu dữ liệu cho Role và Status
# ========================================
class RoleEnum(str, enum.Enum):
    """Vai trò trong dự án"""
    PM = "PM"  # Project Manager (Trưởng dự án)
    MEMBER = "MEMBER"  # Team Member (Thành viên)


class TaskStatusEnum(str, enum.Enum):
    """Trạng thái công việc - Dùng cho Kanban Board"""
    TODO = "TODO"  # Chưa làm
    DOING = "DOING"  # Đang làm
    DONE = "DONE"  # Hoàn thành


# ========================================
# MODEL 1: USERS (Quản lý người dùng)
# ========================================
class User(Base):
    """
    Bảng lưu trữ thông tin tài khoản người dùng.
    
    Columns:
    - id: Khóa chính, auto-increment
    - email: Email duy nhất (unique)
    - password_hash: Mật khẩu đã mã hóa (không lưu plain text!)
    - full_name: Họ và tên
    - created_at: Thời gian tạo tài khoản
    - updated_at: Thời gian cập nhật gần nhất
    
    Relationships:
    - project_memberships: List các dự án user tham gia
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # ===== RELATIONSHIPS =====
    project_memberships = relationship(
        "ProjectMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, full_name={self.full_name})>"


# ========================================
# MODEL 2: PROJECTS (Quản lý dự án)
# ========================================
class Project(Base):
    """
    Bảng lưu trữ thông tin dự án.
    
    Columns:
    - id: Khóa chính, auto-increment
    - project_code: Mã dự án duy nhất
    - name: Tên dự án
    - description: Mô tả chi tiết về dự án
    - created_at: Thời gian tạo dự án
    - updated_at: Thời gian cập nhật gần nhất
    
    Relationships:
    - members: List các thành viên (User) qua ProjectMember
    - tasks: List các công việc trong dự án
    """
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # ===== RELATIONSHIPS =====
    members = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
        foreign_keys="Task.project_id"
    )
    
    def __repr__(self):
        return f"<Project(id={self.id}, code={self.project_code}, name={self.name})>"


# ========================================
# MODEL 3: PROJECT_MEMBERS (Phân quyền)
# ========================================
class ProjectMember(Base):
    """
    Bảng trung gian (Junction Table) quản lý:
    - Ai (user_id) tham gia dự án nào (project_id)
    - Vai trò của người đó (role: PM hoặc MEMBER)
    
    Columns:
    - id: Khóa chính, auto-increment
    - user_id: Khóa ngoại trỏ về USERS
    - project_id: Khóa ngoại trỏ về PROJECTS
    - role: Vai trò (PM = Trưởng dự án, MEMBER = Thành viên)
    - joined_at: Thời gian tham gia dự án
    """
    
    __tablename__ = "project_members"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.MEMBER, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # ===== RELATIONSHIPS =====
    user = relationship("User", back_populates="project_memberships")
    project = relationship("Project", back_populates="members")
    
    def __repr__(self):
        return f"<ProjectMember(user_id={self.user_id}, project_id={self.project_id}, role={self.role})>"


# ========================================
# MODEL 4: TASKS (Quản lý công việc - Core)
# ========================================
class Task(Base):
    """
    Bảng "siêu bảng" quản lý tất cả công việc.
    Là lõi của hệ thống: WBS, Gantt, Kanban, PERT, Chi phí đều phụ thuộc Task.
    
    Columns:
    - id: Khóa chính, auto-increment
    - project_id: Khóa ngoại trỏ về PROJECTS
    - parent_id: Self-referencing để tạo cấu trúc Cha-Con (WBS)
    - name: Tên công việc
    - status: Trạng thái (TODO, DOING, DONE) - Dùng cho Kanban
    - start_date: Ngày bắt đầu - Dùng cho Gantt Chart
    - end_date: Ngày kết thúc - Dùng cho Gantt Chart
    - mo, ml, mp: Ba chỉ số PERT (Lạc quan, Khả dĩ, Bi quan)
    - est: Thời gian ước lượng EST = (MO + 4*ML + MP) / 6
    - cost_total: Tổng chi phí ước lượng
    - created_at: Thời gian tạo công việc
    - updated_at: Thời gian cập nhật gần nhất
    
    Relationships:
    - project: Dự án cha
    - parent: Task cha (nếu có)
    - subtasks: List các Task con
    """
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    # Self-referencing: Để tạo cấu trúc cây WBS (Cha - Con - Cháu)
    
    name = Column(String(255), nullable=False)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.TODO, nullable=False)
    
    # ===== DATES (Dùng cho Gantt Chart) =====
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    # ===== PERT ESTIMATION (Ước lượng thời gian chuyên gia) =====
    mo = Column(Float, nullable=True)  # Most Optimistic (Lạc quan nhất)
    ml = Column(Float, nullable=True)  # Most Likely (Khả dĩ nhất)
    mp = Column(Float, nullable=True)  # Most Pessimistic (Bi quan nhất)
    # Công thức: EST = (MO + 4*ML + MP) / 6
    
    est = Column(Float, nullable=True)  # Estimated Time (đã tính)
    
    # ===== COST (Chi phí) =====
    cost_total = Column(Float, nullable=True, default=0.0)
    
    # ===== AUDIT =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # ===== RELATIONSHIPS =====
    project = relationship("Project", back_populates="tasks", foreign_keys=[project_id])
    
    # Self-referencing relationship
    subtasks = relationship(
        "Task",
        remote_side=[id],
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_id],
        single_parent=True  # Mỗi Task con chỉ có 1 Task cha
    )
    
    parent = relationship(
        "Task",
        remote_side=[parent_id],
        back_populates="subtasks"
    )
    
    def __repr__(self):
        return f"<Task(id={self.id}, name={self.name}, status={self.status}, est={self.est})>"
    
    def calculate_est(self) -> Optional[float]:
        """
        Tính EST theo công thức PERT.
        EST = (MO + 4*ML + MP) / 6
        
        Returns:
            float: Thời gian ước lượng
            None: Nếu thiếu 1 trong 3 giá trị MO, ML, MP
        """
        if self.mo is not None and self.ml is not None and self.mp is not None:
            return (self.mo + 4 * self.ml + self.mp) / 6
        return None
