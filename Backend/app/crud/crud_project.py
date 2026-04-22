"""
CRUD operations cho Project - Tương tác với database.
Sử dụng SQLAlchemy async ORM để thực hiện các thao tác database.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.model import Project, ProjectMember
from app.schemas.scm_project import ProjectCreate, ProjectUpdate


async def create_project(
    db: AsyncSession,
    project: ProjectCreate,
    user_id: int,
) -> Project:
    """
    Tạo project mới.
    Creator sẽ tự động trở thành PM (Project Manager) của project.
    
    Args:
        db: Database session
        project: ProjectCreate schema (project_code, name, description)
        user_id: ID của user tạo project (PM)
    
    Returns:
        Project: Object project mới được tạo
        
    Raises:
        IntegrityError: Nếu project_code đã tồn tại (duplicate)
    
    Logic:
        1. Tạo object Project từ schema
        2. Insert vào database
        3. Flush để có được project.id
        4. Tạo ProjectMember với role="PM" cho creator
        5. Commit transaction
        6. Refresh để lấy dữ liệu mới nhất từ database
    """
    try:
        # Tạo object project
        db_project = Project(
            project_code=project.project_code,
            name=project.name,
            description=project.description,
        )
        
        # Thêm vào session
        db.add(db_project)
        
        # Flush để lấy project.id
        await db.flush()
        
        # Tạo ProjectMember - user_id là PM của project này
        db_project_member = ProjectMember(
            user_id=user_id,
            project_id=db_project.id,
            role="PM",  # Enum value
        )
        db.add(db_project_member)
        
        # Commit transaction
        await db.commit()
        
        # Refresh để lấy dữ liệu mới nhất (timestamps, v.v.)
        await db.refresh(db_project)
        
        return db_project
        
    except IntegrityError as e:
        # Rollback nếu lỗi (project_code duplicate)
        await db.rollback()
        # Re-raise để router handle
        raise e


async def get_project_by_id(
    db: AsyncSession,
    project_id: int,
) -> Project | None:
    """
    Lấy project theo ID.
    
    Args:
        db: Database session
        project_id: ID project
    
    Returns:
        Project | None: Object project hoặc None nếu không tìm thấy
    """
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_project_by_code(
    db: AsyncSession,
    project_code: str,
) -> Project | None:
    """
    Lấy project theo mã project.
    Dùng để join project.
    
    Args:
        db: Database session
        project_code: Mã project
    
    Returns:
        Project | None: Object project hoặc None nếu không tìm thấy
    """
    stmt = select(Project).where(Project.project_code == project_code)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_user_projects(
    db: AsyncSession,
    user_id: int,
) -> list[Project]:
    """
    Lấy danh sách tất cả projects của user (user là member).
    
    Args:
        db: Database session
        user_id: ID user
    
    Returns:
        list[Project]: Danh sách projects mà user là member
    
    Logic:
        1. Join Project với ProjectMember
        2. Filter ProjectMember.user_id == user_id
        3. Order by created_at descending (project mới nhất trước)
    """
    stmt = (
        select(Project)
        .join(ProjectMember)
        .where(ProjectMember.user_id == user_id)
        .order_by(Project.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_project_members_count(
    db: AsyncSession,
    project_id: int,
) -> int:
    """
    Lấy số lượng thành viên của project.
    
    Args:
        db: Database session
        project_id: ID project
    
    Returns:
        int: Số lượng thành viên
    """
    stmt = (
        select(func.count(ProjectMember.id))
        .where(ProjectMember.project_id == project_id)
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def update_project(
    db: AsyncSession,
    project_id: int,
    project_update: ProjectUpdate,
    user_id: int,
) -> Project | None:
    """
    Cập nhật project.
    Chỉ PM (creator) của project mới có quyền cập nhật.
    
    Args:
        db: Database session
        project_id: ID project
        project_update: ProjectUpdate schema (name, description - cả 2 tùy chọn)
        user_id: ID user thực hiện update (phải là PM)
    
    Returns:
        Project | None: Project sau cập nhật, hoặc None nếu không tìm thấy
        
    Logic:
        1. Kiểm tra user có quyền update không (role = PM)
        2. Cập nhật những field được gửi (skip None values)
        3. Commit
        4. Refresh
    """
    # Kiểm tra quyền - user phải là PM
    pm_stmt = (
        select(ProjectMember)
        .where(
            (ProjectMember.project_id == project_id)
            & (ProjectMember.user_id == user_id)
            & (ProjectMember.role == "PM")
        )
    )
    pm_result = await db.execute(pm_stmt)
    is_pm = pm_result.scalar_one_or_none() is not None
    
    if not is_pm:
        # Không có quyền
        return None
    
    # Lấy project
    project = await get_project_by_id(db, project_id)
    
    if not project:
        return None
    
    # Cập nhật những field được gửi
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(project, field, value)
    
    # Commit
    await db.commit()
    
    # Refresh
    await db.refresh(project)
    
    return project


async def delete_project(
    db: AsyncSession,
    project_id: int,
    user_id: int,
) -> bool:
    """
    Xóa project.
    Chỉ PM (creator) của project mới có quyền xóa.
    
    Args:
        db: Database session
        project_id: ID project
        user_id: ID user thực hiện delete (phải là PM)
    
    Returns:
        bool: True nếu xóa thành công, False nếu không có quyền hoặc project không tìm thấy
        
    Logic:
        1. Kiểm tra user có quyền delete không (role = PM)
        2. Xóa project (cascade delete sẽ xóa ProjectMembers)
        3. Commit
    """
    # Kiểm tra quyền - user phải là PM
    pm_stmt = (
        select(ProjectMember)
        .where(
            (ProjectMember.project_id == project_id)
            & (ProjectMember.user_id == user_id)
            & (ProjectMember.role == "PM")
        )
    )
    pm_result = await db.execute(pm_stmt)
    is_pm = pm_result.scalar_one_or_none() is not None
    
    if not is_pm:
        # Không có quyền
        return False
    
    # Lấy project
    project = await get_project_by_id(db, project_id)
    
    if not project:
        return False
    
    # Xóa project (cascade delete sẽ xóa ProjectMembers liên quan)
    await db.delete(project)
    
    # Commit
    await db.commit()
    
    return True

from sqlalchemy.orm import joinedload

# 1. Lấy danh sách thành viên dự án
async def get_project_members(db: AsyncSession, project_id: int) -> list[ProjectMember]:
    stmt = (
        select(ProjectMember)
        .options(joinedload(ProjectMember.user)) # Móc luôn bảng User sang
        .where(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.role.asc()) # PM hiện lên đầu, Member hiện sau
    )
    result = await db.execute(stmt)
    return result.scalars().all()

# 2. Đổi quyền thành viên (Set Role)
async def change_member_role(db: AsyncSession, project_id: int, target_user_id: int, new_role: str) -> ProjectMember | None:
    # BƯỚC 1: Lấy member ra (KHÔNG CẦN joinedload ở bước này vì chỉ để update)
    stmt = select(ProjectMember).where(
        (ProjectMember.project_id == project_id) & (ProjectMember.user_id == target_user_id)
    )
    member = (await db.execute(stmt)).scalar_one_or_none()
    
    if member:
        # BƯỚC 2: Cập nhật role an toàn bằng Enum
        # Thường SQLAlchemy Enum thích nhận giá trị Enum chuẩn hơn là chuỗi thuần
        member.role = RoleEnum.PM if new_role == "PM" else RoleEnum.MEMBER
        
        await db.commit()
        
        # BƯỚC 3: QUAN TRỌNG NHẤT
        # Bắt buộc phải query lại từ đầu KÈM THEO joinedload để trả về Router.
        # Tuyệt đối không dùng `await db.refresh(member)` ở đây.
        refresh_stmt = (
            select(ProjectMember)
            .options(joinedload(ProjectMember.user))
            .where(ProjectMember.id == member.id)
        )
        refreshed_member = (await db.execute(refresh_stmt)).scalar_one_or_none()
        
        return refreshed_member
    
    return None

# 3. Kích thành viên khỏi dự án
async def remove_project_member(db: AsyncSession, project_id: int, target_user_id: int) -> bool:
    stmt = select(ProjectMember).where(
        (ProjectMember.project_id == project_id) & (ProjectMember.user_id == target_user_id)
    )
    member = (await db.execute(stmt)).scalar_one_or_none()
    
    if member:
        await db.delete(member)
        await db.commit()
        return True
        
    return False