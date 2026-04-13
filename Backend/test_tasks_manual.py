"""
Script test Tasks CRUD endpoints
Chạy: python test_tasks_manual.py
"""

import asyncio
import httpx
import json
from datetime import datetime
import random
import string

# URL của API
BASE_URL = "http://localhost:8000"

# ===== HELPER FUNCTIONS =====

async def print_response(response, title):
    """In response một cách đẹp"""
    print(f"\n{'='*60}")
    print(f"🔷 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")


async def test_tasks_crud():
    """Test toàn bộ Tasks CRUD"""
    
    # Tạo email ngẫu nhiên để tránh xung đột
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    test_email = f"test{random_suffix}@example.com"
    
    async with httpx.AsyncClient() as client:
        # ===== 1. ĐĂNG KÝ USER =====
        print("\n\n🚀 BẮT ĐẦU TEST TASKS CRUD\n")
        
        register_data = {
            "email": test_email,
            "password": "TestPass123@",
            "full_name": "Lý Lâm Vũ"
        }
        
        response = await client.post(f"{BASE_URL}/auth/register", json=register_data)
        await print_response(response, "1️⃣ ĐĂNG KÝ USER")
        
        if response.status_code != 201:
            print("❌ Đăng ký thất bại!")
            return
        
        tokens = response.json()
        access_token = tokens["access_token"]
        print(f"✅ Lấy access token: {access_token[:30]}...")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # ===== 2. TẠO DỰ ÁN =====
        project_code = f"PROJ{random_suffix.upper()}"
        project_data = {
            "project_code": project_code,
            "name": "Dự án Test",
            "description": "Dự án để test Tasks CRUD"
        }
        
        response = await client.post(f"{BASE_URL}/projects", json=project_data, headers=headers)
        await print_response(response, "2️⃣ TẠO DỰ ÁN")
        
        if response.status_code != 201:
            print("❌ Tạo dự án thất bại!")
            return
        
        project = response.json()
        project_id = project["id"]
        print(f"✅ Dự án ID: {project_id}")
        
        # ===== 3. TẠO CÔNG VIỆC =====
        task_data = {
            "title": "Công việc test 1",
            "description": "Đây là công việc test đầu tiên",
            "status": "pending",
            "priority": "high",
            "assigned_to": None
        }
        
        response = await client.post(
            f"{BASE_URL}/projects/{project_id}/tasks",
            json=task_data,
            headers=headers
        )
        await print_response(response, "3️⃣ TẠO CÔNG VIỆC")
        
        if response.status_code != 201:
            print("❌ Tạo công việc thất bại!")
            return
        
        task = response.json()
        task_id = task["id"]
        print(f"✅ Công việc ID: {task_id}")
        
        # ===== 4. DANH SÁCH CÔNG VIỆC =====
        response = await client.get(
            f"{BASE_URL}/projects/{project_id}/tasks",
            headers=headers
        )
        await print_response(response, "4️⃣ DANH SÁCH CÔNG VIỆC")
        
        if response.status_code != 200:
            print("❌ Lấy danh sách công việc thất bại!")
            return
        
        tasks_list = response.json()
        print(f"✅ Tổng công việc: {len(tasks_list)}")
        
        # ===== 5. LẤY CHI TIẾT CÔNG VIỆC =====
        response = await client.get(
            f"{BASE_URL}/tasks/{task_id}",
            headers=headers
        )
        await print_response(response, "5️⃣ LẤY CHI TIẾT CÔNG VIỆC")
        
        if response.status_code != 200:
            print("❌ Lấy chi tiết công việc thất bại!")
            return
        
        # ===== 6. SỬA CÔNG VIỆC =====
        update_data = {
            "status": "in_progress",
            "priority": "critical"
        }
        
        response = await client.put(
            f"{BASE_URL}/tasks/{task_id}",
            json=update_data,
            headers=headers
        )
        await print_response(response, "6️⃣ SỬA CÔNG VIỆC")
        
        if response.status_code != 200:
            print("❌ Sửa công việc thất bại!")
            return
        
        # ===== 7. TẠO CÔNG VIỆC THỨ 2 =====
        task_data_2 = {
            "title": "Công việc test 2",
            "description": "Công việc thứ hai",
            "status": "pending",
            "priority": "medium"
        }
        
        response = await client.post(
            f"{BASE_URL}/projects/{project_id}/tasks",
            json=task_data_2,
            headers=headers
        )
        await print_response(response, "7️⃣ TẠO CÔNG VIỆC THỨ 2")
        
        if response.status_code != 201:
            print("❌ Tạo công việc thứ 2 thất bại!")
            return
        
        task_2 = response.json()
        task_2_id = task_2["id"]
        print(f"✅ Công việc 2 ID: {task_2_id}")
        
        # ===== 8. DANH SÁCH CÔNG VIỆC (CHECK CÓ 2 CÔNG VIỆC) =====
        response = await client.get(
            f"{BASE_URL}/projects/{project_id}/tasks",
            headers=headers
        )
        await print_response(response, "8️⃣ DANH SÁCH CÔNG VIỆC (CHECK CÓ 2 TASK)")
        
        # ===== 9. XÓA CÔNG VIỆC =====
        response = await client.delete(
            f"{BASE_URL}/tasks/{task_2_id}",
            headers=headers
        )
        await print_response(response, "9️⃣ XÓA CÔNG VIỆC")
        
        if response.status_code != 200:
            print("❌ Xóa công việc thất bại!")
            return
        
        # ===== 10. KIỂM TRA LẠI DANH SÁCH =====
        response = await client.get(
            f"{BASE_URL}/projects/{project_id}/tasks",
            headers=headers
        )
        await print_response(response, "🔟 DANH SÁCH CÔNG VIỆC (SAU KHI XÓA)")
        
        print("\n" + "="*60)
        print("✅ TEST HOÀN THÀNH!")
        print("="*60)


# ===== CHẠY TEST =====

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║                 TEST TASKS CRUD ENDPOINTS                  ║
║                                                            ║
║ Đảm bảo server đang chạy: uvicorn main:app --reload       ║
║ Chạy script này: python test_tasks_manual.py               ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(test_tasks_crud())
    except Exception as e:
        print(f"\n❌ LỖI: {str(e)}")
        print("\n💡 Đảm bảo:")
        print("  1. Server đang chạy trên http://localhost:8000")
        print("  2. Database đã được migrate (alembic upgrade head)")
        print("  3. .env file đã được cấu hình đúng")
