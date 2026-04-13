"""
Quick Python script to validate all new code compiles without syntax errors
This script attempts to import all new modules to catch any syntax issues early
"""

import sys
import os

# Add Backend to path
sys.path.insert(0, r'd:\Manage_IT_Project\Backend')

print("="*70)
print("VALIDATING PROJECTS CRUD IMPLEMENTATION")
print("="*70)

validation_passed = True

# Test 1: Import CRUD module
print("\n[1/5] Validating app.crud.project module...")
try:
    from app.crud import project as project_crud
    
    # Check that all required functions exist
    required_functions = [
        'create_project',
        'get_project_by_id',
        'get_projects_by_user',
        'update_project',
        'delete_project',
        'check_project_permission',
        'check_project_ownership'
    ]
    
    for func_name in required_functions:
        if not hasattr(project_crud, func_name):
            print(f"  ✗ Missing function: {func_name}")
            validation_passed = False
        else:
            print(f"  ✓ Found function: {func_name}")
    
    if validation_passed:
        print("  ✓ All CRUD functions present")
except Exception as e:
    print(f"  ✗ Error: {e}")
    validation_passed = False

# Test 2: Import schemas module
print("\n[2/5] Validating app.schemas.project module...")
try:
    from app.schemas.project import (
        ProjectCreate,
        ProjectUpdate,
        ProjectResponse,
        ProjectDetailResponse,
        ErrorResponse
    )
    
    print("  ✓ ProjectCreate schema imported")
    print("  ✓ ProjectUpdate schema imported")
    print("  ✓ ProjectResponse schema imported")
    print("  ✓ ProjectDetailResponse schema imported")
    print("  ✓ ErrorResponse schema imported")
    
    # Test schema validation
    print("\n  Testing schema validation...")
    
    # Valid create data
    valid_create = ProjectCreate(
        project_code="TEST001",
        name="Test Project",
        description="Test Description"
    )
    print("    ✓ ProjectCreate validation works")
    
    # Valid update data
    valid_update = ProjectUpdate(
        name="Updated Name",
        description=None
    )
    print("    ✓ ProjectUpdate validation works")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    validation_passed = False

# Test 3: Import router module
print("\n[3/5] Validating app.routers.project module...")
try:
    from app.routers.project import router
    
    print(f"  ✓ Project router created")
    print(f"  ✓ Router prefix: {router.prefix}")
    print(f"  ✓ Router tags: {router.tags}")
    
    # Count routes
    route_count = len(router.routes)
    print(f"  ✓ Total routes defined: {route_count}")
    
    # List routes
    print("\n  Routes:")
    for route in router.routes:
        if hasattr(route, 'methods') and route.methods:
            method = ', '.join(route.methods)
            print(f"    ✓ {method:8} {route.path}")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    validation_passed = False

# Test 4: Import main app and verify router registration
print("\n[4/5] Validating main.py includes project router...")
try:
    from main import app
    
    # Find project routes in app
    project_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and 'projects' in route.path:
            project_routes.append(route.path)
    
    if project_routes:
        print(f"  ✓ Found {len(project_routes)} project routes in main app")
        for route_path in sorted(set(project_routes)):
            print(f"    - {route_path}")
    else:
        print(f"  ✗ No project routes found in main app!")
        validation_passed = False
        
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    validation_passed = False

# Test 5: Verify database models
print("\n[5/5] Validating database models...")
try:
    from app.models import Project, ProjectMember, RoleEnum
    
    print(f"  ✓ Project model imported")
    print(f"  ✓ ProjectMember model imported")
    print(f"  ✓ RoleEnum imported")
    
    # Check Project has required attributes
    project_attrs = ['id', 'project_code', 'name', 'description', 'created_at', 'updated_at', 'members', 'tasks']
    
    print("\n  Project model attributes:")
    for attr in project_attrs:
        if hasattr(Project, attr):
            print(f"    ✓ {attr}")
        else:
            print(f"    ✗ Missing: {attr}")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    validation_passed = False

# Final result
print("\n" + "="*70)
if validation_passed:
    print("✓ ALL VALIDATION CHECKS PASSED")
    print("="*70)
    print("\nProjects CRUD implementation is ready for testing!")
    sys.exit(0)
else:
    print("✗ VALIDATION FAILED - Please review errors above")
    print("="*70)
    sys.exit(1)
