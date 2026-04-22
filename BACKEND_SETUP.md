# 📚 HƯỚNG DẪN CÁCH SỬ DỤNG THƯ VIỆN - BACKEND

## 🗂️ DANH SÁCH THƯ VIỆN BACKEND

### 1. **WEB FRAMEWORK**

| Thư viện    | Phiên bản | Mục đích                                                                                                                  |
| ----------- | --------- | ------------------------------------------------------------------------------------------------------------------------- |
| **FastAPI** | 0.115.6   | Framework web hiện đại, async-first. Tự động tạo Swagger UI docs, Pydantic validation tích hợp, Dependency Injection mạnh |
| **Uvicorn** | 0.34.0    | ASGI server chạy FastAPI. [standard] = có websockets, httptools, uvloop. Chạy với: `uvicorn main:app --reload`            |

### 2. **DATABASE**

| Thư viện            | Phiên bản | Mục đích                                                                                       |
| ------------------- | --------- | ---------------------------------------------------------------------------------------------- |
| **SQLAlchemy**      | 2.0.45    | ORM mạnh nhất Python. Async/await native (v2.0+), query builder, schema migrations             |
| **asyncpg**         | latest    | Driver ASYNC cho PostgreSQL. Nhanh nhất cho async operations, dùng với SQLAlchemy async engine |
| **psycopg2-binary** | 2.9.11    | Driver SYNC cho PostgreSQL, dùng cho Alembic migrations. Binary = đã compile, cài nhanh        |
| **Alembic**         | 1.14.0    | Migration tool quản lý version DB schema. Commands: `alembic revision --autogenerate -m "msg"` |

### 3. **AUTHENTICATION & SECURITY**

| Thư viện            | Phiên bản | Mục đích                                                                                |
| ------------------- | --------- | --------------------------------------------------------------------------------------- |
| **python-jose**     | 3.3.0     | JWT tokens cho authentication. Tạo & verify access tokens. [cryptography] = mã hóa mạnh |
| **passlib**         | >=1.7.4   | Hash password an toàn với bcrypt. Functions: `hash()`, `verify()`                       |
| **bcrypt**          | 4.1.3     | Backend mã hóa cho passlib. Fix lỗi compatibility với v5.x                              |
| **email-validator** | 2.1.0     | Validate email theo RFC, DNS lookup, normalize email                                    |

### 4. **CONFIGURATION**

| Thư viện              | Phiên bản | Mục đích                                                                            |
| --------------------- | --------- | ----------------------------------------------------------------------------------- |
| **python-dotenv**     | 1.0.1     | Load environment variables từ .env file. Tách config khỏi code (dev/prod khác nhau) |
| **pydantic**          | 2.10.5    | Data validation & settings management. FastAPI dùng cho request/response            |
| **pydantic-settings** | 2.7.0     | BaseSettings class load config từ .env. Priority: env vars > .env > defaults        |

### 5. **KHÁC**

| Thư viện         | Phiên bản | Mục đích                                                                    |
| ---------------- | --------- | --------------------------------------------------------------------------- |
| **slowapi**      | 0.1.9     | Rate limiting bảo vệ API. Ví dụ: `@limiter.limit("5/minute")`               |
| **fastapi-mail** | 1.4.1     | Gửi email SMTP (password reset, verification). Hỗ trợ async, templates HTML |

---

## 🚀 CÀI ĐẶT BACKEND

### Yêu cầu tiên quyết:

- Python 3.9+
- PostgreSQL (hoặc SQLite nếu dev)

### Bước cài:

```bash
# 1. Tạo virtual environment
python -m venv venv

# 2. Kích hoạt (Linux/Mac)
source venv/bin/activate
# Hoặc Windows:
venv\Scripts\activate

# 3. Cài đặt thư viện
pip install -r requirements.txt

# 4. Setup .env file (xem .env.example)
cp .env.example .env
# Sửa DATABASE_URL, SECRET_KEY, vv...

# 5. Chạy migrations
alembic upgrade head

# 6. (Optional) Seed dữ liệu test
python seed_data.py

# 7. Chạy server
uvicorn main:app --reload
```

### Server chạy ở:

- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc Docs: http://localhost:8000/redoc

---

## 📝 THÔNG TIN POSTGRESQL

- **Driver ASYNC**: asyncpg (trong SQLAlchemy async engine)
- **Driver SYNC**: psycopg2-binary (cho migrations qua Alembic)
- **Connection String** (Async): `postgresql+asyncpg://user:password@localhost/dbname`

---
