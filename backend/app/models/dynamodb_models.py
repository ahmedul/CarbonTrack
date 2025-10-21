from datetime import datetime, date
from typing import Optional, Dict, Any
from decimal import Decimal
import uuid
from dataclasses import dataclass, field

@dataclass
class CarbonEmissionModel:
    user_id: str
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    emission_date: date = field(default_factory=date.today)
    category: str = ""
    activity: str = ""
    amount: Decimal = field(default_factory=lambda: Decimal('0'))
    unit: str = ""
    description: Optional[str] = None
    co2_equivalent: Optional[Decimal] = None
    emission_factor: Optional[Decimal] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dynamodb_item(self) -> Dict[str, Any]:
        item = {
            # Use table's partition key naming (user_id)
            'user_id': self.user_id,
            'entry_id': self.entry_id,
            'date': self.emission_date.isoformat(),
            'category': self.category,
            'activity': self.activity,
            'amount': float(self.amount),
            'unit': self.unit,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if self.description:
            item['description'] = self.description
        if self.co2_equivalent:
            item['co2_equivalent'] = float(self.co2_equivalent)
        if self.emission_factor:
            item['emission_factor'] = float(self.emission_factor)
        return item

@dataclass
class UserProfileModel:
    user_id: str
    email: str = ""
    full_name: str = ""
    avatar_url: Optional[str] = None
    preferred_units: Dict[str, str] = field(default_factory=lambda: {"distance": "km", "energy": "kWh", "weight": "kg"})
    carbon_budget: Optional[Decimal] = None
    total_emissions: Decimal = field(default_factory=lambda: Decimal('0'))
    current_month_emissions: Decimal = field(default_factory=lambda: Decimal('0'))
    entries_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)

@dataclass  
class GoalModel:
    user_id: str
    goal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: Optional[str] = None
    target_reduction: Decimal = field(default_factory=lambda: Decimal('0'))
    target_date: date = field(default_factory=date.today)
    category: Optional[str] = None
    current_progress: Decimal = field(default_factory=lambda: Decimal('0'))
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AchievementModel:
    achievement_id: str
    title: str = ""
    description: str = ""
    icon: str = ""
    points: int = 0
    requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserAchievementModel:
    user_id: str
    achievement_id: str
    progress: Decimal = field(default_factory=lambda: Decimal('0'))
    unlocked_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
