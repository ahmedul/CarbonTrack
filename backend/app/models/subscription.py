"""
Subscription and payment models for CarbonTrack premium features
"""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class SubscriptionTier(str, Enum):
    """Subscription tier levels"""
    FREE = "free"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


class Subscription(BaseModel):
    """Subscription model"""
    subscription_id: str = Field(..., description="Unique subscription ID")
    user_id: str = Field(..., description="User ID")
    company_id: Optional[str] = Field(None, description="Company ID for B2B")
    tier: SubscriptionTier = Field(..., description="Subscription tier")
    status: SubscriptionStatus = Field(..., description="Subscription status")
    
    # Stripe integration
    stripe_customer_id: Optional[str] = Field(None, description="Stripe customer ID")
    stripe_subscription_id: Optional[str] = Field(None, description="Stripe subscription ID")
    stripe_price_id: Optional[str] = Field(None, description="Stripe price ID")
    
    # Billing
    amount: float = Field(..., description="Monthly/yearly amount in USD")
    billing_period: str = Field("monthly", description="monthly or yearly")
    currency: str = Field("USD", description="Currency code")
    
    # Dates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    trial_start: Optional[datetime] = Field(None, description="Trial start date")
    trial_end: Optional[datetime] = Field(None, description="Trial end date")
    current_period_start: datetime = Field(default_factory=datetime.utcnow)
    current_period_end: datetime = Field(..., description="Current billing period end")
    canceled_at: Optional[datetime] = Field(None, description="Cancellation date")
    
    # Features
    features: dict = Field(default_factory=dict, description="Enabled features")
    
    class Config:
        schema_extra = {
            "example": {
                "subscription_id": "sub_123abc",
                "user_id": "user_456def",
                "company_id": "company_789ghi",
                "tier": "enterprise",
                "status": "active",
                "stripe_customer_id": "cus_stripe123",
                "stripe_subscription_id": "sub_stripe456",
                "amount": 99.00,
                "billing_period": "monthly",
                "currency": "USD",
                "current_period_end": "2026-01-29T00:00:00Z",
                "features": {
                    "csrd_compliance": True,
                    "multi_entity": True,
                    "audit_trail": True,
                    "api_access": True
                }
            }
        }


class FeatureAccess(BaseModel):
    """Feature access control"""
    user_id: str
    tier: SubscriptionTier
    has_csrd_access: bool = False
    has_api_access: bool = False
    has_multi_entity: bool = False
    has_audit_trail: bool = False
    has_priority_support: bool = False
    max_entities: int = 1  # Number of companies/subsidiaries
    max_reports_per_month: int = 10
    
    @classmethod
    def from_subscription(cls, subscription: Subscription):
        """Create FeatureAccess from Subscription"""
        tier = subscription.tier
        
        # Define features per tier - CSRD is PROFESSIONAL+ only
        features = {
            SubscriptionTier.FREE: {
                "has_csrd_access": False,  # No CSRD for free users
                "has_api_access": False,
                "has_multi_entity": False,
                "has_audit_trail": False,
                "has_priority_support": False,
                "max_entities": 1,
                "max_reports_per_month": 5
            },
            SubscriptionTier.PROFESSIONAL: {
                "has_csrd_access": True,  # ✅ CSRD access enabled at PROFESSIONAL
                "has_api_access": False,
                "has_multi_entity": False,
                "has_audit_trail": True,
                "has_priority_support": False,
                "max_entities": 1,
                "max_reports_per_month": 50
            },
            SubscriptionTier.BUSINESS: {
                "has_csrd_access": True,  # ✅ Full CSRD access
                "has_api_access": True,
                "has_multi_entity": True,
                "has_audit_trail": True,
                "has_priority_support": True,
                "max_entities": 5,
                "max_reports_per_month": -1  # Unlimited
            },
            SubscriptionTier.ENTERPRISE: {
                "has_csrd_access": True,  # ✅ Full CSRD access
                "has_api_access": True,
                "has_multi_entity": True,
                "has_audit_trail": True,
                "has_priority_support": True,
                "max_entities": -1,  # Unlimited
                "max_reports_per_month": -1  # Unlimited
            }
        }
        
        return cls(
            user_id=subscription.user_id,
            tier=tier,
            **features.get(tier, features[SubscriptionTier.FREE])
        )


class PaymentIntent(BaseModel):
    """Payment intent for Stripe checkout"""
    amount: float
    currency: str = "USD"
    tier: SubscriptionTier
    billing_period: str  # "monthly" or "yearly"
    success_url: str
    cancel_url: str


# Pricing configuration
PRICING = {
    SubscriptionTier.FREE: {
        "monthly": 0,
        "yearly": 0,
        "stripe_price_id_monthly": None,
        "stripe_price_id_yearly": None,
        "features": [
            "Basic carbon tracking",
            "Personal dashboard",
            "Mobile app access",
            "Up to 10 emissions entries/month",
            "Community support"
        ],
        "limits": {
            "max_entities": 1,
            "max_users": 1,
            "max_reports_per_year": 0,
            "api_access": False
        },
        "csrd_access": False
    },
    SubscriptionTier.PROFESSIONAL: {
        "monthly": 49,
        "yearly": 470,  # ~20% discount
        "stripe_price_id_monthly": "price_professional_monthly",
        "stripe_price_id_yearly": "price_professional_yearly",
        "features": [
            "✅ CSRD Compliance Module",
            "Single entity reporting",
            "Unlimited emissions tracking",
            "ESRS standards (E1-E5, S1-S4, G1)",
            "PDF export for submission",
            "Basic analytics",
            "Email support"
        ],
        "limits": {
            "max_entities": 1,
            "max_users": 3,
            "max_reports_per_year": 12,
            "api_access": False
        },
        "csrd_access": True,
        "most_popular": True
    },
    SubscriptionTier.BUSINESS: {
        "monthly": 149,
        "yearly": 1430,  # ~20% discount
        "stripe_price_id_monthly": "price_business_monthly",
        "stripe_price_id_yearly": "price_business_yearly",
        "features": [
            "✅ Everything in Professional",
            "✅ Multi-entity consolidation (up to 5)",
            "✅ Advanced analytics & trends",
            "✅ API access & webhooks",
            "Custom report templates",
            "Data export (CSV, JSON, Excel)",
            "Priority email support",
            "Up to 10 team members"
        ],
        "limits": {
            "max_entities": 5,
            "max_users": 10,
            "max_reports_per_year": -1,  # Unlimited
            "api_access": True,
            "api_calls_per_day": 10000
        },
        "csrd_access": True
    },
    SubscriptionTier.ENTERPRISE: {
        "monthly": 499,
        "yearly": 4790,  # ~20% discount
        "stripe_price_id_monthly": "price_enterprise_monthly",
        "stripe_price_id_yearly": "price_enterprise_yearly",
        "features": [
            "✅ Everything in Business",
            "✅ Unlimited entities & subsidiaries",
            "✅ White-label branding",
            "✅ SSO (Single Sign-On)",
            "✅ Advanced API access",
            "Custom integrations (SAP, Oracle)",
            "Automated data collection",
            "Dedicated account manager",
            "Custom training sessions",
            "SLA guarantee (99.9% uptime)",
            "24/7 priority support",
            "Unlimited team members"
        ],
        "limits": {
            "max_entities": -1,  # Unlimited
            "max_users": -1,  # Unlimited
            "max_reports_per_year": -1,  # Unlimited
            "api_access": True,
            "api_calls_per_day": 100000
        },
        "csrd_access": True,
        "white_label": True,
        "sso": True,
        "dedicated_support": True
    }
}


class SubscriptionPlan:
    """Helper class for subscription plan details"""
    
    @staticmethod
    def get_plan_details(tier: SubscriptionTier) -> dict:
        """Get detailed plan information for a subscription tier"""
        base_info = PRICING.get(tier, PRICING[SubscriptionTier.FREE])
        
        return {
            "tier": tier.value,
            "name": f"{tier.value.title()} Plan",
            "price_monthly": base_info["monthly"],
            "price_annual": base_info["yearly"],
            "currency": "USD",
            "features": base_info.get("features", []),
            "csrd_access": base_info.get("csrd_access", False),
            "most_popular": base_info.get("most_popular", False)
        }
