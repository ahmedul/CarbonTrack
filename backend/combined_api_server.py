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
from jose import jwt
import uuid
import os
import uvicorn

# Configuration
USERS_TABLE = "carbontrack-users"
EMISSIONS_TABLE = "carbontrack-entries"
EMISSION_FACTORS_TABLE = "carbontrack-emission-factors"
REGION = "eu-central-1"  # Updated to match actual deployment region 
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
            # Support both userId (primary key) and user_id (compatibility)
            user_id = item.get('userId', item.get('user_id', {})).get('S', '')
            return {
                'user_id': user_id,
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
            'userId': {'S': user_id},
            'user_id': {'S': user_id},  # Keep both for compatibility
            'email': {'S': registration_data.email},
            'password_hash': {'S': hash_password(registration_data.password)},
            'full_name': {'S': registration_data.full_name},
            'role': {'S': 'user'},
            'status': {'S': 'pending'},  # Default to pending, admin must approve
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
            'status': 'pending',  # User needs admin approval
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
def get_emission_factor_from_db(category: str, activity: str) -> Dict[str, Any]:
    """Fetch emission factor from DynamoDB"""
    try:
        dynamodb = get_dynamodb_client()
        response = dynamodb.get_item(
            TableName=EMISSION_FACTORS_TABLE,
            Key={
                'category': {'S': category},
                'activity': {'S': activity}
            }
        )
        
        if 'Item' not in response:
            return None
            
        item = response['Item']
        return {
            'emission_factor': float(item['emission_factor']['N']),
            'unit': item['unit']['S'],
            'description': item.get('description', {}).get('S', ''),
            'source': item.get('source', {}).get('S', ''),
            'region': item.get('region', {}).get('S', 'Global Average')
        }
    except Exception as e:
        print(f"Error fetching emission factor: {str(e)}")
        return None

def calculate_carbon_footprint(category: str, activity: str, amount: float, unit: str) -> Dict[str, Any]:
    """
    Calculate carbon footprint by fetching emission factors from database.
    Falls back to default factor if activity not found.
    """
    
    # Try to get emission factor from database
    emission_data = get_emission_factor_from_db(category, activity)
    
    if emission_data:
        factor = emission_data['emission_factor']
        region = emission_data['region']
        description = emission_data.get('description', '')
    else:
        # Fallback to default factor if not found
        factor = 0.3
        region = "Global Average"
        description = "Default emission factor (activity not found in database)"
        print(f"Warning: No emission factor found for {category}/{activity}, using default: {factor}")
    
    co2_equivalent = amount * factor
    
    return {
        "co2_equivalent": co2_equivalent,
        "emission_factor": factor,
        "calculation_details": f"{amount} {unit} × {factor} kg CO2/{unit}",
        "region": region,
        "description": description
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

# Admin endpoints
@app.get("/api/admin/users")
async def get_all_users(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        dynamodb = get_dynamodb_client()
        response = dynamodb.scan(TableName=USERS_TABLE)
        
        users = []
        for item in response.get('Items', []):
            user_id = item.get('userId', item.get('user_id', {})).get('S', '')
            users.append({
                'user_id': user_id,
                'email': item.get('email', {}).get('S', ''),
                'full_name': item.get('full_name', {}).get('S', ''),
                'role': item.get('role', {}).get('S', 'user'),
                'status': item.get('status', {}).get('S', 'pending'),
                'created_at': item.get('created_at', {}).get('S', ''),
                'last_active': item.get('last_active', {}).get('S', ''),
                'total_emissions': float(item.get('total_emissions', {}).get('N', '0')),
                'entries_count': int(item.get('entries_count', {}).get('N', '0'))
            })
        
        return {"success": True, "users": users, "count": len(users)}
    except Exception as e:
        print(f"Error fetching users: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching users")

@app.get("/api/admin/pending-users")
async def get_pending_users(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get users with pending status (admin only)"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        dynamodb = get_dynamodb_client()
        response = dynamodb.scan(
            TableName=USERS_TABLE,
            FilterExpression='#status = :pending',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':pending': {'S': 'pending'}}
        )
        
        pending_users = []
        for item in response.get('Items', []):
            user_id = item.get('userId', item.get('user_id', {})).get('S', '')
            pending_users.append({
                'user_id': user_id,
                'email': item.get('email', {}).get('S', ''),
                'full_name': item.get('full_name', {}).get('S', ''),
                'created_at': item.get('created_at', {}).get('S', ''),
                'role': item.get('role', {}).get('S', 'user')
            })
        
        return {"success": True, "pending_users": pending_users, "count": len(pending_users)}
    except Exception as e:
        print(f"Error fetching pending users: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching pending users")

@app.post("/api/admin/users/{user_id}/approve")
async def approve_user(user_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Approve a pending user (admin only)"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        dynamodb = get_dynamodb_client()
        now = datetime.utcnow().isoformat()
        
        dynamodb.update_item(
            TableName=USERS_TABLE,
            Key={'userId': {'S': user_id}},
            UpdateExpression='SET #status = :active, updated_at = :now',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':active': {'S': 'active'},
                ':now': {'S': now}
            }
        )
        
        return {"success": True, "message": "User approved successfully", "user_id": user_id}
    except Exception as e:
        print(f"Error approving user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error approving user")

@app.delete("/api/admin/users/{user_id}")
async def reject_user(user_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Reject/delete a pending user (admin only)"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        dynamodb = get_dynamodb_client()
        dynamodb.delete_item(
            TableName=USERS_TABLE,
            Key={'userId': {'S': user_id}}
        )
        
        return {"success": True, "message": "User rejected successfully", "user_id": user_id}
    except Exception as e:
        print(f"Error rejecting user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error rejecting user")

@app.get("/api/admin/stats")
async def get_admin_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get admin dashboard statistics"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        dynamodb = get_dynamodb_client()
        
        # Get all users
        users_response = dynamodb.scan(TableName=USERS_TABLE)
        all_users = users_response.get('Items', [])
        
        # Calculate stats
        total_users = len(all_users)
        pending_count = sum(1 for u in all_users if u.get('status', {}).get('S') == 'pending')
        active_count = sum(1 for u in all_users if u.get('status', {}).get('S') == 'active')
        
        # Get users active this month
        current_month = datetime.utcnow().strftime('%Y-%m')
        active_this_month = sum(1 for u in all_users 
                                if u.get('last_active', {}).get('S', '').startswith(current_month))
        
        # Get total carbon tracked
        entries_response = dynamodb.scan(TableName=EMISSIONS_TABLE)
        total_carbon = sum(float(item.get('co2_equivalent', item.get('amount', {})).get('N', '0')) 
                          for item in entries_response.get('Items', []))
        
        return {
            "success": True,
            "stats": {
                "total_users": total_users,
                "pending_registrations": pending_count,
                "active_users": active_count,
                "active_this_month": active_this_month,
                "total_carbon_tracked": round(total_carbon, 2)
            }
        }
    except Exception as e:
        print(f"Error fetching admin stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching statistics")

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

# Emission Factors Management Endpoints

@app.get("/api/v1/emission-factors/")
async def list_emission_factors(
    category: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    List all emission factors, optionally filtered by category.
    Available to all authenticated users.
    """
    try:
        dynamodb = get_dynamodb_client()
        
        if category:
            # Query by category
            response = dynamodb.query(
                TableName=EMISSION_FACTORS_TABLE,
                KeyConditionExpression='category = :cat',
                ExpressionAttributeValues={
                    ':cat': {'S': category}
                }
            )
        else:
            # Scan all
            response = dynamodb.scan(TableName=EMISSION_FACTORS_TABLE)
        
        items = response.get('Items', [])
        
        emission_factors = []
        for item in items:
            emission_factors.append({
                'category': item['category']['S'],
                'activity': item['activity']['S'],
                'emission_factor': float(item['emission_factor']['N']),
                'unit': item['unit']['S'],
                'description': item.get('description', {}).get('S', ''),
                'source': item.get('source', {}).get('S', ''),
                'region': item.get('region', {}).get('S', 'Global Average')
            })
        
        return {
            "count": len(emission_factors),
            "category_filter": category,
            "emission_factors": emission_factors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching emission factors: {str(e)}"
        )

@app.get("/api/v1/emission-factors/categories")
async def list_categories(current_user: Dict = Depends(get_current_user)):
    """
    List all available emission factor categories.
    """
    try:
        dynamodb = get_dynamodb_client()
        
        # Scan and get unique categories
        response = dynamodb.scan(
            TableName=EMISSION_FACTORS_TABLE,
            ProjectionExpression='category'
        )
        
        items = response.get('Items', [])
        categories = list(set([item['category']['S'] for item in items]))
        categories.sort()
        
        return {
            "count": len(categories),
            "categories": categories
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching categories: {str(e)}"
        )

@app.get("/api/v1/emission-factors/{category}/{activity}")
async def get_emission_factor(
    category: str,
    activity: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get a specific emission factor by category and activity.
    """
    try:
        emission_data = get_emission_factor_from_db(category, activity)
        
        if not emission_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Emission factor not found for {category}/{activity}"
            )
        
        return {
            "category": category,
            "activity": activity,
            **emission_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching emission factor: {str(e)}"
        )

class EmissionFactorCreate(BaseModel):
    category: str
    activity: str
    emission_factor: float
    unit: str
    description: Optional[str] = ""
    source: Optional[str] = "User-defined"
    region: Optional[str] = "Global Average"

@app.post("/api/v1/emission-factors/", status_code=status.HTTP_201_CREATED)
async def create_emission_factor(
    factor_data: EmissionFactorCreate,
    current_user: Dict = Depends(get_current_user)
):
    """
    Create a new emission factor (Admin only).
    """
    # Check if user is admin
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create emission factors"
        )
    
    try:
        dynamodb = get_dynamodb_client()
        
        # Check if already exists
        existing = get_emission_factor_from_db(factor_data.category, factor_data.activity)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Emission factor already exists for {factor_data.category}/{factor_data.activity}"
            )
        
        # Create new emission factor
        dynamodb.put_item(
            TableName=EMISSION_FACTORS_TABLE,
            Item={
                'category': {'S': factor_data.category},
                'activity': {'S': factor_data.activity},
                'emission_factor': {'N': str(factor_data.emission_factor)},
                'unit': {'S': factor_data.unit},
                'description': {'S': factor_data.description},
                'source': {'S': factor_data.source},
                'region': {'S': factor_data.region},
            }
        )
        
        return {
            "message": "Emission factor created successfully",
            "category": factor_data.category,
            "activity": factor_data.activity,
            "emission_factor": factor_data.emission_factor,
            "unit": factor_data.unit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating emission factor: {str(e)}"
        )

@app.put("/api/v1/emission-factors/{category}/{activity}")
async def update_emission_factor(
    category: str,
    activity: str,
    factor_data: EmissionFactorCreate,
    current_user: Dict = Depends(get_current_user)
):
    """
    Update an existing emission factor (Admin only).
    """
    # Check if user is admin
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update emission factors"
        )
    
    try:
        dynamodb = get_dynamodb_client()
        
        # Check if exists
        existing = get_emission_factor_from_db(category, activity)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Emission factor not found for {category}/{activity}"
            )
        
        # Update emission factor
        dynamodb.put_item(
            TableName=EMISSION_FACTORS_TABLE,
            Item={
                'category': {'S': category},
                'activity': {'S': activity},
                'emission_factor': {'N': str(factor_data.emission_factor)},
                'unit': {'S': factor_data.unit},
                'description': {'S': factor_data.description},
                'source': {'S': factor_data.source},
                'region': {'S': factor_data.region},
            }
        )
        
        return {
            "message": "Emission factor updated successfully",
            "category": category,
            "activity": activity,
            "emission_factor": factor_data.emission_factor,
            "unit": factor_data.unit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating emission factor: {str(e)}"
        )

@app.delete("/api/v1/emission-factors/{category}/{activity}")
async def delete_emission_factor(
    category: str,
    activity: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Delete an emission factor (Admin only).
    """
    # Check if user is admin
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete emission factors"
        )
    
    try:
        dynamodb = get_dynamodb_client()
        
        # Check if exists
        existing = get_emission_factor_from_db(category, activity)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Emission factor not found for {category}/{activity}"
            )
        
        # Delete emission factor
        dynamodb.delete_item(
            TableName=EMISSION_FACTORS_TABLE,
            Key={
                'category': {'S': category},
                'activity': {'S': activity}
            }
        )
        
        return {
            "message": "Emission factor deleted successfully",
            "category": category,
            "activity": activity
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting emission factor: {str(e)}"
        )

# Lambda handler for AWS deployment
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    # Mangum not available (local development)
    handler = None

if __name__ == "__main__":
    uvicorn.run(
        "combined_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )