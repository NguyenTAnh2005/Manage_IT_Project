"""
Test script for Projects CRUD API
Tests all endpoints with various scenarios
"""

import asyncio
import httpx
import json
from typing import Optional

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 30.0

# Test data
TEST_USER_1 = {
    "email": "test_user_1@example.com",
    "password": "TestPass@123",
    "full_name": "Test User 1"
}

TEST_USER_2 = {
    "email": "test_user_2@example.com",
    "password": "TestPass@456",
    "full_name": "Test User 2"
}

TEST_PROJECT_1 = {
    "project_code": "PRJ001",
    "name": "Project A",
    "description": "This is project A"
}

TEST_PROJECT_2 = {
    "project_code": "PRJ002",
    "name": "Project B",
    "description": "This is project B"
}

TEST_PROJECT_UPDATE = {
    "name": "Project A Updated",
    "description": "Updated description"
}


class TestClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = None
        self.user1_token = None
        self.user2_token = None
        self.project1_id = None
        self.project2_id = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=TIMEOUT)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def print_result(self, title: str, status_code: int, data: dict = None):
        """Print test result"""
        print(f"\n{'='*60}")
        print(f"Test: {title}")
        print(f"Status: {status_code}")
        if data:
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print(f"{'='*60}")
    
    async def register_user(self, user_data: dict) -> Optional[str]:
        """Register a new user and return access token"""
        print(f"\n[REGISTER] Registering user: {user_data['email']}")
        
        try:
            response = await self.client.post("/auth/register", json=user_data)
            self.print_result(f"Register {user_data['email']}", response.status_code, response.json())
            
            if response.status_code == 201:
                token = response.json().get("access_token")
                return token
            return None
        except Exception as e:
            print(f"Error registering user: {e}")
            return None
    
    async def create_project(self, project_data: dict, token: str) -> Optional[int]:
        """Create a new project and return project ID"""
        print(f"\n[CREATE] Creating project: {project_data.get('name')}")
        
        try:
            response = await self.client.post(
                "/projects",
                json=project_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            self.print_result(f"Create project {project_data.get('name')}", response.status_code, response.json())
            
            if response.status_code == 201:
                project_id = response.json().get("id")
                return project_id
            return None
        except Exception as e:
            print(f"Error creating project: {e}")
            return None
    
    async def list_projects(self, token: str) -> dict:
        """List all projects for current user"""
        print(f"\n[LIST] Getting projects list")
        
        try:
            response = await self.client.get(
                "/projects",
                headers={"Authorization": f"Bearer {token}"}
            )
            self.print_result("List projects", response.status_code, response.json())
            return response.json()
        except Exception as e:
            print(f"Error listing projects: {e}")
            return {}
    
    async def get_project(self, project_id: int, token: str) -> dict:
        """Get a single project"""
        print(f"\n[GET] Getting project: {project_id}")
        
        try:
            response = await self.client.get(
                f"/projects/{project_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            self.print_result(f"Get project {project_id}", response.status_code, response.json())
            return response.json()
        except Exception as e:
            print(f"Error getting project: {e}")
            return {}
    
    async def update_project(self, project_id: int, project_data: dict, token: str) -> dict:
        """Update a project"""
        print(f"\n[UPDATE] Updating project: {project_id}")
        
        try:
            response = await self.client.put(
                f"/projects/{project_id}",
                json=project_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            self.print_result(f"Update project {project_id}", response.status_code, response.json())
            return response.json()
        except Exception as e:
            print(f"Error updating project: {e}")
            return {}
    
    async def delete_project(self, project_id: int, token: str) -> dict:
        """Delete a project"""
        print(f"\n[DELETE] Deleting project: {project_id}")
        
        try:
            response = await self.client.delete(
                f"/projects/{project_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            self.print_result(f"Delete project {project_id}", response.status_code, response.json())
            return response.json()
        except Exception as e:
            print(f"Error deleting project: {e}")
            return {}


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PROJECTS CRUD API - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    async with TestClient(BASE_URL) as client:
        # Test 1: Register users
        print("\n\n--- TEST 1: User Registration ---")
        client.user1_token = await client.register_user(TEST_USER_1)
        client.user2_token = await client.register_user(TEST_USER_2)
        
        if not client.user1_token or not client.user2_token:
            print("ERROR: Failed to register users. Stopping tests.")
            return
        
        # Test 2: Create projects
        print("\n\n--- TEST 2: Create Projects ---")
        client.project1_id = await client.create_project(TEST_PROJECT_1, client.user1_token)
        client.project2_id = await client.create_project(TEST_PROJECT_2, client.user1_token)
        
        if not client.project1_id or not client.project2_id:
            print("ERROR: Failed to create projects. Stopping tests.")
            return
        
        # Test 3: List projects
        print("\n\n--- TEST 3: List Projects ---")
        projects_list = await client.list_projects(client.user1_token)
        
        if isinstance(projects_list, list) and len(projects_list) >= 2:
            print("✓ List projects successful")
        else:
            print("✗ List projects failed")
        
        # Test 4: Get single project
        print("\n\n--- TEST 4: Get Single Project ---")
        project = await client.get_project(client.project1_id, client.user1_token)
        
        if project.get("id") == client.project1_id:
            print("✓ Get project successful")
        else:
            print("✗ Get project failed")
        
        # Test 5: Update project
        print("\n\n--- TEST 5: Update Project ---")
        updated = await client.update_project(client.project1_id, TEST_PROJECT_UPDATE, client.user1_token)
        
        if updated.get("name") == TEST_PROJECT_UPDATE["name"]:
            print("✓ Update project successful")
        else:
            print("✗ Update project failed")
        
        # Test 6: Permission check - User 2 cannot access User 1's project
        print("\n\n--- TEST 6: Permission Check - Cannot Access Other User's Project ---")
        response = await client.client.get(
            f"/projects/{client.project1_id}",
            headers={"Authorization": f"Bearer {client.user2_token}"}
        )
        client.print_result("Get project (unauthorized)", response.status_code, response.json())
        
        if response.status_code == 403:
            print("✓ Permission check successful (403 Forbidden)")
        else:
            print("✗ Permission check failed")
        
        # Test 7: Permission check - User 2 cannot delete User 1's project
        print("\n\n--- TEST 7: Permission Check - Cannot Delete Other User's Project ---")
        response = await client.client.delete(
            f"/projects/{client.project1_id}",
            headers={"Authorization": f"Bearer {client.user2_token}"}
        )
        client.print_result("Delete project (unauthorized)", response.status_code, response.json())
        
        if response.status_code == 403:
            print("✓ Permission check successful (403 Forbidden)")
        else:
            print("✗ Permission check failed")
        
        # Test 8: Delete project
        print("\n\n--- TEST 8: Delete Project ---")
        deleted = await client.delete_project(client.project1_id, client.user1_token)
        
        if deleted.get("message") == "Dự án đã được xóa":
            print("✓ Delete project successful")
        else:
            print("✗ Delete project failed")
        
        # Test 9: Verify project is deleted (404)
        print("\n\n--- TEST 9: Verify Project is Deleted ---")
        response = await client.client.get(
            f"/projects/{client.project1_id}",
            headers={"Authorization": f"Bearer {client.user1_token}"}
        )
        client.print_result("Get deleted project", response.status_code, response.json())
        
        if response.status_code == 404:
            print("✓ Project successfully deleted (404 Not Found)")
        else:
            print("✗ Project deletion verification failed")
        
        # Test 10: List projects after deletion
        print("\n\n--- TEST 10: List Projects After Deletion ---")
        projects_list = await client.list_projects(client.user1_token)
        
        if isinstance(projects_list, list) and len(projects_list) == 1:
            print("✓ List projects after deletion successful")
        else:
            print("✗ List projects after deletion failed")
        
        print("\n\n" + "="*60)
        print("TEST SUITE COMPLETED")
        print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
