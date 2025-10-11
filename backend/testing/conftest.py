"""Pytest configuration and shared fixtures for testing."""

import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import the main app and dependencies
import sys
sys.path.append('/home/hafidmahdi/personal/task-manager/backend')

from main import app
from src.infrastructure.database.repository import Repository
from src.infrastructure.security.tokenManager import JwtTokenManager
from src.common.token import TokenPayload
from migrations.schema import Base, Account, Tenant, Authentication

# Test database URL
TEST_DATABASE_URL = "postgresql://local:local@localhost:5432/taskdb"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def override_get_db_session(test_db_session):
    """Override the database dependency for testing."""
    def _override_get_db_session():
        return test_db_session
    
    app.dependency_overrides[Repository] = _override_get_db_session
    yield test_db_session
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_client(override_get_db_session) -> TestClient:
    """Create a test client."""
    return TestClient(app)

@pytest.fixture(scope="function")
async def async_test_client(override_get_db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
def test_tenant(test_db_session) -> Tenant:
    """Create a test tenant."""
    tenant = Tenant(
        tenant_id=1,
        name="Test Company",
    )
    test_db_session.add(tenant)
    test_db_session.commit()
    test_db_session.refresh(tenant)
    return tenant

@pytest.fixture(scope="function")
def test_user(test_db_session, test_tenant) -> Account:
    """Create a test user."""
    from argon2 import PasswordHasher
    ph = PasswordHasher()
    
    user = Account(
        account_id=1,
        tenant_id=test_tenant.tenant_id,
        username="testuser",
        full_name="Test User",
        email = "testuser@example.com",
        hashed_password=ph.hash("testpassword"),
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin_user(test_db_session, test_tenant) -> Account:
    """Create a test admin user."""
    from argon2 import PasswordHasher
    ph = PasswordHasher()
    
    user = Account(
        account_id=2,
        tenant_id=test_tenant.tenant_id,
        full_name="Admin User",
        username="admin",
        email = "admin@example.com",
        hashed_password=ph.hash("adminpassword"),
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def token_manager() -> JwtTokenManager:
    """Create a JWT token manager for testing."""
    return JwtTokenManager()

@pytest.fixture(scope="function")
def test_token_payload(test_user) -> TokenPayload:
    """Create a test token payload."""
    return TokenPayload(
        tenant_id=test_user.tenant_id,
        id=test_user.account_id,
        username=test_user.username
    )

@pytest.fixture(scope="function")
def test_access_token(token_manager, test_token_payload) -> str:
    """Create a test access token."""
    return token_manager.create_access_token(test_token_payload)

@pytest.fixture(scope="function")
def test_refresh_token(token_manager, test_token_payload) -> str:
    """Create a test refresh token."""
    return token_manager.create_refresh_token(test_token_payload)

@pytest.fixture(scope="function")
def authenticated_client(test_client, test_access_token) -> TestClient:
    """Create an authenticated test client."""
    test_client.headers.update({"Authorization": f"Bearer {test_access_token}"})
    return test_client

@pytest.fixture(scope="function")
async def authenticated_async_client(async_test_client, test_access_token) -> AsyncClient:
    """Create an authenticated async test client."""
    async_test_client.headers.update({"Authorization": f"Bearer {test_access_token}"})
    return async_test_client

@pytest.fixture(scope="function")
def sample_workspace_data():
    """Sample workspace data for testing."""
    return {
        "name": "Test Workspace",
        "description": "A test workspace for unit testing"
    }

@pytest.fixture(scope="function")
def sample_task_data():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "A test task for unit testing",
        "due_date": "2024-12-31T23:59:59"
    }

@pytest.fixture(scope="function")
def sample_group_data():
    """Sample group data for testing."""
    return {
        "name": "Test Group",
        "description": "A test group for unit testing"
    }

# Performance testing fixtures
@pytest.fixture(scope="function")
def benchmark_config():
    """Configuration for benchmark tests."""
    return {
        "min_rounds": 5,
        "max_time": 1.0,
        "warmup": True,
        "warmup_iterations": 2
    }

# Load testing fixtures
@pytest.fixture(scope="session")
def load_test_config():
    """Configuration for load tests."""
    return {
        "base_url": os.getenv("TEST_BASE_URL", "http://localhost:8000"),
        "users": int(os.getenv("LOAD_TEST_USERS", "10")),
        "spawn_rate": int(os.getenv("LOAD_TEST_SPAWN_RATE", "2")),
        "run_time": os.getenv("LOAD_TEST_RUNTIME", "60s"),
        "test_username": "testuser",
        "test_password": "testpassword"
    }

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    original_env = os.environ.get("ENV")
    os.environ["ENV"] = "test"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["ACCESS_TOKEN_SECRET"] = "test-access-secret-key"
    os.environ["REFRESH_TOKEN_SECRET"] = "test-refresh-secret-key"
    yield
    if original_env:
        os.environ["ENV"] = original_env
    else:
        os.environ.pop("ENV", None)