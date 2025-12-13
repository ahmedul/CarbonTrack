"""
Goals management API routes
"""

from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import date, datetime
from decimal import Decimal

from app.schemas.carbon import GoalCreate, EmissionCategory
from app.core.middleware import get_current_user
from app.services.dynamodb_service import dynamodb_service
from app.models.dynamodb_models import GoalModel

router = APIRouter(prefix="/goals", tags=["Goals"])


# Goal schemas (should eventually move to schemas/goals.py)
from pydantic import BaseModel, Field

class GoalUpdate(BaseModel):
    """Schema for updating a goal"""
    category: Optional[EmissionCategory] = None
    target_amount: Optional[float] = Field(None, gt=0)
    target_period: Optional[str] = Field(None, pattern="^(daily|weekly|monthly|yearly)$")
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class GoalResponse(BaseModel):
    """Schema for goal response"""
    goal_id: str
    user_id: str
    category: str
    target_amount: float
    target_period: str
    description: Optional[str]
    current_amount: float = 0.0
    is_active: bool = True
    is_achieved: bool = False
    start_date: date
    end_date: date
    achieved_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    progress_percentage: float = 0.0


@router.get("/", response_model=List[GoalResponse])
async def get_goals(
    current_user: Dict[str, Any] = Depends(get_current_user),
    active_only: bool = Query(True, description="Filter for active goals only"),
    category: Optional[EmissionCategory] = Query(None, description="Filter by category")
):
    """
    Get user's carbon reduction goals
    
    - **active_only**: Only return active goals (default: true)
    - **category**: Optional category filter
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get goals from DynamoDB
        goals = await dynamodb_service.get_user_goals(user_id, active_only)
        
        # Filter by category if specified
        if category:
            goals = [g for g in goals if g.get('category') == category.value]
        
        # Transform to response format
        goal_responses = []
        for goal in goals:
            # Calculate progress percentage
            target = float(goal.get('target_amount', 0))
            current = float(goal.get('current_amount', 0))
            progress = (current / target * 100) if target > 0 else 0.0
            
            goal_response = GoalResponse(
                goal_id=goal.get('goalId', ''),
                user_id=goal.get('userId', ''),
                category=goal.get('category', ''),
                target_amount=target,
                target_period=goal.get('target_period', 'monthly'),
                description=goal.get('description'),
                current_amount=current,
                is_active=goal.get('is_active', True),
                is_achieved=goal.get('is_achieved', False),
                start_date=datetime.fromisoformat(goal.get('start_date', datetime.now().date().isoformat())).date(),
                end_date=datetime.fromisoformat(goal.get('end_date', datetime.now().date().isoformat())).date(),
                achieved_date=datetime.fromisoformat(goal['achieved_date']).date() if goal.get('achieved_date') else None,
                created_at=datetime.fromisoformat(goal.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(goal.get('updated_at', datetime.now().isoformat())),
                progress_percentage=progress
            )
            goal_responses.append(goal_response)
        
        return goal_responses
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving goals: {str(e)}")


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new carbon reduction goal
    
    - **category**: Category to target (transportation, energy, etc.)
    - **target_amount**: Target emission amount in kg CO2
    - **target_period**: Time period (daily, weekly, monthly, yearly)
    - **description**: Optional goal description
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Calculate start and end dates based on period
        start_date = date.today()
        if goal_data.target_period == "daily":
            end_date = start_date
        elif goal_data.target_period == "weekly":
            days_ahead = 6 - start_date.weekday()
            end_date = start_date.replace(day=start_date.day + days_ahead)
        elif goal_data.target_period == "monthly":
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1, day=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1, day=1)
            end_date = end_date.replace(day=end_date.day - 1)  # Last day of current month
        else:  # yearly
            end_date = start_date.replace(year=start_date.year + 1, month=1, day=1)
            end_date = end_date.replace(day=end_date.day - 1)  # Dec 31
        
        # Create GoalModel
        goal = GoalModel(
            user_id=user_id,
            category=goal_data.category.value,
            target_amount=Decimal(str(goal_data.target_amount)),
            target_period=goal_data.target_period,
            description=goal_data.description,
            start_date=start_date,
            end_date=end_date
        )
        
        # Save to DynamoDB
        result = await dynamodb_service.create_goal(goal)
        
        if result.get("success"):
            return GoalResponse(
                goal_id=result["goal_id"],
                user_id=user_id,
                category=goal_data.category.value,
                target_amount=goal_data.target_amount,
                target_period=goal_data.target_period,
                description=goal_data.description,
                start_date=start_date,
                end_date=end_date,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to create goal"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating goal: {str(e)}")


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific goal by ID"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get all user goals and find the specific one
        goals = await dynamodb_service.get_user_goals(user_id, active_only=False)
        goal = next((g for g in goals if g.get('goalId') == goal_id), None)
        
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Transform to response format
        target = float(goal.get('target_amount', 0))
        current = float(goal.get('current_amount', 0))
        progress = (current / target * 100) if target > 0 else 0.0
        
        return GoalResponse(
            goal_id=goal.get('goalId', ''),
            user_id=goal.get('userId', ''),
            category=goal.get('category', ''),
            target_amount=target,
            target_period=goal.get('target_period', 'monthly'),
            description=goal.get('description'),
            current_amount=current,
            is_active=goal.get('is_active', True),
            is_achieved=goal.get('is_achieved', False),
            start_date=datetime.fromisoformat(goal.get('start_date', datetime.now().date().isoformat())).date(),
            end_date=datetime.fromisoformat(goal.get('end_date', datetime.now().date().isoformat())).date(),
            achieved_date=datetime.fromisoformat(goal['achieved_date']).date() if goal.get('achieved_date') else None,
            created_at=datetime.fromisoformat(goal.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(goal.get('updated_at', datetime.now().isoformat())),
            progress_percentage=progress
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving goal: {str(e)}")


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    goal_data: GoalUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update an existing goal"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Prepare updates
        updates = {}
        for field, value in goal_data.dict().items():
            if value is not None:
                if field == "category" and value is not None:
                    updates[field] = value.value if hasattr(value, 'value') else str(value)
                elif field == "target_amount":
                    updates[field] = Decimal(str(value))
                else:
                    updates[field] = value
        
        if not updates:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # For now, we don't have a direct update method for goals in dynamodb_service
        # This would need to be implemented similar to the carbon emissions update
        raise HTTPException(status_code=501, detail="Goal update not yet implemented")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating goal: {str(e)}")


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a goal"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # For now, we don't have a direct delete method for goals in dynamodb_service
        # This would need to be implemented similar to the carbon emissions delete
        raise HTTPException(status_code=501, detail="Goal deletion not yet implemented")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting goal: {str(e)}")