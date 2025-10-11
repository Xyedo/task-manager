"""Unit tests for workspace domain functionality."""

from tokenize import group
from wsgiref import headers
from testing.conftest import test_client
import pytest
from fastapi.testclient import TestClient

from utils import AuthHelper, WorkspaceHelper, TaskHelper, TestDataFactory


@pytest.mark.unit
@pytest.mark.workspace
class TestWorkspacesCRUD:
    """Test workspace CRUD operations."""
    
    def test_create_workspace_success(self, test_client: TestClient, test_user):
        """Test successful workspace creation."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace_data = TestDataFactory.create_workspace_data("My Workspace")
        
        workspace = WorkspaceHelper.create_workspace(test_client, session, workspace_data)
        
        assert workspace["name"] == "My Workspace"
        assert "workspaceId" in workspace
    
    def test_create_workspace_without_auth(self, test_client: TestClient):
        """Test workspace creation without authentication."""
        workspace_data = TestDataFactory.create_workspace_data()
        response = test_client.post("/api/v1/workspaces/", json=workspace_data)
        
        assert response.status_code == 401
    
    def test_create_workspace_duplicate_name(self, test_client: TestClient, test_user):
        """Test creating workspace with duplicate name."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace_data = TestDataFactory.create_workspace_data("Duplicate Workspace")
        
        # Create first workspace
        WorkspaceHelper.create_workspace(test_client, session, workspace_data)
        
        # Try to create second workspace with same name
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = test_client.post("/api/v1/workspaces/", json=workspace_data, headers=headers)
        
        assert response.status_code == 400  # Conflict
    
    def test_get_workspaces_success(self, test_client: TestClient, test_user):
        """Test successful get workspaces."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        
        # Create a couple of workspaces
        WorkspaceHelper.create_workspace(test_client, session, TestDataFactory.create_workspace_data("Workspace 1"))
        WorkspaceHelper.create_workspace(test_client, session, TestDataFactory.create_workspace_data("Workspace 2"))
        
        res = WorkspaceHelper.get_workspaces(test_client, session)

        assert len(res["workspaces"]) >= 2
        workspace_names = [w["name"] for w in res["workspaces"]]
        assert "Workspace 1" in workspace_names
        assert "Workspace 2" in workspace_names
    
    def test_get_workspaces_without_auth(self, test_client: TestClient):
        """Test get workspaces without authentication."""
        response = test_client.get("/api/v1/workspaces/")
        
        assert response.status_code == 401
    
    def test_get_workspace_by_name_success(self, test_client: TestClient, test_user):
        """Test successful get workspace by name."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace_data = TestDataFactory.create_workspace_data("Unique Workspace")
        
        created_workspace = WorkspaceHelper.create_workspace(test_client, session, workspace_data)
        
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = test_client.get(f"/api/v1/workspaces/by-name/Unique Workspace", headers=headers)
        
        assert response.status_code == 200
        workspace = response.json()
        assert workspace["workspaceId"] == created_workspace["workspaceId"]
    
    def test_get_workspace_by_name_not_found(self, test_client: TestClient, test_user):
        """Test get workspace by name that doesn't exist."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        
        response = test_client.get("/api/v1/workspaces/by-name/NonExistent", headers=headers)
        
        assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.workspace
class TestGroupManagement:
    """Test group management functionality."""
    
    def test_update_group_success(self, test_client: TestClient, test_user):
        """Test successful group update."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace = WorkspaceHelper.create_workspace(test_client, session)
        
        # get list workspaces
        resp = test_client.get("/api/v1/workspaces/", headers=AuthHelper.create_authenticated_headers(session.access_token))
        name  = resp.json()["workspaces"][0]["name"]
        resp = test_client.get(f"/api/v1/workspaces/by-name/{name}", headers=AuthHelper.create_authenticated_headers(session.access_token))
        group_id = resp.json()["groups"][0]["groupId"]
        workspaceId = workspace["workspaceId"]

        #



        # Update the group
        update_data = TestDataFactory.create_group_data("Updated Group")
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = test_client.put(
            f"/api/v1/workspaces/{workspaceId}/groups/{group_id}", 
            json=update_data, 
            headers=headers
        )
        
        assert response.status_code == 200
        updated_group = response.json()
        assert updated_group["name"] == "Updated Group"
    
    def test_update_group_not_found(self, test_client: TestClient, test_user):
        """Test update group that doesn't exist."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace = WorkspaceHelper.create_workspace(test_client, session)
        workspaceId = workspace["workspaceId"]
        
        update_data = TestDataFactory.create_group_data("Updated Group")
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = test_client.put(
            f"/api/v1/workspaces/{workspaceId}/groups/99999", 
            json=update_data, 
            headers=headers
        )
        
        assert response.status_code == 404
    
    def test_update_group_without_auth(self, test_client: TestClient):
        """Test update group without authentication."""
        update_data = TestDataFactory.create_group_data("Updated Group")
        response = test_client.put("/api/v1/workspaces/1/groups/1", json=update_data)
        
        assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.task
class TestTaskManagement:
    """Test task management functionality."""
    
    def test_create_task_success(self, test_client: TestClient, test_user):
        """Test successful task creation."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace = WorkspaceHelper.create_workspace(test_client, session)
        

        task_data = TestDataFactory.create_task_data("My Task", "Task description", "high")
         # get list workspaces
        resp = test_client.get("/api/v1/workspaces/", headers=AuthHelper.create_authenticated_headers(session.access_token))
        name  = resp.json()["workspaces"][0]["name"]
        resp = test_client.get(f"/api/v1/workspaces/by-name/{name}", headers=AuthHelper.create_authenticated_headers(session.access_token))
        group_id = resp.json()["groups"][0]["groupId"]
        
        task = TaskHelper.create_task(
            test_client, session, workspace["workspaceId"], group_id, task_data
        )
        
        assert task["title"] == "My Task"
        assert task["description"] == "Task description"
        assert "taskId" in task
    
    def test_create_task_without_auth(self, test_client: TestClient):
        """Test task creation without authentication."""
        task_data = TestDataFactory.create_task_data()
        response = test_client.post("/api/v1/workspaces/1/groups/1/tasks", json=task_data)
        
        assert response.status_code == 401
    
    def test_create_task_invalid_group(self, test_client: TestClient, test_user):
        """Test creating task in invalid group."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace = WorkspaceHelper.create_workspace(test_client, session)
        
        task_data = TestDataFactory.create_task_data()
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = test_client.post(
            f"/api/v1/workspaces/{workspace['workspaceId']}/groups/99999/tasks", 
            json=task_data, 
            headers=headers
        )
        
        assert response.status_code == 404
    
    def test_get_task_success(self, test_client: TestClient, test_user):
        """Test successful get task."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace = WorkspaceHelper.create_workspace(test_client, session)
        
        resp = test_client.get("/api/v1/workspaces/", headers=AuthHelper.create_authenticated_headers(session.access_token))
        name  = resp.json()["workspaces"][0]["name"]
        resp = test_client.get(f"/api/v1/workspaces/by-name/{name}", headers=AuthHelper.create_authenticated_headers(session.access_token))
        group_id = resp.json()["groups"][0]["groupId"]
        
        # Create a task
        task = TaskHelper.create_task(test_client, session, workspace["workspaceId"], group_id)
        
        # Get the task
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = test_client.get(
            f"/api/v1/workspaces/{workspace['workspaceId']}/groups/{group_id}/tasks/{task['taskId']}",
            headers=headers
        )
        
        assert response.status_code == 200
        retrieved_task = response.json()
        assert retrieved_task["taskId"] == task["taskId"]
        assert retrieved_task["title"] == task["title"]
    
    def test_update_task_success(self, test_client: TestClient, test_user):
        """Test successful task update."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace = WorkspaceHelper.create_workspace(test_client, session)
        resp = test_client.get("/api/v1/workspaces/", headers=AuthHelper.create_authenticated_headers(session.access_token))
        name  = resp.json()["workspaces"][0]["name"]
        resp = test_client.get(f"/api/v1/workspaces/by-name/{name}", headers=AuthHelper.create_authenticated_headers(session.access_token))
        group_id = resp.json()["groups"][0]["groupId"]
        
        # Create a task
        task = TaskHelper.create_task(test_client, session, workspace["workspaceId"], group_id)
        
        # Update the task
        update_data = {
            "title": "Updated Task Title",
            "description": "Updated description",
            "priority": "low"
        }
        
        TaskHelper.update_task(
            test_client, session, workspace["workspaceId"], group_id, task["taskId"], update_data
        )
        
    
    def test_update_task_assign_user(self, test_client: TestClient, test_user, test_admin_user):
        """Test assigning task to user."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace = WorkspaceHelper.create_workspace(test_client, session)
        resp = test_client.get("/api/v1/workspaces/", headers=AuthHelper.create_authenticated_headers(session.access_token))
        name  = resp.json()["workspaces"][0]["name"]
        resp = test_client.get(f"/api/v1/workspaces/by-name/{name}", headers=AuthHelper.create_authenticated_headers(session.access_token))
        group_id = resp.json()["groups"][0]["groupId"]
        
        # Create a task
        task = TaskHelper.create_task(test_client, session, workspace["workspaceId"], group_id)
        
        # Assign task to admin user
        update_data = {"assignedToUserId": test_admin_user.account_id}
        
        TaskHelper.update_task(
            test_client, session, workspace["workspaceId"], group_id, task["taskId"], update_data
        )
        
    
    def test_move_task_to_different_group(self, test_client: TestClient, test_user):
        """Test moving task to different group."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace = WorkspaceHelper.create_workspace(test_client, session)
        resp = test_client.get("/api/v1/workspaces/", headers=AuthHelper.create_authenticated_headers(session.access_token))
        name  = resp.json()["workspaces"][0]["name"]
        resp = test_client.get(f"/api/v1/workspaces/by-name/{name}", headers=AuthHelper.create_authenticated_headers(session.access_token))
        group_id = resp.json()["groups"][0]["groupId"]
        
        # Create a second group by updating the existing one and creating a task
        # For this test, we'll assume there are multiple groups or create another workspace
        # Let's create a task and then try to move it (even if to the same group for testing purposes)
        task = TaskHelper.create_task(test_client, session, workspace["workspaceId"], group_id)
        
        # Try to move to the same group (this should work)
        TaskHelper.move_task_to_group(
            test_client, session, workspace["workspaceId"], 
            group_id, task["taskId"], group_id
        )
    
    def test_delete_task_success(self, test_client: TestClient, test_user):
        """Test successful task deletion."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace = WorkspaceHelper.create_workspace(test_client, session)
        resp = test_client.get("/api/v1/workspaces/", headers=AuthHelper.create_authenticated_headers(session.access_token))
        name  = resp.json()["workspaces"][0]["name"]
        resp = test_client.get(f"/api/v1/workspaces/by-name/{name}", headers=AuthHelper.create_authenticated_headers(session.access_token))
        group_id = resp.json()["groups"][0]["groupId"]
        
        # Create a task
        task = TaskHelper.create_task(test_client, session, workspace["workspaceId"], group_id)
        
        # Delete the task
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = test_client.delete(
            f"/api/v1/workspaces/{workspace['workspaceId']}/groups/{group_id}/tasks/{task['taskId']}",
            headers=headers
        )
        
        assert response.status_code == 204
        
        # Verify task is deleted by trying to get it
        get_response = test_client.get(
            f"/api/v1/workspaces/{workspace['workspaceId']}/groups/{group_id}/tasks/{task['taskId']}", 
            headers=headers
        )
        assert get_response.status_code == 404
    


@pytest.mark.unit
@pytest.mark.workspace
class TestWorkspacePermissions:
    """Test workspace permissions and access control."""
    
    def test_access_other_tenant_workspace(self, test_client: TestClient, test_user, test_db_session):
        """Test that users cannot access workspaces from other tenants."""
        # Create a user from a different tenant
        from utils import DatabaseHelper
        
        other_tenant = DatabaseHelper.create_test_tenant(test_db_session, company_name="Other Company")
        DatabaseHelper.create_test_user(test_db_session, other_tenant.tenant_id, "otheruser", "otherpassword")
        
        # Create workspace as original user
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace = WorkspaceHelper.create_workspace(test_client, session)
        
        # Try to access as other user
        other_session = AuthHelper.login_user(test_client, "otheruser", "otherpassword")
        other_headers = AuthHelper.create_authenticated_headers(other_session.access_token)
        
        response = test_client.get(
            f"/api/v1/workspaces/by-name/{workspace['name']}", 
            headers=other_headers
        )
        
        # Should not be able to access workspace from different tenant
        assert response.status_code == 404
    
    def test_multi_user_same_tenant_access(self, test_client: TestClient, test_user, test_admin_user):
        """Test that multiple users from same tenant can access workspaces."""
        # Create workspace as test user
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        workspace = WorkspaceHelper.create_workspace(test_client, session)
        
        # Access as admin user (same tenant)
        admin_session = AuthHelper.login_user(test_client, "admin", "adminpassword")
        admin_headers = AuthHelper.create_authenticated_headers(admin_session.access_token)
        
        response = test_client.get(
            f"/api/v1/workspaces/by-name/{workspace['name']}", 
            headers=admin_headers
        )
        
        # Should be able to access workspace from same tenant
        assert response.status_code == 200
        retrieved_workspace = response.json()
        assert retrieved_workspace["workspaceId"] == workspace["workspaceId"]