"""
DynamoDB service for CarbonTrack application
Handles all database operations for users, carbon data, goals, and achievements
"""

import boto3
from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal
from botocore.exceptions import ClientError

from app.core.config import settings
from app.models.dynamodb_models import (
    CarbonEmissionModel,
    UserProfileModel, 
    GoalModel,
    AchievementModel
)
from boto3.dynamodb.conditions import Key


class DynamoDBService:
    """Service class for DynamoDB operations"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
        self.users_table = self.dynamodb.Table(settings.users_table)
        self.entries_table = self.dynamodb.Table(settings.entries_table)
        self.goals_table = self.dynamodb.Table(settings.goals_table)
        self.achievements_table = self.dynamodb.Table(settings.achievements_table)
    
    # ====================
    # USER OPERATIONS
    # ====================
    
    async def create_user_profile(self, user_data: UserProfileModel) -> Dict[str, Any]:
        """Create a new user profile"""
        try:
            item = user_data.to_dynamodb_item()
            
            # Use condition expression to prevent overwriting existing users
            self.users_table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(userId)',
                ReturnValues='ALL_OLD'
            )
            
            return {"success": True, "user_id": user_data.user_id}
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return {"success": False, "error": "User already exists"}
            raise e
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by user_id"""
        try:
            # Users table uses partition key userId in schema
            response = self.users_table.get_item(Key={'userId': user_id})
            return response.get('Item')
        except ClientError as e:
            print(f"Error getting user profile: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            # Build update expression
            update_expression = "SET "
            expression_values = {}
            
            for key, value in updates.items():
                if key != 'userId':  # Don't update the partition key
                    update_expression += f"{key} = :{key}, "
                    expression_values[f":{key}"] = value
            
            # Add updated_at timestamp
            update_expression += "updated_at = :updated_at"
            expression_values[':updated_at'] = datetime.utcnow().isoformat()
            
            self.users_table.update_item(
                Key={'userId': user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            
            return True
            
        except ClientError as e:
            print(f"Error updating user profile: {e}")
            return False
    
    # ====================
    # CARBON EMISSION OPERATIONS
    # ====================
    
    async def create_carbon_emission(self, emission_data: CarbonEmissionModel) -> Dict[str, Any]:
        """Create a new carbon emission entry"""
        try:
            item = emission_data.to_dynamodb_item()
            
            # Use timestamp as sort key for chronological ordering
            item['timestamp'] = emission_data.created_at.isoformat()
            
            self.entries_table.put_item(Item=item)
            
            # Update user's statistics
            await self._update_user_stats(emission_data.user_id, emission_data.co2_equivalent or Decimal('0'))
            
            return {
                "success": True, 
                "entry_id": emission_data.entry_id,
                "timestamp": item['timestamp']
            }
            
        except ClientError as e:
            print(f"Error creating carbon emission: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_emissions(
        self, 
        user_id: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get carbon emissions for a user with optional date filtering"""
        try:
            # Build query parameters
            query_params = {
                'KeyConditionExpression': Key('userId').eq(user_id),
                'ScanIndexForward': False,  # Sort by timestamp descending (newest first)
                'Limit': limit
            }
            
            # Add date filtering if provided
            if start_date or end_date:
                if start_date and end_date:
                    query_params['KeyConditionExpression'] = query_params['KeyConditionExpression'] & Key('timestamp').between(start_date, end_date)
                elif start_date:
                    query_params['KeyConditionExpression'] = query_params['KeyConditionExpression'] & Key('timestamp').gte(start_date)
                elif end_date:
                    query_params['KeyConditionExpression'] = query_params['KeyConditionExpression'] & Key('timestamp').lte(end_date)
            
            response = self.entries_table.query(**query_params)
            return response.get('Items', [])
            
        except ClientError as e:
            print(f"Error getting user emissions: {e}")
            return []
    
    async def update_carbon_emission(
        self, 
        user_id: str, 
        timestamp: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """Update a carbon emission entry"""
        try:
            # Build update expression
            update_expression = "SET "
            expression_values = {}
            
            for key, value in updates.items():
                if key not in ['user_id', 'timestamp']:  # Don't update keys
                    update_expression += f"{key} = :{key}, "
                    expression_values[f":{key}"] = value
            
            # Add updated_at timestamp
            update_expression += "updated_at = :updated_at"
            expression_values[':updated_at'] = datetime.utcnow().isoformat()
            
            self.entries_table.update_item(
                Key={'userId': user_id, 'timestamp': timestamp},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            
            return True
            
        except ClientError as e:
            print(f"Error updating carbon emission: {e}")
            return False
    
    async def delete_carbon_emission(self, user_id: str, timestamp: str) -> bool:
        """Delete a carbon emission entry"""
        try:
            self.entries_table.delete_item(
                Key={'userId': user_id, 'timestamp': timestamp}
            )
            return True
            
        except ClientError as e:
            print(f"Error deleting carbon emission: {e}")
            return False
    
    # ====================
    # GOAL OPERATIONS
    # ====================
    
    async def create_goal(self, goal_data: GoalModel) -> Dict[str, Any]:
        """Create a new carbon reduction goal"""
        try:
            item = goal_data.to_dynamodb_item()
            
            self.goals_table.put_item(Item=item)
            
            return {"success": True, "goal_id": goal_data.goal_id}
            
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def get_user_goals(self, user_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get goals for a user"""
        try:
            query_params = {
                'KeyConditionExpression': 'userId = :user_id',
                'ExpressionAttributeValues': {':user_id': user_id}
            }
            
            if active_only:
                query_params['FilterExpression'] = 'is_active = :active'
                query_params['ExpressionAttributeValues'][':active'] = True
            
            response = self.goals_table.query(**query_params)
            return response.get('Items', [])
            
        except ClientError as e:
            print(f"Error getting user goals: {e}")
            return []
    
    # ====================
    # ACHIEVEMENT OPERATIONS
    # ====================
    
    async def create_achievement(self, achievement_data: AchievementModel) -> Dict[str, Any]:
        """Create a new achievement"""
        try:
            item = achievement_data.to_dynamodb_item()
            
            self.achievements_table.put_item(Item=item)
            
            return {"success": True, "achievement_id": achievement_data.achievement_id}
            
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get achievements for a user"""
        try:
            response = self.achievements_table.query(
                KeyConditionExpression='userId = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            return response.get('Items', [])
            
        except ClientError as e:
            print(f"Error getting user achievements: {e}")
            return []
    
    # ====================
    # HELPER METHODS
    # ====================
    
    async def _update_user_stats(self, user_id: str, co2_amount: Decimal):
        """Update user's emission statistics"""
        try:
            current_date = datetime.utcnow()
            
            # Update total emissions and entry count
            self.users_table.update_item(
                Key={'userId': user_id},
                UpdateExpression='ADD total_emissions :co2, entries_count :one SET last_active = :now',
                ExpressionAttributeValues={
                    ':co2': float(co2_amount),
                    ':one': 1,
                    ':now': current_date.isoformat()
                }
            )
            
        except ClientError as e:
            print(f"Error updating user stats: {e}")
    
    async def get_analytics(
        self, 
        user_id: str, 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """Get analytics data for a user within a date range"""
        try:
            emissions = await self.get_user_emissions(
                user_id, start_date, end_date, limit=1000
            )
            
            # Calculate analytics
            total_emissions = sum(float(e.get('co2_equivalent', 0)) for e in emissions)
            
            # Group by category
            by_category = {}
            for emission in emissions:
                category = emission.get('category', 'other')
                by_category[category] = by_category.get(category, 0) + float(emission.get('co2_equivalent', 0))
            
            # Group by month
            by_month = {}
            for emission in emissions:
                emission_date = emission.get('date', '')[:7]  # YYYY-MM
                by_month[emission_date] = by_month.get(emission_date, 0) + float(emission.get('co2_equivalent', 0))
            
            return {
                "total_emissions": total_emissions,
                "emissions_by_category": by_category,
                "emissions_by_month": by_month,
                "entry_count": len(emissions),
                "average_daily_emissions": total_emissions / max(1, len(emissions))
            }
            
        except Exception as e:
            print(f"Error calculating analytics: {e}")
            return {}


# Global instance
dynamodb_service = DynamoDBService()
