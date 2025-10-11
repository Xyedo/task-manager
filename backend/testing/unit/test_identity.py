"""Unit tests for identity domain functionality."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from utils import AuthHelper, TestDataFactory


@pytest.mark.unit
@pytest.mark.auth
class TestIdentityLogin:
    """Test identity login functionality."""
    
    def test_login_success(self, test_client: TestClient, test_user):
        """Test successful login."""
        login_data = TestDataFactory.create_user_data("testuser", "testpassword")
        response = test_client.post("/api/v1/identity/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "accessToken" in data
        assert "refreshToken" in data
    
    def test_login_invalid_credentials(self, test_client: TestClient, test_user):
        """Test login with invalid credentials."""
        login_data = TestDataFactory.create_user_data("testuser", "wrongpassword")
        response = test_client.post("/api/v1/identity/login", json=login_data)
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, test_client: TestClient):
        """Test login with nonexistent user."""
        login_data = TestDataFactory.create_user_data("nonexistent", "password")
        response = test_client.post("/api/v1/identity/login", json=login_data)
        
        assert response.status_code == 404
    
    def test_login_missing_fields(self, test_client: TestClient):
        """Test login with missing fields."""
        response = test_client.post("/api/v1/identity/login", json={"username": "testuser"})
        assert response.status_code == 422
        
        response = test_client.post("/api/v1/identity/login", json={"password": "password"})
        assert response.status_code == 422
    
    def test_login_empty_fields(self, test_client: TestClient):
        """Test login with empty fields."""
        login_data = TestDataFactory.create_user_data("", "")
        response = test_client.post("/api/v1/identity/login", json=login_data)
        
        assert response.status_code in [400, 422, 404]


@pytest.mark.unit
@pytest.mark.auth
class TestIdentityRefresh:
    """Test identity refresh functionality."""
    
    def test_refresh_token_success(self, test_client: TestClient, test_user, test_refresh_token):
        """Test successful token refresh."""
        # First, store the refresh token in the database by logging in
        login_data = TestDataFactory.create_user_data("testuser", "testpassword")
        login_response = test_client.post("/api/v1/identity/login", json=login_data)
        assert login_response.status_code == 200
        
        refresh_token = login_response.json()["refreshToken"]
        
        # Now test refresh
        response = test_client.put("/api/v1/identity/refresh", cookies={"refresh_token": refresh_token})
        
        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
    
    def test_refresh_token_invalid(self, test_client: TestClient):
        """Test refresh with invalid token."""
        refresh_data = {"refreshToken": "invalid_token"}
        response = test_client.put("/api/v1/identity/refresh", json=refresh_data)
        
        assert response.status_code in [401, 403]
    
    def test_refresh_token_missing(self, test_client: TestClient):
        """Test refresh with missing token."""
        response = test_client.put("/api/v1/identity/refresh", json={})
        
        assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.auth
class TestIdentityLogout:
    """Test identity logout functionality."""
    
    def test_logout_success(self, test_client: TestClient, test_user):
        """Test successful logout."""
        # Login first
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        
        # Logout
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        response = test_client.delete("/api/v1/identity/logout", headers=headers)
        
        assert response.status_code == 204
    
    def test_logout_without_auth(self, test_client: TestClient):
        """Test logout without authentication."""
        response = test_client.delete("/api/v1/identity/logout")
        
        assert response.status_code == 401
    
    def test_logout_invalid_token(self, test_client: TestClient):
        """Test logout with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = test_client.delete("/api/v1/identity/logout", headers=headers)
        
        assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.auth
class TestIdentityUsers:
    """Test identity users functionality."""
    
    def test_get_users_success(self, test_client: TestClient, test_user, test_admin_user):
        """Test successful get users."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        
        response = test_client.get("/api/v1/identity/users", headers=headers)
        
        assert response.status_code == 200
        res = response.json()
        assert isinstance(res["users"], list)
        assert len(res["users"]) >= 1
        
    
    def test_get_users_without_auth(self, test_client: TestClient):
        """Test get users without authentication."""
        response = test_client.get("/api/v1/identity/users")
        
        assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.auth
class TestIdentityMe:
    """Test identity me functionality."""
    
    def test_get_me_success(self, test_client: TestClient, test_user):
        """Test successful get me."""
        session = AuthHelper.login_user(test_client, "testuser", "testpassword")
        headers = AuthHelper.create_authenticated_headers(session.access_token)
        
        response = test_client.get("/api/v1/identity/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    def test_get_me_without_auth(self, test_client: TestClient):
        """Test get me without authentication."""
        response = test_client.get("/api/v1/identity/me")
        
        assert response.status_code == 401
    
    def test_get_me_invalid_token(self, test_client: TestClient):
        """Test get me with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = test_client.get("/api/v1/identity/me", headers=headers)
        
        assert response.status_code == 401

