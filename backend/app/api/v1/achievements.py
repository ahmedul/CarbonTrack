"""
Achievements API routes
"""

from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from app.core.middleware import get_current_user
from app.services.dynamodb_service import dynamodb_service
from app.models.dynamodb_models import AchievementModel

# Achievement schemas (should eventually move to schemas/achievements.py)
from pydantic import BaseModel, Field

class AchievementCreate(BaseModel):
    """Schema for creating a new achievement"""
    title: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=5, max_length=500)
    category: str = Field(..., description="Achievement category (milestone, reduction, streak, category)")
    icon: Optional[str] = Field(None, max_length=10, description="Emoji icon")
    requirement_type: str = Field(..., description="Type of requirement (entries, reduction, streak)")
    requirement_value: float = Field(..., gt=0, description="Required value to unlock")


class AchievementResponse(BaseModel):
    """Schema for achievement response"""
    achievement_id: str
    user_id: str
    title: str
    description: str
    category: str
    icon: Optional[str]
    requirement_type: str
    requirement_value: float
    current_progress: float = 0.0
    is_unlocked: bool = False
    unlocked_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    progress_percentage: float = 0.0
    points: int = 10  # Default points value


class AchievementStatsResponse(BaseModel):
    """Schema for achievement statistics"""
    total_achievements: int
    unlocked_count: int
    locked_count: int
    total_points: int
    categories: Dict[str, int]
    recent_unlocks: List[AchievementResponse]


router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.get("/", response_model=List[AchievementResponse])
async def get_achievements(
    current_user: Dict[str, Any] = Depends(get_current_user),
    unlocked_only: bool = Query(False, description="Show only unlocked achievements"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get user's achievements and available achievements
    
    - **unlocked_only**: Only show unlocked achievements
    - **category**: Filter by achievement category
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get achievements from DynamoDB
        achievements = await dynamodb_service.get_user_achievements(user_id)
        
        # Filter by category if specified
        if category:
            achievements = [a for a in achievements if a.get('category') == category]
        
        # Filter by unlocked status if specified
        if unlocked_only:
            achievements = [a for a in achievements if a.get('is_unlocked', False)]
        
        # Transform to response format
        achievement_responses = []
        for achievement in achievements:
            # Calculate progress percentage
            requirement = float(achievement.get('requirement_value', 1))
            current = float(achievement.get('current_progress', 0))
            progress = min((current / requirement * 100), 100.0) if requirement > 0 else 0.0
            
            # Calculate points based on category and requirement
            points = 10  # Base points
            if achievement.get('category') == 'milestone':
                points = int(requirement * 5)
            elif achievement.get('category') == 'streak':
                points = int(requirement * 10)
            elif achievement.get('category') == 'reduction':
                points = int(requirement * 2)
            
            achievement_response = AchievementResponse(
                achievement_id=achievement.get('achievementId', ''),
                user_id=achievement.get('userId', ''),
                title=achievement.get('title', ''),
                description=achievement.get('description', ''),
                category=achievement.get('category', 'other'),
                icon=achievement.get('icon'),
                requirement_type=achievement.get('requirement_type', 'entries'),
                requirement_value=requirement,
                current_progress=current,
                is_unlocked=achievement.get('is_unlocked', False),
                unlocked_date=datetime.fromisoformat(achievement['unlocked_date']) if achievement.get('unlocked_date') else None,
                created_at=datetime.fromisoformat(achievement.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(achievement.get('updated_at', datetime.now().isoformat())),
                progress_percentage=progress,
                points=points
            )
            achievement_responses.append(achievement_response)
        
        return achievement_responses
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving achievements: {str(e)}")


@router.get("/stats", response_model=AchievementStatsResponse)
async def get_achievement_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get achievement statistics for the user"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get all achievements
        achievements = await dynamodb_service.get_user_achievements(user_id)
        
        # Calculate statistics
        total_count = len(achievements)
        unlocked_achievements = [a for a in achievements if a.get('is_unlocked', False)]
        unlocked_count = len(unlocked_achievements)
        locked_count = total_count - unlocked_count
        
        # Calculate total points
        total_points = 0
        for achievement in unlocked_achievements:
            requirement = float(achievement.get('requirement_value', 1))
            if achievement.get('category') == 'milestone':
                total_points += int(requirement * 5)
            elif achievement.get('category') == 'streak':
                total_points += int(requirement * 10)
            elif achievement.get('category') == 'reduction':
                total_points += int(requirement * 2)
            else:
                total_points += 10
        
        # Group by categories
        categories = {}
        for achievement in achievements:
            category = achievement.get('category', 'other')
            categories[category] = categories.get(category, 0) + 1
        
        # Get recent unlocks (last 5)
        recent_unlocks = sorted(
            [a for a in unlocked_achievements if a.get('unlocked_date')],
            key=lambda x: x.get('unlocked_date', ''),
            reverse=True
        )[:5]
        
        recent_unlock_responses = []
        for achievement in recent_unlocks:
            requirement = float(achievement.get('requirement_value', 1))
            points = 10
            if achievement.get('category') == 'milestone':
                points = int(requirement * 5)
            elif achievement.get('category') == 'streak':
                points = int(requirement * 10)
            elif achievement.get('category') == 'reduction':
                points = int(requirement * 2)
                
            recent_unlock_responses.append(AchievementResponse(
                achievement_id=achievement.get('achievementId', ''),
                user_id=achievement.get('userId', ''),
                title=achievement.get('title', ''),
                description=achievement.get('description', ''),
                category=achievement.get('category', 'other'),
                icon=achievement.get('icon'),
                requirement_type=achievement.get('requirement_type', 'entries'),
                requirement_value=requirement,
                current_progress=float(achievement.get('current_progress', 0)),
                is_unlocked=True,
                unlocked_date=datetime.fromisoformat(achievement['unlocked_date']) if achievement.get('unlocked_date') else None,
                created_at=datetime.fromisoformat(achievement.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(achievement.get('updated_at', datetime.now().isoformat())),
                progress_percentage=100.0,
                points=points
            ))
        
        return AchievementStatsResponse(
            total_achievements=total_count,
            unlocked_count=unlocked_count,
            locked_count=locked_count,
            total_points=total_points,
            categories=categories,
            recent_unlocks=recent_unlock_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving achievement stats: {str(e)}")


@router.post("/", response_model=AchievementResponse, status_code=status.HTTP_201_CREATED)
async def create_achievement(
    achievement_data: AchievementCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new achievement (admin/system use)
    
    This endpoint is typically used by the system to create new achievements,
    not by regular users.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Create AchievementModel
        achievement = AchievementModel(
            user_id=user_id,
            title=achievement_data.title,
            description=achievement_data.description,
            category=achievement_data.category,
            icon=achievement_data.icon,
            requirement_type=achievement_data.requirement_type,
            requirement_value=Decimal(str(achievement_data.requirement_value))
        )
        
        # Save to DynamoDB
        result = await dynamodb_service.create_achievement(achievement)
        
        if result.get("success"):
            # Calculate points
            points = 10
            if achievement_data.category == 'milestone':
                points = int(achievement_data.requirement_value * 5)
            elif achievement_data.category == 'streak':
                points = int(achievement_data.requirement_value * 10)
            elif achievement_data.category == 'reduction':
                points = int(achievement_data.requirement_value * 2)
            
            return AchievementResponse(
                achievement_id=result["achievement_id"],
                user_id=user_id,
                title=achievement_data.title,
                description=achievement_data.description,
                category=achievement_data.category,
                icon=achievement_data.icon,
                requirement_type=achievement_data.requirement_type,
                requirement_value=achievement_data.requirement_value,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                points=points
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to create achievement"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating achievement: {str(e)}")


@router.get("/{achievement_id}", response_model=AchievementResponse)
async def get_achievement(
    achievement_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific achievement by ID"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get all user achievements and find the specific one
        achievements = await dynamodb_service.get_user_achievements(user_id)
        achievement = next((a for a in achievements if a.get('achievementId') == achievement_id), None)
        
        if not achievement:
            raise HTTPException(status_code=404, detail="Achievement not found")
        
        # Transform to response format
        requirement = float(achievement.get('requirement_value', 1))
        current = float(achievement.get('current_progress', 0))
        progress = min((current / requirement * 100), 100.0) if requirement > 0 else 0.0
        
        # Calculate points
        points = 10
        if achievement.get('category') == 'milestone':
            points = int(requirement * 5)
        elif achievement.get('category') == 'streak':
            points = int(requirement * 10)
        elif achievement.get('category') == 'reduction':
            points = int(requirement * 2)
        
        return AchievementResponse(
            achievement_id=achievement.get('achievementId', ''),
            user_id=achievement.get('userId', ''),
            title=achievement.get('title', ''),
            description=achievement.get('description', ''),
            category=achievement.get('category', 'other'),
            icon=achievement.get('icon'),
            requirement_type=achievement.get('requirement_type', 'entries'),
            requirement_value=requirement,
            current_progress=current,
            is_unlocked=achievement.get('is_unlocked', False),
            unlocked_date=datetime.fromisoformat(achievement['unlocked_date']) if achievement.get('unlocked_date') else None,
            created_at=datetime.fromisoformat(achievement.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(achievement.get('updated_at', datetime.now().isoformat())),
            progress_percentage=progress,
            points=points
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving achievement: {str(e)}")


@router.post("/initialize-defaults", response_model=Dict[str, Any])
async def initialize_default_achievements(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Initialize default achievements for a user
    
    This creates a standard set of achievements that all users can work towards.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Check if user already has achievements
        existing_achievements = await dynamodb_service.get_user_achievements(user_id)
        if existing_achievements:
            return {"message": f"User already has {len(existing_achievements)} achievements"}
        
        # Default achievements to create
        default_achievements = [
            {
                "title": "First Steps",
                "description": "Record your first carbon emission entry",
                "category": "milestone",
                "icon": "🌱",
                "requirement_type": "entries",
                "requirement_value": 1
            },
            {
                "title": "Week Warrior",
                "description": "Track emissions for 7 consecutive days",
                "category": "streak",
                "icon": "💪",
                "requirement_type": "consecutive_days",
                "requirement_value": 7
            },
            {
                "title": "Eco Champion",
                "description": "Record 50 carbon emission entries",
                "category": "milestone",
                "icon": "🏆",
                "requirement_type": "entries",
                "requirement_value": 50
            },
            {
                "title": "Carbon Cutter",
                "description": "Reduce emissions by 20% compared to previous month",
                "category": "reduction",
                "icon": "✂️",
                "requirement_type": "reduction_percentage",
                "requirement_value": 20
            }
        ]
        
        created_count = 0
        for achievement_data in default_achievements:
            achievement = AchievementModel(
                user_id=user_id,
                title=achievement_data["title"],
                description=achievement_data["description"],
                category=achievement_data["category"],
                icon=achievement_data["icon"],
                requirement_type=achievement_data["requirement_type"],
                requirement_value=Decimal(str(achievement_data["requirement_value"]))
            )
            
            result = await dynamodb_service.create_achievement(achievement)
            if result.get("success"):
                created_count += 1
        
        return {
            "message": f"Successfully initialized {created_count} default achievements",
            "created_count": created_count,
            "total_defaults": len(default_achievements)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing achievements: {str(e)}")