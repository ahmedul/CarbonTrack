"""
Authentication API routes
"""

from fastapi import APIRouter, Depends, status
from typing import Dict, Any

from app.schemas.auth import (
    UserRegistration,
    UserLogin,
    TokenResponse,
    PasswordReset,
    PasswordConfirm,
    RefreshTokenRequest,
    MessageResponse
)
from app.services.auth_service import AuthService
from app.core.middleware import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegistration):
    """
    Register a new user
    
    - **email**: Valid email address
    - **password**: Strong password (min 8 characters)
    - **full_name**: User's full name
    - **phone_number**: Optional phone number
    """
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin):
    """
    Authenticate user and return access token
    
    - **email**: User's email address
    - **password**: User's password
    """
    return await auth_service.authenticate_user(credentials)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Refresh access token using refresh token
    
    Requires valid refresh token in request body
    """
    username = current_user.get("username") or current_user.get("email")
    return await auth_service.refresh_token(refresh_data.refresh_token, username)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: PasswordReset):
    """
    Initiate password reset process
    
    Sends a reset code to the user's email address
    """
    return await auth_service.forgot_password(data.email)


@router.post("/confirm-reset-password", response_model=MessageResponse)
async def confirm_password_reset(data: PasswordConfirm):
    """
    Confirm password reset with verification code
    
    - **email**: User's email address
    - **confirmation_code**: 6-digit code from email
    - **new_password**: New password (min 8 characters)
    """
    return await auth_service.confirm_forgot_password(data)


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current authenticated user's information
    
    Requires valid access token
    """
    return {"user": current_user}


@router.post("/logout", response_model=MessageResponse)
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout user (invalidate tokens)
    
    Note: In a stateless JWT system, this mainly serves as a confirmation endpoint.
    Client should discard tokens on logout.
    """
    return MessageResponse(message="Successfully logged out")
