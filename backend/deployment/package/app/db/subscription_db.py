"""
Subscription and billing database operations
Manages user subscription tiers and feature access
"""

import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
import uuid

from app.models.subscription import SubscriptionTier, SubscriptionPlan

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
ENVIRONMENT = 'prod'

subscriptions_table = dynamodb.Table(f'carbontrack-subscriptions-{ENVIRONMENT}')


class SubscriptionDatabase:
    """Database operations for subscriptions"""
    
    @staticmethod
    def _convert_decimals(obj):
        """Convert Decimal objects to float for JSON serialization"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: SubscriptionDatabase._convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [SubscriptionDatabase._convert_decimals(item) for item in obj]
        return obj
    
    @staticmethod
    def _prepare_for_dynamodb(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert data for DynamoDB storage (float to Decimal)"""
        if isinstance(data, dict):
            return {k: SubscriptionDatabase._prepare_for_dynamodb(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [SubscriptionDatabase._prepare_for_dynamodb(item) for item in data]
        elif isinstance(data, float):
            return Decimal(str(data))
        return data
    
    @staticmethod
    async def get_user_subscription(user_id: str) -> Dict[str, Any]:
        """Get user's subscription details"""
        
        try:
            response = subscriptions_table.get_item(Key={'user_id': user_id})
            
            if 'Item' in response:
                subscription = SubscriptionDatabase._convert_decimals(response['Item'])
                
                # Check if subscription is active
                if subscription.get('status') == 'active':
                    # Check if subscription has expired
                    expires_at = subscription.get('expires_at')
                    if expires_at:
                        expiry_date = datetime.fromisoformat(expires_at)
                        if expiry_date < datetime.utcnow():
                            # Subscription expired, downgrade to FREE
                            subscription['tier'] = SubscriptionTier.FREE.value
                            subscription['status'] = 'expired'
                
                return subscription
            else:
                # No subscription found, return FREE tier
                return {
                    'user_id': user_id,
                    'tier': SubscriptionTier.FREE.value,
                    'status': 'active',
                    'created_at': datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            print(f"Error fetching subscription for {user_id}: {e}")
            # Default to FREE tier on error
            return {
                'user_id': user_id,
                'tier': SubscriptionTier.FREE.value,
                'status': 'active',
                'created_at': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def create_subscription(
        user_id: str,
        tier: SubscriptionTier,
        payment_method_id: Optional[str] = None,
        billing_period_months: int = 1
    ) -> Dict[str, Any]:
        """Create or upgrade a subscription"""
        
        now = datetime.utcnow()
        
        # Calculate expiry date
        if tier == SubscriptionTier.FREE:
            expires_at = None
        else:
            # Add billing period months to current date
            from dateutil.relativedelta import relativedelta
            expires_at = (now + relativedelta(months=billing_period_months)).isoformat()
        
        subscription = {
            'user_id': user_id,
            'subscription_id': str(uuid.uuid4()),
            'tier': tier.value,
            'status': 'active',
            'payment_method_id': payment_method_id,
            'billing_period_months': billing_period_months,
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
            'expires_at': expires_at
        }
        
        # Save to DynamoDB
        subscriptions_table.put_item(Item=SubscriptionDatabase._prepare_for_dynamodb(subscription))
        
        return subscription
    
    @staticmethod
    async def update_subscription(
        user_id: str,
        tier: Optional[SubscriptionTier] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update subscription details"""
        
        # Get current subscription
        current = await SubscriptionDatabase.get_user_subscription(user_id)
        
        updates = {}
        if tier:
            updates['tier'] = tier.value
        if status:
            updates['status'] = status
        
        updates['updated_at'] = datetime.utcnow().isoformat()
        
        # Build update expression
        update_expr_parts = []
        expr_attr_names = {}
        expr_attr_values = {}
        
        for i, (key, value) in enumerate(updates.items()):
            attr_name = f"#attr{i}"
            attr_value = f":val{i}"
            update_expr_parts.append(f"{attr_name} = {attr_value}")
            expr_attr_names[attr_name] = key
            expr_attr_values[attr_value] = SubscriptionDatabase._prepare_for_dynamodb(value)
        
        update_expression = "SET " + ", ".join(update_expr_parts)
        
        # Update in DynamoDB
        response = subscriptions_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ReturnValues="ALL_NEW"
        )
        
        return SubscriptionDatabase._convert_decimals(response['Attributes'])
    
    @staticmethod
    async def cancel_subscription(user_id: str) -> bool:
        """Cancel a subscription (downgrade to FREE)"""
        
        try:
            await SubscriptionDatabase.update_subscription(
                user_id=user_id,
                tier=SubscriptionTier.FREE,
                status='cancelled'
            )
            return True
        except Exception as e:
            print(f"Error cancelling subscription for {user_id}: {e}")
            return False
    
    @staticmethod
    def has_feature_access(subscription: Dict[str, Any], feature: str) -> bool:
        """Check if subscription has access to a specific feature"""
        
        tier = subscription.get('tier', SubscriptionTier.FREE.value)
        status = subscription.get('status', 'inactive')
        
        # Subscription must be active
        if status != 'active':
            return False
        
        # Feature access by tier
        feature_matrix = {
            'csrd': [SubscriptionTier.PROFESSIONAL.value, SubscriptionTier.BUSINESS.value, SubscriptionTier.ENTERPRISE.value],
            'advanced_analytics': [SubscriptionTier.BUSINESS.value, SubscriptionTier.ENTERPRISE.value],
            'api_access': [SubscriptionTier.BUSINESS.value, SubscriptionTier.ENTERPRISE.value],
            'multi_entity': [SubscriptionTier.BUSINESS.value, SubscriptionTier.ENTERPRISE.value],
            'white_label': [SubscriptionTier.ENTERPRISE.value],
            'sso': [SubscriptionTier.ENTERPRISE.value],
            'dedicated_support': [SubscriptionTier.ENTERPRISE.value],
            'custom_integrations': [SubscriptionTier.ENTERPRISE.value]
        }
        
        allowed_tiers = feature_matrix.get(feature, [])
        return tier in allowed_tiers


# Singleton instance
subscription_db = SubscriptionDatabase()
