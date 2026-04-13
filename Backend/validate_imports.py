"""
Quick validation script - imports all new modules to check for syntax errors
"""

import sys
import os

# Add Backend to path
sys.path.insert(0, r'd:\Manage_IT_Project\Backend')

print("Validating imports...")

try:
    print("1. Importing project CRUD module...")
    from app.crud.project import (
        create_project,
        get_project_by_id,
        get_projects_by_user,
        update_project,
        delete_project,
        check_project_permission,
        check_project_ownership
    )
    print("   ✓ Project CRUD imports successful")
except Exception as e:
    print(f"   ✗ Error importing project CRUD: {e}")
    sys.exit(1)

try:
    print("2. Importing project schemas...")
    from app.schemas.project import (
        ProjectCreate,
        ProjectUpdate,
        ProjectResponse,
        ProjectDetailResponse,
        ErrorResponse
    )
    print("   ✓ Project schemas imports successful")
except Exception as e:
    print(f"   ✗ Error importing project schemas: {e}")
    sys.exit(1)

try:
    print("3. Importing project router...")
    from app.routers.project import router as project_router
    print("   ✓ Project router imports successful")
except Exception as e:
    print(f"   ✗ Error importing project router: {e}")
    sys.exit(1)

try:
    print("4. Importing main app...")
    from main import app
    print("   ✓ Main app imports successful")
except Exception as e:
    print(f"   ✗ Error importing main app: {e}")
    sys.exit(1)

try:
    print("5. Verifying routes are registered...")
    routes = [route.path for route in app.routes]
    project_routes = [r for r in routes if 'projects' in r]
    
    if project_routes:
        print(f"   ✓ Found {len(project_routes)} project routes:")
        for route in project_routes:
            print(f"     - {route}")
    else:
        print("   ✗ No project routes found!")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Error verifying routes: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✓ All validations passed successfully!")
print("="*60)
