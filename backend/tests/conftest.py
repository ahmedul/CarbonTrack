"""
Test configuration and fixtures
"""

import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables and mocks."""
    # Set fake AWS credentials for testing
    os.environ["AWS_ACCESS_KEY_ID"] = "fake-test-key-id"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "fake-test-secret-key"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["COGNITO_USER_POOL_ID"] = "fake-pool-id" 
    os.environ["COGNITO_CLIENT_ID"] = "fake-client-id"
    os.environ["TESTING"] = "true"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_aws_services():
    """Mock AWS services for all tests."""
    with patch('boto3.client') as mock_boto_client, \
         patch('boto3.resource') as mock_boto_resource:
        
        # Mock Cognito client
        mock_cognito = MagicMock()
        mock_cognito.admin_create_user.return_value = {"User": {"Username": "test_user"}}
        mock_cognito.admin_initiate_auth.return_value = {
            "AuthenticationResult": {
                "AccessToken": "mock_access_token",
                "IdToken": "mock_id_token",
                "RefreshToken": "mock_refresh_token"
            }
        }
        
        # Mock DynamoDB resource
        mock_dynamodb = MagicMock()
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        
        mock_boto_client.return_value = mock_cognito
        mock_boto_resource.return_value = mock_dynamodb
        
        yield mock_cognito, mock_dynamodb


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
