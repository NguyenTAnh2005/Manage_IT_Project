# 🚀 Backend - IT Project Management System

Backend API cho **Hệ Thống Quản Trị Dự Án CNTT** được xây dựng bằng:

- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL + SQLAlchemy (ORM)
- **Async:** asyncpg + async sessions
- **Migration:** Alembic
- **Authentication:** JWT + Bcrypt

---

## 📋 Mục lục

1. [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
2. [Cài đặt (Clone Lần Đầu)](#-cài-đặt-clone-lần-đầu)
3. [Cấu hình PostgreSQL](#-cấu-hình-postgresql)
4. [Cấu hình File `.env`](#-cấu-hình-file-env)
5. [Cấu hình Alembic](#-cấu-hình-alembic)
6. [Chạy Migrations](#-chạy-migrations)
7. [Khởi chạy Backend](#-khởi-chạy-backend)
8. [API Documentation](#-api-documentation)
9. [Cấu trúc Project](#-cấu-trúc-project)
10. [Troubleshooting](#-troubleshooting)

---

## 💻 Yêu cầu hệ thống

Đảm bảo bạn đã cài:

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/)

### ✅ Kiểm tra phiên bản:

```bash
python --version
psql --version
pip --version
```

---

## 📦 Cài Đặt (Clone Lần Đầu)

### **Bước 1: Clone Repository**

```bash
git clone <repository-url>
cd Manage_IT_Project/Backend
```

### **Bước 2: Tạo Virtual Environment**

```bash
# Windows (CMD)
python -m venv venv
venv\Scripts\activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

✅ **Xác nhận:** Prompt sẽ hiện `(venv)` ở đầu dòng

### **Bước 3: Cài Đặt Dependencies**

```bash
pip install -r requirements.txt
```

✅ Chờ đến khi cài xong tất cả packages

---

## 🗄️ Cấu Hình PostgreSQL

### **Bước 1: Tạo Database**

Mở **pgAdmin** hoặc **psql** và chạy:

```sql
CREATE DATABASE QTDA;
```

### **Bước 2: Xác Nhận Kết Nối**

```bash
psql -U postgres -h localhost -d QTDA
```

Nhập password PostgreSQL. Nếu kết nối OK → `psql (version)` sẽ hiện

---

## ⚙️ Cấu Hình File `.env`

### **Bước 1: Tạo File `.env`**

```bash
# Copy từ file example
cp .env.example .env
```

### **Bước 2: Điền Thông Tin Vào `.env`**

```env
# ========== DATABASE ==========
# Format: postgresql+asyncpg://username:password@host:port/database_name
# asyncpg = driver async (nhanh hơn psycopg2)
# Ví dụ: postgresql+asyncpg://postgres:Lamvu123@localhost:5432/QuanTriDuAn
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/QuanTriDuAn

# ========== SECURITY & JWT ==========
# Tạo SECRET_KEY mạnh: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=b0cc87de129cfa89e85a6e9bddab68cbb678b3eb51a3f9c504c740c1994ea6f8
ALGORITHM=HS256
# Token hết hạn sau 1 ngày (1440 phút)
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ========== FRONTEND (CORS) ==========
# URL của frontend (để CORS headers)
FRONTEND_URL=http://localhost:5500

# ========== EMAIL (Tùy chọn) ==========
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=no-reply@yourdomain.com
MAIL_FROM_NAME=IT Project Management

# ========== APP CONFIG ==========
DEBUG=True
PROJECT_NAME=Quản Lý Dự Án CNTT
```

### **Lưu Ý Quan Trọng:**

- ⚠️ **KHÔNG commit file `.env` lên Git!** (Đã trong `.gitignore`)
- 🔐 **SECRET_KEY:** Sinh key mạnh: `python -c "import secrets; print(secrets.token_hex(32))"`
- 🔑 **DATABASE PASSWORD:** Thay `YOUR_PASSWORD` bằng password PostgreSQL thực tế
- 📧 **EMAIL:** Chỉ cần nếu muốn gửi email (reset password, notifications)

### **Kiểm Tra Kết Nối Database**

```bash
# Test kết nối database từ Python
python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def test():
    async with AsyncSessionLocal() as session:
        await session.execute(text('SELECT 1'))
        print('✅ Database connected!')

asyncio.run(test())
"
```

✅ Nếu thấy `✅ Database connected!` → Config đúng

---

## 🔧 Cấu Hình Alembic

### **Bước 1: Kiểm Tra Alembic**

```bash
alembic --version
```

✅ Nên hiện: `alembic 1.14.0`

### **Bước 2: Cấu Hình `alembic/env.py` (QUAN TRỌNG)**

File `alembic/env.py` đã được cấu hình để **đọc `DATABASE_URL` từ file `.env`** (không hardcode).

✅ **Đã tự động:**

- Import `settings` từ `app.core.config`
- Convert async URL (`postgresql+asyncpg://`) → sync URL (`postgresql+psycopg2://`)
- Sử dụng `database_url` cho cả offline và online migrations

```python
# alembic/env.py - Dòng quan trọng:
from app.core.config import settings

# Convert ASYNC -> SYNC
database_url = settings.DATABASE_URL
if "postgresql+asyncpg://" in database_url:
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
```

### **Bước 3: Kiểm Tra `alembic.ini`**

✅ **Dòng 63 - KHÔNG cần hardcode DATABASE_URL:**

```ini
# sqlalchemy.url is read from .env file via alembic/env.py
# See app/core/config.py for DATABASE_URL configuration
```

⚠️ **LƯU Ý:** Không cần sửa gì, Alembic sẽ tự động đọc từ `.env` file

---

## 📊 Chạy Migrations

### **Bước 1: Tạo Migration Đầu Tiên**

```bash
alembic revision --autogenerate -m "init_tables"
```

✅ Sẽ tạo file migration trong `alembic/versions/` (tự động detect models)

### **Bước 2: Áp Dụng Migration (Tạo Tables)**

```bash
alembic upgrade head
```

✅ Output sẽ hiện:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.migration] Running upgrade... -> xxxxx, init_tables
```

✅ Sẽ tạo 4 tables trong PostgreSQL:

- `users` - Người dùng
- `projects` - Dự án
- `project_members` - Thành viên dự án
- `tasks` - Công việc

### **Bước 3: Kiểm Tra Kết Quả**

```bash
# Xem current migration version
alembic current
```

✅ Output:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
xxxxx (head)
```

**Kiểm tra pgAdmin:**

Mở **pgAdmin** → Database `QuanTriDuAn` → Schemas → public → Tables

Nên thấy 4 bảng mới với các columns tương ứng

---

## 🚀 Khởi Chạy Backend

### **Bước 1: Chạy Server**

```bash
uvicorn main:app --reload
```

✅ Output sẽ hiện:

```
Uvicorn running on http://127.0.0.1:8000
```

### **Bước 2: Truy Cập Swagger UI**

Mở browser → `http://localhost:8000/docs`

✅ Nên thấy Swagger UI với API documentation

---

## 📚 API Documentation

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

## 📁 Cấu Trúc Project

```
Backend/
├── alembic/                 # Database migrations
│   ├── versions/           # Các migration files
│   ├── env.py             # Config Alembic
│   └── script.py.mako     # Template migration
├── app/
│   ├── core/
│   │   ├── config.py      # Load config từ .env
│   │   ├── database.py    # Setup PostgreSQL async
│   │   ├── security.py    # JWT + Bcrypt
│   │   └── exceptions.py  # Custom exceptions
│   ├── crud/              # CRUD operations
│   │   ├── crud_user.py
│   │   └── ...
│   ├── models/
│   │   └── model.py       # SQLAlchemy models
│   ├── routers/           # API endpoints
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── ...
│   ├── schemas/           # Pydantic schemas
│   │   ├── sc_user.py
│   │   └── ...
│   └── utils/
│       ├── constants.py
│       └── validators.py
├── main.py               # FastAPI app entry point
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables (KHÔNG commit!)
├── alembic.ini         # Alembic config
└── README.md           # File này
```

---

## 🛠️ Các Lệnh Hữu Ích

### **Alembic Commands**

```bash
# Tạo migration mới
alembic revision --autogenerate -m "message"

# Xem history migrations
alembic history

# Xem current version
alembic current

# Rollback lần migration gần nhất
alembic downgrade -1

# Downgrade tất cả
alembic downgrade base

# Xem các branches
alembic branches
```

### **Server Commands**

```bash
# Chạy development server
uvicorn main:app --reload

# Chạy production server (port 8000)
uvicorn main:app --host 0.0.0.0 --port 8000

# Chạy trên port khác
uvicorn main:app --port 8001 --reload
```

---

## 🐛 Troubleshooting

### **Lỗi: "Can't locate revision"**

```
ERROR [alembic.util.messaging] Can't locate revision identified by 'xxxxx'
```

✅ **Giải pháp:**

```bash
# Xóa migration history và tạo lại
rm alembic/versions/*.py  # Xóa các migration cũ
alembic revision --autogenerate -m "init_tables"
alembic upgrade head
```

---

### **Lỗi: "database does not exist"**

```
FATAL: database "QuanTriDuAn" does not exist
```

✅ **Giải pháp:**

1. Tạo database trong PostgreSQL:

```bash
psql -U postgres -c "CREATE DATABASE QuanTriDuAn;"
```

2. Hoặc dùng pgAdmin:
   - Kết nối PostgreSQL
   - Right-click "Databases"
   - Create → Database
   - Name: `QuanTriDuAn`
   - Click Create

3. Kiểm tra `.env` có tên database đúng không

---

### **Lỗi: "connection refused - PostgreSQL not running"**

```
could not connect to server: Connection refused
```

✅ **Giải pháp:**

- **Windows:** Kiểm tra Services → PostgreSQL
- **macOS:** `brew services start postgresql`
- **Linux:** `sudo systemctl start postgresql`

---

### **Lỗi: "UnicodeDecodeError in alembic.ini"**

```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x8d
```

✅ **Giải pháp:**

Không thêm comment Tiếng Việt vào `alembic.ini` (chỉ tiếng Anh)

---

### **Lỗi: "greenlet_spawn has not been called"**

```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called
```

✅ **Giải pháp:**

Lỗi này bình thường khi chạy `alembic` (chạy sync, database_url được convert). Bỏ qua!

---

### **Lỗi: "psycopg2 connection failed"**

```
could not connect to server: Connection refused
```

✅ **Giải pháp:**

1. Kiểm tra PostgreSQL đã start chưa
2. Xác nhận username/password trong `.env` đúng
3. Xác nhận database đã tạo chưa
4. Test kết nối:

```bash
python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def test():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text('SELECT 1'))
        print('✅ Database connected!')
    except Exception as e:
        print(f'❌ Error: {e}')

asyncio.run(test())
"
```

---

### **Lỗi: "ModuleNotFoundError"**

```
No module named 'fastapi'
```

✅ **Giải pháp:**

1. Kiểm tra virtual environment đã activate chưa
2. Chạy `pip install -r requirements.txt` lại
3. Chạy `pip list` để verify packages

---

### **Lỗi: "alembic: command not found"**

```
alembic: command not found
```

✅ **Giải pháp:**

1. Kiểm tra virtual environment đã activate chưa
2. Chạy `pip install alembic==1.14.0`

---

### **Lỗi: "SECRET_KEY is not set"**

```
ValueError: SECRET_KEY is not set
```

✅ **Giải pháp:**

1. Kiểm tra file `.env` tồn tại trong folder Backend
2. Xác nhận `SECRET_KEY=...` đã điền vào `.env`
3. Restart server

---

### **Port 8000 đã được sử dụng**

```
Address already in use
```

✅ **Giải pháp:**

```bash
# Chạy trên port khác
uvicorn main:app --reload --port 8001
```

---

### **Lỗi: "Connection reset by peer"**

```
ConnectionResetError: [Errno 104] Connection reset by peer
```

✅ **Giải pháp:**

1. Kiểm tra PostgreSQL còn chạy không
2. Kiểm tra connection pool settings trong `app/core/database.py`
3. Restart PostgreSQL service

---

## 📞 Support

Gặp vấn đề? Check:

1. File `.env` đã cấu hình đúng chưa
2. PostgreSQL đã chạy chưa
3. Virtual environment đã activate chưa
4. Tất cả requirements đã cài chưa

---

## ✅ Checklist Setup Hoàn Chỉnh

- [ ] Python 3.10+ cài sẵn
- [ ] PostgreSQL cài sẵn và chạy
- [ ] Clone repository
- [ ] Tạo virtual environment
- [ ] Cài dependencies (`pip install -r requirements.txt`)
- [ ] Tạo database `QTDA`
- [ ] Tạo file `.env` với đúng config
- [ ] Cấu hình `alembic.ini` và `alembic/env.py`
- [ ] Chạy migrations (`alembic upgrade head`)
- [ ] Khởi chạy server (`uvicorn main:app --reload`)
- [ ] Truy cập `http://localhost:8000/docs` để kiểm tra

🎉 **Nếu tất cả OK → Backend sẵn sàng!**

- Thay `your_password` bằng mật khẩu PostgreSQL của bạn
- Thay `QTDA` bằng tên database của bạn (hoặc tạo database mới)
- Sinh random SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **KHÔNG commit `.env` vào Git!** (File này đã trong `.gitignore`)

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
