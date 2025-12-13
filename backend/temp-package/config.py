"""
Configuration settings for CarbonTrack backend
"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # App configuration
    app_name: str = "CarbonTrack API"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Server configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # AWS configuration
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_access_key_id: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # Cognito configuration
    cognito_user_pool_id: str = os.getenv("COGNITO_USER_POOL_ID", "us-east-1_XXXXXXXXX")
    cognito_client_id: str = os.getenv("COGNITO_CLIENT_ID", "your_client_id_here")
    cognito_client_secret: str = os.getenv("COGNITO_CLIENT_SECRET", "your_client_secret_here")
    
    # DynamoDB tables
    users_table: str = os.getenv("USERS_TABLE", "carbontrack-users")
    entries_table: str = os.getenv("ENTRIES_TABLE", "carbontrack-entries")
    
    # JWT configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your_super_secret_jwt_key_change_in_production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # CORS origins
    allowed_origins: list = [
        origin.strip() 
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    ]

# Global settings instance
settings = Settings()
