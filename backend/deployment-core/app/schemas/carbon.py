"""
Pydantic schemas for carbon tracking
"""

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field
from enum import Enum


class EmissionCategory(str, Enum):
    """Carbon emission categories"""
    TRANSPORTATION = "transportation"
    ENERGY = "energy"
    FOOD = "food"
    WASTE = "waste"
    SHOPPING = "shopping"
    OTHER = "other"


class TransportActivity(str, Enum):
    """Transportation activities"""
    CAR_DRIVE = "car_drive"
    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"
    SUBWAY = "subway"
    BIKE = "bike"
    WALK = "walk"


class CarbonEmissionCreate(BaseModel):
    """Schema for creating carbon emission entry"""
    date: date
    category: EmissionCategory
    activity: str
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    unit: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=500)


class CarbonEmissionUpdate(BaseModel):
    """Schema for updating carbon emission entry"""
    date: Optional[date] = None
    category: Optional[EmissionCategory] = None
    activity: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=500)


class CarbonEmissionResponse(BaseModel):
    """Schema for carbon emission response"""
    id: str
    user_id: str
    date: date
    category: EmissionCategory
    activity: str
    amount: float
    unit: str
    description: Optional[str] = None
    co2_equivalent: float  # Calculated CO2 equivalent in kg
    created_at: datetime
    updated_at: datetime


class AnalyticsRequest(BaseModel):
    """Schema for analytics request"""
    start_date: date
    end_date: date
    category: Optional[EmissionCategory] = None


class AnalyticsResponse(BaseModel):
    """Schema for analytics response"""
    total_emissions: float
    emissions_by_category: dict
    emissions_by_month: dict
    average_daily_emissions: float
    reduction_from_previous_period: Optional[float] = None
    period_start: date
    period_end: date


class GoalCreate(BaseModel):
    """Schema for creating a goal"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    target_reduction: float = Field(..., gt=0, le=100, description="Target reduction percentage")
    target_date: date
    category: Optional[EmissionCategory] = None


class GoalResponse(BaseModel):
    """Schema for goal response"""
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    target_reduction: float
    current_progress: float
    target_date: date
    category: Optional[EmissionCategory] = None
    status: str  # active, completed, expired
    created_at: datetime


class AchievementResponse(BaseModel):
    """Schema for achievement response"""
    id: str
    title: str
    description: str
    icon: str
    points: int
    unlocked_at: Optional[datetime] = None
    progress: float  # 0-100 percentage
    requirements: dict
