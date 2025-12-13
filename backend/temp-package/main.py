"""
CarbonTrack FastAPI Backend
A SaaS MVP for tracking and reducing carbon footprints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Import authentication classes (we'll use them in the endpoints)
from auth import UserRegistration, UserLogin, TokenResponse, PasswordReset, PasswordConfirm, cognito_auth
import csrd

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
    entry_type: str  # "energy", "travel", "waste"
    amount: float
    unit: str
    description: Optional[str] = None
    date: datetime

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

# Sample data for demonstration (in production, this would be from DynamoDB)
sample_entries = [
    {
        "id": "1",
        "entry_type": "energy",
        "amount": 250.0,
        "unit": "kWh",
        "co2_equivalent": 100.0,
        "description": "Monthly electricity usage",
        "date": datetime(2025, 8, 1),
        "created_at": datetime(2025, 8, 1)
    },
    {
        "id": "2",
        "entry_type": "travel",
        "amount": 50.0,
        "unit": "km",
        "co2_equivalent": 12.5,
        "description": "Car travel to work",
        "date": datetime(2025, 8, 15),
        "created_at": datetime(2025, 8, 15)
    }
]

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
async def get_carbon_entries():
    """Get all carbon footprint entries for the user"""
    return sample_entries

# Frontend expects /carbon-emissions/ endpoint
@app.get("/carbon-emissions/", response_model=List[CarbonEntryResponse])
@app.get("/carbon-emissions", response_model=List[CarbonEntryResponse])
async def get_carbon_emissions():
    """Get all carbon footprint entries (alternative endpoint)"""
    return sample_entries

# Add a new carbon entry
@app.post("/api/v1/entries", response_model=CarbonEntryResponse)
async def create_carbon_entry(entry: CarbonEntry):
    """Add a new carbon footprint entry"""
    # Simple CO2 calculation (in production, this would be more sophisticated)
    co2_factors = {
        "energy": 0.4,  # kg CO2 per kWh
        "travel": 0.25,  # kg CO2 per km (average car)
        "waste": 0.5    # kg CO2 per kg
    }
    
    co2_equivalent = entry.amount * co2_factors.get(entry.entry_type, 0.3)
    
    new_entry = {
        "id": str(len(sample_entries) + 1),
        "entry_type": entry.entry_type,
        "amount": entry.amount,
        "unit": entry.unit,
        "co2_equivalent": round(co2_equivalent, 2),
        "description": entry.description,
        "date": entry.date,
        "created_at": datetime.now()
    }
    
    sample_entries.append(new_entry)
    return new_entry

# Frontend expects /carbon-emissions/ endpoint for POST
@app.post("/carbon-emissions/", response_model=CarbonEntryResponse)
@app.post("/carbon-emissions", response_model=CarbonEntryResponse)
async def create_carbon_emission(entry: CarbonEntry):
    """Add a new carbon footprint entry (alternative endpoint)"""
    return await create_carbon_entry(entry)

# Get user statistics
@app.get("/api/v1/stats", response_model=UserStats)
async def get_user_stats():
    """Get user's carbon footprint statistics"""
    total_co2 = sum(entry["co2_equivalent"] for entry in sample_entries)
    
    # Calculate monthly CO2 (current month)
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_co2 = sum(
        entry["co2_equivalent"] for entry in sample_entries 
        if entry["date"].month == current_month and entry["date"].year == current_year
    )
    
    last_entry = max(sample_entries, key=lambda x: x["created_at"]) if sample_entries else None
    
    return UserStats(
        total_co2_kg=round(total_co2, 2),
        monthly_co2_kg=round(monthly_co2, 2),
        entries_count=len(sample_entries),
        last_entry_date=last_entry["date"] if last_entry else None
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
        "co2_equivalent_kg": round(co2_equivalent, 2),
        "factor_used": factor
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

# AWS Lambda handler using Mangum
from mangum import Mangum
handler = Mangum(app, lifespan="off")

if __name__ == "__main__":
    # Only import uvicorn when running locally
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
