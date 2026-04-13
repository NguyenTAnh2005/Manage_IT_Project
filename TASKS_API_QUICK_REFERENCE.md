# Tasks API - Hướng dẫn Nhanh / Quick Reference

## API Endpoints

### 1. Lấy danh sách công việc của dự án

```
GET /projects/{project_id}/tasks
Authorization: Bearer <token>

Response (200): List[TaskResponse]
[
  {
    "id": 1,
    "project_id": 1,
    "title": "Công việc A",
    "description": "Mô tả",
    "status": "pending",
    "priority": "high",
    "created_by": 1,
    "assigned_to": 2,
    "created_at": "2026-04-13T10:30:00",
    "updated_at": null
  }
]

Errors:
- 401: Token không hợp lệ
- 403: Bạn không phải là thành viên của dự án này
- 404: Dự án không tồn tại
- 500: Lỗi server
```

### 2. Tạo công việc mới

```
POST /projects/{project_id}/tasks
Authorization: Bearer <token>

Body:
{
  "title": "Tiêu đề công việc",
  "description": "Mô tả chi tiết (optional)",
  "status": "pending",          // pending|in_progress|completed|blocked
  "priority": "high",           // low|medium|high|critical
  "assigned_to": 2              // user_id (optional)
}

Response (201): TaskResponse
{
  "id": 1,
  "project_id": 1,
  "title": "Tiêu đề công việc",
  "description": "Mô tả chi tiết",
  "status": "pending",
  "priority": "high",
  "created_by": 1,
  "assigned_to": 2,
  "created_at": "2026-04-13T10:30:00",
  "updated_at": null
}

Errors:
- 401: Token không hợp lệ
- 403: Chỉ Project Manager mới có quyền tạo công việc
- 404: Dự án không tồn tại
- 422: Dữ liệu không hợp lệ
- 500: Lỗi server

Validation Rules:
- title: 1-255 ký tự, bắt buộc
- description: tối đa 2000 ký tự
- status: phải là pending|in_progress|completed|blocked
- priority: phải là low|medium|high|critical
- assigned_to: user_id phải tồn tại
```

### 3. Lấy chi tiết công việc

```
GET /tasks/{task_id}
Authorization: Bearer <token>

Response (200): TaskResponse
{
  "id": 1,
  "project_id": 1,
  "title": "Tiêu đề công việc",
  "description": "Mô tả chi tiết",
  "status": "pending",
  "priority": "high",
  "created_by": 1,
  "assigned_to": 2,
  "created_at": "2026-04-13T10:30:00",
  "updated_at": "2026-04-14T15:45:00"
}

Errors:
- 401: Token không hợp lệ
- 403: Bạn không có quyền truy cập công việc này
- 404: Công việc không tồn tại
- 500: Lỗi server

Permission: User phải là:
- Thành viên của project, HOẶC
- Được gán công việc này
```

### 4. Sửa công việc

```
PUT /tasks/{task_id}
Authorization: Bearer <token>

Body (tất cả trường optional):
{
  "title": "Tiêu đề mới",
  "description": "Mô tả mới",
  "status": "in_progress",
  "priority": "critical",
  "assigned_to": 3
}

Response (200): TaskResponse
{
  "id": 1,
  "project_id": 1,
  "title": "Tiêu đề mới",
  "description": "Mô tả mới",
  "status": "in_progress",
  "priority": "critical",
  "created_by": 1,
  "assigned_to": 3,
  "created_at": "2026-04-13T10:30:00",
  "updated_at": "2026-04-14T15:45:00"
}

Errors:
- 401: Token không hợp lệ
- 403: Chỉ Project Manager mới có quyền sửa công việc
- 404: Công việc không tồn tại
- 422: Dữ liệu không hợp lệ
- 500: Lỗi server

Permission: User phải là PM của project
```

### 5. Xóa công việc

```
DELETE /tasks/{task_id}
Authorization: Bearer <token>

Response (200):
{
  "message": "Công việc đã được xóa"
}

Errors:
- 401: Token không hợp lệ
- 403: Chỉ Project Manager mới có quyền xóa công việc
- 404: Công việc không tồn tại
- 500: Lỗi server

Permission: User phải là PM của project
```

---

## Status Values / Giá trị Trạng thái

| Value         | Tiếng Việt     | Ý nghĩa                              |
| ------------- | -------------- | ------------------------------------ |
| `pending`     | Chưa bắt đầu   | Công việc vừa được tạo, chưa ai làm  |
| `in_progress` | Đang tiến hành | Công việc đang được thực hiện        |
| `completed`   | Hoàn thành     | Công việc đã xong                    |
| `blocked`     | Bị chặn        | Công việc bị trì hoãn vì vấn đề khác |

---

## Priority Values / Giá trị Mức độ Ưu tiên

| Value      | Tiếng Việt        | Ý nghĩa                 |
| ---------- | ----------------- | ----------------------- |
| `low`      | Thấp              | Công việc không gấp rút |
| `medium`   | Trung bình        | Công việc bình thường   |
| `high`     | Cao               | Công việc quan trọng    |
| `critical` | Cực kỳ quan trọng | Công việc khẩn cấp      |

---

## Error Codes / Mã Lỗi

| Code | Tiếng Việt            | Nguyên nhân                     |
| ---- | --------------------- | ------------------------------- |
| 200  | OK                    | Thành công                      |
| 201  | Created               | Tạo thành công                  |
| 400  | Bad Request           | Yêu cầu sai                     |
| 401  | Unauthorized          | Token không hợp lệ hoặc hết hạn |
| 403  | Forbidden             | Không có quyền                  |
| 404  | Not Found             | Không tìm thấy                  |
| 422  | Unprocessable Entity  | Dữ liệu không hợp lệ            |
| 429  | Too Many Requests     | Quá nhiều yêu cầu               |
| 500  | Internal Server Error | Lỗi server                      |

---

## Permission Rules / Luật Quyền Hạn

### Tạo công việc (CREATE)

- ✅ User phải authenticated
- ✅ User phải là **PM** của project
- ✅ Project phải tồn tại

### Lấy danh sách (LIST)

- ✅ User phải authenticated
- ✅ User phải là **member** hoặc **PM** của project
- ✅ Project phải tồn tại

### Lấy chi tiết (GET)

- ✅ User phải authenticated
- ✅ User phải là:
  - **Member/PM** của project, HOẶC
  - **Được gán công việc** này
- ✅ Task phải tồn tại

### Sửa công việc (UPDATE)

- ✅ User phải authenticated
- ✅ User phải là **PM** của project
- ✅ Task phải tồn tại
- ✅ Chỉ cập nhật được: title, description, status, priority, assigned_to

### Xóa công việc (DELETE)

- ✅ User phải authenticated
- ✅ User phải là **PM** của project
- ✅ Task phải tồn tại

---

## Example cURL Commands

### 1. Lấy danh sách công việc

```bash
curl -X GET "http://localhost:8000/projects/1/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Tạo công việc mới

```bash
curl -X POST "http://localhost:8000/projects/1/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Công việc A",
    "description": "Mô tả chi tiết",
    "status": "pending",
    "priority": "high",
    "assigned_to": 2
  }'
```

### 3. Lấy chi tiết công việc

```bash
curl -X GET "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Sửa công việc

```bash
curl -X PUT "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "critical"
  }'
```

### 5. Xóa công việc

```bash
curl -X DELETE "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Validation Errors / Lỗi Validation

Nếu gửi dữ liệu không hợp lệ, response sẽ là:

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Tiêu đề công việc không được để trống",
      "type": "value_error"
    }
  ]
}
```

Các error messages có thể gặp:

- "Tiêu đề công việc không được để trống"
- "Tiêu đề công việc tối thiểu 1 ký tự"
- "Tiêu đề công việc tối đa 255 ký tự"
- "Mô tả công việc tối đa 2000 ký tự"
- "Trạng thái phải là một trong: pending, in_progress, completed, blocked"
- "Mức độ ưu tiên phải là một trong: low, medium, high, critical"

---

## Testing Checklist / Danh sách Kiểm tra

- [ ] Tạo project
- [ ] Tạo user khác
- [ ] Add user vào project
- [ ] Tạo công việc (as PM)
- [ ] Lấy danh sách công việc
- [ ] Lấy chi tiết công việc
- [ ] Sửa công việc (as PM)
- [ ] Sửa công việc (as member) - should fail
- [ ] Xóa công việc (as PM)
- [ ] Xóa công việc (as member) - should fail
- [ ] Test all status values
- [ ] Test all priority values
- [ ] Test with invalid token - should fail
- [ ] Test Vietnamese error messages

---

**Last Updated:** 2026-04-13
**Status:** ✅ Ready for Testing
