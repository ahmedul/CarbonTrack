"""
Leaderboard System for CarbonTrack Gamification
Handles personal and community leaderboards with different time periods and categories
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass
import logging

# Setup logging
logger = logging.getLogger(__name__)


class LeaderboardType(Enum):
    """Types of leaderboards available"""
    POINTS = "points"
    CARBON_REDUCTION = "carbon_reduction"
    STREAK = "streak"
    ACTIVITIES = "activities"
    GOALS_ACHIEVED = "goals_achieved"


class LeaderboardPeriod(Enum):
    """Time periods for leaderboards"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"


@dataclass
class LeaderboardEntry:
    """Individual leaderboard entry"""
    user_id: str
    username: str
    display_name: str
    rank: int
    score: float
    previous_rank: int
    rank_change: int
    avatar_url: str
    level: int
    badge_icon: str
    additional_stats: Dict[str, Any]


class LeaderboardEngine:
    """
    Manages community leaderboards, rankings, and competitive elements
    """
    
    def __init__(self):
        self.leaderboard_configs = self._initialize_leaderboard_configs()
    
    def _initialize_leaderboard_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize leaderboard configurations"""
        return {
            "points_daily": {
                "type": LeaderboardType.POINTS,
                "period": LeaderboardPeriod.DAILY,
                "title": "Daily Points Leaders",
                "description": "Top point earners today",
                "icon": "🏆",
                "score_label": "Points",
                "min_entries": 1
            },
            "points_weekly": {
                "type": LeaderboardType.POINTS,
                "period": LeaderboardPeriod.WEEKLY,
                "title": "Weekly Points Champions",
                "description": "Top point earners this week",
                "icon": "⭐",
                "score_label": "Points",
                "min_entries": 3
            },
            "points_monthly": {
                "type": LeaderboardType.POINTS,
                "period": LeaderboardPeriod.MONTHLY,
                "title": "Monthly Points Masters",
                "description": "Top point earners this month",
                "icon": "🎯",
                "score_label": "Points",
                "min_entries": 5
            },
            "points_all_time": {
                "type": LeaderboardType.POINTS,
                "period": LeaderboardPeriod.ALL_TIME,
                "title": "All-Time Legends",
                "description": "Highest point earners of all time",
                "icon": "👑",
                "score_label": "Points",
                "min_entries": 10
            },
            "carbon_reduction_weekly": {
                "type": LeaderboardType.CARBON_REDUCTION,
                "period": LeaderboardPeriod.WEEKLY,
                "title": "Weekly Carbon Savers",
                "description": "Biggest CO₂ reductions this week",
                "icon": "🌱",
                "score_label": "CO₂ Reduced (kg)",
                "min_entries": 3
            },
            "carbon_reduction_monthly": {
                "type": LeaderboardType.CARBON_REDUCTION,
                "period": LeaderboardPeriod.MONTHLY,
                "title": "Monthly Environmental Heroes",
                "description": "Biggest CO₂ reductions this month",
                "icon": "🌍",
                "score_label": "CO₂ Reduced (kg)",
                "min_entries": 5
            },
            "streak_current": {
                "type": LeaderboardType.STREAK,
                "period": LeaderboardPeriod.ALL_TIME,
                "title": "Streak Champions",
                "description": "Longest current logging streaks",
                "icon": "🔥",
                "score_label": "Days",
                "min_entries": 3
            },
            "activities_weekly": {
                "type": LeaderboardType.ACTIVITIES,
                "period": LeaderboardPeriod.WEEKLY,
                "title": "Most Active This Week",
                "description": "Most activities logged this week",
                "icon": "📈",
                "score_label": "Activities",
                "min_entries": 3
            },
            "goals_all_time": {
                "type": LeaderboardType.GOALS_ACHIEVED,
                "period": LeaderboardPeriod.ALL_TIME,
                "title": "Goal Crushers",
                "description": "Most goals achieved",
                "icon": "🎯",
                "score_label": "Goals",
                "min_entries": 5
            }
        }
    
    def generate_leaderboard(self, leaderboard_id: str, user_data: List[Dict[str, Any]], 
                           current_user_id: str = None, limit: int = 50) -> Dict[str, Any]:
        """
        Generate a leaderboard based on user data
        
        Args:
            leaderboard_id: ID of the leaderboard configuration
            user_data: List of user statistics
            current_user_id: ID of current user for highlighting
            limit: Maximum number of entries to return
            
        Returns:
            Complete leaderboard with rankings and metadata
        """
        if leaderboard_id not in self.leaderboard_configs:
            return {"error": "Leaderboard configuration not found"}
            
        config = self.leaderboard_configs[leaderboard_id]
        
        # Filter and sort users based on leaderboard type
        ranked_users = self._rank_users(user_data, config, limit)
        
        # Find current user position if specified
        current_user_entry = None
        current_user_rank = None
        
        if current_user_id:
            for i, entry in enumerate(ranked_users):
                if entry.user_id == current_user_id:
                    current_user_entry = entry
                    current_user_rank = i + 1
                    break
        
        # Calculate statistics
        total_participants = len([u for u in user_data if self._get_user_score(u, config) > 0])
        average_score = sum(self._get_user_score(u, config) for u in user_data) / len(user_data) if user_data else 0
        
        return {
            "leaderboard_id": leaderboard_id,
            "title": config["title"],
            "description": config["description"],
            "icon": config["icon"],
            "score_label": config["score_label"],
            "period": config["period"].value,
            "type": config["type"].value,
            "entries": [self._serialize_entry(entry) for entry in ranked_users],
            "current_user": {
                "entry": self._serialize_entry(current_user_entry) if current_user_entry else None,
                "rank": current_user_rank,
                "is_in_top": current_user_rank <= limit if current_user_rank else False
            } if current_user_id else None,
            "statistics": {
                "total_participants": total_participants,
                "average_score": round(average_score, 2),
                "top_score": ranked_users[0].score if ranked_users else 0,
                "last_updated": datetime.utcnow().isoformat()
            },
            "metadata": {
                "period_start": self._get_period_start(config["period"]).isoformat(),
                "period_end": self._get_period_end(config["period"]).isoformat(),
                "next_update": self._get_next_update_time(config["period"]).isoformat()
            }
        }
    
    def _rank_users(self, user_data: List[Dict[str, Any]], config: Dict[str, Any], 
                   limit: int) -> List[LeaderboardEntry]:
        """Rank users based on leaderboard configuration"""
        # Calculate scores and create entries
        entries = []
        
        for user in user_data:
            score = self._get_user_score(user, config)
            
            if score > 0 or config["type"] == LeaderboardType.STREAK:  # Include zero streaks
                entry = LeaderboardEntry(
                    user_id=user.get("user_id", ""),
                    username=user.get("username", user.get("email", "Anonymous")),
                    display_name=user.get("display_name", user.get("full_name", "User")),
                    rank=0,  # Will be set after sorting
                    score=score,
                    previous_rank=user.get("previous_rank", 0),
                    rank_change=0,  # Will be calculated
                    avatar_url=user.get("avatar_url", ""),
                    level=user.get("level", 1),
                    badge_icon=user.get("badge_icon", "🌱"),
                    additional_stats=self._get_additional_stats(user, config)
                )
                entries.append(entry)
        
        # Sort by score (descending)
        entries.sort(key=lambda x: x.score, reverse=True)
        
        # Assign ranks and calculate changes
        for i, entry in enumerate(entries[:limit]):
            entry.rank = i + 1
            entry.rank_change = entry.previous_rank - entry.rank if entry.previous_rank > 0 else 0
            
        return entries[:limit]
    
    def _get_user_score(self, user: Dict[str, Any], config: Dict[str, Any]) -> float:
        """Get user score based on leaderboard type"""
        leaderboard_type = config["type"]
        period = config["period"]
        
        if leaderboard_type == LeaderboardType.POINTS:
            if period == LeaderboardPeriod.DAILY:
                return user.get("points_today", 0)
            elif period == LeaderboardPeriod.WEEKLY:
                return user.get("points_this_week", 0)
            elif period == LeaderboardPeriod.MONTHLY:
                return user.get("points_this_month", 0)
            else:  # ALL_TIME
                return user.get("total_points", 0)
                
        elif leaderboard_type == LeaderboardType.CARBON_REDUCTION:
            if period == LeaderboardPeriod.WEEKLY:
                return user.get("co2_reduced_this_week", 0)
            elif period == LeaderboardPeriod.MONTHLY:
                return user.get("co2_reduced_this_month", 0)
            else:
                return user.get("total_co2_reduced", 0)
                
        elif leaderboard_type == LeaderboardType.STREAK:
            return user.get("current_streak", 0)
            
        elif leaderboard_type == LeaderboardType.ACTIVITIES:
            if period == LeaderboardPeriod.DAILY:
                return user.get("activities_today", 0)
            elif period == LeaderboardPeriod.WEEKLY:
                return user.get("activities_this_week", 0)
            elif period == LeaderboardPeriod.MONTHLY:
                return user.get("activities_this_month", 0)
            else:
                return user.get("total_activities", 0)
                
        elif leaderboard_type == LeaderboardType.GOALS_ACHIEVED:
            return user.get("goals_achieved", 0)
            
        return 0
    
    def _get_additional_stats(self, user: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Get additional statistics to display for each user"""
        stats = {}
        
        leaderboard_type = config["type"]
        
        if leaderboard_type == LeaderboardType.POINTS:
            stats = {
                "level": user.get("level", 1),
                "achievements_count": user.get("achievements_count", 0),
                "streak": user.get("current_streak", 0)
            }
        elif leaderboard_type == LeaderboardType.CARBON_REDUCTION:
            stats = {
                "total_activities": user.get("total_activities", 0),
                "reduction_percentage": user.get("reduction_percentage", 0),
                "points": user.get("total_points", 0)
            }
        elif leaderboard_type == LeaderboardType.STREAK:
            stats = {
                "longest_streak": user.get("longest_streak", 0),
                "total_activities": user.get("total_activities", 0),
                "level": user.get("level", 1)
            }
        elif leaderboard_type == LeaderboardType.ACTIVITIES:
            stats = {
                "points": user.get("total_points", 0),
                "streak": user.get("current_streak", 0),
                "co2_reduced": user.get("total_co2_reduced", 0)
            }
        elif leaderboard_type == LeaderboardType.GOALS_ACHIEVED:
            stats = {
                "goals_set": user.get("goals_set", 0),
                "success_rate": user.get("goal_success_rate", 0),
                "points": user.get("total_points", 0)
            }
            
        return stats
    
    def _serialize_entry(self, entry: LeaderboardEntry) -> Dict[str, Any]:
        """Serialize leaderboard entry to dictionary"""
        if not entry:
            return None
            
        return {
            "user_id": entry.user_id,
            "username": entry.username,
            "display_name": entry.display_name,
            "rank": entry.rank,
            "score": entry.score,
            "previous_rank": entry.previous_rank,
            "rank_change": entry.rank_change,
            "rank_change_direction": "up" if entry.rank_change > 0 else "down" if entry.rank_change < 0 else "same",
            "avatar_url": entry.avatar_url,
            "level": entry.level,
            "badge_icon": entry.badge_icon,
            "additional_stats": entry.additional_stats
        }
    
    def _get_period_start(self, period: LeaderboardPeriod) -> datetime:
        """Get start date for leaderboard period"""
        now = datetime.utcnow()
        
        if period == LeaderboardPeriod.DAILY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == LeaderboardPeriod.WEEKLY:
            return now - timedelta(days=now.weekday())
        elif period == LeaderboardPeriod.MONTHLY:
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # ALL_TIME
            return datetime(2020, 1, 1)  # App launch date
    
    def _get_period_end(self, period: LeaderboardPeriod) -> datetime:
        """Get end date for leaderboard period"""
        now = datetime.utcnow()
        
        if period == LeaderboardPeriod.DAILY:
            return now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif period == LeaderboardPeriod.WEEKLY:
            week_start = now - timedelta(days=now.weekday())
            return week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif period == LeaderboardPeriod.MONTHLY:
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)
            return next_month - timedelta(seconds=1)
        else:  # ALL_TIME
            return datetime(2030, 12, 31)  # Far future
    
    def _get_next_update_time(self, period: LeaderboardPeriod) -> datetime:
        """Get next time leaderboard will be updated"""
        now = datetime.utcnow()
        
        if period == LeaderboardPeriod.DAILY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif period == LeaderboardPeriod.WEEKLY:
            week_start = now - timedelta(days=now.weekday())
            return week_start + timedelta(days=7)
        elif period == LeaderboardPeriod.MONTHLY:
            if now.month == 12:
                return now.replace(year=now.year + 1, month=1, day=1)
            else:
                return now.replace(month=now.month + 1, day=1)
        else:  # ALL_TIME
            return now + timedelta(hours=1)  # Update hourly
    
    def get_available_leaderboards(self) -> List[Dict[str, Any]]:
        """Get list of all available leaderboards"""
        leaderboards = []
        
        for leaderboard_id, config in self.leaderboard_configs.items():
            leaderboards.append({
                "id": leaderboard_id,
                "title": config["title"],
                "description": config["description"],
                "icon": config["icon"],
                "type": config["type"].value,
                "period": config["period"].value,
                "score_label": config["score_label"],
                "min_entries": config["min_entries"]
            })
            
        return leaderboards
    
    def get_user_rankings(self, user_id: str, user_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get a user's rankings across all leaderboards"""
        rankings = {}
        
        for leaderboard_id in self.leaderboard_configs.keys():
            leaderboard = self.generate_leaderboard(leaderboard_id, user_data, user_id, limit=100)
            
            if leaderboard.get("current_user"):
                user_info = leaderboard["current_user"]
                rankings[leaderboard_id] = {
                    "title": leaderboard["title"],
                    "rank": user_info["rank"],
                    "score": user_info["entry"]["score"] if user_info["entry"] else 0,
                    "total_participants": leaderboard["statistics"]["total_participants"],
                    "percentile": round((1 - (user_info["rank"] - 1) / leaderboard["statistics"]["total_participants"]) * 100, 1) if user_info["rank"] else 0,
                    "icon": leaderboard["icon"]
                }
                
        return rankings