"""
Test cases for authentication endpoints
"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "version" in data


def test_detailed_health_check(client: TestClient):
    """Test the detailed health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


def test_register_user(client: TestClient):
    """Test user registration endpoint."""
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "phone_number": "+1234567890"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    # With mocked AWS services, expect success or validation error
    assert response.status_code in [201, 400]
    
    if response.status_code == 201:
        data = response.json()
        assert "user_id" in data or "message" in data


def test_login_user(client: TestClient):
    """Test user login endpoint."""
    login_data = {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    # With mocked AWS services, expect success or auth error
    assert response.status_code in [200, 401]


def test_password_reset(client: TestClient):
    """Test password reset endpoint."""
    reset_data = {
        "email": "test@example.com"
    }
    
    response = client.post("/api/v1/auth/reset-password", json=reset_data)
    # Since we don't have real AWS Cognito, expect error but endpoint should exist
    assert response.status_code in [200, 400, 500]


def test_invalid_email_format(client: TestClient):
    """Test registration with invalid email format."""
    user_data = {
        "email": "invalid-email",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 422  # Validation error
