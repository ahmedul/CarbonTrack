#!/usr/bin/env python3
"""
Simple FastAPI server for CarbonTrack - minimal version for testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime

# Simple standalone server without complex imports
# We'll create a basic emission calculation function

def calculate_simple_carbon_footprint(activity: str, amount: float, unit: str, category: str) -> float:
    """Simple carbon footprint calculation with basic emission factors"""
    
    # Basic emission factors (kg CO2 per unit)
    emission_factors = {
        "transportation": {
            ("km", "car"): 0.23,
            ("km", "flight"): 0.2,
            ("km", "bus"): 0.063,
            ("km", "train"): 0.045,
            ("miles", "car"): 0.37,
            ("miles", "flight"): 0.32,
        },
        "energy": {
            ("kWh", "electricity"): 0.4,
            ("m³", "gas"): 2.0,
            ("liters", "oil"): 2.67,
        },
        "food": {
            ("kg", "beef"): 60.0,
            ("kg", "pork"): 7.0,
            ("kg", "chicken"): 7.0,
            ("kg", "fish"): 6.0,
        },
        "waste": {
            ("kg", "landfill"): 2.1,
            ("kg", "recycling"): 0.2,
        }
    }
    
    # Try to find matching emission factor
    for key, factor in emission_factors.get(category, {}).items():
        unit_check, activity_check = key
        if unit.lower() == unit_check.lower() and activity_check in activity.lower():
            return amount * factor
    
    # Default fallback calculation
    defaults = {"transportation": 0.2, "energy": 0.4, "food": 10.0, "waste": 2.0}
    return amount * defaults.get(category, 0.5)

app = FastAPI(title="CarbonTrack API", description="Simple Carbon Footprint Tracking API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class EmissionCreate(BaseModel):
    activity: str
    amount: float
    unit: str
    category: str
    date: str
    description: Optional[str] = None

class EmissionResponse(BaseModel):
    id: int
    activity: str
    amount: float
    unit: str
    category: str
    date: str
    description: Optional[str]
    co2_equivalent: float
    created_at: str

class LoginRequest(BaseModel):
    email: str
    password: str

# In-memory storage for this demo
emissions_db = []
next_id = 1
current_user = None

@app.get("/")
async def root():
    return {"message": "CarbonTrack API is running!", "status": "ok"}

@app.post("/auth/login")
async def login(request: LoginRequest):
    global current_user
    # Demo authentication - accept demo@carbontrack.dev with any password
    if request.email == "demo@carbontrack.dev":
        current_user = {
            "id": 1,
            "email": request.email,
            "name": "Demo User"
        }
        return {
            "success": True,
            "user": current_user,
            "token": "demo-token-12345"
        }
    return {"success": False, "message": "Invalid credentials"}

@app.post("/auth/logout")
async def logout():
    global current_user
    current_user = None
    return {"success": True, "message": "Logged out successfully"}

@app.get("/auth/me")
async def get_current_user():
    if current_user:
        return {"success": True, "user": current_user}
    return {"success": False, "message": "Not authenticated"}

@app.get("/api/v1/carbon/activities")
async def get_activity_suggestions():
    return {
        "transportation": [
            {"key": "car_gasoline", "name": "Gasoline Car", "unit": "km", "example": "Daily commute: ~50 km → 11.5 kg CO₂"},
            {"key": "car_diesel", "name": "Diesel Car", "unit": "km", "example": "Weekend trip: ~200 km → 39.6 kg CO₂"},
            {"key": "flight_domestic", "name": "Domestic Flight", "unit": "km", "example": "NY to LA: ~4,000 km → 800 kg CO₂"},
            {"key": "flight_international", "name": "International Flight", "unit": "km", "example": "NY to London: ~5,500 km → 1,430 kg CO₂"},
            {"key": "bus", "name": "Bus", "unit": "km", "example": "City commute: ~30 km → 1.9 kg CO₂"},
            {"key": "train", "name": "Train", "unit": "km", "example": "Regional trip: ~300 km → 13.5 kg CO₂"},
        ],
        "energy": [
            {"key": "electricity", "name": "Electricity Usage", "unit": "kWh", "example": "Monthly bill: ~500 kWh → 200 kg CO₂"},
            {"key": "natural_gas", "name": "Natural Gas", "unit": "m³", "example": "Heating: ~100 m³ → 200 kg CO₂"},
            {"key": "heating_oil", "name": "Heating Oil", "unit": "liters", "example": "Winter heating: ~300L → 800 kg CO₂"},
        ],
        "food": [
            {"key": "beef", "name": "Beef", "unit": "kg", "example": "Weekly steak: ~2 kg → 120 kg CO₂"},
            {"key": "pork", "name": "Pork", "unit": "kg", "example": "Monthly consumption: ~3 kg → 21 kg CO₂"},
            {"key": "chicken", "name": "Chicken", "unit": "kg", "example": "Weekly meals: ~1.5 kg → 10.5 kg CO₂"},
            {"key": "fish", "name": "Fish", "unit": "kg", "example": "Seafood dinner: ~0.5 kg → 3 kg CO₂"},
        ],
        "waste": [
            {"key": "landfill", "name": "Landfill Waste", "unit": "kg", "example": "Weekly trash: ~10 kg → 21 kg CO₂"},
            {"key": "recycling", "name": "Recycling", "unit": "kg", "example": "Monthly recycling: ~15 kg → 3 kg CO₂"},
        ]
    }

@app.get("/api/v1/carbon/emissions", response_model=List[EmissionResponse])
async def get_emissions():
    return emissions_db

@app.post("/api/v1/carbon/emissions", response_model=EmissionResponse)
async def create_emission(emission: EmissionCreate):
    global next_id
    
    # Calculate CO2 equivalent using our simple calculator
    try:
        co2_equivalent = calculate_simple_carbon_footprint(
            activity=emission.activity,
            amount=emission.amount,
            unit=emission.unit,
            category=emission.category.lower()
        )
        co2_equivalent = round(co2_equivalent, 2)
    except Exception as e:
        print(f"Error calculating carbon footprint: {e}")
        # Fallback to simple calculation
        co2_equivalent = round(emission.amount * 0.23, 2)
    
    # Create emission record
    emission_record = EmissionResponse(
        id=next_id,
        activity=emission.activity,
        amount=emission.amount,
        unit=emission.unit,
        category=emission.category,
        date=emission.date,
        description=emission.description,
        co2_equivalent=co2_equivalent,
        created_at=datetime.now().isoformat()
    )
    
    emissions_db.append(emission_record)
    next_id += 1
    
    return emission_record

@app.delete("/api/v1/carbon/emissions/{emission_id}")
async def delete_emission(emission_id: int):
    global emissions_db
    emissions_db = [e for e in emissions_db if e.id != emission_id]
    return {"success": True, "message": "Emission deleted successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("🌍 Starting CarbonTrack API server...")
    print("📊 Carbon calculation engine: ✅ Scientific emission factors loaded")
    print("🚀 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    uvicorn.run("simple_server:app", host="0.0.0.0", port=8000, reload=True)