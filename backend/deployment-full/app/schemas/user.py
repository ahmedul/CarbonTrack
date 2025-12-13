"""
Pydantic schemas for user management
"""

from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from decimal import Decimal


class UserProfileCreate(BaseModel):
    """Schema for creating user profile"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    preferred_units: Optional[Dict[str, str]] = Field(
        default={
            "distance": "km",
            "energy": "kWh",
            "weight": "kg"
        },
        description="User's preferred units for measurements"
    )
    carbon_budget: Optional[float] = Field(None, gt=0, description="Monthly carbon budget in kg CO2")


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    preferred_units: Optional[Dict[str, str]] = None
    carbon_budget: Optional[float] = Field(None, gt=0)


class UserProfileResponse(BaseModel):
    """Schema for user profile response"""
    user_id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    preferred_units: Dict[str, str] = Field(default_factory=dict)
    carbon_budget: Optional[float] = None
    total_emissions: float = 0.0
    current_month_emissions: float = 0.0
    entries_count: int = 0
    created_at: datetime
    updated_at: datetime
    last_active: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: float
        }


class UserStatsResponse(BaseModel):
    """Schema for user statistics response"""
    user_id: str
    total_emissions: float
    current_month_emissions: float
    entries_count: int
    goals_count: int = 0
    achievements_count: int = 0
    average_daily_emissions: float = 0.0
    last_entry_date: Optional[str] = None
    streak_days: int = 0
    
    class Config:
        json_encoders = {
            Decimal: float
        }


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences only"""
    preferred_units: Dict[str, str] = Field(
        ...,
        description="User's preferred units for distance, energy, weight etc."
    )
    carbon_budget: Optional[float] = Field(None, gt=0, description="Monthly carbon budget")