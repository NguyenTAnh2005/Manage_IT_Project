# Projects CRUD API - Complete Implementation Guide

## Executive Summary

Successfully implemented full CRUD functionality for project management with:

- ✓ Database operations (create, read, update, delete)
- ✓ RESTful API endpoints with proper HTTP status codes
- ✓ Authentication and authorization checks
- ✓ Comprehensive error handling with Vietnamese messages
- ✓ Data validation with Pydantic
- ✓ Logging for important operations
- ✓ Permission-based access control

## Files Created

### 1. `Backend/app/crud/project.py` (NEW)

**Purpose:** Database access layer for project operations

**Functions:**

```python
create_project(db, user_id, project_code, project_name, description) -> Project
get_project_by_id(db, project_id) -> Project | None
get_projects_by_user(db, user_id) -> List[Project]
update_project(db, project_id, **kwargs) -> Project | None
delete_project(db, project_id) -> bool
check_project_permission(db, project_id, user_id, require_pm=False) -> bool
check_project_ownership(db, project_id, user_id) -> bool
```

**Key Features:**

- Async/await for non-blocking database operations
- Automatic project owner (PM role) assignment on creation
- Permission validation: only PM can modify/delete
- Member checking via ProjectMember join table
- Cascade delete support (deletes tasks and members)

### 2. `Backend/app/schemas/project.py` (NEW)

**Purpose:** Request/response validation and serialization

**Classes:**

```python
ProjectCreate(BaseModel)
  - project_code: str (1-50 chars, unique)
  - name: str (1-255 chars)
  - description: Optional[str] (0-1000 chars)

ProjectUpdate(BaseModel)
  - name: Optional[str] (1-255 chars)
  - description: Optional[str] (0-1000 chars)

ProjectResponse(BaseModel)
  - id: int
  - project_code: str
  - name: str
  - description: Optional[str]
  - created_at: datetime
  - updated_at: Optional[datetime]

ProjectDetailResponse(BaseModel)
  - Same as ProjectResponse

ErrorResponse(BaseModel)
  - detail: str
  - status_code: int
```

**Validation Features:**

- Field length limits enforced
- Whitespace trimming
- Vietnamese error messages
- Field-specific validators
- SQLAlchemy model conversion support

### 3. `Backend/app/routers/project.py` (NEW)

**Purpose:** HTTP API endpoints for project operations

**Endpoints:**

#### GET /projects

List all projects for authenticated user

```
- Authentication: Required (JWT Bearer token)
- Response: List[ProjectResponse] (200 OK)
- Errors: 401 (Unauthorized), 500 (Server Error)
```

#### POST /projects

Create a new project

```
- Authentication: Required
- Request: ProjectCreate
- Response: ProjectResponse (201 Created)
- Errors:
  - 401: Unauthorized
  - 409: Project code already exists
  - 422: Validation error
  - 500: Server error
```

#### GET /projects/{project_id}

Get single project (if user has access)

```
- Authentication: Required
- Response: ProjectResponse (200 OK)
- Errors:
  - 401: Unauthorized
  - 403: No permission
  - 404: Project not found
  - 500: Server error
```

#### PUT /projects/{project_id}

Update project (PM only)

```
- Authentication: Required
- Authorization: User must be PM
- Request: ProjectUpdate
- Response: ProjectResponse (200 OK)
- Errors:
  - 401: Unauthorized
  - 403: Not PM
  - 404: Project not found
  - 422: Validation error
  - 500: Server error
```

#### DELETE /projects/{project_id}

Delete project (PM only)

```
- Authentication: Required
- Authorization: User must be PM
- Response: {"message": "Dự án đã được xóa"} (200 OK)
- Errors:
  - 401: Unauthorized
  - 403: Not PM
  - 404: Project not found
  - 500: Server error
```

### 4. `Backend/main.py` (MODIFIED)

**Changes:**

- Added project router import: `from app.routers import auth, user, project`
- Registered router: `app.include_router(project.router)`

## API Error Messages (Vietnamese)

| Status | Scenario          | Message                                         |
| ------ | ----------------- | ----------------------------------------------- |
| 401    | No/Invalid token  | "Yêu cầu đăng nhập"                             |
| 403    | No permission     | "Bạn không có quyền truy cập/sửa/xóa dự án này" |
| 404    | Project not found | "Dự án không tồn tại"                           |
| 409    | Duplicate code    | "Mã dự án đã tồn tại"                           |
| 422    | Invalid data      | "Dữ liệu không hợp lệ" + field messages         |
| 500    | Server error      | "Có lỗi xảy ra, vui lòng thử lại"               |

## Database Schema

The implementation uses existing models from `Backend/app/models/__init__.py`:

```python
class Project(Base):
    __tablename__ = "projects"

    id: int (Primary Key)
    project_code: str (Unique, 1-50 chars)
    name: str (1-255 chars)
    description: Text (Optional, 0-1000 chars)
    created_at: DateTime (auto-set on creation)
    updated_at: DateTime (auto-update on modification)

    # Relationships
    members: List[ProjectMember] (cascade delete)
    tasks: List[Task] (cascade delete)

class ProjectMember(Base):
    __tablename__ = "project_members"

    id: int (Primary Key)
    user_id: int (Foreign Key to users)
    project_id: int (Foreign Key to projects)
    role: RoleEnum (PM or MEMBER)
    created_at: DateTime (auto-set on creation)

    # Relationships
    user: User
    project: Project

class RoleEnum(str, Enum):
    PM = "PM"           # Project Manager (full control)
    MEMBER = "MEMBER"   # Team Member (read-only)
```

## Access Control Rules

| Action            | Owner/PM | Member | Non-member |
| ----------------- | -------- | ------ | ---------- |
| List own projects | ✓        | ✓      | ✗          |
| View project      | ✓        | ✓      | ✗          |
| Create project    | ✓        | -      | -          |
| Update project    | ✓        | ✗      | ✗          |
| Delete project    | ✓        | ✗      | ✗          |
| Add members       | ✓        | ✗      | ✗          |

## Implementation Details

### Automatic User Assignment

When creating a project, the current user is automatically:

1. Added to the project_members table
2. Assigned the PM (Project Manager) role
3. Given full control over the project

### Project Code Uniqueness

- `project_code` is unique across all projects
- Attempting to create duplicate → 409 Conflict error
- Cannot be updated (only name and description are updatable)

### Cascade Delete

When a project is deleted:

- All related ProjectMembers are deleted
- All related Tasks and their subtasks are deleted
- Complete cleanup via SQLAlchemy cascade rules

### Timestamps

- `created_at`: Set automatically on creation, never changes
- `updated_at`: Set on creation, auto-updated on any modification

### Logging

Important operations are logged:

```python
logger.info(f"Created project: {project.id} - {project.name} by user {user_id}")
logger.info(f"Listed {count} projects for user {user_id}")
logger.info(f"Updated project: {project_id}")
logger.info(f"Deleted project: {project_id}")
logger.error(f"Operation failed: {error}")
```

## Testing

### Validation Script

```bash
# Quick validation of all imports
python Backend\validate_projects_crud.py
```

### Test Suite

```bash
# Comprehensive API testing (requires running server)
python Backend\test_projects.py
```

### Manual Testing with cURL

```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Password@123",
    "full_name": "Test User"
  }'

# Create project
curl -X POST http://localhost:8000/projects \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project_code": "PRJ001",
    "name": "My Project",
    "description": "Project description"
  }'

# List projects
curl http://localhost:8000/projects \
  -H "Authorization: Bearer <token>"

# Get project
curl http://localhost:8000/projects/1 \
  -H "Authorization: Bearer <token>"

# Update project
curl -X PUT http://localhost:8000/projects/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Project Name"
  }'

# Delete project
curl -X DELETE http://localhost:8000/projects/1 \
  -H "Authorization: Bearer <token>"
```

### Interactive API Documentation

When server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Field Validation Rules

### project_code

- Required
- 1-50 characters
- Must be unique
- No whitespace-only values
- Used as project identifier

### name

- Required
- 1-255 characters
- Cannot be only whitespace
- Human-readable project name

### description

- Optional (can be null)
- Maximum 1000 characters
- Can be empty string or null

## Type Safety

All functions use proper type hints:

```python
async def create_project(...) -> Project:
async def get_projects_by_user(...) -> List[Project]:
async def check_project_permission(...) -> bool:
```

Uses modern Python 3.10+ syntax:

- `Project | None` instead of `Optional[Project]`
- `List[Project]` from typing for response_model compatibility
- Async/await for all I/O operations

## Dependencies

- **FastAPI**: HTTP framework
- **SQLAlchemy**: ORM with async support
- **Pydantic**: Data validation
- **python-jose**: JWT token handling
- **passlib**: Password hashing

## Security Considerations

1. **Authentication**: All endpoints require valid JWT token
2. **Authorization**: Permission checks enforce access control
3. **Data Validation**: Pydantic ensures type safety and constraints
4. **SQL Injection**: SQLAlchemy ORM prevents injection attacks
5. **Password Hashing**: Uses bcrypt (never plaintext)
6. **Unique Constraints**: Database enforces project_code uniqueness

## Performance Optimizations

1. **Async Operations**: Non-blocking database queries
2. **Efficient Queries**: Single query joins instead of N+1 queries
3. **Index on Unique Columns**: project_code indexed for fast lookups
4. **Cascade Operations**: Database-level deletion cascades

## Future Enhancements

Possible additions to the implementation:

- Add project members management endpoints
- Add role management (change member roles)
- Add project archived/soft-delete state
- Add project category/tags
- Add project permissions audit trail
- Add bulk project operations
- Add project search/filtering
- Add project statistics/metrics

## Troubleshooting

### Common Issues

**Issue**: 403 Forbidden when accessing own project

- **Cause**: User is not a PM or member of the project
- **Fix**: User must be added to project_members table

**Issue**: 409 Conflict on project creation

- **Cause**: project_code already exists
- **Fix**: Use a unique project_code value

**Issue**: 422 Unprocessable Entity

- **Cause**: Validation failed on input data
- **Fix**: Check field lengths and required fields

**Issue**: 401 Unauthorized

- **Cause**: Token missing, invalid, or expired
- **Fix**: Get new token via /auth/register or /users/refresh

## Verification Checklist

- [x] CRUD operations implemented
- [x] Authentication required on all endpoints
- [x] Authorization checks for ownership/PM role
- [x] Vietnamese error messages
- [x] Data validation with Pydantic
- [x] Database cascading deletes
- [x] Automatic timestamp management
- [x] Logging for important operations
- [x] Proper HTTP status codes
- [x] Type hints for all functions
- [x] Project router registered in main.py
- [x] Documentation and test files

## Summary

The Projects CRUD implementation provides a complete, production-ready API for project management with:

- Full authentication and authorization
- Comprehensive error handling
- Data validation
- Logging and monitoring
- Type safety
- RESTful design
- Vietnamese localization

All requirements have been met and the implementation is ready for integration and testing.
