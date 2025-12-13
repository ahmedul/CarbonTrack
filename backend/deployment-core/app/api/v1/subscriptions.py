"""
Subscription Management API Endpoints
Handles subscription tiers, upgrades, and billing
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from datetime import datetime

from app.models.subscription import SubscriptionTier, SubscriptionPlan
from app.core.middleware import get_current_user
from app.db.subscription_db import subscription_db

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/me", response_model=dict)
async def get_my_subscription(current_user: dict = Depends(get_current_user)):
    """
    Get current user's subscription details
    """
    user_id = current_user.get("user_id")
    subscription = await subscription_db.get_user_subscription(user_id)
    
    # Add plan details
    tier = subscription.get('tier', SubscriptionTier.FREE.value)
    plan_details = SubscriptionPlan.get_plan_details(SubscriptionTier(tier))
    
    return {
        "subscription": subscription,
        "plan": plan_details,
        "features": {
            "csrd": subscription_db.has_feature_access(subscription, 'csrd'),
            "advanced_analytics": subscription_db.has_feature_access(subscription, 'advanced_analytics'),
            "api_access": subscription_db.has_feature_access(subscription, 'api_access'),
            "white_label": subscription_db.has_feature_access(subscription, 'white_label'),
            "blockchain_verification": subscription_db.has_feature_access(subscription, 'blockchain_verification'),
            "dedicated_support": subscription_db.has_feature_access(subscription, 'dedicated_support')
        }
    }


@router.get("/plans", response_model=list)
async def list_subscription_plans():
    """
    List all available subscription plans
    """
    plans = []
    
    for tier in SubscriptionTier:
        plan_details = SubscriptionPlan.get_plan_details(tier)
        plans.append(plan_details)
    
    return plans


@router.post("/upgrade", response_model=dict)
async def upgrade_subscription(
    tier: SubscriptionTier,
    payment_method_id: Optional[str] = None,
    billing_period_months: int = 1,
    current_user: dict = Depends(get_current_user)
):
    """
    Upgrade subscription to a higher tier
    
    - **tier**: Target subscription tier (PROFESSIONAL or ENTERPRISE)
    - **payment_method_id**: Stripe payment method ID
    - **billing_period_months**: Billing period (1, 3, 6, or 12 months)
    """
    user_id = current_user.get("user_id")
    
    # Validate tier upgrade
    if tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upgrade to FREE tier. Use /cancel endpoint instead."
        )
    
    if tier not in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.BUSINESS, SubscriptionTier.ENTERPRISE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription tier. Choose PROFESSIONAL, BUSINESS, or ENTERPRISE."
        )
    
    # Validate billing period
    if billing_period_months not in [1, 3, 6, 12]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Billing period must be 1, 3, 6, or 12 months"
        )
    
    # Get current subscription
    current_subscription = await subscription_db.get_user_subscription(user_id)
    current_tier = current_subscription.get('tier', SubscriptionTier.FREE.value)
    
    # TODO: Process payment via Stripe
    # For now, we'll just create/update the subscription
    if not payment_method_id and tier != SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment method required for paid subscriptions"
        )
    
    # Create or update subscription
    if current_tier == SubscriptionTier.FREE.value:
        # Create new paid subscription
        subscription = await subscription_db.create_subscription(
            user_id=user_id,
            tier=tier,
            payment_method_id=payment_method_id,
            billing_period_months=billing_period_months
        )
    else:
        # Update existing subscription
        subscription = await subscription_db.update_subscription(
            user_id=user_id,
            tier=tier,
            status='active'
        )
    
    return {
        "success": True,
        "message": f"Successfully upgraded to {tier.value} plan",
        "subscription": subscription,
        "next_billing_date": subscription.get('expires_at')
    }


@router.post("/cancel", response_model=dict)
async def cancel_subscription(current_user: dict = Depends(get_current_user)):
    """
    Cancel subscription (downgrade to FREE tier)
    """
    user_id = current_user.get("user_id")
    
    success = await subscription_db.cancel_subscription(user_id)
    
    if success:
        return {
            "success": True,
            "message": "Subscription cancelled successfully. You have been downgraded to the FREE tier.",
            "effective_date": datetime.utcnow().isoformat()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


@router.get("/check-feature/{feature_name}", response_model=dict)
async def check_feature_access(
    feature_name: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Check if user has access to a specific feature
    
    Available features:
    - csrd
    - advanced_analytics
    - api_access
    - white_label
    - blockchain_verification
    - dedicated_support
    """
    user_id = current_user.get("user_id")
    subscription = await subscription_db.get_user_subscription(user_id)
    
    has_access = subscription_db.has_feature_access(subscription, feature_name)
    
    return {
        "feature": feature_name,
        "has_access": has_access,
        "current_tier": subscription.get('tier'),
        "message": "Access granted" if has_access else f"Upgrade to PROFESSIONAL or ENTERPRISE for {feature_name} access"
    }
