"""
Pydantic schemas for authentication
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegistration(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: Optional[dict] = None


class UserProfile(BaseModel):
    """Schema for user profile"""
    user_id: str
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    email_verified: bool = False
    created_at: datetime


class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordConfirm(BaseModel):
    """Schema for password reset confirmation"""
    email: EmailStr
    confirmation_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class MessageResponse(BaseModel):
    """Schema for generic message responses"""
    message: str
    status: str = "success"
