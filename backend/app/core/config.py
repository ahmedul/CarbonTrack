"""
Configuration settings for CarbonTrack backend
"""

from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings for better validation"""
    
    # App configuration
    app_name: str = "CarbonTrack API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # AWS configuration
    aws_region: str = "eu-central-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # Cognito configuration (EU-CENTRAL-1)
    cognito_user_pool_id: str = "eu-central-1_liszdknXy"
    cognito_client_id: str = "3rg58gvke8v6afmfng7o4fk0r1"
    cognito_client_secret: str = ""  # No secret for this client
    
    # DynamoDB tables
    users_table: str = "carbontrack-users"
    entries_table: str = "carbontrack-entries"
    goals_table: str = "carbontrack-goals"
    achievements_table: str = "carbontrack-achievements"
    
    # JWT configuration
    jwt_secret_key: str = "your_super_secret_jwt_key_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 30
    
    # CORS origins - allow all in production for ease of access
    allowed_origins: List[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )

    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
