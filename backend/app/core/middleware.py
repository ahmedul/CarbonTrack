"""
Authentication middleware and dependencies for CarbonTrack
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional

# Security scheme for JWT tokens
security = HTTPBearer()

# Temporary mock implementation until auth service is fully integrated
def mock_verify_token(token: str) -> Dict[str, Any]:
    """Mock token verification for development"""
    # This is a temporary implementation
    # In production, this would verify the actual JWT token
    if token == "mock_jwt_token":
        return {
            "user_id": "mock_user_123",
            "email": "test@example.com",
            "username": "test@example.com",
            "cognito:groups": ["user"]
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT token
    
    This can be used as a dependency in protected endpoints:
    @app.get("/protected")
    async def protected_route(current_user: dict = Depends(get_current_user)):
        return {"user": current_user}
    """
    token = credentials.credentials
    
    try:
        payload = mock_verify_token(token)
        return payload
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Optional authentication dependency
    Returns user data if token is valid, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = mock_verify_token(token)
        return payload
    except Exception:
        return None


async def verify_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to verify admin privileges
    """
    user_groups = current_user.get("cognito:groups", [])
    if "admin" not in user_groups:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
