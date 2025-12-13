"""
Gamification API endpoints for CarbonTrack
Handles achievements, streaks, challenges, leaderboards, and user progress
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
from app.services.achievement_engine import AchievementEngine
from app.services.streaks_challenges import StreaksChallengesEngine
from app.services.leaderboard_engine import LeaderboardEngine
from app.core.middleware import get_current_user
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/gamification",
    tags=["gamification"]
)

# Initialize gamification engines
achievement_engine = AchievementEngine()
streaks_challenges_engine = StreaksChallengesEngine()
leaderboard_engine = LeaderboardEngine()


@router.get("/profile")
async def get_gamification_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get comprehensive gamification profile for the user
    
    Returns:
        Complete gamification profile with points, level, achievements, streaks
    """
    try:
        user_id = current_user.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user authentication")
        
        # Privacy-safe behavior: for non-demo users without data, return empty/zeroed profile
        user_stats = await _get_user_stats(user_id)
        
        # Calculate user level and progress
        level_info = achievement_engine.calculate_user_level(user_stats.get("total_points", 0))
        
        # Get recent achievements
        recent_achievements = await _get_recent_achievements(user_id, limit=5)
        
        # Get streak information
        activity_dates = user_stats.get("activity_dates", [])
        streak_info = streaks_challenges_engine.calculate_streak(activity_dates)
        
        # Get current challenges progress
        active_challenges = streaks_challenges_engine.get_active_challenges()
        challenges_progress = []
        for challenge in active_challenges[:3]:  # Top 3 challenges
            progress = streaks_challenges_engine.check_challenge_progress(
                challenge["id"], user_stats
            )
            challenges_progress.append(progress)
        
        return {
            "success": True,
            "data": {
                "user_profile": {
                    "user_id": user_id,
                    "total_points": user_stats.get("total_points", 0),
                    "level": level_info,
                    "achievements_count": user_stats.get("achievements_count", 0),
                    "goals_achieved": user_stats.get("goals_achieved", 0),
                    "streak": streak_info
                },
                "recent_achievements": recent_achievements,
                "active_challenges": challenges_progress,
                "statistics": {
                    "total_activities": user_stats.get("total_activities", 0),
                    "carbon_saved_kg": user_stats.get("total_co2_reduced", 0),
                    "recommendations_completed": user_stats.get("recommendations_completed", 0),
                    "days_active": len(set(activity_dates)) if activity_dates else 0
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting gamification profile for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get gamification profile")


@router.get("/achievements")
async def get_achievements(
    current_user: Dict[str, Any] = Depends(get_current_user),
    include_progress: bool = Query(True, description="Include progress towards incomplete achievements")
) -> Dict[str, Any]:
    """
    Get user achievements and progress
    
    Args:
        include_progress: Whether to include progress towards incomplete achievements
        
    Returns:
        User achievements, progress, and available achievements
    """
    try:
        user_id = current_user.get('user_id')
        user_stats = await _get_user_stats(user_id)
        
        # Get all available achievements
        all_achievements = achievement_engine.get_all_achievements()
        
        # Get user's earned achievements
        earned_achievements = await _get_user_achievements(user_id)
        earned_ids = {ach["achievement_id"] for ach in earned_achievements}
        
        # Calculate progress for unearned achievements
        progress_info = []
        if include_progress:
            for achievement in all_achievements:
                if achievement["id"] not in earned_ids:
                    progress = achievement_engine.get_achievement_progress(
                        achievement["id"], user_stats
                    )
                    if progress:
                        progress_info.append(progress)
        
        return {
            "success": True,
            "data": {
                "earned_achievements": earned_achievements,
                "achievements_progress": sorted(progress_info, key=lambda x: x["progress"], reverse=True),
                "statistics": {
                    "total_earned": len(earned_achievements),
                    "total_available": len(all_achievements),
                    "completion_rate": round((len(earned_achievements) / len(all_achievements)) * 100, 1),
                    "total_points_from_achievements": sum(ach.get("points", 0) for ach in earned_achievements)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting achievements for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get achievements")


@router.get("/challenges")
async def get_challenges(
    current_user: Dict[str, Any] = Depends(get_current_user),
    challenge_type: Optional[str] = Query(None, description="Filter by challenge type (daily, weekly, monthly)")
) -> Dict[str, Any]:
    """
    Get active challenges and user progress
    
    Args:
        challenge_type: Optional filter by challenge type
        
    Returns:
        Active challenges with user progress
    """
    try:
        user_id = current_user.get('user_id')
        user_stats = await _get_user_stats(user_id)
        
        # Get active challenges
        active_challenges = streaks_challenges_engine.get_active_challenges()
        
        # Filter by type if specified
        if challenge_type:
            active_challenges = [c for c in active_challenges if c["type"] == challenge_type]
        
        # Get progress for each challenge
        challenges_with_progress = []
        for challenge in active_challenges:
            progress = streaks_challenges_engine.check_challenge_progress(
                challenge["id"], user_stats
            )
            challenges_with_progress.append(progress)
        
        # Get completed challenges for today
        completed_today = await _get_completed_challenges_today(user_id)
        
        return {
            "success": True,
            "data": {
                "active_challenges": challenges_with_progress,
                "completed_today": completed_today,
                "statistics": {
                    "total_active": len(challenges_with_progress),
                    "completed_count": len(completed_today),
                    "potential_points": sum(c.get("points_reward", 0) for c in active_challenges),
                    "potential_bonus": sum(c.get("bonus_points", 0) for c in active_challenges)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting challenges for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get challenges")


@router.post("/challenges/{challenge_id}/complete")
async def complete_challenge(
    challenge_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Mark a challenge as completed
    
    Args:
        challenge_id: ID of the challenge to complete
        
    Returns:
        Challenge completion result with points earned
    """
    try:
        user_id = current_user.get('user_id')
        
        # Complete the challenge
        result = streaks_challenges_engine.complete_challenge(challenge_id, user_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Update user points (in production, save to database)
        await _update_user_points(user_id, result["points_earned"])
        
        # Check for new achievements
        user_stats = await _get_user_stats(user_id)
        new_achievements = achievement_engine.check_achievements(user_stats)
        
        return {
            "success": True,
            "data": {
                "challenge_completion": result,
                "new_achievements": new_achievements,
                "total_points_earned": result["points_earned"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error completing challenge {challenge_id} for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete challenge")


@router.get("/leaderboards")
async def get_leaderboards(
    current_user: Dict[str, Any] = Depends(get_current_user),
    leaderboard_type: Optional[str] = Query(None, description="Filter by leaderboard type"),
    period: Optional[str] = Query(None, description="Filter by time period"),
    limit: int = Query(50, description="Number of entries per leaderboard")
) -> Dict[str, Any]:
    """
    Get available leaderboards
    
    Args:
        leaderboard_type: Optional filter by type (points, carbon_reduction, streak, activities)
        period: Optional filter by period (daily, weekly, monthly, all_time)
        limit: Maximum entries per leaderboard
        
    Returns:
        Available leaderboards with current rankings
    """
    try:
        user_id = current_user.get('user_id')
        
        # Get available leaderboards
        available_leaderboards = leaderboard_engine.get_available_leaderboards()
        
        # Filter leaderboards if specified
        if leaderboard_type:
            available_leaderboards = [lb for lb in available_leaderboards if lb["type"] == leaderboard_type]
        if period:
            available_leaderboards = [lb for lb in available_leaderboards if lb["period"] == period]
        
        # For privacy, don't include mock global data for regular users
        user_data = await _get_leaderboard_user_data()
        
        # Generate leaderboards
        leaderboards = []
        for lb_config in available_leaderboards[:6]:  # Limit to 6 leaderboards
            leaderboard = leaderboard_engine.generate_leaderboard(
                lb_config["id"], user_data, user_id, limit
            )
            leaderboards.append(leaderboard)
        
        return {
            "success": True,
            "data": {
                "leaderboards": leaderboards,
                "available_types": list(set(lb["type"] for lb in available_leaderboards)),
                "available_periods": list(set(lb["period"] for lb in available_leaderboards))
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting leaderboards: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboards")


@router.get("/leaderboards/{leaderboard_id}")
async def get_leaderboard_by_id(
    leaderboard_id: str,
    limit: int = Query(default=10, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get a specific leaderboard with detailed rankings
    
    Args:
        leaderboard_id: ID of the leaderboard to retrieve
        limit: Maximum number of entries to return
        
    Returns:
        Detailed leaderboard with rankings
    """
    try:
        user_id = current_user.get('user_id')
        
        # Get user data for leaderboard
        user_data = await _get_leaderboard_user_data()
        
        # Generate specific leaderboard
        leaderboard = leaderboard_engine.generate_leaderboard(
            leaderboard_id, user_data, user_id, limit
        )
        
        if "error" in leaderboard:
            raise HTTPException(status_code=404, detail="Leaderboard not found")
        
        return {
            "success": True,
            "data": leaderboard
        }
        
    except Exception as e:
        logger.error(f"Error getting leaderboard {leaderboard_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")


@router.get("/stats")
async def get_gamification_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get comprehensive gamification statistics for the user
    
    Returns:
        Detailed gamification statistics and progress metrics
    """
    try:
        user_id = current_user.get('user_id')
        user_stats = await _get_user_stats(user_id)
        
        # Get user rankings across all leaderboards
        leaderboard_data = await _get_leaderboard_user_data()
        rankings = leaderboard_engine.get_user_rankings(user_id, leaderboard_data)
        
        # Calculate engagement metrics
        activity_dates = user_stats.get("activity_dates", [])
        streak_info = streaks_challenges_engine.calculate_streak(activity_dates)
        
        return {
            "success": True,
            "data": {
                "overview": {
                    "total_points": user_stats.get("total_points", 0),
                    "current_level": achievement_engine.calculate_user_level(user_stats.get("total_points", 0))["current_level"],
                    "achievements_earned": user_stats.get("achievements_count", 0),
                    "current_streak": streak_info["current_streak"],
                    "goals_achieved": user_stats.get("goals_achieved", 0)
                },
                "rankings": rankings,
                "engagement": {
                    "total_active_days": len(set(activity_dates)) if activity_dates else 0,
                    "longest_streak": streak_info["longest_streak"],
                    "avg_activities_per_day": user_stats.get("avg_activities_per_day", 0),
                    "consistency_score": min(100, (streak_info["current_streak"] / 30) * 100)
                },
                "impact": {
                    "total_co2_saved": user_stats.get("total_co2_reduced", 0),
                    "recommendations_completed": user_stats.get("recommendations_completed", 0),
                    "environmental_impact_score": user_stats.get("environmental_impact_score", 0)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting gamification stats for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get gamification stats")


# Helper functions (in production, these would interact with database)

async def _get_user_stats(user_id: str) -> Dict[str, Any]:
    """Get user statistics for gamification calculations.
    Privacy-safe default: return zeros/empty for regular users until real data exists.
    Demo/admin/mock users may receive illustrative sample data in debug.
    """
    from app.core.config import settings
    def _is_demo(uid: str) -> bool:
        return uid in ("demo-user", "admin-user", "mock_admin_id") or (settings.debug and str(uid).startswith("mock_"))

    if _is_demo(user_id):
        return {
            "total_points": 2850,
            "total_activities": 47,
            "achievements_count": 8,
            "goals_achieved": 3,
            "goals_set": 5,
            "current_streak": 12,
            "longest_streak": 18,
            "total_co2_reduced": 245.7,
            "recommendations_completed": 6,
            "activity_dates": [
                "2025-09-19", "2025-09-20", "2025-09-21", "2025-09-22", "2025-09-23",
                "2025-09-24", "2025-09-25", "2025-09-26", "2025-09-27", "2025-09-28",
                "2025-09-29", "2025-09-30"
            ],
            "points_today": 150,
            "points_this_week": 850,
            "points_this_month": 2850,
            "activities_today": 3,
            "activities_this_week": 18,
            "activities_this_month": 47,
            "co2_reduced_this_week": 45.2,
            "co2_reduced_this_month": 245.7,
            "avg_activities_per_day": 2.3,
            "environmental_impact_score": 78
        }
    # Regular users: empty defaults
    return {
        "total_points": 0,
        "total_activities": 0,
        "achievements_count": 0,
        "goals_achieved": 0,
        "goals_set": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "total_co2_reduced": 0,
        "recommendations_completed": 0,
        "activity_dates": [],
        "points_today": 0,
        "points_this_week": 0,
        "points_this_month": 0,
        "activities_today": 0,
        "activities_this_week": 0,
        "activities_this_month": 0,
        "co2_reduced_this_week": 0,
        "co2_reduced_this_month": 0,
        "avg_activities_per_day": 0,
        "environmental_impact_score": 0
    }


async def _get_user_achievements(user_id: str) -> List[Dict[str, Any]]:
    """Get user's earned achievements.
    Returns empty for regular users by default; sample only for demo/admin/mock in debug.
    """
    from app.core.config import settings
    if user_id in ("demo-user", "admin-user", "mock_admin_id") or (settings.debug and str(user_id).startswith("mock_")):
        return [
            {
                "achievement_id": "first_entry",
                "name": "Getting Started",
                "points": 50,
                "tier": "bronze",
                "icon": "🌱",
                "earned_at": "2025-09-15T10:00:00Z"
            },
            {
                "achievement_id": "carbon_conscious",
                "name": "Carbon Conscious",
                "points": 200,
                "tier": "bronze", 
                "icon": "🌍",
                "earned_at": "2025-09-18T14:30:00Z"
            }
        ]
    return []


async def _get_recent_achievements(user_id: str, limit: int) -> List[Dict[str, Any]]:
    """Get user's most recent achievements"""
    achievements = await _get_user_achievements(user_id)
    return sorted(achievements, key=lambda x: x["earned_at"], reverse=True)[:limit]


async def _get_completed_challenges_today(user_id: str) -> List[Dict[str, Any]]:
    """Get challenges completed by user today.
    Returns empty by default for regular users.
    """
    from app.core.config import settings
    if user_id in ("demo-user", "admin-user", "mock_admin_id") or (settings.debug and str(user_id).startswith("mock_")):
        return [
            {
                "challenge_id": "daily_logger",
                "name": "Daily Logger",
                "points_earned": 150,
                "completed_at": "2025-09-30T16:45:00Z"
            }
        ]
    return []


async def _update_user_points(user_id: str, points: int) -> bool:
    """Update user's total points"""
    # In production, update database
    logger.info(f"Updated user {user_id} points by {points}")
    return True


async def _get_leaderboard_user_data() -> List[Dict[str, Any]]:
    """Get user data for leaderboard generation.
    For now, return empty to avoid showing unrelated users to regular accounts.
    Demo/admin users may receive sample data in future behind an explicit flag.
    """
    return []


# Helper functions for gamification API endpoints