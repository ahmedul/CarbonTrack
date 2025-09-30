"""
API endpoints for carbon reduction recommendations
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any
from app.services.recommendation_engine import RecommendationEngine
from app.services.activity_service import ActivityService
from app.core.middleware import get_current_user
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"]
)

# Initialize services
recommendation_engine = RecommendationEngine()
activity_service = ActivityService()


@router.get("/")
async def get_user_recommendations(
    category: str = Query(default=None, description="Category filter"),
    limit: int = Query(default=10, ge=1, le=50),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get personalized carbon reduction recommendations for the user
    
    Args:
        category: Optional category filter (transportation, energy, food, waste, lifestyle)
        limit: Maximum number of recommendations to return (default: 10)
        current_user: Authenticated user information
        
    Returns:
        Dict containing recommendations, user stats, and potential savings
    """
    try:
        user_id = current_user.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user authentication")
            
        # Get user activities for analysis
        activities = await activity_service.get_user_activities(user_id)
        
        # Generate personalized recommendations
        recommendations = recommendation_engine.generate_recommendations(
            activities=activities,
            category_filter=category,
            limit=limit
        )
        
        # Get user patterns for context
        user_patterns = recommendation_engine.analyze_user_patterns(activities)
        
        # Calculate potential total savings
        total_potential_savings = sum(
            rec.get('co2_savings_kg', 0) for rec in recommendations
        )
        
        # Get implementation stats
        implementation_stats = _get_implementation_stats(recommendations)
        
        return {
            "success": True,
            "data": {
                "recommendations": recommendations,
                "user_patterns": user_patterns,
                "total_potential_savings_kg": round(total_potential_savings, 2),
                "implementation_stats": implementation_stats,
                "count": len(recommendations)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendations for user {current_user.get('user_id')}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


@router.get("/categories")
async def get_recommendation_categories() -> Dict[str, Any]:
    """
    Get available recommendation categories
    
    Returns:
        Dict containing available categories and their descriptions
    """
    try:
        categories = {
            "transportation": {
                "name": "Transportation",
                "description": "Reduce emissions from travel and commuting",
                "icon": "🚗"
            },
            "energy": {
                "name": "Energy",
                "description": "Optimize home and office energy usage",
                "icon": "⚡"
            },
            "food": {
                "name": "Food & Diet",
                "description": "Make sustainable dietary choices",
                "icon": "🥗"
            },
            "waste": {
                "name": "Waste Management",
                "description": "Reduce, reuse, and recycle effectively",
                "icon": "♻️"
            },
            "lifestyle": {
                "name": "Lifestyle",
                "description": "Adopt sustainable living practices",
                "icon": "🌱"
            }
        }
        
        return {
            "success": True,
            "data": {
                "categories": categories
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching recommendation categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")


@router.get("/stats")
async def get_recommendation_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get recommendation statistics and impact metrics for the user
    
    Args:
        current_user: Authenticated user information
        
    Returns:
        Dict containing recommendation statistics and impact data
    """
    try:
        user_id = current_user.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user authentication")
            
        # Get user activities
        activities = await activity_service.get_user_activities(user_id)
        
        # Generate recommendations for analysis
        all_recommendations = recommendation_engine.generate_recommendations(
            activities=activities,
            limit=50  # Get more for comprehensive stats
        )
        
        # Calculate statistics
        stats = {
            "total_recommendations": len(all_recommendations),
            "by_category": _get_category_breakdown(all_recommendations),
            "by_difficulty": _get_difficulty_breakdown(all_recommendations),
            "by_cost": _get_cost_breakdown(all_recommendations),
            "potential_impact": {
                "total_co2_savings_kg": sum(rec.get('co2_savings_kg', 0) for rec in all_recommendations),
                "high_impact_count": len([rec for rec in all_recommendations if rec.get('co2_savings_kg', 0) > 50]),
                "quick_wins": len([rec for rec in all_recommendations if rec.get('difficulty') == 'Easy' and rec.get('co2_savings_kg', 0) > 10])
            }
        }
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendation stats for user {current_user.get('user_id')}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate statistics")


def _get_implementation_stats(recommendations: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate implementation statistics for recommendations"""
    stats = {
        "easy": 0,
        "medium": 0,
        "hard": 0,
        "free": 0,
        "low_cost": 0,
        "medium_cost": 0,
        "high_cost": 0
    }
    
    for rec in recommendations:
        # Difficulty breakdown
        difficulty = rec.get('difficulty', '').lower()
        if difficulty in stats:
            stats[difficulty] += 1
            
        # Cost breakdown
        cost = rec.get('cost', '').lower().replace(' ', '_')
        if cost in stats:
            stats[cost] += 1
            
    return stats


def _get_category_breakdown(recommendations: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get breakdown of recommendations by category"""
    breakdown = {}
    for rec in recommendations:
        category = rec.get('category', 'other')
        breakdown[category] = breakdown.get(category, 0) + 1
    return breakdown


def _get_difficulty_breakdown(recommendations: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get breakdown of recommendations by difficulty"""
    breakdown = {}
    for rec in recommendations:
        difficulty = rec.get('difficulty', 'Unknown')
        breakdown[difficulty] = breakdown.get(difficulty, 0) + 1
    return breakdown


def _get_cost_breakdown(recommendations: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get breakdown of recommendations by cost"""
    breakdown = {}
    for rec in recommendations:
        cost = rec.get('cost', 'Unknown')
        breakdown[cost] = breakdown.get(cost, 0) + 1
    return breakdown