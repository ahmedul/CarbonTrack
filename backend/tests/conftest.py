"""
Test configuration and fixtures
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    """Mock authentication headers for testing protected endpoints."""
    # In real tests, you would generate a proper JWT token
    return {"Authorization": "Bearer mock_jwt_token"}


@pytest.fixture
def mock_user_data():
    """Mock user data for testing."""
    return {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "full_name": "Test User",
        "email_verified": True
    }
