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
from app.models.dynamodb_models import CarbonEmissionModel

router = APIRouter(prefix="/carbon-emissions", tags=["Carbon Tracking"])


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
        
        # Calculate CO2 equivalent (simple calculation - can be enhanced)
        co2_equivalent = Decimal(str(emission_data.amount * 0.2))  # Basic emission factor
        
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
            emission_factor=Decimal('0.2')  # Basic factor
        )
        
        # Save to DynamoDB
        result = await dynamodb_service.create_carbon_emission(carbon_emission)
        
        if result.get("success"):
            return {
                "id": result["entry_id"],
                "user_id": user_id,
                "message": "Carbon emission recorded successfully",
                "co2_equivalent": float(co2_equivalent),
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
