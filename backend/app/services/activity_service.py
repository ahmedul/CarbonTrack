"""
Activity Service - Manages user carbon tracking activities
"""

from typing import List, Dict, Any
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
            # Generate sample activities for demo purposes
            activities = []
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Sample activity types and their carbon impact
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
            
            # Generate activities for the time period
            current_date = start_date
            while current_date <= end_date:
                # Add 2-4 activities per day
                import random
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
                
            logger.info(f"Generated {len(activities)} activities for user {user_id}")
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