"""
Activity Service - Manages user carbon tracking activities
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ActivityService:
    """Service for managing user activities and carbon tracking data."""
    
    def __init__(self):
        """Initialize the ActivityService."""
        self.activities = {}  # In-memory storage for demo purposes
        
    async def get_user_activities(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get user activities for the specified number of days.
        
        Args:
            user_id: User identifier
            days: Number of days to look back (default: 30)
            
        Returns:
            List of user activities with carbon impact data
        """
        try:
            # Only generate sample activities for explicit demo/admin/mock users; otherwise derive from real emissions or return empty
            from app.core.config import settings
            from app.services.dynamodb_service import dynamodb_service

            def _is_demo_user(uid: Optional[str]) -> bool:
                return bool(
                    uid
                    and (
                        uid in ("demo-user", "admin-user", "mock_admin_id")
                        or (settings.debug and str(uid).startswith("mock_"))
                    )
                )

            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            # Demo/admin users get generated sample activities for UX demos
            if _is_demo_user(user_id):
                activities: List[Dict[str, Any]] = []
                
                # Sample activity types and their carbon impact (demo only)
                sample_activities = [
                    {
                        "activity_type": "transportation",
                        "activity_name": "Drive to work",
                        "carbon_footprint": 12.5,
                        "category": "commute",
                        "description": "Daily commute by car"
                    },
                    {
                        "activity_type": "transportation",
                        "activity_name": "Public transport",
                        "carbon_footprint": 3.2,
                        "category": "commute",
                        "description": "Bus/metro commute"
                    },
                    {
                        "activity_type": "energy",
                        "activity_name": "Home electricity",
                        "carbon_footprint": 8.7,
                        "category": "utilities",
                        "description": "Daily electricity usage"
                    },
                    {
                        "activity_type": "food",
                        "activity_name": "Meat consumption",
                        "carbon_footprint": 6.1,
                        "category": "diet",
                        "description": "Beef/pork meals"
                    },
                    {
                        "activity_type": "food",
                        "activity_name": "Plant-based meal",
                        "carbon_footprint": 1.8,
                        "category": "diet",
                        "description": "Vegetarian/vegan meals"
                    },
                    {
                        "activity_type": "waste",
                        "activity_name": "Recycling",
                        "carbon_footprint": -2.1,
                        "category": "sustainability",
                        "description": "Waste recycling activities"
                    }
                ]

                current_date = start_date
                import random
                while current_date <= end_date:
                    daily_activities = random.sample(sample_activities, random.randint(2, 4))
                    for idx, activity in enumerate(daily_activities):
                        activity_record = {
                            "activity_id": f"{user_id}_{current_date.strftime('%Y%m%d')}_{idx}",
                            "user_id": user_id,
                            "timestamp": current_date.isoformat(),
                            "date": current_date.strftime('%Y-%m-%d'),
                            **activity
                        }
                        activities.append(activity_record)
                    current_date += timedelta(days=1)

                logger.info(f"Generated {len(activities)} demo activities for user {user_id}")
                return activities

            # For real users, derive activities from stored emissions within date range
            start_iso = start_date.isoformat()
            end_iso = end_date.isoformat()
            emissions = await dynamodb_service.get_user_emissions(user_id, start_iso, end_iso, limit=1000)

            if not emissions:
                return []

            activities: List[Dict[str, Any]] = []
            for idx, emission in enumerate(emissions):
                # Map emission record to an activity-like structure
                ts = emission.get("timestamp") or emission.get("created_at") or datetime.utcnow().isoformat()
                date_str = emission.get("date") or (ts[:10] if isinstance(ts, str) else datetime.utcnow().strftime("%Y-%m-%d"))
                activity_record = {
                    "activity_id": emission.get("entry_id") or f"{user_id}_{idx}",
                    "user_id": user_id,
                    "timestamp": ts,
                    "date": date_str,
                    "activity_type": emission.get("category", "other"),
                    "activity_name": emission.get("activity", "unknown"),
                    "category": emission.get("category", "other"),
                    "carbon_footprint": float(emission.get("co2_equivalent", 0) or 0),
                    "description": emission.get("description", ""),
                    # Fields used by RecommendationEngine
                    "co2_equivalent": float(emission.get("co2_equivalent", 0) or 0),
                    "activity": emission.get("activity", "unknown"),
                }
                activities.append(activity_record)

            logger.info(f"Derived {len(activities)} activities from emissions for user {user_id}")
            return activities
            
        except Exception as e:
            logger.error(f"Error getting user activities: {str(e)}")
            return []
    
    async def add_activity(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new activity for the user.
        
        Args:
            user_id: User identifier
            activity_data: Activity information
            
        Returns:
            Created activity record
        """
        try:
            activity_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            activity_record = {
                "activity_id": activity_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "date": datetime.now().strftime('%Y-%m-%d'),
                **activity_data
            }
            
            # Store activity (in production, this would go to a database)
            if user_id not in self.activities:
                self.activities[user_id] = []
            self.activities[user_id].append(activity_record)
            
            logger.info(f"Added activity {activity_id} for user {user_id}")
            return activity_record
            
        except Exception as e:
            logger.error(f"Error adding activity: {str(e)}")
            raise
    
    async def get_activity_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get activity summary for the user.
        
        Args:
            user_id: User identifier
            days: Number of days to summarize (default: 7)
            
        Returns:
            Activity summary with totals and averages
        """
        try:
            activities = await self.get_user_activities(user_id, days)
            
            total_carbon = sum(activity.get('carbon_footprint', 0) for activity in activities)
            activity_count = len(activities)
            
            # Group by category
            categories = {}
            for activity in activities:
                category = activity.get('category', 'other')
                if category not in categories:
                    categories[category] = {
                        'count': 0,
                        'total_carbon': 0
                    }
                categories[category]['count'] += 1
                categories[category]['total_carbon'] += activity.get('carbon_footprint', 0)
            
            summary = {
                "user_id": user_id,
                "period_days": days,
                "total_activities": activity_count,
                "total_carbon_footprint": round(total_carbon, 2),
                "average_daily_carbon": round(total_carbon / max(days, 1), 2),
                "categories": categories,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated activity summary for user {user_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating activity summary: {str(e)}")
            return {}