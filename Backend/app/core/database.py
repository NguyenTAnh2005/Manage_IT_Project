# ========================================
# IMPORTS - ASYNC VERSION
# ========================================

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# create_async_engine: Tạo async engine (thay create_engine)
# AsyncSession: Class cho async database session (thay Session)
# async_sessionmaker: Factory tạo async sessions (thay sessionmaker)

from sqlalchemy.orm import declarative_base
# declarative_base: Vẫn dùng như cũ, không đổi
# Base class cho tất cả models (User, Habit, HabitLog...)

from app.core.config import settings
# settings: Load config từ .env (DATABASE_URL, SECRET_KEY...)


# ========================================
# ASYNC ENGINE - KẾT NỐI DATABASE
# ========================================

engine = create_async_engine(
    settings.DATABASE_URL,  # postgresql+asyncpg://user:pass@localhost/dbname
    echo=False,  # True = print SQL queries (dùng khi debug)
    pool_pre_ping=True,  # Kiểm tra connection còn sống trước khi dùng
    pool_size=5,  # Số connection giữ sẵn trong pool (default: 5)
    max_overflow=10  # Số connection thêm khi cần (default: 10)
)

# GIẢI THÍCH:
# - create_async_engine: Tạo engine async, support await
# - pool_pre_ping: Tự động reconnect nếu connection bị đứt
# - pool_size + max_overflow: Tối đa 15 connections đồng thời


# ========================================
# ASYNC SESSION FACTORY
# ========================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,  # Kết nối tới engine ở trên
    class_=AsyncSession,  # Tạo ra AsyncSession objects
    expire_on_commit=False,  # Không expire objects sau commit (giữ data trong memory)
    autocommit=False,  # Phải gọi commit() thủ công
    autoflush=False  # Phải gọi flush() thủ công
)

# GIẢI THÍCH:
# - async_sessionmaker: Factory pattern, tạo session mới mỗi lần call
# - class_=AsyncSession: Chỉ định tạo AsyncSession (không phải Session sync)
# - expire_on_commit=False: Sau commit, vẫn truy cập được object.field
# - autocommit=False: Phải tự db.commit() khi muốn lưu changes
# - autoflush=False: Phải tự db.flush() khi muốn sync changes với DB


# ========================================
# BASE CLASS CHO MODELS
# ========================================

Base = declarative_base()

# GIẢI THÍCH:
# - Base: Class cha cho tất cả models
# - Mọi model phải inherit từ Base: class User(Base)
# - Base chứa metadata, __tablename__, columns...


# ========================================
# DEPENDENCY INJECTION - LẤY DATABASE SESSION
# ========================================

async def get_db():
    """
    Async generator dependency cho FastAPI
    Tạo database session mới cho mỗi request
    Tự động đóng session sau khi request xong
    
    Cách dùng trong endpoint:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        # async with: Context manager tự động close session
        # AsyncSessionLocal(): Tạo session mới
        yield session
        # yield: Trả session cho endpoint sử dụng
        # Sau khi endpoint xong, code sau yield sẽ chạy (tự động close)

# GIẢI THÍCH CHI TIẾT:
# 1. async def: Function bất đồng bộ, phải dùng await khi gọi
# 2. async with: Async context manager
#    - Tự động gọi session.__aenter__() khi vào
#    - Tự động gọi session.__aexit__() khi ra (đóng connection)
# 3. yield session: 
#    - Tạm dừng function, trả session ra ngoài
#    - Endpoint dùng session để query/insert/update
#    - Sau khi endpoint xong, tiếp tục chạy (cleanup)
# 4. Không cần try/finally như sync version
#    - async with tự động handle cleanup


# ========================================
# SO SÁNH SYNC vs ASYNC
# ========================================

# SYNC (CŨ):
# def get_db():
#     db = SessionLocal()      # Tạo sync session
#     try:
#         yield db              # Trả session
#     finally:
#         db.close()            # Đóng session thủ công

# ASYNC (MỚI):
# async def get_db():
#     async with AsyncSessionLocal() as session:  # Tự động close
#         yield session

# LỢI ÍCH ASYNC:
# ✅ Non-blocking: Khi chờ database, server xử lý request khác
# ✅ Hiệu năng cao hơn với nhiều concurrent requests
# ✅ Code ngắn gọn hơn (không cần try/finally)
# ✅ Tương thích với FastAPI async endpoints
