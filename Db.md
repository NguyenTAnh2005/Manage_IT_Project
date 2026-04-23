### Bảng USERS (Quản lý người dùng): Lưu trữ thông tin tài khoản để đăng nhập vào hệ thống.

- id
- email
- password_hash
- full_name (Họ và tên)

### Bảng PROJECTS (Quản lý thông tin dự án): Cấp mã dự án độc quyền theo yêu cầu của Giảng viên.

- id
- project_code ( mã dự án)
- name (Tên dự án)
- description (Mô tả dự án)

### Bảng PROJECT_MEMBERS (Phân quyền Trưởng dự án / Thành viên): Bảng trung gian để xác định ai làm chức vụ gì trong dự án nào.

- id (Khóa chính)
- user_id (Khóa ngoại trỏ về bảng USERS)
- project_id (Khóa ngoại trỏ về bảng PROJECTS)
- role (Vai trò: PM - Trưởng dự án, hoặc MEMBER - Thành viên)

### Bảng TASKS (Siêu bảng Quản lý Công việc - Lõi hệ thống): Bảng này nói về toàn bộ logic về WBS, Gantt, Kanban, PERT và Chi phí.

- id (Khóa chính)
- project_id (Khóa ngoại trỏ về bảng PROJECTS)
- parent_id (Khóa ngoại trỏ về chính bảng TASKS --> Dùng để phân cấp công việc Cha - Con)
- name (Tên công việc)
- status (Trạng thái công việc: TODO, DOING, DONE --> Dùng cho chức năng Bảng Kanban)
- start_date (Ngày bắt đầu --> Dùng cho chức năng vẽ biểu đồ Gantt)
- end_date (Ngày kết thúc --> Dùng cho chức năng vẽ biểu đồ Gantt)
- mo, ml, mp (Lạc quan, Khả dĩ, Bi quan --> Dùng cho tính toán PERT)
- est (Kết quả tính Thời gian chuyên gia)
- cost_total (Tổng chi phí ước lượng)
- owner_id (Công việc này do ai làm)
