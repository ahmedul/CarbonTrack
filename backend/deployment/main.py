#!/usr/bin/env python3
"""
Combined Authentication and Carbon API Server
============================================

This server combines authentication and carbon tracking for easy testing
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, date
from decimal import Decimal
from enum import Enum
import boto3
from botocore.exceptions import ClientError
import hashlib
import jwt
import uuid
import os
import uvicorn

# Configuration
USERS_TABLE = "carbontrack-users"
EMISSIONS_TABLE = "carbontrack-entries"
REGION = "us-east-1" 
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "carbontrack-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="CarbonTrack Full API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    carbon_budget: Optional[float] = 500.0

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class EmissionCategory(str, Enum):
    transportation = "transportation"
    energy = "energy"
    food = "food"
    waste = "waste"

class CarbonEmissionCreate(BaseModel):
    date: date
    category: EmissionCategory
    activity: str
    amount: float
    unit: str
    description: Optional[str] = None

# Authentication helper functions
def get_dynamodb_client():
    return boto3.client('dynamodb', region_name=REGION)

def hash_password(password: str) -> str:
    return hashlib.sha256(f"carbontrack_salt_{password}".encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    try:
        dynamodb = get_dynamodb_client()
        response = dynamodb.query(
            TableName=USERS_TABLE,
            IndexName='EmailIndex',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': {'S': email}}
        )
        
        if response['Items']:
            item = response['Items'][0]
            return {
                'user_id': item['user_id']['S'],
                'email': item['email']['S'],
                'password_hash': item['password_hash']['S'],
                'full_name': item['full_name']['S'],
                'role': item['role']['S'],
                'status': item['status']['S'],
                'email_verified': item['email_verified']['BOOL'],
                'carbon_budget': float(item['carbon_budget']['N']),
                'total_emissions': float(item['total_emissions']['N']),
                'current_month_emissions': float(item['current_month_emissions']['N']),
                'entries_count': int(item['entries_count']['N']),
                'created_at': item['created_at']['S'],
                'updated_at': item['updated_at']['S'],
                'last_active': item['last_active']['S']
            }
        return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def create_user(registration_data: UserRegistration) -> Dict[str, Any]:
    try:
        dynamodb = get_dynamodb_client()
        user_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        item = {
            'user_id': {'S': user_id},
            'email': {'S': registration_data.email},
            'password_hash': {'S': hash_password(registration_data.password)},
            'full_name': {'S': registration_data.full_name},
            'role': {'S': 'user'},
            'status': {'S': 'active'},
            'email_verified': {'BOOL': False},
            'carbon_budget': {'N': str(registration_data.carbon_budget)},
            'total_emissions': {'N': '0'},
            'current_month_emissions': {'N': '0'},
            'entries_count': {'N': '0'},
            'preferred_units': {'M': {
                'distance': {'S': 'km'},
                'energy': {'S': 'kWh'},
                'weight': {'S': 'kg'}
            }},
            'created_at': {'S': now},
            'updated_at': {'S': now},
            'last_active': {'S': now}
        }
        
        dynamodb.put_item(
            TableName=USERS_TABLE,
            Item=item,
            ConditionExpression='attribute_not_exists(email)'
        )
        
        return {
            'user_id': user_id,
            'email': registration_data.email,
            'full_name': registration_data.full_name,
            'role': 'user',
            'status': 'active',
            'carbon_budget': registration_data.carbon_budget,
            'total_emissions': 0,
            'current_month_emissions': 0,
            'entries_count': 0,
            'created_at': now,
            'last_active': now
        }
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error during registration")
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user_by_email(email)
    if user is None:
        raise credentials_exception
    
    return user

# Carbon calculation functions
def calculate_carbon_footprint(category: str, activity: str, amount: float, unit: str) -> Dict[str, Any]:
    """Simple carbon calculation - in production this would be more sophisticated"""
    
    # Simple emission factors (kg CO2 per unit)
    emission_factors = {
        "transportation": {
            "car_drive": 0.21,  # per km
            "flight": 0.255,    # per km
            "bus": 0.089,       # per km
            "train": 0.041,     # per km
        },
        "energy": {
            "electricity": 0.4, # per kWh
            "natural_gas": 0.2, # per kWh
            "heating_oil": 2.5, # per liter
        },
        "food": {
            "beef": 27.0,       # per kg
            "chicken": 6.9,     # per kg
            "vegetables": 2.0,  # per kg
        },
        "waste": {
            "landfill": 0.5,    # per kg
            "recycling": -0.2,  # per kg (negative = carbon saved)
        }
    }
    
    factor = emission_factors.get(category, {}).get(activity, 0.3)  # default factor
    co2_equivalent = amount * factor
    
    return {
        "co2_equivalent": co2_equivalent,
        "emission_factor": factor,
        "calculation_details": f"{amount} {unit} × {factor} kg CO2/{unit}",
        "region": "Global Average"
    }

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "CarbonTrack Full API - Authentication + Carbon Tracking",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "register": "/api/register",
                "login": "/api/login", 
                "profile": "/api/profile"
            },
            "carbon": {
                "emissions": "/api/v1/carbon-emissions/",
                "activities": "/api/v1/carbon-emissions/activities"
            }
        }
    }

# Authentication endpoints
@app.post("/api/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration):
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    
    user = create_user(user_data)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["user_id"]},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user)

@app.post("/api/login", response_model=TokenResponse)
async def login_user(user_credentials: UserLogin):
    user = get_user_by_email(user_credentials.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    if not verify_password(user_credentials.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    if user["status"] != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["user_id"]},
        expires_delta=access_token_expires
    )
    
    user_response = user.copy()
    user_response.pop("password_hash", None)
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

@app.get("/api/profile")
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    user_profile = current_user.copy()
    user_profile.pop("password_hash", None)
    return user_profile

# Carbon tracking endpoints
@app.get("/api/v1/carbon-emissions/activities")
async def get_available_activities():
    """Get available carbon calculation activities"""
    return {
        "message": "Available carbon calculation activities",
        "categories": {
            "transportation": {
                "activities": [
                    {"key": "car_drive", "name": "Car Drive", "unit": "km", "factor": 0.21},
                    {"key": "flight", "name": "Flight", "unit": "km", "factor": 0.255},
                    {"key": "bus", "name": "Bus", "unit": "km", "factor": 0.089},
                    {"key": "train", "name": "Train", "unit": "km", "factor": 0.041},
                ]
            },
            "energy": {
                "activities": [
                    {"key": "electricity", "name": "Electricity", "unit": "kWh", "factor": 0.4},
                    {"key": "natural_gas", "name": "Natural Gas", "unit": "kWh", "factor": 0.2},
                ]
            },
            "food": {
                "activities": [
                    {"key": "beef", "name": "Beef", "unit": "kg", "factor": 27.0},
                    {"key": "chicken", "name": "Chicken", "unit": "kg", "factor": 6.9},
                ]
            }
        }
    }

@app.get("/api/v1/carbon-emissions/")
async def get_carbon_emissions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's carbon emissions"""
    user_id = current_user.get("user_id")
    
    try:
        # Query DynamoDB for user's emissions
        dynamodb = get_dynamodb_client()
        
        response = dynamodb.query(
            TableName=EMISSIONS_TABLE,
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={
                ':user_id': {'S': user_id}
            },
            ScanIndexForward=False  # Sort by date descending
        )
        
        emissions = []
        for item in response.get('Items', []):
            emissions.append({
                "id": item['emission_id']['S'],
                "user_id": item['user_id']['S'],
                "date": item['date']['S'],
                "category": item['category']['S'],
                "activity": item['activity']['S'],
                "amount": float(item['amount']['N']),
                "unit": item['unit']['S'],
                "co2_equivalent": float(item['co2_equivalent']['N']),
                "description": item.get('description', {}).get('S', ''),
                "created_at": item['created_at']['S']
            })
        
        # If no real data, return some sample data for demo purposes
        if not emissions:
            print(f"No emissions found for user {user_id}, returning sample data")
            return await get_sample_emissions_data(user_id)
        
        return emissions
        
    except Exception as e:
        print(f"Error querying emissions: {e}")
        # Fallback to sample data
        return await get_sample_emissions_data(user_id)

async def get_sample_emissions_data(user_id: str):
    """Generate sample emissions data for demo purposes"""
    from datetime import datetime, timedelta
    
    sample_emissions = []
    base_date = datetime.now()
    
    # Generate emissions for the past 15 days to show a trend
    for i in range(15, 0, -1):
        emission_date = base_date - timedelta(days=i)
        
        # Vary emissions to create an interesting trend
        base_emission = 15 + (i % 7) * 2 + (i % 3) * 3
        
        sample_emissions.append({
            "id": f"demo_{i}",
            "user_id": user_id,
            "date": emission_date.strftime("%Y-%m-%d"),
            "category": "transportation",
            "activity": "car_drive",
            "amount": 40 + (i % 10) * 5,
            "unit": "km",
            "co2_equivalent": base_emission,
            "description": f"Sample day {i} activities"
        })
        
        # Add some energy emissions
        if i % 3 == 0:
            sample_emissions.append({
                "id": f"energy_{i}",
                "user_id": user_id,
                "date": emission_date.strftime("%Y-%m-%d"),
                "category": "energy", 
                "activity": "electricity",
                "amount": 25 + (i % 5) * 3,
                "unit": "kWh",
                "co2_equivalent": 8 + (i % 4) * 2,
                "description": f"Sample home energy day {i}"
            })
    
    # Sort by date
    sample_emissions.sort(key=lambda x: x["date"])
    return sample_emissions

@app.post("/api/v1/carbon-emissions/", status_code=status.HTTP_201_CREATED)
async def create_carbon_emission(
    emission_data: CarbonEmissionCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new carbon emission entry"""
    user_id = current_user.get("user_id")
    
    # Calculate CO2 equivalent
    calculation_result = calculate_carbon_footprint(
        category=emission_data.category.value,
        activity=emission_data.activity,
        amount=emission_data.amount,
        unit=emission_data.unit
    )
    
    emission_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    try:
        # Save to DynamoDB
        dynamodb = get_dynamodb_client()
        
        item = {
            'emission_id': {'S': emission_id},
            'user_id': {'S': user_id},
            'date': {'S': emission_data.date.isoformat()},
            'category': {'S': emission_data.category.value},
            'activity': {'S': emission_data.activity},
            'amount': {'N': str(emission_data.amount)},
            'unit': {'S': emission_data.unit},
            'co2_equivalent': {'N': str(calculation_result["co2_equivalent"])},
            'emission_factor': {'N': str(calculation_result["emission_factor"])},
            'description': {'S': emission_data.description or ''},
            'created_at': {'S': now},
            'updated_at': {'S': now}
        }
        
        dynamodb.put_item(
            TableName=EMISSIONS_TABLE,
            Item=item
        )
        
        print(f"✅ Saved emission {emission_id} to DynamoDB for user {user_id}")
        
        return {
            "id": emission_id,
            "user_id": user_id,
            "message": "Carbon emission recorded successfully in database",
            "co2_equivalent": calculation_result["co2_equivalent"],
            "emission_factor": calculation_result["emission_factor"],
            "calculation_details": calculation_result["calculation_details"],
            "saved_to_database": True,
            **emission_data.dict()
        }
        
    except Exception as e:
        print(f"❌ Error saving emission to DynamoDB: {e}")
        
        # Still return success but indicate it wasn't saved
        return {
            "id": emission_id,
            "user_id": user_id,
            "message": "Carbon emission calculated (database save failed)",
            "co2_equivalent": calculation_result["co2_equivalent"],
            "emission_factor": calculation_result["emission_factor"],
            "calculation_details": calculation_result["calculation_details"],
            "saved_to_database": False,
            "error": str(e),
            **emission_data.dict()
        }

if __name__ == "__main__":
    uvicorn.run(
        "combined_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )