"""
🌱 SEED DATA SCRIPT - Dữ liệu mẫu cho Backend Testing

Tệp này tạo dữ liệu mẫu toàn bộ hệ thống:
- 3 người dùng (users)
- 2 dự án (projects)
- Phân công thành viên dự án (project_members)
- Nhiều công việc phân cấp (tasks) - WBS Tree Structure
- PERT estimates (mo, ml, mp) - cho tính toán
- Dates & Costs - cho Gantt & Cost Analysis

Chạy: python seed_data.py
"""

import asyncio
from datetime import datetime, timedelta
from app.core.database import AsyncSessionLocal, Base, engine
from app.models.model import User, Project, ProjectMember, Task, RoleEnum, TaskStatusEnum
from app.core.security import hash_password


async def seed_database():
    """
    Tạo bảng (nếu chưa tồn tại) và insert dữ liệu mẫu
    """
    print("🌱 Bắt đầu seed data...")

    # ==========================================
    # 1. TẠO BẢNG (Create tables if not exists)
    # ==========================================
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created/verified")

    # ==========================================
    # 2. TẠO SESSION VÀ CLEAR DỮ LIỆU CŨ (Optional)
    # ==========================================
    async with AsyncSessionLocal() as session:
        # Xóa dữ liệu cũ (tùy chọn - uncomment để xóa)
        # await session.query(Task).delete()
        # await session.query(ProjectMember).delete()
        # await session.query(Project).delete()
        # await session.query(User).delete()
        # await session.commit()
        # print("🗑️ Old data cleared")

        # ==========================================
        # 3. TẠO NGƯỜI DÙNG (USERS)
        # ==========================================
        print("\n📝 Creating users...")

        users = [
            User(
                email="tuananh@example.com",
                password_hash=hash_password("Password123!"),
                full_name="Nguyễn Tuấn Anh",
            ),
            User(
                email="hoangminh@example.com",
                password_hash=hash_password("Password123!"),
                full_name="Hoàng Minh Đức",
            ),
            User(
                email="thule@example.com",
                password_hash=hash_password("Password123!"),
                full_name="Thủ Lê Phương",
            ),
        ]

        session.add_all(users)
        await session.flush()  # Flush để lấy ID
        print(f"✅ Created {len(users)} users")

        user_tuananh = users[0]
        user_hoangminh = users[1]
        user_thule = users[2]

        # ==========================================
        # 4. TẠO DỰ ÁN (PROJECTS)
        # ==========================================
        print("\n📋 Creating projects...")

        projects = [
            Project(
                project_code="QTDA001",
                name="Quản Lý Dự Án CNTT",
                description="Hệ thống quản lý dự án công nghệ thông tin",
            ),
            Project(
                project_code="WEBNEW",
                name="Website E-Commerce",
                description="Phát triển website bán hàng trực tuyến",
            ),
        ]

        session.add_all(projects)
        await session.flush()
        print(f"✅ Created {len(projects)} projects")

        project1 = projects[0]
        project2 = projects[1]

        # ==========================================
        # 5. PHÂN CÔNG DỰ ÁN (PROJECT MEMBERS)
        # ==========================================
        print("\n👥 Creating project members...")

        project_members = [
            # Project 1: QTDA001
            ProjectMember(
                project_id=project1.id,
                user_id=user_tuananh.id,
                role=RoleEnum.PM,  # Trưởng dự án
            ),
            ProjectMember(
                project_id=project1.id,
                user_id=user_hoangminh.id,
                role=RoleEnum.MEMBER,  # Thành viên
            ),
            ProjectMember(
                project_id=project1.id,
                user_id=user_thule.id,
                role=RoleEnum.MEMBER,
            ),
            # Project 2: WEBNEW
            ProjectMember(
                project_id=project2.id,
                user_id=user_hoangminh.id,
                role=RoleEnum.PM,
            ),
            ProjectMember(
                project_id=project2.id,
                user_id=user_thule.id,
                role=RoleEnum.MEMBER,
            ),
        ]

        session.add_all(project_members)
        await session.flush()
        print(f"✅ Created {len(project_members)} project memberships")

        # ==========================================
        # 6. TẠO CÔNG VIỆC (TASKS) - WBS TREE
        # ==========================================
        print("\n📌 Creating tasks with hierarchical structure...")

        # --- PROJECT 1: QTDA001 ---
        # Level 1 (Parent tasks)
        task_1_1 = Task(
            project_id=project1.id,
            name="Thiết kế và kiến trúc hệ thống",
            status=TaskStatusEnum.DOING,
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=30)).date(),
            mo=10,
            ml=15,
            mp=25,
            cost_total=5000,
        )

        task_1_2 = Task(
            project_id=project1.id,
            name="Phát triển Backend",
            status=TaskStatusEnum.TODO,
            start_date=(datetime.now() + timedelta(days=30)).date(),
            end_date=(datetime.now() + timedelta(days=70)).date(),
            mo=20,
            ml=30,
            mp=50,
            cost_total=10000,
        )

        task_1_3 = Task(
            project_id=project1.id,
            name="Phát triển Frontend",
            status=TaskStatusEnum.TODO,
            start_date=(datetime.now() + timedelta(days=40)).date(),
            end_date=(datetime.now() + timedelta(days=80)).date(),
            mo=20,
            ml=25,
            mp=40,
            cost_total=8000,
        )

        task_1_4 = Task(
            project_id=project1.id,
            name="Testing & QA",
            status=TaskStatusEnum.TODO,
            start_date=(datetime.now() + timedelta(days=80)).date(),
            end_date=(datetime.now() + timedelta(days=100)).date(),
            mo=10,
            ml=15,
            mp=20,
            cost_total=3000,
        )

        # Level 2 (Subtasks của task_1_1)
        task_1_1_1 = Task(
            project_id=project1.id,
            parent_id=None,  # Will be set after flush
            name="Phân tích yêu cầu chức năng",
            status=TaskStatusEnum.DONE,
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=10)).date(),
            mo=3,
            ml=5,
            mp=8,
            cost_total=1000,
        )

        task_1_1_2 = Task(
            project_id=project1.id,
            parent_id=None,  # Will be set after flush
            name="Thiết kế Database",
            status=TaskStatusEnum.DOING,
            start_date=(datetime.now() + timedelta(days=8)).date(),
            end_date=(datetime.now() + timedelta(days=18)).date(),
            mo=4,
            ml=6,
            mp=10,
            cost_total=1500,
        )

        task_1_1_3 = Task(
            project_id=project1.id,
            parent_id=None,  # Will be set after flush
            name="Thiết kế API Endpoints",
            status=TaskStatusEnum.TODO,
            start_date=(datetime.now() + timedelta(days=15)).date(),
            end_date=(datetime.now() + timedelta(days=30)).date(),
            mo=3,
            ml=5,
            mp=7,
            cost_total=1500,
        )

        # Level 2 (Subtasks của task_1_2)
        task_1_2_1 = Task(
            project_id=project1.id,
            parent_id=None,  # Will be set after flush
            name="Cài đặt FastAPI & Dependencies",
            status=TaskStatusEnum.TODO,
            start_date=(datetime.now() + timedelta(days=30)).date(),
            end_date=(datetime.now() + timedelta(days=35)).date(),
            mo=2,
            ml=3,
            mp=5,
            cost_total=500,
        )

        task_1_2_2 = Task(
            project_id=project1.id,
            parent_id=None,  # Will be set after flush
            name="Phát triển API Authentication",
            status=TaskStatusEnum.TODO,
            start_date=(datetime.now() + timedelta(days=35)).date(),
            end_date=(datetime.now() + timedelta(days=50)).date(),
            mo=8,
            ml=12,
            mp=20,
            cost_total=3000,
        )

        task_1_2_3 = Task(
            project_id=project1.id,
            parent_id=None,  # Will be set after flush
            name="Phát triển API Projects & Tasks",
            status=TaskStatusEnum.TODO,
            start_date=(datetime.now() + timedelta(days=48)).date(),
            end_date=(datetime.now() + timedelta(days=70)).date(),
            mo=10,
            ml=15,
            mp=25,
            cost_total=5000,
        )

        # Level 2 (Subtasks của task_1_3)
        task_1_3_1 = Task(
            project_id=project1.id,
            parent_id=None,  # Will be set after flush
            name="Thiết kế giao diện UI",
            status=TaskStatusEnum.TODO,
            start_date=(datetime.now() + timedelta(days=40)).date(),
            end_date=(datetime.now() + timedelta(days=50)).date(),
            mo=5,
            ml=8,
            mp=12,
            cost_total=2000,
        )

        task_1_3_2 = Task(
            project_id=project1.id,
            parent_id=None,  # Will be set after flush
            name="Phát triển components React",
            status=TaskStatusEnum.TODO,
            start_date=(datetime.now() + timedelta(days=48)).date(),
            end_date=(datetime.now() + timedelta(days=80)).date(),
            mo=10,
            ml=15,
            mp=20,
            cost_total=4000,
        )

        # Add all tasks
        all_tasks = [
            task_1_1, task_1_2, task_1_3, task_1_4,
            task_1_1_1, task_1_1_2, task_1_1_3,
            task_1_2_1, task_1_2_2, task_1_2_3,
            task_1_3_1, task_1_3_2,
        ]

        session.add_all(all_tasks)
        await session.flush()

        # Set parent relationships
        task_1_1_1.parent_id = task_1_1.id
        task_1_1_2.parent_id = task_1_1.id
        task_1_1_3.parent_id = task_1_1.id
        task_1_2_1.parent_id = task_1_2.id
        task_1_2_2.parent_id = task_1_2.id
        task_1_2_3.parent_id = task_1_2.id
        task_1_3_1.parent_id = task_1_3.id
        task_1_3_2.parent_id = task_1_3.id

        # --- PROJECT 2: WEBNEW ---
        task_2_1 = Task(
            project_id=project2.id,
            name="Thiết kế mockup trang web",
            status=TaskStatusEnum.DOING,
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=15)).date(),
            mo=5,
            ml=8,
            mp=12,
            cost_total=2000,
        )

        task_2_2 = Task(
            project_id=project2.id,
            name="Phát triển trang chủ",
            status=TaskStatusEnum.TODO,
            start_date=(datetime.now() + timedelta(days=15)).date(),
            end_date=(datetime.now() + timedelta(days=35)).date(),
            mo=8,
            ml=12,
            mp=18,
            cost_total=3000,
        )

        task_2_3 = Task(
            project_id=project2.id,
            name="Phát triển trang sản phẩm",
            status=TaskStatusEnum.TODO,
            start_date=(datetime.now() + timedelta(days=30)).date(),
            end_date=(datetime.now() + timedelta(days=50)).date(),
            mo=8,
            ml=10,
            mp=15,
            cost_total=2500,
        )

        task_2_4 = Task(
            project_id=project2.id,
            name="Tích hợp thanh toán",
            status=TaskStatusEnum.TODO,
            start_date=(datetime.now() + timedelta(days=50)).date(),
            end_date=(datetime.now() + timedelta(days=70)).date(),
            mo=10,
            ml=15,
            mp=25,
            cost_total=4000,
        )

        session.add_all([task_2_1, task_2_2, task_2_3, task_2_4])
        await session.flush()

        # ==========================================
        # 7. TÍNH TOÁN EST (Estimated Time)
        # ==========================================
        print("\n⏱️ Calculating EST values...")

        for task in all_tasks + [task_2_1, task_2_2, task_2_3, task_2_4]:
            if task.mo and task.ml and task.mp:
                task.est = task.calculate_est()

        # ==========================================
        # 8. COMMIT TẬT CẢ
        # ==========================================
        await session.commit()

        print("\n✅ Seed data created successfully!")
        print("\n" + "="*60)
        print("📊 SUMMARY:")
        print("="*60)
        print(f"✅ Users created: {len(users)}")
        print(f"✅ Projects created: {len(projects)}")
        print(f"✅ Project members: {len(project_members)}")
        print(f"✅ Tasks created: {len(all_tasks) + 4}")
        print("\n📋 Users:")
        for user in users:
            print(f"  - {user.email} ({user.full_name})")
        print("\n📌 Projects:")
        for project in projects:
            print(f"  - {project.project_code} - {project.name}")
        print("\n🔑 Test Credentials:")
        print("  - Email: tuananh@example.com")
        print("    Password: Password123!")
        print("    Role: PM (Project Manager) in QTDA001")
        print("\n  - Email: hoangminh@example.com")
        print("    Password: Password123!")
        print("    Role: MEMBER in QTDA001, PM in WEBNEW")
        print("\n  - Email: thule@example.com")
        print("    Password: Password123!")
        print("    Role: MEMBER in both projects")
        print("="*60)


if __name__ == "__main__":
    print("\n🚀 Starting Database Seeding...\n")
    asyncio.run(seed_database())
    print("\n✨ Done! Seed data ready for testing.\n")
