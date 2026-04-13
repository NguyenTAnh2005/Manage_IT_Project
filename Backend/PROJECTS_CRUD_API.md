# Projects CRUD API - Implementation Summary

## Overview

Implemented full CRUD (Create, Read, Update, Delete) functionality for the Projects management system with complete authentication, authorization, and error handling in Vietnamese.

## Files Created/Modified

### 1. **Backend/app/crud/project.py** (NEW)

Database CRUD operations for projects.

**Functions:**

- `create_project(db, user_id, project_code, project_name, description)` - Creates new project and adds creator as PM
- `get_project_by_id(db, project_id)` - Retrieves single project
- `get_projects_by_user(db, user_id)` - Retrieves all projects where user is a member
- `update_project(db, project_id, **kwargs)` - Updates project fields
- `delete_project(db, project_id)` - Deletes project (cascades to tasks, project_members)
- `check_project_permission(db, project_id, user_id, require_pm=False)` - Verifies user access
- `check_project_ownership(db, project_id, user_id)` - Verifies user is project PM

**Key Features:**

- Async/await for database operations
- Automatic timestamp management (created_at, updated_at)
- Permission checking: only PM can modify/delete
- Logging for important operations
- Cascade delete support

### 2. **Backend/app/schemas/project.py** (NEW)

Pydantic request/response models with validation.

**Models:**

- `ProjectCreate` - Request model for creating projects
  - Fields: project_code (1-50 chars), name (1-255 chars), description (0-1000 chars)
  - Custom validators for all fields
- `ProjectUpdate` - Request model for updating projects
  - Fields: name (optional, 1-255 chars), description (optional, 0-1000 chars)
  - Custom validators for all fields
- `ProjectResponse` - Response model for single project
  - Fields: id, project_code, name, description, created_at, updated_at
- `ProjectDetailResponse` - Response model with full details
- `ErrorResponse` - Error response format

**Key Features:**

- Field length validation
- Optional field support
- Whitespace trimming
- Vietnamese error messages
- from_attributes support for SQLAlchemy models

### 3. **Backend/app/routers/project.py** (NEW)

FastAPI API endpoints for project management.

**Endpoints:**

#### GET /projects

Lists all projects for current user.

```
Response: [ProjectResponse, ...]
Status: 200 OK
Errors: 401 (auth required), 500 (server error)
```

#### POST /projects

Creates new project.

```
Request: ProjectCreate
Response: ProjectResponse
Status: 201 Created
Errors: 401 (auth required), 409 (duplicate project_code), 422 (validation), 500 (server error)
```

#### GET /projects/{project_id}

Gets single project details (permission required).

```
Response: ProjectResponse
Status: 200 OK
Errors: 401 (auth required), 403 (no permission), 404 (not found), 500 (server error)
```

#### PUT /projects/{project_id}

Updates project (PM only).

```
Request: ProjectUpdate
Response: ProjectResponse
Status: 200 OK
Errors: 401 (auth required), 403 (PM required), 404 (not found), 422 (validation), 500 (server error)
```

#### DELETE /projects/{project_id}

Deletes project (PM only).

```
Response: {"message": "Dự án đã được xóa"}
Status: 200 OK
Errors: 401 (auth required), 403 (PM required), 404 (not found), 500 (server error)
```

**Key Features:**

- Authentication via JWT (get_current_user dependency)
- Authorization checks (permission, PM role)
- Vietnamese error messages
- Comprehensive logging
- Proper HTTP status codes
- Exception handling for database integrity

### 4. **Backend/main.py** (MODIFIED)

Updated to include project router.

**Changes:**

```python
# Line 15: Added project to imports
from app.routers import auth, user, project

# Lines 65: Added project router to app
app.include_router(project.router)
```

## Error Handling

All endpoints return Vietnamese error messages:

| Status | Error             | Message                                        |
| ------ | ----------------- | ---------------------------------------------- |
| 401    | Not authenticated | Yêu cầu đăng nhập                              |
| 403    | No permission     | Bạn không có quyền truy cập/sửa/xóa dự án này  |
| 404    | Not found         | Dự án không tồn tại                            |
| 409    | Conflict          | Mã dự án đã tồn tại                            |
| 422    | Validation        | Dữ liệu không hợp lệ + field-specific messages |
| 500    | Server error      | Có lỗi xảy ra, vui lòng thử lại                |

## Testing Scenarios

The implementation supports all CRUD operations:

1. **Create Project**
   - User creates project with unique project_code
   - Creator automatically added as PM
   - timestamps auto-set

2. **Read Projects**
   - List: Get all projects for authenticated user
   - Get Single: Retrieve specific project if user has permission

3. **Update Project**
   - Only PM can update project details
   - Can update name and/or description
   - updated_at timestamp auto-updated

4. **Delete Project**
   - Only PM can delete
   - Cascades to related tasks, project_members
   - Returns success message

5. **Authorization**
   - User can only access own projects
   - Cannot view other users' projects (403)
   - Cannot modify/delete other users' projects (403)
   - Non-PM members can view but not modify (403)

## Project-User Relationship

- Projects use ProjectMember join table
- Each user has a role: PM (Project Manager) or MEMBER
- Creator automatically becomes PM
- PM = Full control (create, read, update, delete)
- MEMBER = Read only

## Database Model Reference

From Backend/app/models/**init**.py:

```python
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    project_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    members = relationship("ProjectMember", back_populates="project")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
```

## Validation Rules

### ProjectCreate

- project_code: Required, 1-50 characters, must be unique
- name: Required, 1-255 characters, cannot be all whitespace
- description: Optional, maximum 1000 characters

### ProjectUpdate

- name: Optional, 1-255 characters if provided
- description: Optional, maximum 1000 characters if provided
- Both fields can be null (not required)

## Logging

Important operations are logged:

- Project creation with user and project info
- Project retrieval with user and project info
- Project updates with IDs
- Project deletion with IDs
- Warnings for duplicate project codes
- Errors with full stack traces

## Development/Testing

Test files included:

- `test_projects.py` - Comprehensive async test suite covering:
  - User registration
  - Project creation
  - Project listing
  - Project retrieval
  - Project updates
  - Permission checks (403 Forbidden)
  - Project deletion
  - Deletion verification (404 Not Found)

- `validate_imports.py` - Quick validation script to verify all imports work

## Dependencies

- FastAPI - Web framework
- SQLAlchemy - ORM with async support
- Pydantic - Data validation
- python-jose - JWT handling
- passlib - Password hashing

## API Documentation

When server is running, access interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

All project endpoints are documented with:

- Request/response models
- Parameter descriptions
- Error responses
- Example values
