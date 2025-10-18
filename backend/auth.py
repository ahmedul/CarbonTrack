"""
Authentication module for CarbonTrack
Handles user registration, login, and JWT token management with AWS Cognito
"""

import boto3
import hmac
import hashlib
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from botocore.exceptions import ClientError

# Pydantic models for authentication
class UserRegistration(BaseModel):
    email: str  # Using str instead of EmailStr for now
    password: str
    full_name: str
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: str  # Using str instead of EmailStr for now
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None

class UserProfile(BaseModel):
    user_id: str
    email: str
    full_name: str
    phone_number: Optional[str] = None
    email_verified: bool = False
    created_at: datetime

class PasswordReset(BaseModel):
    email: str  # Using str instead of EmailStr for now

class PasswordConfirm(BaseModel):
    email: str  # Using str instead of EmailStr for now
    confirmation_code: str
    new_password: str

# Authentication configuration
class AuthConfig:
    def __init__(self):
        # AWS Cognito configuration (use environment variables in production)
        self.user_pool_id = os.getenv("COGNITO_USER_POOL_ID", "eu-central-1_XXXXXXXXX")
        self.client_id = os.getenv("COGNITO_CLIENT_ID", "your_client_id_here")
        self.client_secret = os.getenv("COGNITO_CLIENT_SECRET", "your_client_secret_here")
        self.region = os.getenv("AWS_REGION", "eu-central-1")
        
        # JWT configuration
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "your_super_secret_jwt_key_change_in_production")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration_hours = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

config = AuthConfig()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CognitoAuth:
    def __init__(self):
        self.client = boto3.client('cognito-idp', region_name=config.region)
        self.user_pool_id = config.user_pool_id
        self.client_id = config.client_id
        self.client_secret = config.client_secret

    def _get_secret_hash(self, username: str) -> str:
        """Generate secret hash for Cognito client"""
        message = username + self.client_id
        dig = hmac.new(
            str(self.client_secret).encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()

    async def register_user(self, user_data: UserRegistration) -> Dict[str, Any]:
        """Register a new user with AWS Cognito"""
        try:
            response = self.client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=user_data.email,
                UserAttributes=[
                    {'Name': 'email', 'Value': user_data.email},
                    {'Name': 'name', 'Value': user_data.full_name},
                    {'Name': 'email_verified', 'Value': 'false'}
                ] + ([{'Name': 'phone_number', 'Value': user_data.phone_number}] if user_data.phone_number else []),
                TemporaryPassword=user_data.password,
                MessageAction='SUPPRESS'  # Don't send welcome email
            )
            
            # Set permanent password
            self.client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=user_data.email,
                Password=user_data.password,
                Permanent=True
            )
            
            return {
                "user_id": response['User']['Username'],
                "email": user_data.email,
                "status": "confirmed",
                "message": "User registered successfully"
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists"
                )
            elif error_code == 'InvalidPasswordException':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password does not meet requirements"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Registration failed: {str(e)}"
                )

    async def authenticate_user(self, credentials: UserLogin) -> Dict[str, Any]:
        """Authenticate user with AWS Cognito"""
        try:
            secret_hash = self._get_secret_hash(credentials.email)
            
            response = self.client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': credentials.email,
                    'PASSWORD': credentials.password,
                    'SECRET_HASH': secret_hash
                }
            )
            
            if 'AuthenticationResult' in response:
                tokens = response['AuthenticationResult']
                
                # Get user info
                user_info = self.client.admin_get_user(
                    UserPoolId=self.user_pool_id,
                    Username=credentials.email
                )
                
                return {
                    "access_token": tokens['AccessToken'],
                    "refresh_token": tokens.get('RefreshToken'),
                    "id_token": tokens.get('IdToken'),
                    "expires_in": tokens['ExpiresIn'],
                    "user_info": {
                        "user_id": user_info['Username'],
                        "email": credentials.email,
                        "attributes": {attr['Name']: attr['Value'] for attr in user_info['UserAttributes']}
                    }
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication failed"
                )
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NotAuthorizedException':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            elif error_code == 'UserNotConfirmedException':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User email not confirmed"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Authentication failed: {str(e)}"
                )

    async def refresh_token(self, refresh_token: str, username: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            secret_hash = self._get_secret_hash(username)
            
            response = self.client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token,
                    'SECRET_HASH': secret_hash
                }
            )
            
            tokens = response['AuthenticationResult']
            return {
                "access_token": tokens['AccessToken'],
                "expires_in": tokens['ExpiresIn']
            }
            
        except ClientError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed"
            )

    async def forgot_password(self, email: str) -> Dict[str, str]:
        """Initiate password reset process"""
        try:
            secret_hash = self._get_secret_hash(email)
            
            self.client.forgot_password(
                ClientId=self.client_id,
                Username=email,
                SecretHash=secret_hash
            )
            
            return {"message": "Password reset code sent to email"}
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UserNotFoundException':
                # Don't reveal if user exists for security
                return {"message": "If the email exists, a reset code has been sent"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Password reset failed"
                )

    async def confirm_forgot_password(self, email: str, confirmation_code: str, new_password: str) -> Dict[str, str]:
        """Confirm password reset with code"""
        try:
            secret_hash = self._get_secret_hash(email)
            
            self.client.confirm_forgot_password(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code,
                Password=new_password,
                SecretHash=secret_hash
            )
            
            return {"message": "Password reset successful"}
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'CodeMismatchException':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid confirmation code"
                )
            elif error_code == 'ExpiredCodeException':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Confirmation code has expired"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Password confirmation failed"
                )

# JWT token utilities
def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=config.jwt_expiration_hours)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.jwt_secret, algorithm=config.jwt_algorithm)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, config.jwt_secret, algorithms=[config.jwt_algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Initialize Cognito auth instance
cognito_auth = CognitoAuth()
