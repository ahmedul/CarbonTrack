"""
DynamoDB models for CarbonTrack application
Defines the data structure and operations for DynamoDB tables
"""

from datetime import datetime, date
from typing import Optional, Dict, Any
from decimal import Decimal
import uuid

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback for when pydantic is not available
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def dict(self):
            return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def Field(default=None, **kwargs):
        return default


class CarbonEmissionModel(BaseModel):
    """Carbon emission entry model for DynamoDB"""
    
    # Primary key
    user_id: str = Field(..., description="User ID from Cognito")
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique entry ID")
    
    # Emission data
    date: date = Field(..., description="Date of the emission")
    category: str = Field(..., description="Category (transportation, energy, food, etc.)")
    activity: str = Field(..., description="Specific activity (car_drive, flight, etc.)")
    amount: Decimal = Field(..., description="Amount of activity")
    unit: str = Field(..., description="Unit of measurement (km, kWh, etc.)")
    description: Optional[str] = Field(None, description="Optional description")
    
    # Calculated values
    co2_equivalent: Optional[Decimal] = Field(None, description="CO2 equivalent in kg")
    emission_factor: Optional[Decimal] = Field(None, description="Emission factor used")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        # Allow decimal types for DynamoDB
        json_encoders = {
            Decimal: float,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert model to DynamoDB item format"""
        item = self.dict()
        
        # Convert datetime objects to ISO strings
        item['created_at'] = self.created_at.isoformat()
        item['updated_at'] = self.updated_at.isoformat()
        item['date'] = self.date.isoformat()
        
        # Convert Decimal to float for JSON serialization
        if self.co2_equivalent:
            item['co2_equivalent'] = float(self.co2_equivalent)
        if self.emission_factor:
            item['emission_factor'] = float(self.emission_factor)
        item['amount'] = float(self.amount)
        
        return item


class UserProfileModel(BaseModel):
    """User profile model for DynamoDB"""
    
    # Primary key
    user_id: str = Field(..., description="User ID from Cognito")
    
    # Profile data
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    
    # Preferences
    preferred_units: Dict[str, str] = Field(
        default={
            "distance": "km",
            "energy": "kWh",
            "weight": "kg"
        },
        description="User's preferred units"
    )
    carbon_budget: Optional[Decimal] = Field(None, description="Monthly carbon budget in kg CO2")
    
    # Statistics
    total_emissions: Decimal = Field(default=Decimal('0'), description="Total emissions in kg CO2")
    current_month_emissions: Decimal = Field(default=Decimal('0'), description="Current month emissions")
    entries_count: int = Field(default=0, description="Total number of entries")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            Decimal: float,
            datetime: lambda v: v.isoformat()
        }

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert model to DynamoDB item format"""
        item = self.dict()
        
        # Convert datetime objects
        item['created_at'] = self.created_at.isoformat()
        item['updated_at'] = self.updated_at.isoformat()
        item['last_active'] = self.last_active.isoformat()
        
        # Convert Decimal to float
        item['total_emissions'] = float(self.total_emissions)
        item['current_month_emissions'] = float(self.current_month_emissions)
        if self.carbon_budget:
            item['carbon_budget'] = float(self.carbon_budget)
        
        return item


class GoalModel(BaseModel):
    """Carbon reduction goal model for DynamoDB"""
    
    # Primary key
    user_id: str = Field(..., description="User ID from Cognito")
    goal_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique goal ID")
    
    # Goal data
    category: str = Field(..., description="Category of emissions to target")
    target_amount: Decimal = Field(..., description="Target amount in kg CO2")
    target_period: str = Field(..., description="Period (daily, weekly, monthly, yearly)")
    description: Optional[str] = Field(None, description="Goal description")
    
    # Progress tracking
    current_amount: Decimal = Field(default=Decimal('0'), description="Current amount achieved")
    is_active: bool = Field(default=True, description="Whether goal is active")
    is_achieved: bool = Field(default=False, description="Whether goal is achieved")
    
    # Dates
    start_date: date = Field(..., description="Goal start date")
    end_date: date = Field(..., description="Goal end date")
    achieved_date: Optional[date] = Field(None, description="Date when goal was achieved")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            Decimal: float,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert model to DynamoDB item format"""
        item = self.dict()
        
        # Convert datetime and date objects
        item['created_at'] = self.created_at.isoformat()
        item['updated_at'] = self.updated_at.isoformat()
        item['start_date'] = self.start_date.isoformat()
        item['end_date'] = self.end_date.isoformat()
        if self.achieved_date:
            item['achieved_date'] = self.achieved_date.isoformat()
        
        # Convert Decimal to float
        item['target_amount'] = float(self.target_amount)
        item['current_amount'] = float(self.current_amount)
        
        return item


class AchievementModel(BaseModel):
    """User achievement model for DynamoDB"""
    
    # Primary key
    user_id: str = Field(..., description="User ID from Cognito")
    achievement_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique achievement ID")
    
    # Achievement data
    title: str = Field(..., description="Achievement title")
    description: str = Field(..., description="Achievement description")
    category: str = Field(..., description="Achievement category")
    icon: Optional[str] = Field(None, description="Achievement icon")
    
    # Achievement details
    requirement_type: str = Field(..., description="Type of requirement (entries, reduction, streak)")
    requirement_value: Decimal = Field(..., description="Required value to unlock")
    current_progress: Decimal = Field(default=Decimal('0'), description="Current progress")
    
    # Status
    is_unlocked: bool = Field(default=False, description="Whether achievement is unlocked")
    unlocked_date: Optional[datetime] = Field(None, description="Date when unlocked")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            Decimal: float,
            datetime: lambda v: v.isoformat()
        }

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert model to DynamoDB item format"""
        item = self.dict()
        
        # Convert datetime objects
        item['created_at'] = self.created_at.isoformat()
        item['updated_at'] = self.updated_at.isoformat()
        if self.unlocked_date:
            item['unlocked_date'] = self.unlocked_date.isoformat()
        
        # Convert Decimal to float
        item['requirement_value'] = float(self.requirement_value)
        item['current_progress'] = float(self.current_progress)
        
        return item
