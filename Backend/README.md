# 🚀 Backend - IT Project Management System

Backend API cho Hệ Thống Quản Trị Dự Án CNTT được xây dựng bằng **FastAPI** + **PostgreSQL** + **SQLAlchemy**.

---

## 📋 Mục lục

- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Cài đặt](#-cài-đặt)
- [Cấu hình môi trường](#-cấu-hình-môi-trường)
- [Khởi chạy](#-khởi-chạy)
- [API Documentation](#-api-documentation)
- [Cấu trúc project](#-cấu-trúc-project)
- [Các lệnh hữu ích](#-các-lệnh-hữu-ích)

---

## 💻 Yêu cầu hệ thống

Trước khi cài đặt, đảm bảo bạn có:

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download](https://www.postgresql.org/download/)
- **pip** - Python package manager (thường đi kèm Python)
- **Git** - [Download](https://git-scm.com/)

### Kiểm tra phiên bản:

```bash
python --version
psql --version
pip --version
```

---

## 📦 Cài đặt

### 1️⃣ Clone dự án

```bash
git clone <repository-url>
cd Manage_IT_Project/Backend
```

### 2️⃣ Tạo môi trường ảo (Virtual Environment)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Cài đặt dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Cấu hình môi trường

### 1️⃣ Tạo file `.env`

```bash
# Copy file example
cp .env.example .env

# Hoặc tạo file .env mới
```

### 2️⃣ Cấu hình `.env`

Mở file `.env` và điền thông tin:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/QTDA

# JWT
SECRET_KEY=your-random-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# App
APP_NAME=IT Project Management System
DEBUG=True
```

**Lưu ý:**

- Thay `your_password` bằng mật khẩu PostgreSQL của bạn
- Thay `QTDA` bằng tên database của bạn (hoặc tạo database mới)
- Sinh random SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

---

## 🗄️ Cấu hình Database

### 1️⃣ Tạo database PostgreSQL

```bash
# Mở terminal/cmd PostgreSQL
psql -U postgres

# Hoặc dùng pgAdmin (GUI tool)
```

```sql
-- Tạo database
CREATE DATABASE QTDA;

-- Xem danh sách database
\l
```

### 2️⃣ Chạy Alembic migrations (tạo bảng)

```bash
# Xem các migration sẵn có
alembic history

# Apply tất cả migrations
alembic upgrade head

# Hoặc apply từng migration
alembic upgrade <revision>
```

**Các bảng được tạo:**

- `users` - Người dùng
- `projects` - Dự án
- `project_members` - Thành viên dự án
- `tasks` - Công việc

---

## 🚀 Khởi chạy

### 1️⃣ Chạy server development

```bash
# Tự động reload khi code thay đổi
uvicorn main:app --reload

# Server sẽ chạy ở: http://localhost:8000
```

### 2️⃣ Kiểm tra server

```bash
# Health check
curl http://localhost:8000/health

# Response: {"status": "ok"}
```

---

## 📚 API Documentation

### Swagger UI (Interactive API Docs)

```
http://localhost:8000/docs
```

### ReDoc (Alternative API Docs)

```
http://localhost:8000/redoc
```

### Root endpoint

```
GET http://localhost:8000/
```

---

## 📁 Cấu trúc project

```
Backend/
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   ├── env.py                 # Alembic config
│   └── script.py.mako         # Migration template
│
├── app/
│   ├── core/
│   │   ├── config.py          # Cấu hình ứng dụng
│   │   ├── database.py        # Database setup
│   │   ├── security.py        # JWT & password hashing
│   │   ├── dependencies.py    # Dependency injection
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── __init__.py
│   │
│   ├── crud/
│   │   ├── user.py            # User database operations
│   │   └── __init__.py
│   │
│   ├── models/
│   │   ├── __init__.py        # SQLAlchemy models (User, Project, Task, etc.)
│   │
│   ├── routers/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── user.py            # User endpoints
│   │   └── __init__.py
│   │
│   ├── schemas/
│   │   ├── user.py            # Pydantic schemas (Request/Response models)
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── main.py                     # FastAPI app entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (Gitignored)
├── .env.example               # Environment template (Commit vào git)
├── alembic.ini                # Alembic config
└── README.md                  # Documentation
```

---

## 🛠️ Các lệnh hữu ích

### Database Migrations

```bash
# Tạo migration mới (auto-detect changes)
alembic revision --autogenerate -m "description"

# Apply all migrations
alembic upgrade head

# Rollback migration cuối cùng
alembic downgrade -1

# Xem migration history
alembic history

# Xem current version
alembic current
```

### Python & Pip

```bash
# Cập nhật dependencies
pip install -r requirements.txt --upgrade

# Xuất dependencies ra file (sau khi add package mới)
pip freeze > requirements.txt

# List tất cả packages
pip list
```

### Server

```bash
# Chạy production (không reload)
uvicorn main:app --host 0.0.0.0 --port 8000

# Chạy development (auto reload)
uvicorn main:app --reload

# Chạy trên port khác
uvicorn main:app --reload --port 8001
```

### Virtual Environment

```bash
# Deactivate venv
deactivate

# Remove venv
rm -r venv  # macOS/Linux
rmdir /s venv  # Windows
```

---

## 🔐 Security Notes

⚠️ **IMPORTANT - Trước khi deploy production:**

1. **Thay SECRET_KEY**

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Tắt DEBUG mode**

   ```bash
   DEBUG=False
   ```

3. **Dùng environment variables** thay vì hard-code passwords

4. **HTTPS only** - Dùng reverse proxy (nginx, Cloudflare)

5. **CORS config** - Hạn chế origins thay vì `"*"`

6. **Database backups** - Backup thường xuyên

---

## 🐛 Troubleshooting

### Lỗi: "ModuleNotFoundError: No module named 'app'"

```bash
# Đảm bảo bạn ở folder Backend
cd Backend

# Cài lại dependencies
pip install -r requirements.txt
```

### Lỗi: "psycopg2 or asyncpg driver not installed"

```bash
pip install asyncpg
pip install psycopg2-binary
```

### Lỗi: "Database does not exist"

```bash
# Tạo database PostgreSQL
psql -U postgres -c "CREATE DATABASE QTDA;"

# Hoặc kiểm tra DATABASE_URL trong .env
```

### Lỗi: "Connection refused - PostgreSQL not running"

```bash
# Kiểm tra PostgreSQL status
# Windows: Task Manager → PostgreSQL
# macOS: brew services list
# Linux: systemctl status postgresql
```

### Port 8000 đã được sử dụng

```bash
# Chạy trên port khác
uvicorn main:app --reload --port 8001
```

---

## 📞 Support

Nếu gặp vấn đề:

1. Kiểm tra logs trong terminal
2. Xem lại `.env` configuration
3. Đảm bảo PostgreSQL đang chạy
4. Kiểm tra database migration status

---

## 📝 API Endpoints Overview

### Authentication

- `POST /auth/register` - Đăng ký tài khoản
- `POST /auth/login` - Đăng nhập

### User

- `GET /users/me` - Lấy thông tin user hiện tại (cần auth)
- `POST /users/logout` - Đăng xuất
- `POST /users/refresh` - Refresh access token

### Projects (Coming Soon)

- `GET /projects` - Danh sách dự án
- `POST /projects` - Tạo dự án mới
- `GET /projects/{id}` - Chi tiết dự án
- `PUT /projects/{id}` - Cập nhật dự án
- `DELETE /projects/{id}` - Xóa dự án

### Tasks (Coming Soon)

- `GET /projects/{id}/tasks` - Danh sách công việc
- `POST /projects/{id}/tasks` - Tạo công việc mới
- `GET /tasks/{id}` - Chi tiết công việc
- `PUT /tasks/{id}` - Cập nhật công việc
- `DELETE /tasks/{id}` - Xóa công việc

---

**Happy Coding! 🎉**

Viết bởi: Team Backend
Cập nhật: 13/04/2026
