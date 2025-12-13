"""
User profile API routes
"""

from fastapi import APIRouter, Depends, status, HTTPException
from typing import Dict, Any

from app.schemas.user import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    UserStatsResponse,
    UserPreferencesUpdate
)
from app.core.middleware import get_current_user
from app.services.dynamodb_service import dynamodb_service
from app.models.dynamodb_models import UserProfileModel

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get current user's profile
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get profile from DynamoDB
        profile = await dynamodb_service.get_user_profile(user_id)
        
        if not profile:
            # Create a basic profile if it doesn't exist
            email = current_user.get("email", f"user-{user_id}@carbontrack.dev")
            name = current_user.get("name", "User")
            
            new_profile = UserProfileModel(
                user_id=user_id,
                email=email,
                full_name=name
            )
            
            await dynamodb_service.create_user_profile(new_profile)
            profile = new_profile.to_dynamodb_item()
        
        return UserProfileResponse(**profile)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update current user's profile
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Prepare updates
        updates = {}
        for field, value in profile_data.dict().items():
            if value is not None:
                updates[field] = value
        
        if not updates:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # Update in DynamoDB
        success = await dynamodb_service.update_user_profile(user_id, updates)
        
        if not success:
            raise HTTPException(status_code=404, detail="Profile not found or could not be updated")
        
        # Get updated profile
        updated_profile = await dynamodb_service.get_user_profile(user_id)
        
        return UserProfileResponse(**updated_profile)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get current user's statistics and metrics
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get profile for basic stats
        profile = await dynamodb_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get additional stats (goals and achievements counts)
        goals = await dynamodb_service.get_user_goals(user_id)
        achievements = await dynamodb_service.get_user_achievements(user_id)
        
        # Get recent emissions for streak calculation
        recent_emissions = await dynamodb_service.get_user_emissions(user_id, limit=30)
        
        # Calculate streak days and last entry date
        streak_days = 0
        last_entry_date = None
        if recent_emissions:
            last_entry_date = recent_emissions[0].get("date")
            # Simple streak calculation - can be enhanced
            streak_days = len(set([e.get("date") for e in recent_emissions[:7]]))
        
        # Calculate average daily emissions (simplified)
        total_emissions = profile.get("total_emissions", 0)
        entries_count = profile.get("entries_count", 0)
        average_daily = total_emissions / max(entries_count, 1) if entries_count > 0 else 0
        
        return UserStatsResponse(
            user_id=user_id,
            total_emissions=total_emissions,
            current_month_emissions=profile.get("current_month_emissions", 0),
            entries_count=entries_count,
            goals_count=len(goals),
            achievements_count=len([a for a in achievements if a.get("is_unlocked", False)]),
            average_daily_emissions=average_daily,
            last_entry_date=last_entry_date,
            streak_days=streak_days
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


@router.put("/preferences", response_model=Dict[str, Any])
async def update_user_preferences(
    preferences_data: UserPreferencesUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user's preferences (units and carbon budget)
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Update preferences in DynamoDB
        updates = preferences_data.dict()
        success = await dynamodb_service.update_user_profile(user_id, updates)
        
        if not success:
            raise HTTPException(status_code=404, detail="Profile not found or could not be updated")
        
        return {
            "message": "Preferences updated successfully",
            **updates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")


@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete user's profile and all associated data
    WARNING: This action cannot be undone!
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # This is a placeholder - in a real app, you'd want to:
        # 1. Delete all user's emissions
        # 2. Delete all user's goals  
        # 3. Delete all user's achievements
        # 4. Delete user profile
        # 5. Consider soft delete vs hard delete
        
        raise HTTPException(
            status_code=501, 
            detail="Profile deletion not implemented - contact support for account deletion"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting profile: {str(e)}")