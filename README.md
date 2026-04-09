# 🚀 Hệ Thống Quản Trị Dự Án CNTT (IT Project Management System)

Xây dựng hệ thống website quản lý dự án CNTT giúp các đội nhóm dễ dàng lập kế hoạch, theo dõi tiến độ, và kiểm soát chặt chẽ thời gian, chi phí một cách hiệu quả và minh bạch.

## 🛠 Công Nghệ Sử Dụng (Tech Stack)

- **Frontend:** ReactJS + Vite + Tailwind CSS
- **Backend:** FastAPI (Python) + SQLAlchemy
- **Database:** PostgreSQL

## 🎯 Mục Tiêu Dự Án

1. Hoàn thành thiết kế, lập trình và triển khai dự án hoạt động ổn định.
2. Hỗ trợ phân quyền **Trưởng dự án (PM)** và **Đội dự án (Member)**.
3. Quản lý truy cập an toàn và độc lập thông qua **Mã dự án (Project Code)**.
4. Nộp đầy đủ tài liệu theo yêu cầu môn học (Source code cập nhật theo buổi, file phân công nhiệm vụ).

## ✨ Các Chức Năng Cốt Lõi

Hệ thống cung cấp 5 phân hệ tính năng chính để quản lý toàn diện vòng đời dự án:

1. **Quản lý bảng công việc (WBS):** Quản lý cấu trúc phân rã công việc (Task Cha - Task Con).
2. **Ước lượng thời gian chuyên gia (PERT):** Tự động tính toán thời gian dự kiến (EST) dựa trên 3 trọng số: Lạc quan (MO), Khả dĩ (ML), Bi quan (MP).
3. **Ước lượng chi phí cho dự án:** Tổng hợp ngân sách dựa trên từng đầu mục công việc.
4. **Quản lý lịch trình dự án:** Trực quan hóa tiến độ bằng biểu đồ **Gantt Chart**.
5. **Quản lý lịch trình công việc:** Cập nhật trạng thái công việc qua bảng **Kanban Board** (Kéo thả thẻ TO DO - DOING - DONE).

---

## 👥 Danh Sách Thành Viên

| STT | MSSV     | Họ và Tên           | Vai trò           | Trách nhiệm chính                                  |
| :-: | :------- | :------------------ | :---------------- | :------------------------------------------------- |
|  1  | 23050118 | **Nguyễn Tuấn Anh** | Trưởng dự án (PM) | Thiết kế UI/UX, Code Frontend (React), Ghép API    |
|  2  | 23050102 | **Lý Lâm Vũ**       | Thành viên        | Thiết kế CSDL (PostgreSQL), Code Backend (FastAPI) |

---

## 📅 Lộ Trình Triển Khai & Phân Công Nhiệm Vụ

| Giai đoạn         | Nhiệm vụ Frontend (Tuấn Anh)                 | Nhiệm vụ Backend (Vũ)                        |
| :---------------- | :------------------------------------------- | :------------------------------------------- |
| **Setup Project** | Khởi tạo dự án Vite + React + Tailwind       | Khởi tạo FastAPI + SQLAlchemy                |
| **Database**      | Chốt cấu trúc dữ liệu JSON                   | Thiết kế 4 bảng (Users, Projects, Tasks,...) |
| **Auth**          | Dựng form Login, lưu Token (Local Storage)   | Code API Login, tạo & mã hóa JWT             |
| **Join Dự án**    | Dựng form nhập mã, gọi API join dự án        | Code API kiểm tra mã & phân quyền User       |
| **Bảng WBS**      | Dựng Table hiển thị dạng phân cấp Cha-Con    | Xây dựng API CRUD cho bảng Tasks             |
| **Tính PERT**     | Form nhập liệu 3 chỉ số MO, ML, MP           | Viết logic tính công thức EST, lưu vào DB    |
| **Chi phí**       | Giao diện nhập liệu và tính tổng chi phí     | Cập nhật DB và API để nhận biến số Tiền      |
| **Kanban Board**  | Tích hợp thư viện kéo thả (dnd-kit), code UI | Cung cấp API cập nhật trạng thái Task        |
| **Gantt Chart**   | Tích hợp thư viện Gantt, map data ngày tháng | Hỗ trợ xuất luồng data chuẩn cho Frontend    |

---

## 🚀 Hướng Dẫn Chạy Dự Án (Local Development)

### 1. Khởi chạy Backend (FastAPI)

```bash
cd Backend
# Tạo môi trường ảo và cài đặt thư viện (nếu cần)
pip install -r requirements.txt
# Chạy server
uvicorn main:app --reload
```

### 2. Khởi chạy Frontend (ReactJS)

```bash
cd Frontend
# Cài đặt thư viện
npm install
# Khởi chạy server development
npm run dev
```
