import asyncio
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession

# Import database session và models từ project
from app.core.database import AsyncSessionLocal
from app.models.model import User, Project, ProjectMember, Task, RoleEnum, TaskStatusEnum
from app.core.security import hash_password 

async def run_seed():
    print("🚀 Bắt đầu quá trình seed dữ liệu Vippro...")
    async with AsyncSessionLocal() as db:
        try:
            # ========================================
            # 1. TẠO USERS
            # ========================================
            print("⏳ Đang tạo Users...")
            user_tuan_anh = User(
                email="tuananh@example.com", 
                password_hash=hash_password("tuananh123!"), 
                full_name="Tuấn Anh"
            )
            user_vu = User(
                email="vu@example.com", 
                password_hash=hash_password("lamvu123!"), 
                full_name="Vũ"
            )
            
            db.add_all([user_tuan_anh, user_vu])
            await db.flush() 

            # ========================================
            # 2. TẠO PROJECT
            # ========================================
            print("⏳ Đang tạo Project...")
            project = Project(
                project_code="PM_APP_01",
                name="Ứng dụng Quản trị Dự án",
                description="Dự án thực hành code chung của Tuấn Anh và Vũ",
            )
            db.add(project)
            await db.flush()

            # ========================================
            # 3. PHÂN QUYỀN (PROJECT MEMBERS)
            # ========================================
            print("⏳ Đang phân quyền...")
            pm_role = ProjectMember(user_id=user_tuan_anh.id, project_id=project.id, role=RoleEnum.PM)
            member_role = ProjectMember(user_id=user_vu.id, project_id=project.id, role=RoleEnum.MEMBER)
            db.add_all([pm_role, member_role])
            await db.flush()

            # ========================================
            # 4. TẠO TASKS (WBS TỪ EXCEL)
            # ========================================
            print("⏳ Đang tạo cây công việc (WBS) với logic tính tổng & ngày tháng...")
            
            wbs_data = [
                {
                    "parent": "1. Khởi tạo & Phân quyền (Login)",
                    "children": [
                        {"name": "1.1 [FE] Tạo dự án Vite + React + Tailwind", "owner": user_tuan_anh.id},
                        {"name": "1.1 [BE] Khởi tạo FastAPI + SQLAlchemy", "owner": user_vu.id},
                        {"name": "1.2 [FE] Phối hợp chốt schema JSON", "owner": user_tuan_anh.id},
                        {"name": "1.2 [BE] Thiết kế 4 bảng (Users, Projects, Tasks...)", "owner": user_vu.id},
                        {"name": "1.3 [FE] Dựng Form Login, lưu Token (Local Storage)", "owner": user_tuan_anh.id},
                        {"name": "1.3 [BE] Code API Login, tạo & mã hóa JWT", "owner": user_vu.id},
                        {"name": "1.4 [FE] Dựng Form nhập mã, gọi API join dự án", "owner": user_tuan_anh.id},
                        {"name": "1.4 [BE] Code API kiểm tra mã & phân quyền", "owner": user_vu.id},
                    ]
                },
                {
                    "parent": "2. Quản lý WBS & PERT",
                    "children": [
                        {"name": "2.1 [FE] Dùng AntD/MUI dựng Table hiển thị dạng Cha-Con", "owner": user_tuan_anh.id},
                        {"name": "2.1 [BE] API CRUD cho bảng Tasks", "owner": user_vu.id},
                        {"name": "2.2 [FE] Làm Form nhập 3 số MO, ML, MP", "owner": user_tuan_anh.id},
                        {"name": "2.2 [BE] Viết logic tính EST, cập nhật vào DB", "owner": user_vu.id},
                        {"name": "2.3 [FE] Thêm cột nhập Tiền vào bảng Table", "owner": user_tuan_anh.id},
                        {"name": "2.3 [BE] Cập nhật API Tasks để nhận & lưu biến số Tiền", "owner": user_vu.id},
                    ]
                },
                {
                    "parent": "3. Trực quan hóa (Kanban & Gantt)",
                    "children": [
                        {"name": "3.1 [FE] Tích hợp thư viện (dnd-kit), code giao diện kéo thả", "owner": user_tuan_anh.id},
                        {"name": "3.1 [BE] API Update Status (/tasks/{id}/status)", "owner": user_vu.id},
                        {"name": "3.2 [FE] Tích hợp thư viện Gantt, map data ngày tháng", "owner": user_tuan_anh.id},
                        {"name": "3.2 [BE] (Đã có data từ API Tasks, hỗ trợ test)", "owner": user_vu.id},
                        {"name": "3.3 [FE] Viết file báo cáo UI/UX, hướng dẫn sử dụng", "owner": user_tuan_anh.id},
                        {"name": "3.3 [BE] Khởi chạy test Postman hoặc Swagger UI, fix bug logic API", "owner": user_vu.id},
                    ]
                }
            ]

            # Khởi tạo ngày bắt đầu: 3 tuần trước
            today = datetime.utcnow().date()
            current_date = today - timedelta(weeks=3)

            for section in wbs_data:
                # 4.1 Tạo Task Cha (Chưa có thông số, cập nhật sau)
                parent_task = Task(
                    project_id=project.id,
                    name=section["parent"],
                    status=TaskStatusEnum.TODO,
                    cost_total=0.0
                )
                db.add(parent_task)
                await db.flush() # Lấy parent_id

                # Các biến để cộng dồn cho Task Cha
                sum_mo = 0.0
                sum_ml = 0.0
                sum_mp = 0.0
                sum_cost = 0.0
                parent_start_date = current_date
                parent_end_date = current_date

                # 4.2 Tạo các Task Con
                for child in section["children"]:
                    # Set cứng mỗi task nhỏ mất khoảng 3 ngày để làm
                    child_start = current_date
                    child_end = current_date + timedelta(days=2) 
                    
                    child_mo = 2.0
                    child_ml = 3.0
                    child_mp = 5.0
                    child_est = (child_mo + 4 * child_ml + child_mp) / 6
                    child_cost = 100.0

                    child_task = Task(
                        project_id=project.id,
                        parent_id=parent_task.id,
                        owner_id=child["owner"],
                        name=child["name"],
                        status=TaskStatusEnum.TODO,
                        mo=child_mo, ml=child_ml, mp=child_mp, est=child_est,
                        cost_total=child_cost,
                        start_date=child_start,
                        end_date=child_end
                    )
                    db.add(child_task)

                    # Cộng dồn số liệu lên cho Task Cha
                    sum_mo += child_mo
                    sum_ml += child_ml
                    sum_mp += child_mp
                    sum_cost += child_cost
                    parent_end_date = child_end

                    # Dịch chuyển ngày cho Task tiếp theo (cộng thêm 3 ngày)
                    current_date = child_end + timedelta(days=1)

                # 4.3 Cập nhật ngược lại thông số cho Task Cha
                parent_task.mo = sum_mo
                parent_task.ml = sum_ml
                parent_task.mp = sum_mp
                parent_task.est = (sum_mo + 4 * sum_ml + sum_mp) / 6
                parent_task.cost_total = sum_cost
                parent_task.start_date = parent_start_date
                parent_task.end_date = parent_end_date
            
            # Lưu toàn bộ
            await db.commit()
            print("✅ Seed dữ liệu WBS siêu xịn thành công rực rỡ!")

        except Exception as e:
            await db.rollback()
            print(f"❌ Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    asyncio.run(run_seed())