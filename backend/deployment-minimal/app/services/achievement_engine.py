"""
Gamification Achievement System
Defines achievements, badges, and point calculations for CarbonTrack users
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Setup logging
logger = logging.getLogger(__name__)


class AchievementType(Enum):
    """Types of achievements available"""
    CARBON_REDUCTION = "carbon_reduction"
    STREAK = "streak"
    ACTIVITY_COUNT = "activity_count"
    GOAL_ACHIEVEMENT = "goal_achievement"
    SOCIAL = "social"
    MILESTONE = "milestone"


class BadgeTier(Enum):
    """Achievement badge tiers"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


@dataclass
class Achievement:
    """Achievement definition"""
    id: str
    name: str
    description: str
    type: AchievementType
    tier: BadgeTier
    points: int
    icon: str
    criteria: Dict[str, Any]
    unlocked_message: str
    progress_description: str
    is_repeatable: bool = False
    max_completions: Optional[int] = None


class AchievementEngine:
    """
    Comprehensive achievement and gamification system for CarbonTrack
    """
    
    def __init__(self):
        self.achievements = self._initialize_achievements()
    
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Initialize all available achievements"""
        achievements = {}
        
        # Carbon Reduction Achievements
        carbon_achievements = [
            Achievement(
                id="first_entry",
                name="Getting Started",
                description="Log your first carbon emission activity",
                type=AchievementType.ACTIVITY_COUNT,
                tier=BadgeTier.BRONZE,
                points=50,
                icon="🌱",
                criteria={"activity_count": 1},
                unlocked_message="Welcome to your carbon journey! Every step counts.",
                progress_description="Log 1 activity"
            ),
            Achievement(
                id="carbon_conscious",
                name="Carbon Conscious",
                description="Log 10 different carbon activities",
                type=AchievementType.ACTIVITY_COUNT,
                tier=BadgeTier.BRONZE,
                points=200,
                icon="🌍",
                criteria={"activity_count": 10},
                unlocked_message="You're building awareness of your carbon footprint!",
                progress_description="Log 10 activities"
            ),
            Achievement(
                id="eco_warrior",
                name="Eco Warrior",
                description="Log 50 carbon activities",
                type=AchievementType.ACTIVITY_COUNT,
                tier=BadgeTier.SILVER,
                points=500,
                icon="⚔️",
                criteria={"activity_count": 50},
                unlocked_message="You're fighting the good fight for our planet!",
                progress_description="Log 50 activities"
            ),
            Achievement(
                id="carbon_champion",
                name="Carbon Champion",
                description="Log 100 carbon activities",
                type=AchievementType.ACTIVITY_COUNT,
                tier=BadgeTier.GOLD,
                points=1000,
                icon="🏆",
                criteria={"activity_count": 100},
                unlocked_message="Champion level! You're a carbon tracking master!",
                progress_description="Log 100 activities"
            ),
            Achievement(
                id="planet_guardian",
                name="Planet Guardian",
                description="Log 250 carbon activities",
                type=AchievementType.ACTIVITY_COUNT,
                tier=BadgeTier.PLATINUM,
                points=2500,
                icon="🛡️",
                criteria={"activity_count": 250},
                unlocked_message="Guardian status achieved! You're protecting our planet!",
                progress_description="Log 250 activities"
            )
        ]
        
        # Streak Achievements
        streak_achievements = [
            Achievement(
                id="daily_habit",
                name="Daily Habit",
                description="Log activities for 7 consecutive days",
                type=AchievementType.STREAK,
                tier=BadgeTier.BRONZE,
                points=300,
                icon="🔥",
                criteria={"streak_days": 7},
                unlocked_message="You're building a sustainable habit!",
                progress_description="Log for 7 consecutive days"
            ),
            Achievement(
                id="consistency_king",
                name="Consistency King",
                description="Log activities for 30 consecutive days",
                type=AchievementType.STREAK,
                tier=BadgeTier.SILVER,
                points=1000,
                icon="👑",
                criteria={"streak_days": 30},
                unlocked_message="Incredible consistency! You're the king of habits!",
                progress_description="Log for 30 consecutive days"
            ),
            Achievement(
                id="unstoppable_force",
                name="Unstoppable Force",
                description="Log activities for 90 consecutive days",
                type=AchievementType.STREAK,
                tier=BadgeTier.GOLD,
                points=3000,
                icon="⚡",
                criteria={"streak_days": 90},
                unlocked_message="Unstoppable! Your commitment is inspiring!",
                progress_description="Log for 90 consecutive days"
            ),
            Achievement(
                id="carbon_centurion",
                name="Carbon Centurion",
                description="Log activities for 100 consecutive days",
                type=AchievementType.STREAK,
                tier=BadgeTier.PLATINUM,
                points=5000,
                icon="💯",
                criteria={"streak_days": 100},
                unlocked_message="Centurion status! Your dedication is legendary!",
                progress_description="Log for 100 consecutive days"
            )
        ]
        
        # Carbon Reduction Achievements
        reduction_achievements = [
            Achievement(
                id="first_reduction",
                name="First Steps",
                description="Reduce your weekly emissions by 5%",
                type=AchievementType.CARBON_REDUCTION,
                tier=BadgeTier.BRONZE,
                points=400,
                icon="📉",
                criteria={"reduction_percentage": 5},
                unlocked_message="Your first reduction! Every kilogram matters!",
                progress_description="Reduce weekly emissions by 5%"
            ),
            Achievement(
                id="progress_maker",
                name="Progress Maker",
                description="Reduce your monthly emissions by 10%",
                type=AchievementType.CARBON_REDUCTION,
                tier=BadgeTier.SILVER,
                points=800,
                icon="📊",
                criteria={"reduction_percentage": 10, "timeframe": "monthly"},
                unlocked_message="Significant progress! You're making a real difference!",
                progress_description="Reduce monthly emissions by 10%"
            ),
            Achievement(
                id="impact_creator",
                name="Impact Creator",
                description="Reduce your monthly emissions by 25%",
                type=AchievementType.CARBON_REDUCTION,
                tier=BadgeTier.GOLD,
                points=2000,
                icon="🌟",
                criteria={"reduction_percentage": 25, "timeframe": "monthly"},
                unlocked_message="Amazing impact! You're creating real change!",
                progress_description="Reduce monthly emissions by 25%"
            ),
            Achievement(
                id="carbon_neutral_hero",
                name="Carbon Neutral Hero",
                description="Achieve net-zero emissions for a month",
                type=AchievementType.CARBON_REDUCTION,
                tier=BadgeTier.DIAMOND,
                points=5000,
                icon="💎",
                criteria={"net_zero": True, "timeframe": "monthly"},
                unlocked_message="Net-zero achieved! You're a true climate hero!",
                progress_description="Achieve net-zero emissions for one month"
            )
        ]
        
        # Goal Achievement 
        goal_achievements = [
            Achievement(
                id="goal_setter",
                name="Goal Setter",
                description="Set your first carbon reduction goal",
                type=AchievementType.GOAL_ACHIEVEMENT,
                tier=BadgeTier.BRONZE,
                points=100,
                icon="🎯",
                criteria={"goals_set": 1},
                unlocked_message="Great! Setting goals is the first step to success!",
                progress_description="Set 1 carbon reduction goal"
            ),
            Achievement(
                id="goal_crusher",
                name="Goal Crusher",
                description="Achieve your first carbon reduction goal",
                type=AchievementType.GOAL_ACHIEVEMENT,
                tier=BadgeTier.SILVER,
                points=1000,
                icon="💪",
                criteria={"goals_achieved": 1},
                unlocked_message="Goal crushed! You're unstoppable!",
                progress_description="Achieve 1 carbon reduction goal"
            ),
            Achievement(
                id="serial_achiever",
                name="Serial Achiever",
                description="Achieve 5 carbon reduction goals",
                type=AchievementType.GOAL_ACHIEVEMENT,
                tier=BadgeTier.GOLD,
                points=3000,
                icon="🏅",
                criteria={"goals_achieved": 5},
                unlocked_message="Serial achiever! Your success inspires others!",
                progress_description="Achieve 5 carbon reduction goals"
            )
        ]
        
        # Milestone Achievements
        milestone_achievements = [
            Achievement(
                id="ton_saver",
                name="Ton Saver",
                description="Save 1,000kg (1 ton) of CO₂ compared to your baseline",
                type=AchievementType.MILESTONE,
                tier=BadgeTier.GOLD,
                points=2500,
                icon="🏔️",
                criteria={"co2_saved_kg": 1000},
                unlocked_message="You've saved a full ton of CO₂! Incredible impact!",
                progress_description="Save 1,000kg of CO₂"
            ),
            Achievement(
                id="carbon_saver_supreme",
                name="Carbon Saver Supreme",
                description="Save 5,000kg (5 tons) of CO₂ compared to baseline",
                type=AchievementType.MILESTONE,
                tier=BadgeTier.PLATINUM,
                points=10000,
                icon="🚀",
                criteria={"co2_saved_kg": 5000},
                unlocked_message="5 tons saved! You're a carbon reduction superstar!",
                progress_description="Save 5,000kg of CO₂"
            ),
            Achievement(
                id="earth_protector",
                name="Earth Protector", 
                description="Save 10,000kg (10 tons) of CO₂ compared to baseline",
                type=AchievementType.MILESTONE,
                tier=BadgeTier.DIAMOND,
                points=25000,
                icon="🌎",
                criteria={"co2_saved_kg": 10000},
                unlocked_message="Earth Protector! Your impact echoes across the planet!",
                progress_description="Save 10,000kg of CO₂"
            )
        ]
        
        # Social Achievements
        social_achievements = [
            Achievement(
                id="recommendation_follower",
                name="Action Taker",
                description="Complete your first recommended action",
                type=AchievementType.SOCIAL,
                tier=BadgeTier.BRONZE,
                points=300,
                icon="✅",
                criteria={"recommendations_completed": 1},
                unlocked_message="Action taken! You're turning insights into impact!",
                progress_description="Complete 1 recommendation"
            ),
            Achievement(
                id="recommendation_master",
                name="Recommendation Master",
                description="Complete 10 recommended actions",
                type=AchievementType.SOCIAL,
                tier=BadgeTier.GOLD,
                points=2000,
                icon="🎓",
                criteria={"recommendations_completed": 10},
                unlocked_message="Master level! You're maximizing your impact!",
                progress_description="Complete 10 recommendations"
            )
        ]
        
        # Combine all achievements
        all_achievements = (
            carbon_achievements + 
            streak_achievements + 
            reduction_achievements + 
            goal_achievements + 
            milestone_achievements + 
            social_achievements
        )
        
        # Convert to dictionary
        for achievement in all_achievements:
            achievements[achievement.id] = achievement
            
        return achievements
    
    def calculate_user_level(self, total_points: int) -> Dict[str, Any]:
        """Calculate user level based on total points"""
        levels = [
            {"level": 1, "name": "Seedling", "min_points": 0, "icon": "🌱"},
            {"level": 2, "name": "Sprout", "min_points": 500, "icon": "🌿"},
            {"level": 3, "name": "Sapling", "min_points": 1500, "icon": "🌳"},
            {"level": 4, "name": "Tree", "min_points": 3500, "icon": "🌲"},
            {"level": 5, "name": "Forest", "min_points": 7500, "icon": "🌲"},
            {"level": 6, "name": "Eco Warrior", "min_points": 15000, "icon": "⚔️"},
            {"level": 7, "name": "Climate Champion", "min_points": 25000, "icon": "🏆"},
            {"level": 8, "name": "Planet Guardian", "min_points": 40000, "icon": "🛡️"},
            {"level": 9, "name": "Earth Protector", "min_points": 60000, "icon": "🌍"},
            {"level": 10, "name": "Carbon Zero Hero", "min_points": 100000, "icon": "💎"}
        ]
        
        current_level = levels[0]
        next_level = None
        
        for i, level in enumerate(levels):
            if total_points >= level["min_points"]:
                current_level = level
                if i + 1 < len(levels):
                    next_level = levels[i + 1]
            else:
                break
                
        progress_to_next = 0
        if next_level:
            points_needed = next_level["min_points"] - current_level["min_points"]
            points_earned = total_points - current_level["min_points"]
            progress_to_next = (points_earned / points_needed) * 100
            
        return {
            "current_level": current_level,
            "next_level": next_level,
            "progress_to_next": min(100, max(0, progress_to_next)),
            "total_points": total_points
        }
    
    def check_achievements(self, user_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check which achievements a user has earned based on their statistics
        
        Args:
            user_stats: Dictionary containing user statistics like:
                - activity_count: int
                - streak_days: int
                - reduction_percentage: float
                - goals_set: int
                - goals_achieved: int
                - co2_saved_kg: float
                - recommendations_completed: int
                
        Returns:
            List of newly earned achievements
        """
        newly_earned = []
        
        for achievement_id, achievement in self.achievements.items():
            if self._check_achievement_criteria(achievement, user_stats):
                newly_earned.append({
                    "achievement_id": achievement_id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "tier": achievement.tier.value,
                    "points": achievement.points,
                    "icon": achievement.icon,
                    "unlocked_message": achievement.unlocked_message,
                    "earned_at": datetime.utcnow().isoformat()
                })
                
        return newly_earned
    
    def _check_achievement_criteria(self, achievement: Achievement, user_stats: Dict[str, Any]) -> bool:
        """Check if user meets the criteria for a specific achievement"""
        try:
            criteria = achievement.criteria
            
            # Activity count achievements
            if "activity_count" in criteria:
                if user_stats.get("activity_count", 0) >= criteria["activity_count"]:
                    return True
                    
            # Streak achievements
            if "streak_days" in criteria:
                if user_stats.get("streak_days", 0) >= criteria["streak_days"]:
                    return True
                    
            # Reduction achievements
            if "reduction_percentage" in criteria:
                user_reduction = user_stats.get("reduction_percentage", 0)
                if user_reduction >= criteria["reduction_percentage"]:
                    return True
                    
            # Net zero achievements
            if "net_zero" in criteria:
                if user_stats.get("net_zero", False) == criteria["net_zero"]:
                    return True
                    
            # Goal achievements
            if "goals_set" in criteria:
                if user_stats.get("goals_set", 0) >= criteria["goals_set"]:
                    return True
                    
            if "goals_achieved" in criteria:
                if user_stats.get("goals_achieved", 0) >= criteria["goals_achieved"]:
                    return True
                    
            # CO2 savings achievements
            if "co2_saved_kg" in criteria:
                if user_stats.get("co2_saved_kg", 0) >= criteria["co2_saved_kg"]:
                    return True
                    
            # Recommendation achievements
            if "recommendations_completed" in criteria:
                if user_stats.get("recommendations_completed", 0) >= criteria["recommendations_completed"]:
                    return True
                    
        except Exception as e:
            logger.error(f"Error checking achievement criteria for {achievement.id}: {str(e)}")
            
        return False
    
    def get_achievement_progress(self, achievement_id: str, user_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Get progress towards a specific achievement"""
        if achievement_id not in self.achievements:
            return {}
            
        achievement = self.achievements[achievement_id]
        criteria = achievement.criteria
        progress = 0
        
        try:
            if "activity_count" in criteria:
                progress = min(100, (user_stats.get("activity_count", 0) / criteria["activity_count"]) * 100)
            elif "streak_days" in criteria:
                progress = min(100, (user_stats.get("streak_days", 0) / criteria["streak_days"]) * 100)
            elif "reduction_percentage" in criteria:
                progress = min(100, (user_stats.get("reduction_percentage", 0) / criteria["reduction_percentage"]) * 100)
            elif "goals_set" in criteria:
                progress = min(100, (user_stats.get("goals_set", 0) / criteria["goals_set"]) * 100)
            elif "goals_achieved" in criteria:
                progress = min(100, (user_stats.get("goals_achieved", 0) / criteria["goals_achieved"]) * 100)
            elif "co2_saved_kg" in criteria:
                progress = min(100, (user_stats.get("co2_saved_kg", 0) / criteria["co2_saved_kg"]) * 100)
            elif "recommendations_completed" in criteria:
                progress = min(100, (user_stats.get("recommendations_completed", 0) / criteria["recommendations_completed"]) * 100)
                
        except Exception as e:
            logger.error(f"Error calculating progress for {achievement_id}: {str(e)}")
            
        return {
            "achievement_id": achievement_id,
            "name": achievement.name,
            "progress": round(progress, 1),
            "progress_description": achievement.progress_description,
            "tier": achievement.tier.value,
            "points": achievement.points,
            "icon": achievement.icon
        }
    
    def get_all_achievements(self) -> List[Dict[str, Any]]:
        """Get all available achievements"""
        return [
            {
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "type": achievement.type.value,
                "tier": achievement.tier.value,
                "points": achievement.points,
                "icon": achievement.icon,
                "progress_description": achievement.progress_description
            }
            for achievement in self.achievements.values()
        ]