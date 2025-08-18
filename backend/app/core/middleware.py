"""
Authentication middleware and dependencies for CarbonTrack
Supports both real AWS Cognito tokens and mock tokens for development
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Dict, Any, Optional

from app.core.config import settings

# Security scheme for JWT tokens
security = HTTPBearer()


def _is_mock_token(token: str) -> bool:
    """Check if this is a mock token for development"""
    return (
        token.startswith("mock_") or 
        token == "test_token" or
        token == "mock_jwt_token" or
        len(token) < 50  # Real JWT tokens are much longer
    )


def _handle_mock_authentication(token: str) -> Dict[str, Any]:
    """Handle mock authentication for development"""
    if token == "mock_admin" or token == "mock_jwt_token":
        return {
            "user_id": "mock_admin_id",
            "email": "admin@carbontrack.dev",
            "username": "admin@carbontrack.dev",
            "first_name": "Admin",
            "last_name": "User",
            "cognito:groups": ["admin", "user"]
        }
    elif token.startswith("mock_"):
        user_id = token.replace("mock_", "")
        return {
            "user_id": f"mock_{user_id}",
            "email": f"{user_id}@carbontrack.dev",
            "username": f"{user_id}@carbontrack.dev",
            "first_name": "Test",
            "last_name": "User",
            "cognito:groups": ["user"]
        }
    else:
        return {
            "user_id": "test_user_id",
            "email": "test@carbontrack.dev",
            "username": "test@carbontrack.dev", 
            "first_name": "Test",
            "last_name": "User",
            "cognito:groups": ["user"]
        }


async def _validate_cognito_token(token: str) -> Dict[str, Any]:
    """Validate real AWS Cognito JWT token"""
    try:
        # For development, we can decode without verification
        # In production, implement proper JWT verification with Cognito public keys
        if settings.debug:
            payload = jwt.get_unverified_claims(token)
        else:
            # TODO: Implement proper JWT verification with Cognito public keys
            payload = jwt.decode(
                token,
                options={"verify_signature": False},  # Disable for development
                audience=settings.cognito_client_id
            )
        
        # Extract user information from the token
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "username": payload.get("email"),  # Cognito uses email as username
            "first_name": payload.get("given_name", ""),
            "last_name": payload.get("family_name", ""),
            "cognito:groups": payload.get("cognito:groups", ["user"])
        }
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token - supports both mock and real tokens
    """
    # Check if we're using mock authentication in development
    if settings.debug and _is_mock_token(token):
        return _handle_mock_authentication(token)
    
    # For non-mock tokens, try Cognito validation
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_validate_cognito_token(token))
    except Exception as e:
        if settings.debug:
            # Fall back to mock in development if Cognito fails
            return _handle_mock_authentication(token)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )


# Temporary mock implementation until auth service is fully integrated
def mock_verify_token(token: str) -> Dict[str, Any]:
    """Mock token verification for development - kept for backward compatibility"""
    return verify_token(token)


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
