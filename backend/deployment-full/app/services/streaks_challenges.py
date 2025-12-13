"""
Streaks and Challenges System for CarbonTrack Gamification
Handles daily streaks, weekly/monthly challenges, and progress tracking
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass
import logging

# Setup logging
logger = logging.getLogger(__name__)


class ChallengeType(Enum):
    """Types of challenges available"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SPECIAL = "special"


class ChallengeDifficulty(Enum):
    """Challenge difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXTREME = "extreme"


@dataclass
class Challenge:
    """Challenge definition"""
    id: str
    name: str
    description: str
    type: ChallengeType
    difficulty: ChallengeDifficulty
    points_reward: int
    bonus_points: int
    duration_days: int
    criteria: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    icon: str
    completion_message: str
    is_active: bool = True


class StreaksChallengesEngine:
    """
    Manages user streaks, daily/weekly/monthly challenges, and progress tracking
    """
    
    def __init__(self):
        self.challenges = self._initialize_challenges()
    
    def _initialize_challenges(self) -> Dict[str, Challenge]:
        """Initialize all available challenges"""
        challenges = {}
        now = datetime.utcnow()
        
        # Daily Challenges (rotate daily)
        daily_challenges = [
            Challenge(
                id="daily_logger",
                name="Daily Logger",
                description="Log at least 3 carbon activities today",
                type=ChallengeType.DAILY,
                difficulty=ChallengeDifficulty.EASY,
                points_reward=100,
                bonus_points=50,
                duration_days=1,
                criteria={"activities_logged": 3, "timeframe": "today"},
                start_date=now.replace(hour=0, minute=0, second=0, microsecond=0),
                end_date=now.replace(hour=23, minute=59, second=59, microsecond=0),
                icon="📝",
                completion_message="Great job logging your activities today!"
            ),
            Challenge(
                id="transport_tracker",
                name="Transport Tracker", 
                description="Log 5 transportation activities today",
                type=ChallengeType.DAILY,
                difficulty=ChallengeDifficulty.MEDIUM,
                points_reward=150,
                bonus_points=75,
                duration_days=1,
                criteria={"category": "transportation", "activities_logged": 5, "timeframe": "today"},
                start_date=now.replace(hour=0, minute=0, second=0, microsecond=0),
                end_date=now.replace(hour=23, minute=59, second=59, microsecond=0),
                icon="🚗",
                completion_message="Transport tracking mastered for today!"
            ),
            Challenge(
                id="energy_monitor",
                name="Energy Monitor",
                description="Log your home energy usage for today",
                type=ChallengeType.DAILY,
                difficulty=ChallengeDifficulty.EASY,
                points_reward=120,
                bonus_points=60,
                duration_days=1,
                criteria={"category": "energy", "activities_logged": 2, "timeframe": "today"},
                start_date=now.replace(hour=0, minute=0, second=0, microsecond=0),
                end_date=now.replace(hour=23, minute=59, second=59, microsecond=0),
                icon="⚡",
                completion_message="Energy monitoring complete!"
            ),
            Challenge(
                id="food_conscious",
                name="Food Conscious",
                description="Log 3 food-related carbon activities today",
                type=ChallengeType.DAILY,
                difficulty=ChallengeDifficulty.MEDIUM,
                points_reward=140,
                bonus_points=70,
                duration_days=1,
                criteria={"category": "food", "activities_logged": 3, "timeframe": "today"},
                start_date=now.replace(hour=0, minute=0, second=0, microsecond=0),
                end_date=now.replace(hour=23, minute=59, second=59, microsecond=0),
                icon="🥗",
                completion_message="Food tracking excellence achieved!"
            )
        ]
        
        # Weekly Challenges
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        weekly_challenges = [
            Challenge(
                id="weekly_warrior",
                name="Weekly Warrior",
                description="Log activities every day this week",
                type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.MEDIUM,
                points_reward=500,
                bonus_points=250,
                duration_days=7,
                criteria={"daily_streak": 7, "timeframe": "week"},
                start_date=week_start,
                end_date=week_end,
                icon="⚔️",
                completion_message="Weekly warrior status achieved! Incredible consistency!"
            ),
            Challenge(
                id="carbon_reducer",
                name="Carbon Reducer",
                description="Reduce your weekly emissions by 10% compared to last week",
                type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.HARD,
                points_reward=800,
                bonus_points=400,
                duration_days=7,
                criteria={"reduction_percentage": 10, "timeframe": "week"},
                start_date=week_start,
                end_date=week_end,
                icon="📉",
                completion_message="Significant reduction achieved! You're making real impact!"
            ),
            Challenge(
                id="category_master",
                name="Category Master",
                description="Log activities in all 4 categories this week",
                type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.MEDIUM,
                points_reward=600,
                bonus_points=300,
                duration_days=7,
                criteria={"all_categories": True, "timeframe": "week"},
                start_date=week_start,
                end_date=week_end,
                icon="🏆",
                completion_message="Category mastery! You're tracking comprehensively!"
            ),
            Challenge(
                id="recommendation_champion",
                name="Recommendation Champion",
                description="Complete 3 recommended actions this week",
                type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.HARD,
                points_reward=750,
                bonus_points=375,
                duration_days=7,
                criteria={"recommendations_completed": 3, "timeframe": "week"},
                start_date=week_start,
                end_date=week_end,
                icon="💡",
                completion_message="Recommendation champion! You're turning insights into action!"
            )
        ]
        
        # Monthly Challenges
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            month_end = month_start.replace(year=now.year + 1, month=1) - timedelta(seconds=1)
        else:
            month_end = month_start.replace(month=now.month + 1) - timedelta(seconds=1)
        
        monthly_challenges = [
            Challenge(
                id="monthly_milestone",
                name="Monthly Milestone",
                description="Log 100 activities this month",
                type=ChallengeType.MONTHLY,
                difficulty=ChallengeDifficulty.HARD,
                points_reward=2000,
                bonus_points=1000,
                duration_days=30,
                criteria={"activities_logged": 100, "timeframe": "month"},
                start_date=month_start,
                end_date=month_end,
                icon="🎯",
                completion_message="Monthly milestone crushed! Your dedication is inspiring!"
            ),
            Challenge(
                id="carbon_impact_hero",
                name="Carbon Impact Hero",
                description="Achieve 20% carbon reduction this month",
                type=ChallengeType.MONTHLY,
                difficulty=ChallengeDifficulty.EXTREME,
                points_reward=3000,
                bonus_points=1500,
                duration_days=30,
                criteria={"reduction_percentage": 20, "timeframe": "month"},
                start_date=month_start,
                end_date=month_end,
                icon="🦸",
                completion_message="Carbon Impact Hero! Your environmental impact is extraordinary!"
            ),
            Challenge(
                id="streak_legend",
                name="Streak Legend",
                description="Maintain a 30-day logging streak",
                type=ChallengeType.MONTHLY,
                difficulty=ChallengeDifficulty.HARD,
                points_reward=2500,
                bonus_points=1250,
                duration_days=30,
                criteria={"streak_days": 30, "timeframe": "month"},
                start_date=month_start,
                end_date=month_end,
                icon="🔥",
                completion_message="Streak Legend! Your consistency is legendary!"
            )
        ]
        
        # Special/Seasonal Challenges
        special_challenges = [
            Challenge(
                id="earth_week_hero",
                name="Earth Week Hero",
                description="Special Earth Week challenge - Complete 10 eco-actions",
                type=ChallengeType.SPECIAL,
                difficulty=ChallengeDifficulty.MEDIUM,
                points_reward=1000,
                bonus_points=500,
                duration_days=7,
                criteria={"eco_actions": 10, "timeframe": "special"},
                start_date=now,
                end_date=now + timedelta(days=7),
                icon="🌍",
                completion_message="Earth Week Hero! You're celebrating our planet in action!"
            )
        ]
        
        # Combine all challenges
        all_challenges = daily_challenges + weekly_challenges + monthly_challenges + special_challenges
        
        # Convert to dictionary
        for challenge in all_challenges:
            challenges[challenge.id] = challenge
            
        return challenges
    
    def calculate_streak(self, activity_dates: List[str]) -> Dict[str, Any]:
        """
        Calculate user's current streak and streak statistics
        
        Args:
            activity_dates: List of dates when user logged activities (YYYY-MM-DD format)
            
        Returns:
            Dictionary with streak information
        """
        if not activity_dates:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "last_activity_date": None,
                "streak_status": "no_activities"
            }
        
        # Convert strings to dates and sort
        dates = []
        for date_str in activity_dates:
            try:
                dates.append(datetime.strptime(date_str, "%Y-%m-%d").date())
            except ValueError:
                continue
                
        if not dates:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "last_activity_date": None,
                "streak_status": "no_activities"
            }
        
        dates = sorted(set(dates))  # Remove duplicates and sort
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # Calculate current streak
        current_streak = 0
        if dates[-1] == today or dates[-1] == yesterday:
            # Streak is active
            for i in range(len(dates) - 1, -1, -1):
                expected_date = dates[-1] - timedelta(days=len(dates) - 1 - i)
                if dates[i] == expected_date:
                    current_streak += 1
                else:
                    break
        
        # Calculate longest streak
        longest_streak = 1
        temp_streak = 1
        
        for i in range(1, len(dates)):
            if dates[i] == dates[i-1] + timedelta(days=1):
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
        
        # Determine streak status
        if dates[-1] == today:
            streak_status = "active_today"
        elif dates[-1] == yesterday:
            streak_status = "active_yesterday"
        else:
            streak_status = "broken"
            
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_activity_date": dates[-1].isoformat(),
            "streak_status": streak_status,
            "total_active_days": len(dates)
        }
    
    def check_challenge_progress(self, challenge_id: str, user_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check progress on a specific challenge
        
        Args:
            challenge_id: ID of the challenge to check
            user_stats: User statistics and activity data
            
        Returns:
            Challenge progress information
        """
        if challenge_id not in self.challenges:
            return {}
            
        challenge = self.challenges[challenge_id]
        progress = self._calculate_challenge_progress(challenge, user_stats)
        
        return {
            "challenge_id": challenge_id,
            "name": challenge.name,
            "description": challenge.description,
            "type": challenge.type.value,
            "difficulty": challenge.difficulty.value,
            "points_reward": challenge.points_reward,
            "bonus_points": challenge.bonus_points,
            "progress": progress["progress"],
            "is_completed": progress["is_completed"],
            "completion_rate": progress["completion_rate"],
            "time_remaining": self._get_time_remaining(challenge),
            "icon": challenge.icon,
            "is_active": challenge.is_active and datetime.utcnow() <= challenge.end_date
        }
    
    def _calculate_challenge_progress(self, challenge: Challenge, user_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate progress for a specific challenge"""
        criteria = challenge.criteria
        progress = {
            "progress": 0,
            "is_completed": False,
            "completion_rate": 0.0
        }
        
        try:
            if "activities_logged" in criteria:
                target = criteria["activities_logged"]
                current = user_stats.get("activities_logged", 0)
                
                # Filter by category if specified
                if "category" in criteria:
                    current = user_stats.get(f"{criteria['category']}_activities", 0)
                
                progress["progress"] = current
                progress["completion_rate"] = min(100.0, (current / target) * 100)
                progress["is_completed"] = current >= target
                
            elif "reduction_percentage" in criteria:
                target = criteria["reduction_percentage"]
                current = user_stats.get("reduction_percentage", 0)
                progress["progress"] = current
                progress["completion_rate"] = min(100.0, (current / target) * 100)
                progress["is_completed"] = current >= target
                
            elif "daily_streak" in criteria:
                target = criteria["daily_streak"]
                current = user_stats.get("current_streak", 0)
                progress["progress"] = current
                progress["completion_rate"] = min(100.0, (current / target) * 100)
                progress["is_completed"] = current >= target
                
            elif "all_categories" in criteria:
                categories_logged = user_stats.get("categories_logged", [])
                required_categories = ["transportation", "energy", "food", "waste"]
                completed_categories = len([cat for cat in required_categories if cat in categories_logged])
                progress["progress"] = completed_categories
                progress["completion_rate"] = (completed_categories / len(required_categories)) * 100
                progress["is_completed"] = completed_categories == len(required_categories)
                
            elif "recommendations_completed" in criteria:
                target = criteria["recommendations_completed"]
                current = user_stats.get("recommendations_completed", 0)
                progress["progress"] = current
                progress["completion_rate"] = min(100.0, (current / target) * 100)
                progress["is_completed"] = current >= target
                
            elif "streak_days" in criteria:
                target = criteria["streak_days"]
                current = user_stats.get("current_streak", 0)
                progress["progress"] = current
                progress["completion_rate"] = min(100.0, (current / target) * 100)
                progress["is_completed"] = current >= target
                
        except Exception as e:
            logger.error(f"Error calculating challenge progress for {challenge.id}: {str(e)}")
            
        return progress
    
    def _get_time_remaining(self, challenge: Challenge) -> Dict[str, Any]:
        """Get time remaining for a challenge"""
        now = datetime.utcnow()
        
        if now > challenge.end_date:
            return {
                "expired": True,
                "days": 0,
                "hours": 0,
                "minutes": 0
            }
            
        time_diff = challenge.end_date - now
        days = time_diff.days
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60
        
        return {
            "expired": False,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "total_seconds": time_diff.total_seconds()
        }
    
    def get_active_challenges(self) -> List[Dict[str, Any]]:
        """Get all currently active challenges"""
        now = datetime.utcnow()
        active = []
        
        for challenge in self.challenges.values():
            if challenge.is_active and now <= challenge.end_date:
                active.append({
                    "id": challenge.id,
                    "name": challenge.name,
                    "description": challenge.description,
                    "type": challenge.type.value,
                    "difficulty": challenge.difficulty.value,
                    "points_reward": challenge.points_reward,
                    "bonus_points": challenge.bonus_points,
                    "duration_days": challenge.duration_days,
                    "icon": challenge.icon,
                    "time_remaining": self._get_time_remaining(challenge)
                })
                
        return active
    
    def complete_challenge(self, challenge_id: str, user_id: str) -> Dict[str, Any]:
        """Mark a challenge as completed and calculate rewards"""
        if challenge_id not in self.challenges:
            return {"success": False, "error": "Challenge not found"}
            
        challenge = self.challenges[challenge_id]
        now = datetime.utcnow()
        
        if now > challenge.end_date:
            return {"success": False, "error": "Challenge has expired"}
            
        # Calculate points (with potential bonus for early completion)
        total_points = challenge.points_reward
        
        # Bonus points for completing with time remaining
        time_remaining = self._get_time_remaining(challenge)
        if not time_remaining["expired"]:
            remaining_percentage = time_remaining["total_seconds"] / (challenge.duration_days * 24 * 3600)
            if remaining_percentage > 0.5:  # More than 50% time remaining
                total_points += challenge.bonus_points
                
        return {
            "success": True,
            "challenge_id": challenge_id,
            "challenge_name": challenge.name,
            "points_earned": total_points,
            "bonus_earned": challenge.bonus_points if remaining_percentage > 0.5 else 0,
            "completion_message": challenge.completion_message,
            "completed_at": now.isoformat()
        }