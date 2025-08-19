"""
Carbon tracking API routes
"""

from fastapi import APIRouter, Depends, status, Query
from typing import Dict, Any, List, Optional
from datetime import date

from app.schemas.carbon import (
    CarbonEmissionCreate,
    CarbonEmissionUpdate,
    GoalCreate,
    EmissionCategory
)
from app.core.middleware import get_current_user

router = APIRouter(prefix="/carbon-emissions", tags=["Carbon Tracking"])


@router.get("/", response_model=List[Dict[str, Any]])
async def get_carbon_emissions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    category: Optional[EmissionCategory] = Query(None, description="Filter by category"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter")
):
    """
    Get user's carbon emissions with optional filtering
    
    - **category**: Optional category filter
    - **start_date**: Optional start date filter
    - **end_date**: Optional end date filter
    """
    # Mock response for now - replace with actual database implementation
    return [
        {
            "id": "emission_1",
            "user_id": current_user.get("user_id", "mock_user"),
            "date": "2024-01-15",
            "category": "transportation",
            "activity": "car_drive",
            "amount": 25.5,
            "unit": "km",
            "description": "Daily commute to office",
            "co2_equivalent": 5.1,
            "created_at": "2024-01-15T08:00:00Z",
            "updated_at": "2024-01-15T08:00:00Z"
        }
    ]


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_carbon_emission(
    emission_data: CarbonEmissionCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new carbon emission entry
    
    - **date**: Date of the emission
    - **category**: Category of emission (transportation, energy, etc.)
    - **activity**: Specific activity (car_drive, flight, etc.)
    - **amount**: Amount of activity
    - **unit**: Unit of measurement (km, kWh, etc.)
    - **description**: Optional description
    """
    # Mock response - replace with actual database implementation
    return {
        "id": "new_emission_id",
        "user_id": current_user.get("user_id", "mock_user"),
        "message": "Carbon emission recorded successfully",
        **emission_data.dict()
    }


@router.put("/{emission_id}", response_model=Dict[str, Any])
async def update_carbon_emission(
    emission_id: str,
    emission_data: CarbonEmissionUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update an existing carbon emission entry
    
    Only the owner of the emission can update it
    """
    # Mock response - replace with actual database implementation
    return {
        "id": emission_id,
        "user_id": current_user.get("user_id", "mock_user"),
        "message": "Carbon emission updated successfully",
        **{k: v for k, v in emission_data.dict().items() if v is not None}
    }


@router.delete("/{emission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_carbon_emission(
    emission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a carbon emission entry
    
    Only the owner of the emission can delete it
    """
    # Mock implementation - replace with actual database implementation
    pass


@router.get("/analytics", response_model=Dict[str, Any])
async def get_analytics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    start_date: date = Query(..., description="Start date for analytics"),
    end_date: date = Query(..., description="End date for analytics"),
    category: Optional[EmissionCategory] = Query(None, description="Filter by category")
):
    """
    Get carbon footprint analytics for a date range
    
    - **start_date**: Start date for analytics
    - **end_date**: End date for analytics
    - **category**: Optional category filter
    """
    # Mock response - replace with actual analytics calculation
    return {
        "total_emissions": 125.5,
        "emissions_by_category": {
            "transportation": 75.2,
            "energy": 30.1,
            "food": 15.8,
            "other": 4.4
        },
        "emissions_by_month": {
            "2024-01": 45.2,
            "2024-02": 38.7,
            "2024-03": 41.6
        },
        "average_daily_emissions": 4.18,
        "reduction_from_previous_period": 12.5,
        "period_start": start_date,
        "period_end": end_date
    }


# Goals endpoints
goals_router = APIRouter(prefix="/goals", tags=["Goals"])


@goals_router.get("/", response_model=List[Dict[str, Any]])
async def get_goals(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's carbon reduction goals"""
    # Mock response
    return [
        {
            "id": "goal_1",
            "user_id": current_user.get("user_id", "mock_user"),
            "title": "Reduce Transportation Emissions",
            "description": "Reduce car usage by 30% this year",
            "target_reduction": 30.0,
            "current_progress": 15.5,
            "target_date": "2024-12-31",
            "category": "transportation",
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]


@goals_router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new carbon reduction goal"""
    # Mock response
    return {
        "id": "new_goal_id",
        "user_id": current_user.get("user_id", "mock_user"),
        "message": "Goal created successfully",
        **goal_data.dict()
    }


# Achievements endpoints
achievements_router = APIRouter(prefix="/achievements", tags=["Achievements"])


@achievements_router.get("/", response_model=List[Dict[str, Any]])
async def get_achievements(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's achievements and available achievements"""
    # Mock response
    return [
        {
            "id": "first_entry",
            "title": "First Steps",
            "description": "Record your first carbon emission",
            "icon": "🌱",
            "points": 10,
            "unlocked_at": "2024-01-15T08:00:00Z",
            "progress": 100,
            "requirements": {"entries_count": 1}
        },
        {
            "id": "week_warrior",
            "title": "Week Warrior",
            "description": "Track emissions for 7 consecutive days",
            "icon": "💪",
            "points": 50,
            "unlocked_at": None,
            "progress": 42.8,
            "requirements": {"consecutive_days": 7}
        }
    ]
