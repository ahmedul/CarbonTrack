"""
Authentication service for CarbonTrack
Handles user registration, login, and JWT token management with AWS Cognito
"""

import boto3
import hmac
import hashlib
import base64
import os
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from botocore.exceptions import ClientError, NoCredentialsError

from app.core.config import settings
from app.schemas.auth import (
    UserRegistration, 
    UserLogin, 
    TokenResponse,
    PasswordConfirm,
    MessageResponse
)


class AuthService:
    """Authentication service using AWS Cognito"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Check if we're in a testing environment
        is_testing = os.getenv('TESTING', '').lower() == 'true'
        
        if is_testing:
            # In testing mode, use mock configuration
            self.client = None
            self.user_pool_id = "fake-pool-id"
            self.client_id = "fake-client-id" 
            self.client_secret = "fake-client-secret"
            self.is_mock = True
        else:
            try:
                # Try to initialize AWS Cognito client for production
                self.client = boto3.client('cognito-idp', region_name=settings.aws_region)
                self.user_pool_id = settings.cognito_user_pool_id
                self.client_id = settings.cognito_client_id
                self.client_secret = settings.cognito_client_secret
                self.is_mock = False
            except (NoCredentialsError, Exception) as e:
                # In production without proper credentials, fail
                raise e

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
            if self.is_mock:
                # Mock response for testing
                return {
                    "user_id": f"test_user_{user_data.email.split('@')[0]}",
                    "email": user_data.email,
                    "full_name": user_data.full_name,
                    "message": "User registered successfully (mock)"
                }
            
            response = self.client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=user_data.email,
                UserAttributes=[
                    {'Name': 'email', 'Value': user_data.email},
                    {'Name': 'name', 'Value': user_data.full_name},
                    {'Name': 'email_verified', 'Value': 'false'}
                ] + ([{'Name': 'phone_number', 'Value': user_data.phone_number}] 
                     if user_data.phone_number else []),
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
            
            # Save user to DynamoDB
            user_id = response['User']['Username']
            from datetime import datetime
            import boto3
            from ..core.config import settings
            
            dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
            users_table = dynamodb.Table(settings.users_table)
            
            users_table.put_item(
                Item={
                    'userId': user_id,
                    'email': user_data.email,
                    'full_name': user_data.full_name,
                    'role': 'user',
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    'carbon_budget': 500,  # Default budget
                    'email_verified': False
                }
            )
            
            return {
                "user_id": user_id,
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

    async def authenticate_user(self, credentials: UserLogin) -> TokenResponse:
        """Authenticate user with AWS Cognito"""
        try:
            if self.is_mock:
                # Mock response for testing
                mock_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoidGVzdF91c2VyIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjo5OTk5OTk5OTk5fQ.test-signature"
                return TokenResponse(
                    access_token=mock_token,
                    token_type="Bearer",
                    expires_in=3600,
                    refresh_token="mock_refresh_token",
                    user_id="test_user_123",
                    email=credentials.email
                )
            
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
                
                user_attributes = {
                    attr['Name']: attr['Value'] 
                    for attr in user_info['UserAttributes']
                }
                
                # Determine user role (admin for specific email)
                admin_emails = ['ahmedulkabir55@gmail.com']
                user_role = 'admin' if credentials.email in admin_emails else 'user'
                
                return TokenResponse(
                    access_token=tokens['AccessToken'],
                    refresh_token=tokens.get('RefreshToken'),
                    expires_in=tokens['ExpiresIn'],
                    user={
                        "user_id": user_info['Username'],
                        "email": credentials.email,
                        "full_name": user_attributes.get('name', ''),
                        "email_verified": user_attributes.get('email_verified') == 'true',
                        "role": user_role
                    }
                )
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

    async def refresh_token(self, refresh_token: str, username: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        try:
            if self.is_mock:
                # Mock response for testing
                return TokenResponse(
                    access_token="new_mock_access_token",
                    token_type="Bearer",
                    expires_in=3600,
                    refresh_token="new_mock_refresh_token"
                )
            
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
            return TokenResponse(
                access_token=tokens['AccessToken'],
                expires_in=tokens['ExpiresIn']
            )
            
        except ClientError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed"
            )

    async def forgot_password(self, email: str) -> MessageResponse:
        """Initiate password reset process"""
        try:
            if self.is_mock:
                # Mock response for testing
                return MessageResponse(message="Password reset code sent to email (mock)")
            
            secret_hash = self._get_secret_hash(email)
            
            self.client.forgot_password(
                ClientId=self.client_id,
                Username=email,
                SecretHash=secret_hash
            )
            
            return MessageResponse(message="Password reset code sent to email")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UserNotFoundException':
                # Don't reveal if user exists for security
                return MessageResponse(message="If the email exists, a reset code has been sent")
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Password reset failed"
                )

    async def confirm_forgot_password(self, data: PasswordConfirm) -> MessageResponse:
        """Confirm password reset with code"""
        try:
            if self.is_mock:
                # Mock response for testing
                return MessageResponse(message="Password reset successful (mock)")
            
            secret_hash = self._get_secret_hash(data.email)
            
            self.client.confirm_forgot_password(
                ClientId=self.client_id,
                Username=data.email,
                ConfirmationCode=data.confirmation_code,
                Password=data.new_password,
                SecretHash=secret_hash
            )
            
            return MessageResponse(message="Password reset successful")
            
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

    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
