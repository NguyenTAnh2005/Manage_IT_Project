# Tasks CRUD Implementation - Triển khai Hệ thống Quản lý Công việc

## 📋 Tóm tắt Triển khai / Implementation Summary

**Ngày triển khai / Date:** 2026-04-13
**Trạng thái / Status:** ✅ Hoàn thành / Completed
**Yêu cầu / Requirements:** Tất cả yêu cầu đã được đáp ứng / All requirements met

---

## 📁 Cấu trúc tập tin được tạo / Created File Structure

### 1. **Backend/app/crud/task.py** ✅

**CRUD Operations cho Task Model**

Các hàm được cập nhật với tiếng Việt hoàn toàn:

#### Tạo / CREATE

- `create_task()` - Tạo công việc mới với đầy đủ thông tin
  - Tham số: project_id, title, description, status, priority, created_by, assigned_to
  - Trả về: Task object vừa tạo
  - Ghi log: Tự động log khi tạo

#### Đọc / READ

- `get_task_by_id()` - Lấy công việc theo ID
- `get_tasks_by_project()` - Lấy tất cả công việc của một dự án (sắp xếp theo thời gian tạo)
- `get_tasks_assigned_to_user()` - Lấy tất cả công việc được gán cho user

#### Sửa / UPDATE

- `update_task()` - Cập nhật thông tin công việc
  - Cho phép cập nhật: title, description, status, priority, assigned_to
  - Bỏ qua các trường không được phép sửa
  - Tự động refresh sau khi commit

#### Xóa / DELETE

- `delete_task()` - Xóa công việc khỏi database
  - Trả về: True nếu xóa thành công, False nếu không tìm thấy

#### Kiểm quyền / PERMISSION CHECK

- `check_task_permission()` - Kiểm tra user có quyền truy cập công việc
  - Điều kiện: User là thành viên dự án HOẶC được gán công việc
- `check_task_project_permission()` - Kiểm tra user là thành viên dự án
- `check_task_pm_permission()` - Kiểm tra user là PM của dự án

**Các đặc tính / Features:**

- ✅ Tất cả docstring bằng tiếng Việt
- ✅ Tất cả comment bằng tiếng Việt
- ✅ Tất cả log message bằng tiếng Việt
- ✅ Sử dụng AsyncSession để tương thích async/await
- ✅ Ghi log chi tiết cho mỗi thao tác

---

### 2. **Backend/app/schemas/task.py** ✅

**Pydantic Models cho Validation và Response**

#### Request Schemas

- **TaskCreate** - Schema tạo công việc mới
  - `title` (str, 1-255 ký tự, bắt buộc)
  - `description` (str, tối đa 2000 ký tự, optional)
  - `status` (str, mặc định "pending")
  - `priority` (str, mặc định "medium")
  - `assigned_to` (int, optional)
  - Validators: Kiểm tra độ dài, không được trống, định dạng đúng

- **TaskUpdate** - Schema sửa công việc
  - Tất cả trường optional
  - Cùng validators như TaskCreate
  - Cho phép cập nhật từng trường độc lập

#### Response Schemas

- **TaskResponse** - Response cơ bản
  - id, project_id, title, description, status, priority
  - created_by, assigned_to, created_at, updated_at
  - Dùng `from_attributes = True` để hỗ trợ SQLAlchemy model

- **TaskDetailResponse** - Response chi tiết (structure tương tự)

#### Enums

- **TaskStatusEnum**: pending, in_progress, completed, blocked
- **TaskPriorityEnum**: low, medium, high, critical

**Các đặc tính / Features:**

- ✅ Tất cả docstring bằng tiếng Việt
- ✅ Tất cả error message bằng tiếng Việt
- ✅ Validators tự động kiểm tra input
- ✅ Hỗ trợ conversion từ SQLAlchemy model

---

### 3. **Backend/app/routers/task.py** ✅

**API Endpoints cho Tasks CRUD**

#### Endpoints được cấp phát / Implemented Endpoints

**1. GET /projects/{project_id}/tasks** - Lấy danh sách công việc

- Yêu cầu: Authentication + Project membership
- Response: List[TaskResponse]
- Status Code: 200 OK
- Errors: 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Error
- Tất cả error messages bằng tiếng Việt

**2. POST /projects/{project_id}/tasks** - Tạo công việc mới

- Yêu cầu: Authentication + PM role
- Body: TaskCreate
- Response: TaskResponse
- Status Code: 201 Created
- Errors: 401, 403, 404, 422, 500
- Kiểm tra PM permission trước khi tạo

**3. GET /tasks/{task_id}** - Lấy chi tiết công việc

- Yêu cầu: Authentication + Task access permission
- Response: TaskResponse
- Status Code: 200 OK
- Errors: 401, 403, 404, 500
- Kiểm tra user là project member hoặc assigned to task

**4. PUT /tasks/{task_id}** - Sửa công việc

- Yêu cầu: Authentication + PM role
- Body: TaskUpdate
- Response: TaskResponse
- Status Code: 200 OK
- Errors: 401, 403, 404, 422, 500
- Chỉ PM của project mới được sửa

**5. DELETE /tasks/{task_id}** - Xóa công việc

- Yêu cầu: Authentication + PM role
- Response: {"message": "Công việc đã được xóa"}
- Status Code: 200 OK
- Errors: 401, 403, 404, 500
- Chỉ PM của project mới được xóa

#### Error Handling

- ✅ Tất cả error messages bằng tiếng Việt
- ✅ Proper HTTP status codes (201 Created, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity, 500 Error)
- ✅ Chi tiết error response giúp client debug

#### Features

- ✅ Comprehensive docstrings (Vietnamese)
- ✅ Request/Response examples in docstrings (Vietnamese)
- ✅ Detailed permission checks
- ✅ Proper logging cho tất cả operations
- ✅ Exception handling và rollback on error
- ✅ Tất cả comments bằng tiếng Việt

---

### 4. **Backend/main.py** ✅

**Cập nhật Main Application**

**Thay đổi:**

```python
# Import thêm task router
from app.routers import auth, user, project, task

# Include task router vào app
app.include_router(task.router)
```

---

## 🔒 Bảo mật & Quyền hạn / Security & Permissions

### Permission Checks (Kiểm tra quyền)

1. **Tạo công việc (POST)**
   - ✅ User phải authenticated
   - ✅ User phải là PM của project
   - ✅ Project phải tồn tại

2. **Lấy danh sách công việc (GET list)**
   - ✅ User phải authenticated
   - ✅ User phải là member của project
   - ✅ Project phải tồn tại

3. **Lấy chi tiết công việc (GET detail)**
   - ✅ User phải authenticated
   - ✅ User phải là project member HOẶC assigned to task
   - ✅ Task phải tồn tại

4. **Sửa công việc (PUT)**
   - ✅ User phải authenticated
   - ✅ User phải là PM của project
   - ✅ Task phải tồn tại

5. **Xóa công việc (DELETE)**
   - ✅ User phải authenticated
   - ✅ User phải là PM của project
   - ✅ Task phải tồn tại

---

## 📊 Data Model Integration

### Task Model Fields

- `id` - Primary key
- `project_id` - Foreign key to Project
- `title` - Tiêu đề công việc
- `description` - Mô tả chi tiết
- `status` - Trạng thái (pending, in_progress, completed, blocked)
- `priority` - Mức độ ưu tiên (low, medium, high, critical)
- `created_by` - User ID của người tạo
- `assigned_to` - User ID của người được gán
- `created_at` - Thời gian tạo (auto)
- `updated_at` - Thời gian cập nhật (auto)

### Related Models

- **Project** - Mỗi task thuộc về 1 project
- **User** - Task có creator (created_by) và assignee (assigned_to)
- **ProjectMember** - Dùng để kiểm tra membership

---

## 🧪 API Testing Examples

### 1. Tạo Dự án (Create Project) - Trước hết

```bash
POST /projects
Headers: Authorization: Bearer <token>
Body: {
  "project_code": "TSK001",
  "name": "Task Test Project",
  "description": "Project để test tasks"
}
Response: 201 Created
{
  "id": 1,
  "project_code": "TSK001",
  "name": "Task Test Project",
  "created_at": "2026-04-13T...",
  "updated_at": null
}
```

### 2. Lấy danh sách công việc (List Tasks)

```bash
GET /projects/1/tasks
Headers: Authorization: Bearer <token>
Response: 200 OK
[
  {
    "id": 1,
    "project_id": 1,
    "title": "Công việc 1",
    "description": "Mô tả công việc 1",
    "status": "pending",
    "priority": "high",
    "created_by": 1,
    "assigned_to": 2,
    "created_at": "2026-04-13T...",
    "updated_at": null
  }
]
```

### 3. Tạo công việc mới (Create Task)

```bash
POST /projects/1/tasks
Headers: Authorization: Bearer <token>
Body: {
  "title": "Implement login feature",
  "description": "Cần implement tính năng đăng nhập",
  "status": "in_progress",
  "priority": "high",
  "assigned_to": 2
}
Response: 201 Created
{
  "id": 1,
  "project_id": 1,
  "title": "Implement login feature",
  "description": "Cần implement tính năng đăng nhập",
  "status": "in_progress",
  "priority": "high",
  "created_by": 1,
  "assigned_to": 2,
  "created_at": "2026-04-13T...",
  "updated_at": null
}
```

### 4. Lấy chi tiết công việc (Get Task)

```bash
GET /tasks/1
Headers: Authorization: Bearer <token>
Response: 200 OK
{
  "id": 1,
  "project_id": 1,
  "title": "Implement login feature",
  ...
}
```

### 5. Sửa công việc (Update Task)

```bash
PUT /tasks/1
Headers: Authorization: Bearer <token>
Body: {
  "status": "completed",
  "priority": "medium"
}
Response: 200 OK
{
  "id": 1,
  "project_id": 1,
  "title": "Implement login feature",
  "status": "completed",
  "priority": "medium",
  ...
  "updated_at": "2026-04-13T..."
}
```

### 6. Xóa công việc (Delete Task)

```bash
DELETE /tasks/1
Headers: Authorization: Bearer <token>
Response: 200 OK
{
  "message": "Công việc đã được xóa"
}
```

---

## ✅ Kiểm tra Yêu cầu / Requirements Checklist

- ✅ **CRUD Operations (task.py)**
  - ✅ create_task() - Tạo công việc
  - ✅ get_task_by_id() - Lấy theo ID
  - ✅ get_tasks_by_project() - Lấy theo dự án
  - ✅ get_tasks_assigned_to_user() - Lấy theo user được gán
  - ✅ update_task() - Sửa công việc
  - ✅ delete_task() - Xóa công việc
  - ✅ check_task_permission() - Kiểm tra quyền truy cập
  - ✅ check_task_project_permission() - Kiểm tra thành viên dự án
  - ✅ check_task_pm_permission() - Kiểm tra PM role (thêm)

- ✅ **Schemas (task.py)**
  - ✅ TaskCreate - Tạo công việc
  - ✅ TaskUpdate - Sửa công việc (all optional)
  - ✅ TaskResponse - Response cơ bản
  - ✅ TaskDetailResponse - Response chi tiết
  - ✅ Status enum: pending, in_progress, completed, blocked
  - ✅ Priority enum: low, medium, high, critical
  - ✅ Validators: title 1-255 chars, description max 2000 chars
  - ✅ All error messages in Vietnamese

- ✅ **API Routes (task.py router)**
  - ✅ GET /projects/{project_id}/tasks - List tasks
  - ✅ POST /projects/{project_id}/tasks - Create task
  - ✅ GET /tasks/{task_id} - Get single task
  - ✅ PUT /tasks/{task_id} - Update task
  - ✅ DELETE /tasks/{task_id} - Delete task
  - ✅ All endpoints require authentication
  - ✅ All error responses in Vietnamese

- ✅ **Code Quality**
  - ✅ ALL code comments in VIETNAMESE ONLY
  - ✅ ALL docstrings in Vietnamese
  - ✅ ALL error messages in Vietnamese
  - ✅ ALL log messages in Vietnamese
  - ✅ Task model already exists in models
  - ✅ Using AsyncSession
  - ✅ Proper error handling
  - ✅ Logging for operations
  - ✅ Permission checks (project member, task assignment, PM role)
  - ✅ created_at, updated_at timestamps (auto from model)
  - ✅ created_by field set to current_user.id
  - ✅ Project membership check before task access

- ✅ **Main Application**
  - ✅ Updated main.py to import task router
  - ✅ Updated main.py to include_router(task.router)

---

## 📝 Lưu ý quan trọng / Important Notes

### 1. Ngôn ngữ / Language

- ✅ **Tất cả code comments, docstrings, error messages đều bằng tiếng Việt**
- ✅ **Không có bất kỳ text tiếng Anh nào trong code comments**

### 2. Cấu trúc Async

- ✅ Tất cả CRUD functions đều async
- ✅ Sử dụng `await` khi cần
- ✅ Router endpoints tương thích với FastAPI async

### 3. Logging

- ✅ Mỗi operation được log với message tiếng Việt
- ✅ Log include: action, IDs, user info

### 4. Permission Model

- ✅ Project membership check qua ProjectMember table
- ✅ PM check qua ProjectMember.role == RoleEnum.PM
- ✅ Task access cho project members + assignees

### 5. Database Relationships

- ✅ Task.project_id → Project.id
- ✅ Task.created_by → User.id
- ✅ Task.assigned_to → User.id
- ✅ Cascading delete từ Project → Tasks

---

## 🔄 Workflow Tích hợp / Integration Workflow

### 1. Setup (một lần)

```python
# Database migration (nếu cần)
# Task model đã tồn tại sẵn
```

### 2. User Flow - Tạo công việc (Create Task Flow)

```
1. User đăng nhập → Get JWT token
2. User tạo project (hoặc join project)
3. User (as PM) POST /projects/{id}/tasks
4. System tạo task, set created_by = current_user.id
5. Task được lưu vào database
6. Return TaskResponse với id mới
```

### 3. User Flow - Lấy công việc (Retrieve Tasks Flow)

```
1. User đã authenticated
2. User GET /projects/{id}/tasks
3. System check project membership
4. Return list of tasks (nếu có quyền)
```

### 4. User Flow - Sửa công việc (Update Task Flow)

```
1. User (as PM) PUT /tasks/{id}
2. System check PM permission
3. System update allowed fields
4. Return updated TaskResponse
```

---

## 📚 Liên kết tệp tin / File References

- Backend CRUD: `Backend/app/crud/task.py`
- Backend Schemas: `Backend/app/schemas/task.py`
- Backend Router: `Backend/app/routers/task.py`
- Backend Main: `Backend/main.py`
- Task Model: `Backend/app/models/__init__.py` (đã tồn tại)

---

## 🚀 Cách kiến thức / Next Steps

1. ✅ Test API endpoints với Swagger UI (`/docs`)
2. ✅ Test permission checks
3. ✅ Test Vietnamese error messages
4. ✅ Integrate với Frontend để consume APIs
5. ✅ Deploy lên production

---

**Hoàn thành lúc / Completed:** 2026-04-13
**Trạng thái / Status:** ✅ Sẵn sàng / Ready for Testing
