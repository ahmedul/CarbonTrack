"""Carbon tracking API routes"""

from fastapi import APIRouter, Depends, status, Query, HTTPException
from typing import Dict, Any, List, Optional
from datetime import date
from decimal import Decimal

from app.schemas.carbon import (
    CarbonEmissionCreate,
    CarbonEmissionUpdate,
    EmissionCategory
)
from app.core.middleware import get_current_user
from app.services.dynamodb_service import dynamodb_service
from app.services.carbon_calculator import calculate_carbon_footprint, calculator
from app.models.dynamodb_models import CarbonEmissionModel

router = APIRouter(prefix="/carbon-emissions", tags=["Carbon Tracking"])


@router.get("/activities", response_model=Dict[str, Any])
async def get_available_activities():
    """
    Get available activities and their emission factors for each category
    
    This helps frontend applications show users appropriate activity options
    and provides transparency about emission calculations.
    """
    try:
        activities = {
            "transportation": {
                "description": "Transportation activities with CO₂ emissions per km",
                "activities": [
                    {"key": "car_gasoline_small", "name": "Small Gasoline Car", "unit": "km", "factor": float(calculator.transportation_factors["car_gasoline_small"])},
                    {"key": "car_gasoline_medium", "name": "Medium Gasoline Car", "unit": "km", "factor": float(calculator.transportation_factors["car_gasoline_medium"])},
                    {"key": "car_gasoline_large", "name": "Large Gasoline Car/SUV", "unit": "km", "factor": float(calculator.transportation_factors["car_gasoline_large"])},
                    {"key": "car_diesel_small", "name": "Small Diesel Car", "unit": "km", "factor": float(calculator.transportation_factors["car_diesel_small"])},
                    {"key": "car_diesel_medium", "name": "Medium Diesel Car", "unit": "km", "factor": float(calculator.transportation_factors["car_diesel_medium"])},
                    {"key": "car_hybrid", "name": "Hybrid Vehicle", "unit": "km", "factor": float(calculator.transportation_factors["car_hybrid"])},
                    {"key": "car_electric", "name": "Electric Vehicle", "unit": "km", "factor": float(calculator.transportation_factors["car_electric"])},
                    {"key": "motorcycle", "name": "Motorcycle", "unit": "km", "factor": float(calculator.transportation_factors["motorcycle"])},
                    {"key": "bus_city", "name": "City Bus", "unit": "km", "factor": float(calculator.transportation_factors["bus_city"])},
                    {"key": "train_local", "name": "Local/Commuter Train", "unit": "km", "factor": float(calculator.transportation_factors["train_local"])},
                    {"key": "flight_domestic_short", "name": "Domestic Flight (<500km)", "unit": "km", "factor": float(calculator.transportation_factors["flight_domestic_short"])},
                    {"key": "flight_domestic_medium", "name": "Domestic Flight (500-1500km)", "unit": "km", "factor": float(calculator.transportation_factors["flight_domestic_medium"])},
                    {"key": "flight_international", "name": "International Flight (>1500km)", "unit": "km", "factor": float(calculator.transportation_factors["flight_international"])},
                ]
            },
            "energy": {
                "description": "Energy consumption activities with CO₂ emissions per unit",
                "activities": [
                    {"key": "electricity", "name": "Electricity", "unit": "kWh", "factor": float(calculator.energy_factors["electricity"])},
                    {"key": "natural_gas_therms", "name": "Natural Gas", "unit": "therms", "factor": float(calculator.energy_factors["natural_gas_therms"])},
                    {"key": "natural_gas_kwh", "name": "Natural Gas", "unit": "kWh", "factor": float(calculator.energy_factors["natural_gas_kwh"])},
                    {"key": "heating_oil_gallons", "name": "Heating Oil", "unit": "gallons", "factor": float(calculator.energy_factors["heating_oil_gallons"])},
                    {"key": "propane_gallons", "name": "Propane", "unit": "gallons", "factor": float(calculator.energy_factors["propane_gallons"])},
                ]
            },
            "food": {
                "description": "Food consumption activities with CO₂ emissions per kg",
                "activities": [
                    {"key": "beef", "name": "Beef", "unit": "kg", "factor": float(calculator.food_factors["beef"])},
                    {"key": "lamb", "name": "Lamb", "unit": "kg", "factor": float(calculator.food_factors["lamb"])},
                    {"key": "pork", "name": "Pork", "unit": "kg", "factor": float(calculator.food_factors["pork"])},
                    {"key": "chicken", "name": "Chicken", "unit": "kg", "factor": float(calculator.food_factors["chicken"])},
                    {"key": "fish_farmed", "name": "Farmed Fish", "unit": "kg", "factor": float(calculator.food_factors["fish_farmed"])},
                    {"key": "fish_wild", "name": "Wild Fish", "unit": "kg", "factor": float(calculator.food_factors["fish_wild"])},
                    {"key": "milk", "name": "Milk", "unit": "liters", "factor": float(calculator.food_factors["milk"])},
                    {"key": "cheese", "name": "Cheese", "unit": "kg", "factor": float(calculator.food_factors["cheese"])},
                    {"key": "eggs", "name": "Eggs", "unit": "kg", "factor": float(calculator.food_factors["eggs"])},
                    {"key": "rice", "name": "Rice", "unit": "kg", "factor": float(calculator.food_factors["rice"])},
                    {"key": "vegetables_root", "name": "Root Vegetables", "unit": "kg", "factor": float(calculator.food_factors["vegetables_root"])},
                    {"key": "fruits_local", "name": "Local Fruits", "unit": "kg", "factor": float(calculator.food_factors["fruits_local"])},
                ]
            },
            "waste": {
                "description": "Waste disposal activities with CO₂ impact per kg (negative = carbon savings)",
                "activities": [
                    {"key": "landfill_mixed", "name": "Mixed Waste to Landfill", "unit": "kg", "factor": float(calculator.waste_factors["landfill_mixed"])},
                    {"key": "recycling_paper", "name": "Paper Recycling", "unit": "kg", "factor": float(calculator.waste_factors["recycling_paper"])},
                    {"key": "recycling_plastic", "name": "Plastic Recycling", "unit": "kg", "factor": float(calculator.waste_factors["recycling_plastic"])},
                    {"key": "recycling_aluminum", "name": "Aluminum Recycling", "unit": "kg", "factor": float(calculator.waste_factors["recycling_aluminum"])},
                    {"key": "composting_food", "name": "Food Composting", "unit": "kg", "factor": float(calculator.waste_factors["composting_food"])},
                ]
            }
        }
        
        return {
            "message": "Available carbon calculation activities",
            "region": calculator.region.value,
            "categories": activities
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving activities: {str(e)}")


@router.get("/", response_model=List[Dict[str, Any]])
async def get_carbon_emissions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    category: Optional[EmissionCategory] = Query(None, description="Filter by category"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    limit: int = Query(50, description="Maximum number of entries to return")
):
    """
    Get user's carbon emissions with optional filtering
    
    - **category**: Optional category filter
    - **start_date**: Optional start date filter
    - **end_date**: Optional end date filter
    - **limit**: Maximum number of entries to return
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Convert dates to ISO strings if provided
        start_date_str = start_date.isoformat() if start_date else None
        end_date_str = end_date.isoformat() if end_date else None
        
        # Get emissions from DynamoDB
        emissions = await dynamodb_service.get_user_emissions(
            user_id=user_id,
            start_date=start_date_str,
            end_date=end_date_str,
            limit=limit
        )
        
        # Filter by category if specified
        if category:
            emissions = [e for e in emissions if e.get('category') == category.value]
        
        return emissions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving emissions: {str(e)}")


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_carbon_emission(
    emission_data: CarbonEmissionCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new carbon emission entry
    
    - **date**: Date of the emission
    - **category**: Category of emission (transportation, energy, etc.)
    - **activity**: Specific activity (car_drive, flight, etc.)
    - **amount**: Amount of activity
    - **unit**: Unit of measurement (km, kWh, etc.)
    - **description**: Optional description
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Calculate CO2 equivalent using sophisticated carbon calculator
        calculation_result = calculate_carbon_footprint(
            category=emission_data.category.value,
            activity=emission_data.activity,
            amount=float(emission_data.amount),
            unit=emission_data.unit
        )
        
        co2_equivalent = Decimal(str(calculation_result["co2_equivalent"]))
        emission_factor = Decimal(str(calculation_result["emission_factor"]))
        
        # Create CarbonEmissionModel
        carbon_emission = CarbonEmissionModel(
            user_id=user_id,
            date=emission_data.date,
            category=emission_data.category.value,
            activity=emission_data.activity,
            amount=Decimal(str(emission_data.amount)),
            unit=emission_data.unit,
            description=emission_data.description,
            co2_equivalent=co2_equivalent,
            emission_factor=emission_factor
        )
        
        # Save to DynamoDB
        result = await dynamodb_service.create_carbon_emission(carbon_emission)
        
        if result.get("success"):
            return {
                "id": result["entry_id"],
                "user_id": user_id,
                "message": "Carbon emission recorded successfully",
                "co2_equivalent": float(co2_equivalent),
                "emission_factor": float(emission_factor),
                "calculation_details": calculation_result["calculation_details"],
                "calculation_region": calculation_result["region"],
                **emission_data.dict()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to create emission"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating emission: {str(e)}")


@router.put("/{timestamp}", response_model=Dict[str, Any])
async def update_carbon_emission(
    timestamp: str,
    emission_data: CarbonEmissionUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update an existing carbon emission entry by timestamp
    
    Only the owner of the emission can update it.
    Use the timestamp from the entry as the ID.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Prepare updates dictionary
        updates = {}
        for field, value in emission_data.dict().items():
            if value is not None:
                if field == "amount" and value is not None:
                    updates[field] = Decimal(str(value))
                    # Recalculate CO2 equivalent if amount changes
                    updates["co2_equivalent"] = Decimal(str(value * 0.2))
                elif field == "category" and value is not None:
                    updates[field] = value.value if hasattr(value, 'value') else str(value)
                else:
                    updates[field] = value
        
        if not updates:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # Update in DynamoDB
        success = await dynamodb_service.update_carbon_emission(user_id, timestamp, updates)
        
        if not success:
            raise HTTPException(status_code=404, detail="Emission not found or could not be updated")
        
        return {
            "timestamp": timestamp,
            "user_id": user_id,
            "message": "Carbon emission updated successfully",
            **{k: (float(v) if isinstance(v, Decimal) else v) for k, v in updates.items()}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating emission: {str(e)}")


@router.delete("/{timestamp}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_carbon_emission(
    timestamp: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a carbon emission entry by timestamp
    
    Only the owner of the emission can delete it.
    Use the timestamp from the entry as the ID.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Delete from DynamoDB
        success = await dynamodb_service.delete_carbon_emission(user_id, timestamp)
        
        if not success:
            raise HTTPException(status_code=404, detail="Emission not found or could not be deleted")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting emission: {str(e)}")


@router.get("/analytics", response_model=Dict[str, Any])
async def get_analytics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    start_date: date = Query(..., description="Start date for analytics"),
    end_date: date = Query(..., description="End date for analytics"),
    category: Optional[EmissionCategory] = Query(None, description="Filter by category")
):
    """
    Get carbon footprint analytics for a date range
    
    - **start_date**: Start date for analytics
    - **end_date**: End date for analytics
    - **category**: Optional category filter
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get analytics from DynamoDB
        analytics = await dynamodb_service.get_analytics(
            user_id=user_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Add period information
        analytics["period_start"] = start_date
        analytics["period_end"] = end_date
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analytics: {str(e)}")
