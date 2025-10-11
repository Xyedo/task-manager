"""Load testing with Locust for user flow scenarios."""

import random
import time
from locust import HttpUser, task, between


class TaskManagerUser(HttpUser):
    """Simulates a user interacting with the Task Manager API."""
    
    wait_time = between(1, 3)
    weight = 9
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.tenant_id = None
        self.username = None
        self.workspaces = []
        self.user_tasks = []  # Renamed to avoid conflict with 'tasks' attribute
    
    def on_start(self):
        """Called when a user starts. Login and setup initial data."""
        self.login()
    
    def on_stop(self):
        """Called when a user stops. Cleanup."""
        if self.access_token:
            self.logout()
    
    def login(self):
        """Login with test credentials."""
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        with self.client.post("/api/v1/identity/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["accessToken"]
                self.refresh_token = data["refreshToken"]
                
                # Set authorization header for subsequent requests
                self.client.headers.update({"Authorization": f"Bearer {self.access_token}"})
                
                # Get user info from /me endpoint
                with self.client.get("/api/v1/identity/me", catch_response=True) as me_response:
                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        self.user_id = user_data["accountId"]  # Note: API returns accountId, not user_id
                        self.username = user_data["username"]
                        
                        # For tenant_id, we need to decode the token or make assumptions
                        # For load testing, we'll assume tenant_id = 1 (first tenant from seeds)
                        self.tenant_id = 1
                        
                        response.success()
                    else:
                        response.failure(f"Failed to get user info: {me_response.status_code}")
            else:
                response.failure(f"Login failed: {response.status_code}")
    
    def logout(self):
        """Logout and revoke tokens."""
        with self.client.delete("/api/v1/identity/logout", catch_response=True) as response:
            if response.status_code in [200, 204]:
                self.access_token = None
                self.refresh_token = None
                response.success()
            else:
                response.failure(f"Logout failed: {response.status_code}")
    
    @task(3)
    def get_workspaces(self):
        """Get workspace by name (frequent operation)."""
        workspace_name = "My Kanban Project"
        url = f"/api/v1/workspaces/by-name/{workspace_name}"
        with self.client.get(url, catch_response=True) as response:
            if response.status_code == 200:
                workspace = response.json()
                self.workspaces = [workspace]  # Store as list for consistency
                response.success()
            else:
                response.failure(f"Get workspace by name failed: {response.status_code}")
    
    @task(2)
    def create_workspace(self):
        """Create a new workspace."""
        workspace_data = {
            "name": f"Workspace-{random.randint(1000, 9999)}-{int(time.time())}",
            "description": f"Load test workspace created at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        with self.client.post("/api/v1/workspaces/", json=workspace_data, catch_response=True) as response:
            if response.status_code in [200, 201]:
                workspace = response.json()
                self.workspaces.append(workspace)
                response.success()
            elif response.status_code == 409:
                response.success()
            else:
                response.failure(f"Create workspace failed: {response.status_code}")
    
    @task(4)
    def create_task(self):
        """Create a new task in a workspace."""
        if not self.workspaces:
            self.get_workspaces()
        
        if self.workspaces and len(self.workspaces) > 0:
            workspace = random.choice(self.workspaces)
            if workspace.get("groups"):
                group = random.choice(workspace["groups"])
                
                task_data = {
                    "title": f"Task-{random.randint(1000, 9999)}",
                    "description": f"Load test task created at {time.strftime('%Y-%m-%d %H:%M:%S')}",
                    "priority": random.choice(["low", "medium", "high"]),
                    "assigned_to_user_id": self.user_id
                }
                
                url = f"/api/v1/workspaces/{workspace['workspaceId']}/groups/{group['groupId']}/tasks"
                with self.client.post(url, json=task_data, catch_response=True) as response:
                    if response.status_code in [200, 201]:
                        try:
                            task = response.json()
                            # Only store if we got a valid task with required fields
                            if task and task.get("taskId"):
                                self.user_tasks.append({
                                    "task": task,
                                    "workspaceId": workspace["workspaceId"],
                                    "groupId": group["groupId"]
                                })
                            response.success()
                        except (ValueError, KeyError):
                            response.failure(f"Invalid task response: {response.text}")
                    else:
                        response.failure(f"Create task failed: {response.status_code}")
    
    @task(2)
    def update_task(self):
        """Update an existing task."""
        if self.user_tasks:
            task_info = random.choice(self.user_tasks)
            task = task_info.get("task")
            
            # Skip if task is None or missing required fields
            if not task or not task.get("taskId") or not task.get("title"):
                return
                
            workspaceId = task_info["workspaceId"]
            groupId = task_info["groupId"]
            
            update_data = {
                "title": f"Updated-{task['title']}",
                "description": f"Updated at {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "priority": random.choice(["low", "medium", "high"])
            }
            
            url = f"/api/v1/workspaces/{workspaceId}/groups/{groupId}/tasks/{task['taskId']}"
            with self.client.patch(url, json=update_data, catch_response=True) as response:
                if response.status_code == 200:
                    updated_task = response.json()
                    task_info["task"] = updated_task
                    response.success()
                else:
                    response.failure(f"Update task failed: {response.status_code}")
    
    @task(1)
    def move_task_between_groups(self):
        """Move a task to a different group."""
        if self.user_tasks and self.workspaces:
            task_info = random.choice(self.user_tasks)
            task = task_info.get("task")
            
            # Skip if task is None or missing required fields
            if not task or not task.get("taskId"):
                return
                
            workspaceId = task_info["workspaceId"]
            current_groupId = task_info["groupId"]
            
            workspace = next((w for w in self.workspaces if w["workspaceId"] == workspaceId), None)
            if workspace and len(workspace.get("groups", [])) > 1:
                other_groups = [g for g in workspace["groups"] if g["groupId"] != current_groupId]
                if other_groups:
                    new_group = random.choice(other_groups)
                    
                    update_data = {"groupId": new_group["groupId"]}
                    url = f"/api/v1/workspaces/{workspaceId}/groups/{current_groupId}/tasks/{task['taskId']}"
                    
                    with self.client.patch(url, json=update_data, catch_response=True) as response:
                        if response.status_code == 200:
                            task_info["groupId"] = new_group["groupId"]
                            response.success()
                        else:
                            response.failure(f"Move task failed: {response.status_code}")
    
    @task(1)
    def get_task_details(self):
        """Get details of a specific task."""
        if self.user_tasks:
            task_info = random.choice(self.user_tasks)
            task = task_info.get("task")
            
            # Skip if task is None or missing required fields
            if not task or not task.get("taskId"):
                return
                
            workspaceId = task_info["workspaceId"]
            groupId = task_info["groupId"]
            
            url = f"/api/v1/workspaces/{workspaceId}/groups/{groupId}/tasks/{task['taskId']}"
            with self.client.get(url, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Get task details failed: {response.status_code}")
    
    @task(1)
    def refresh_token(self):
        """Refresh access token using refresh token."""
        if self.refresh_token:
            refresh_data = {"refreshToken": self.refresh_token}
            
            with self.client.put("/api/v1/identity/refresh", json=refresh_data, catch_response=True) as response:
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data["accessToken"]
                    
                    self.client.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    response.success()
                else:
                    response.failure(f"Token refresh failed: {response.status_code}")
    
    @task(1)
    def get_users(self):
        """Get list of users in the same tenant."""
        with self.client.get("/api/v1/identity/users", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Get users failed: {response.status_code}")
    
    @task(1)
    def get_my_info(self):
        """Get current user info."""
        with self.client.get("/api/v1/identity/me", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Get my info failed: {response.status_code}")


class AdminUser(HttpUser):
    """Admin user with additional administrative tasks."""
    
    wait_time = between(1, 3)
    weight = 1
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.tenant_id = None
        self.username = None
        self.workspaces = []
        self.user_tasks = []
    
    def on_start(self):
        """Called when a user starts. Login and setup initial data."""
        self.login()
    
    def on_stop(self):
        """Called when a user stops. Cleanup."""
        if self.access_token:
            self.logout()
    
    def login(self):
        """Login with admin credentials."""
        login_data = {
            "username": "admin",
            "password": "adminpassword"
        }
        
        with self.client.post("/api/v1/identity/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["accessToken"]
                self.refresh_token = data["refreshToken"]
                
                # Set authorization header for subsequent requests
                self.client.headers.update({"Authorization": f"Bearer {self.access_token}"})
                
                # Get user info from /me endpoint
                with self.client.get("/api/v1/identity/me", catch_response=True) as me_response:
                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        self.user_id = user_data["accountId"]  # Note: API returns accountId, not user_id
                        self.username = user_data["username"]
                        
                        # For tenant_id, we need to decode the token or make assumptions
                        # For load testing, we'll assume tenant_id = 1 (first tenant from seeds)
                        self.tenant_id = 1
                        
                        response.success()
                    else:
                        response.failure(f"Admin failed to get user info: {me_response.status_code}")
            else:
                response.failure(f"Admin login failed: {response.status_code}")
    
    def logout(self):
        """Logout and revoke tokens."""
        with self.client.delete("/api/v1/identity/logout", catch_response=True) as response:
            if response.status_code in [200, 204]:
                self.access_token = None
                self.refresh_token = None
                response.success()
            else:
                response.failure(f"Admin logout failed: {response.status_code}")
    
    @task(3)
    def get_workspaces(self):
        """Get workspace by name."""
        workspace_name = "My Kanban Project"
        url = f"/api/v1/workspaces/by-name/{workspace_name}"
        with self.client.get(url, catch_response=True) as response:
            if response.status_code == 200:
                workspace = response.json()
                self.workspaces = [workspace]  # Store as list for consistency
                response.success()
            else:
                response.failure(f"Admin get workspace by name failed: {response.status_code}")
    
    @task(2)
    def create_workspace(self):
        """Create a new workspace."""
        workspace_data = {
            "name": f"Admin-Workspace-{random.randint(1000, 9999)}-{int(time.time())}",
            "description": f"Admin workspace created at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        with self.client.post("/api/v1/workspaces/", json=workspace_data, catch_response=True) as response:
            if response.status_code in [200, 201]:
                workspace = response.json()
                self.workspaces.append(workspace)
                response.success()
            elif response.status_code == 409:
                response.success()
            else:
                response.failure(f"Admin create workspace failed: {response.status_code}")
    
    @task(2)
    def create_task(self):
        """Create a new task."""
        if not self.workspaces:
            self.get_workspaces()
        
        if self.workspaces and len(self.workspaces) > 0:
            workspace = random.choice(self.workspaces)
            if workspace.get("groups"):
                group = random.choice(workspace["groups"])
                
                task_data = {
                    "title": f"Admin-Task-{random.randint(1000, 9999)}",
                    "description": f"Admin task created at {time.strftime('%Y-%m-%d %H:%M:%S')}",
                    "priority": random.choice(["low", "medium", "high"]),
                    "assigned_to_user_id": self.user_id
                }
                
                url = f"/api/v1/workspaces/{workspace['workspaceId']}/groups/{group['groupId']}/tasks"
                with self.client.post(url, json=task_data, catch_response=True) as response:
                    if response.status_code in [200, 201]:
                        try:
                            task = response.json()
                            # Only store if we got a valid task with required fields
                            if task and task.get("taskId"):
                                self.user_tasks.append({
                                    "task": task,
                                    "workspaceId": workspace["workspaceId"],
                                    "groupId": group["groupId"]
                                })
                            response.success()
                        except (ValueError, KeyError):
                            response.failure(f"Invalid admin task response: {response.text}")
                    else:
                        response.failure(f"Admin create task failed: {response.status_code}")
    
    @task(3)
    def delete_task(self):
        """Delete a task (admin operation)."""
        if self.user_tasks:
            task_info = self.user_tasks.pop()
            task = task_info.get("task")
            
            # Skip if task is None or missing required fields
            if not task or not task.get("taskId"):
                return
                
            workspaceId = task_info["workspaceId"]
            groupId = task_info["groupId"]
            
            url = f"/api/v1/workspaces/{workspaceId}/groups/{groupId}/tasks/{task['taskId']}"
            with self.client.delete(url, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Admin delete task failed: {response.status_code}")
    
    @task(2)
    def update_group(self):
        """Update group information (admin operation)."""
        if self.workspaces and len(self.workspaces) > 0:
            workspace = random.choice(self.workspaces)
            if workspace.get("groups"):
                group = random.choice(workspace["groups"])
                
                update_data = {
                    "name": f"Admin-Updated-{group['name']}-{int(time.time())}",
                    "description": f"Admin updated at {time.strftime('%Y-%m-%d %H:%M:%S')}"
                }
                
                url = f"/api/v1/workspaces/{workspace['workspaceId']}/groups/{group['groupId']}"
                with self.client.put(url, json=update_data, catch_response=True) as response:
                    if response.status_code == 200:
                        response.success()
                    else:
                        response.failure(f"Admin update group failed: {response.status_code}")
    
    @task(1)
    def get_users(self):
        """Get list of users."""
        with self.client.get("/api/v1/identity/users", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Admin get users failed: {response.status_code}")


if __name__ == "__main__":
    import locust.main
    locust.main.main()