"""Test utilities and helper functions."""

import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from fastapi.testclient import TestClient
from httpx import AsyncClient


@dataclass
class UserSession:
    """Represents a user session with tokens and user info."""
    access_token: str
    refresh_token: str


class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_user_data(username: str = "testuser", password: str = "testpassword") -> Dict[str, str]:
        """Create user login data."""
        return {
            "username": username,
            "password": password
        }
    
    @staticmethod
    def create_workspace_data(name: str = "Test Workspace") -> Dict[str, str]:
        """Create workspace data."""
        return {
            "name": name,
        }
    
    @staticmethod
    def create_task_data(
        title: str = "Test Task",
        description: str = "Test task description",
        priority: str = "medium",
        due_date: Optional[str] = None,
        assigned_to_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create task data."""
        data = {
            "title": title,
            "description": description,
            "priority": priority
        }
        if due_date:
            data["due_date"] = due_date
        if assigned_to_user_id:
            data["assigned_to_user_id"] = assigned_to_user_id
        return data
    
    @staticmethod
    def create_group_data(name: str = "Test Group") -> Dict[str, str]:
        """Create group data."""
        return {
            "name": name,
        }


class AuthHelper:
    """Helper for authentication operations."""
    
    @staticmethod
    def login_user(client: TestClient, username: str = "testuser", password: str = "testpassword") -> UserSession:
        """Login a user and return session data."""
        login_data = TestDataFactory.create_user_data(username, password)
        response = client.post("/api/v1/identity/login", json=login_data)
        
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.status_code} - {response.text}")
        
        data = response.json()
        return UserSession(
            access_token=data["accessToken"],
            refresh_token=data["refreshToken"],
        )
    
    @staticmethod
    async def async_login_user(client: AsyncClient, username: str = "testuser", password: str = "testpassword") -> UserSession:
        """Async login a user and return session data."""
        login_data = TestDataFactory.create_user_data(username, password)
        response = await client.post("/api/v1/identity/login", json=login_data)
        
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.status_code} - {response.text}")
        
        data = response.json()
        return UserSession(
            access_token=data["accessToken"],
            refresh_token=data["refreshToken"],
        )
    
    @staticmethod
    def create_authenticated_headers(access_token: str) -> Dict[str, str]:
        """Create headers with authentication token."""
        return {"Authorization": f"Bearer {access_token}"}


class WorkspaceHelper:
    """Helper for workspace operations."""
    
    @staticmethod
    def create_workspace(client: TestClient, session: UserSession, workspace_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a workspace and return the response data."""
        if workspace_data is None:
            workspace_data = TestDataFactory.create_workspace_data()
        
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = client.post("/api/v1/workspaces/", json=workspace_data, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Workspace creation failed: {response.status_code} - {response.text}")
        
        return response.json()
    
    @staticmethod
    async def async_create_workspace(client: AsyncClient, session: UserSession, workspace_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Async create a workspace and return the response data."""
        if workspace_data is None:
            workspace_data = TestDataFactory.create_workspace_data()
        
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = await client.post("/api/v1/workspaces/", json=workspace_data, headers=headers)
        
        if response.status_code != 201:
            raise Exception(f"Workspace creation failed: {response.status_code} - {response.text}")
        
        return response.json()
    
    @staticmethod
    def get_workspaces(client: TestClient, session: UserSession) -> List[Dict[str, Any]]:
        """Get all workspaces for a user."""
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = client.get("/api/v1/workspaces/", headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Get workspaces failed: {response.status_code} - {response.text}")
        
        return response.json()


class TaskHelper:
    """Helper for task operations."""
    
    @staticmethod
    def create_task(
        client: TestClient, 
        session: UserSession, 
        workspace_id: int, 
        group_id: int, 
        task_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a task and return the response data."""
        if task_data is None:
            task_data = TestDataFactory.create_task_data()
        
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = client.post(
            f"/api/v1/workspaces/{workspace_id}/groups/{group_id}/tasks", 
            json=task_data, 
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Task creation failed: {response.status_code} - {response.text}")
        
        return response.json()
    
    @staticmethod
    async def async_create_task(
        client: AsyncClient, 
        session: UserSession, 
        workspace_id: int, 
        group_id: int, 
        task_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Async create a task and return the response data."""
        if task_data is None:
            task_data = TestDataFactory.create_task_data()
        
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = await client.post(
            f"/api/v1/workspaces/{workspace_id}/groups/{group_id}/tasks", 
            json=task_data, 
            headers=headers
        )
        
        if response.status_code != 201:
            raise Exception(f"Task creation failed: {response.status_code} - {response.text}")
        
        return response.json()
    
    @staticmethod
    def update_task(
        client: TestClient, 
        session: UserSession, 
        workspace_id: int, 
        group_id: int, 
        task_id: int, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a task and return the response data."""
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = client.patch(
            f"/api/v1/workspaces/{workspace_id}/groups/{group_id}/tasks/{task_id}", 
            json=update_data, 
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Task update failed: {response.status_code} - {response.text}")
        
        return response.json()
    
    @staticmethod
    def move_task_to_group(
        client: TestClient, 
        session: UserSession, 
        workspace_id: int, 
        current_group_id: int, 
        task_id: int, 
        new_group_id: int
    ) -> Dict[str, Any]:
        """Move a task to a different group."""
        update_data = {"group_id": new_group_id}
        return TaskHelper.update_task(client, session, workspace_id, current_group_id, task_id, update_data)


class PerformanceHelper:
    """Helper for performance testing."""
    
    @staticmethod
    def measure_response_time(func, *args, **kwargs) -> float:
        """Measure the response time of a function."""
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time
    
    @staticmethod
    async def async_measure_response_time(func, *args, **kwargs) -> float:
        """Async measure the response time of a function."""
        start_time = time.perf_counter()
        await func(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time


class DatabaseHelper:
    """Helper for database operations."""
    
    @staticmethod
    def clear_test_data(session):
        """Clear test data from database."""
        # Clear in order to respect foreign key constraints
        from migrations.schema import Authentication, Task, Group, Workspaces, Account, Tenant
        
        session.query(Authentication).delete()
        session.query(Task).delete()
        session.query(Group).delete()
        session.query(Workspaces).delete()
        session.query(Account).delete()
        session.query(Tenant).delete()
        session.commit()
    
    @staticmethod
    def create_test_tenant(session, company_name: str = "Test Company"):
        """Create a test tenant."""
        from migrations.schema import Tenant
        tenant = Tenant(
            name=company_name,
        )
        session.add(tenant)
        session.commit()
        return tenant
    
    @staticmethod
    def create_test_user(session, tenant_id: int, username: str = "testuser", full_name: str = "Test User", password: str = "testpassword"):
        """Create a test user."""
        from argon2 import PasswordHasher
        from migrations.schema import Account
        
        ph = PasswordHasher()
        user = Account(
            tenant_id=tenant_id,
            username=username,
            full_name=full_name,
            email=username + "@example.com",
            hashed_password=ph.hash(password),
        )
        session.add(user)
        session.flush()
        session.commit()

        return user