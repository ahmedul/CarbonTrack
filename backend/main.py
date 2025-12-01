"""
CarbonTrack FastAPI Backend
A SaaS MVP for tracking and reducing carbon footprints
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from mangum import Mangum
import boto3
import uuid
from decimal import Decimal

# Import authentication classes (we'll use them in the endpoints)
from auth import UserRegistration, UserLogin, TokenResponse, PasswordReset, PasswordConfirm, cognito_auth
import csrd

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
entries_table = dynamodb.Table('carbontrack-entries')
users_table = dynamodb.Table('carbontrack-users')

# Initialize FastAPI app
app = FastAPI(
    title="CarbonTrack API",
    description="A SaaS MVP for tracking and reducing individual and organizational carbon footprints",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include CSRD Router
app.include_router(csrd.router)

# Custom CORS middleware that works with Lambda
class CORSMiddleware2(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        return response

app.add_middleware(CORSMiddleware2)

# Pydantic models for data validation
class CarbonEntry(BaseModel):
    entry_type: Optional[str] = None  # "energy", "travel", "waste"
    category: Optional[str] = None  # Alternative field name (frontend compatibility)
    amount: float
    unit: str
    description: Optional[str] = None
    date: datetime
    
    @property
    def get_entry_type(self):
        """Return entry_type, falling back to category"""
        return self.entry_type or self.category or "unknown"

class CarbonEntryResponse(BaseModel):
    id: str
    entry_type: str
    amount: float
    unit: str
    co2_equivalent: float  # Calculated CO2 equivalent in kg
    description: Optional[str] = None
    date: datetime
    created_at: datetime

class UserStats(BaseModel):
    total_co2_kg: float
    monthly_co2_kg: float
    entries_count: int
    last_entry_date: Optional[datetime] = None

# Helper function to convert Decimal to float
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# Helper function to get user ID from token
def get_user_id_from_token(authorization: Optional[str] = None):
    """Extract user ID from JWT token - for now return a demo user ID"""
    # In production, decode the JWT token here
    # For now, use a fixed user ID for testing
    return "demo-user-123"

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to CarbonTrack API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Get all carbon entries
@app.get("/api/v1/entries", response_model=List[CarbonEntryResponse])
async def get_carbon_entries(authorization: Optional[str] = Header(None)):
    """Get all carbon footprint entries for the user from DynamoDB"""
    try:
        user_id = get_user_id_from_token(authorization)
        
        response = entries_table.query(
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )
        
        entries = []
        for item in response.get('Items', []):
            entries.append({
                "id": item['timestamp'],
                "entry_type": item.get('category', item.get('entry_type', 'unknown')),
                "amount": float(item.get('amount', 0)),
                "unit": item.get('unit', ''),
                "co2_equivalent": float(item.get('co2_equivalent', 0)),
                "description": item.get('description', ''),
                "date": datetime.fromisoformat(item.get('date', item['timestamp'])),
                "created_at": datetime.fromisoformat(item['timestamp'])
            })
        
        return entries
    except Exception as e:
        print(f"Error fetching entries: {str(e)}")
        return []

# Frontend expects /api/v1/carbon-emissions/ endpoint
@app.get("/api/v1/carbon-emissions/", response_model=List[CarbonEntryResponse])
@app.get("/api/v1/carbon-emissions", response_model=List[CarbonEntryResponse])
async def get_carbon_emissions(authorization: Optional[str] = Header(None)):
    """Get all carbon footprint entries (frontend compatible endpoint)"""
    return await get_carbon_entries(authorization)

# Add a new carbon entry
@app.post("/api/v1/entries", response_model=CarbonEntryResponse)
async def create_carbon_entry(entry: CarbonEntry, authorization: Optional[str] = Header(None)):
    """Add a new carbon footprint entry to DynamoDB"""
    try:
        user_id = get_user_id_from_token(authorization)
        
        # Get entry_type from either field
        entry_type = entry.entry_type or entry.category or "unknown"
        
        # Simple CO2 calculation
        co2_factors = {
            "energy": 0.4,  # kg CO2 per kWh
            "travel": 0.25,  # kg CO2 per km (average car)
            "waste": 0.5,   # kg CO2 per kg
            "transportation": 0.25,
            "food": 2.5,
            "electricity": 0.4  # kg CO2 per kWh (same as energy)
        }
        
        co2_equivalent = entry.amount * co2_factors.get(entry_type.lower(), 0.3)
        
        # Create timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Store in DynamoDB
        item = {
            'userId': user_id,
            'timestamp': timestamp,
            'entry_type': entry_type,  # Store as entry_type for consistency
            'amount': Decimal(str(entry.amount)),
            'unit': entry.unit,
            'co2_equivalent': Decimal(str(round(co2_equivalent, 2))),
            'description': entry.description or '',
            'date': entry.date.isoformat()
        }
        
        entries_table.put_item(Item=item)
        
        # Return the created entry
        return {
            "id": timestamp,
            "entry_type": entry_type,
            "amount": entry.amount,
            "unit": entry.unit,
            "co2_equivalent": round(co2_equivalent, 2),
            "description": entry.description,
            "date": entry.date,
            "created_at": datetime.fromisoformat(timestamp)
        }
    except Exception as e:
        print(f"Error creating entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")

# Frontend expects /api/v1/carbon-emissions/ endpoint for POST
@app.post("/api/v1/carbon-emissions/", response_model=CarbonEntryResponse)
@app.post("/api/v1/carbon-emissions", response_model=CarbonEntryResponse)
async def create_carbon_emission(entry: CarbonEntry, authorization: Optional[str] = Header(None)):
    """Add a new carbon footprint entry (frontend compatible endpoint)"""
    return await create_carbon_entry(entry, authorization)

# Get user statistics
@app.get("/api/v1/stats", response_model=UserStats)
async def get_user_stats(authorization: Optional[str] = Header(None)):
    """Get user's carbon footprint statistics from DynamoDB"""
    try:
        user_id = get_user_id_from_token(authorization)
        
        response = entries_table.query(
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )
        
        entries = response.get('Items', [])
        
        if not entries:
            return UserStats(
                total_co2_kg=0.0,
                monthly_co2_kg=0.0,
                entries_count=0,
                last_entry_date=None
            )
        
        total_co2 = sum(float(entry.get('co2_equivalent', 0)) for entry in entries)
        
        # Calculate monthly CO2 (current month)
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_co2 = sum(
            float(entry.get('co2_equivalent', 0)) for entry in entries 
            if datetime.fromisoformat(entry['timestamp']).month == current_month 
            and datetime.fromisoformat(entry['timestamp']).year == current_year
        )
        
        # Get last entry date
        timestamps = [datetime.fromisoformat(e['timestamp']) for e in entries]
        last_entry = max(timestamps) if timestamps else None
        
        return UserStats(
            total_co2_kg=round(total_co2, 2),
            monthly_co2_kg=round(monthly_co2, 2),
            entries_count=len(entries),
            last_entry_date=last_entry
        )
    except Exception as e:
        print(f"Error fetching stats: {str(e)}")
        return UserStats(
            total_co2_kg=0.0,
            monthly_co2_kg=0.0,
            entries_count=0,
            last_entry_date=None
        )

# CO2 calculation endpoint
@app.post("/api/v1/calculate-co2")
async def calculate_co2(entry_type: str, amount: float, unit: str):
    """Calculate CO2 equivalent for a given activity"""
    co2_factors = {
        "energy": {"kWh": 0.4, "MWh": 400},
        "travel": {"km": 0.25, "miles": 0.4},
        "waste": {"kg": 0.5, "lbs": 0.23}
    }
    
    if entry_type not in co2_factors:
        raise HTTPException(status_code=400, detail="Invalid entry type")
    
    if unit not in co2_factors[entry_type]:
        raise HTTPException(status_code=400, detail="Invalid unit for entry type")
    
    factor = co2_factors[entry_type][unit]
    co2_equivalent = amount * factor
    
    return {
        "entry_type": entry_type,
        "amount": amount,
        "unit": unit,
        "co2_equivalent": co2_equivalent
    }

# Get current user profile (for session validation)
@app.get("/api/v1/auth/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user profile from token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization token provided")
    
    user_id = get_user_id_from_token(authorization)
    
    # For now, return a basic profile
    # TODO: Query Cognito or DynamoDB for actual user details
    return {
        "user": {
            "user_id": user_id,
            "email": "ahmedulkabir55@gmail.com",  # Placeholder
            "full_name": "Admin User",
            "carbon_budget": 1000,
            "role": "admin"
        }
    }

# =============================================================================
# 🔐 AUTHENTICATION ENDPOINTS (Step 2 - Cognito Integration)
# =============================================================================

@app.post("/api/v1/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration):
    """
    Register a new user with AWS Cognito
    
    Creates a new user account and returns authentication tokens
    """
    try:
        # Register user with Cognito
        await cognito_auth.register_user(user_data)
        
        # Authenticate the newly registered user to get tokens
        login_data = UserLogin(email=user_data.email, password=user_data.password)
        auth_result = await cognito_auth.authenticate_user(login_data)
        
        return TokenResponse(
            access_token=auth_result["access_token"],
            token_type="bearer",
            expires_in=auth_result["expires_in"],
            refresh_token=auth_result.get("refresh_token")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin):
    """
    Authenticate user with AWS Cognito
    
    Validates credentials and returns authentication tokens
    """
    try:
        auth_result = await cognito_auth.authenticate_user(credentials)
        
        return TokenResponse(
            access_token=auth_result["access_token"],
            token_type="bearer",
            expires_in=auth_result["expires_in"],
            refresh_token=auth_result.get("refresh_token")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )

@app.post("/api/v1/auth/forgot-password")
async def forgot_password(password_reset: PasswordReset):
    """
    Initiate password reset process
    
    Sends a password reset code to the user's email
    """
    try:
        result = await cognito_auth.forgot_password(password_reset.email)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Password reset failed: {str(e)}"
        )

@app.post("/api/v1/auth/confirm-password")
async def confirm_password_reset(password_confirm: PasswordConfirm):
    """
    Confirm password reset with verification code
    
    Completes the password reset process using the emailed code
    """
    try:
        result = await cognito_auth.confirm_forgot_password(
            password_confirm.email,
            password_confirm.confirmation_code,
            password_confirm.new_password
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Password confirmation failed: {str(e)}"
        )

@app.post("/api/v1/auth/refresh")
async def refresh_access_token(refresh_token: str, username: str):
    """
    Refresh access token using refresh token
    
    Returns a new access token when the current one expires
    """
    try:
        result = await cognito_auth.refresh_token(refresh_token, username)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Token refresh failed: {str(e)}"
        )

# =============================================================================
# 🎮 GAMIFICATION ENDPOINTS (Stub implementations)
# =============================================================================

@app.get("/api/v1/gamification/profile")
async def get_gamification_profile(authorization: Optional[str] = Header(None)):
    """Get user's gamification profile"""
    return {
        "level": 1,
        "points": 0,
        "badges": [],
        "challenges_completed": 0
    }

@app.get("/api/v1/gamification/achievements")
async def get_achievements(authorization: Optional[str] = Header(None)):
    """Get available achievements"""
    return []

@app.get("/api/v1/gamification/leaderboards")
async def get_leaderboards(authorization: Optional[str] = Header(None)):
    """Get leaderboard data"""
    return {"users": []}

@app.post("/api/v1/gamification/challenges/{challenge_id}/complete")
async def complete_challenge(challenge_id: str, authorization: Optional[str] = Header(None)):
    """Mark a challenge as complete"""
    return {"success": True, "message": "Challenge completed"}

# =============================================================================
# 💡 RECOMMENDATIONS ENDPOINTS (Stub implementations)
# =============================================================================

@app.get("/api/v1/recommendations/")
async def get_recommendations(authorization: Optional[str] = Header(None)):
    """Get personalized carbon reduction recommendations"""
    return []

@app.get("/api/v1/recommendations/stats")
async def get_recommendation_stats(authorization: Optional[str] = Header(None)):
    """Get statistics about recommendations"""
    return {
        "total_recommendations": 0,
        "completed": 0,
        "potential_savings_kg": 0
    }

# =============================================================================
# 👥 ADMIN ENDPOINTS (Stub implementations)
# =============================================================================

@app.get("/api/v1/admin/users")
async def get_all_users(authorization: Optional[str] = Header(None)):
    """Get all users (admin only)"""
    return []

@app.get("/api/v1/admin/pending-users")
async def get_pending_users(authorization: Optional[str] = Header(None)):
    """Get users pending approval (admin only)"""
    return []

@app.get("/api/v1/admin/stats")
async def get_admin_stats(authorization: Optional[str] = Header(None)):
    """Get system-wide statistics (admin only)"""
    return {
        "total_users": 0,
        "total_entries": 0,
        "total_co2_kg": 0
    }

@app.post("/api/v1/admin/users/{user_id}/approve")
async def approve_user(user_id: str, authorization: Optional[str] = Header(None)):
    """Approve a pending user (admin only)"""
    return {"success": True, "message": "User approved"}

# =============================================================================
# AWS Lambda handler
# =============================================================================

# AWS Lambda handler using Mangum
handler = Mangum(app, lifespan="off")

if __name__ == "__main__":
    # Only import uvicorn when running locally
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
