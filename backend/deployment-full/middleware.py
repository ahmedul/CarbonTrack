"""
Authentication middleware and dependencies for CarbonTrack
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import verify_token
from typing import Dict, Any

# Security scheme for JWT tokens
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT token
    
    This can be used as a dependency in protected endpoints:
    @app.get("/protected")
    async def protected_route(current_user: dict = Depends(get_current_user)):
        return {"user": current_user}
    """
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        return payload
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Optional dependency for routes that can work with or without authentication
async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Optional authentication dependency
    Returns user data if token is valid, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        return payload
    except Exception:
        return None
