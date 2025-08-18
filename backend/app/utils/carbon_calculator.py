"""
Utility functions for carbon calculations
"""

from typing import Dict, Any


# Carbon emission factors (kg CO2 per unit)
EMISSION_FACTORS = {
    "transportation": {
        "car_drive": {"km": 0.2},  # 0.2 kg CO2 per km
        "flight": {"km": 0.15},    # 0.15 kg CO2 per km
        "train": {"km": 0.04},     # 0.04 kg CO2 per km
        "bus": {"km": 0.08},       # 0.08 kg CO2 per km
        "subway": {"km": 0.03},    # 0.03 kg CO2 per km
        "bike": {"km": 0.0},       # 0 kg CO2 per km
        "walk": {"km": 0.0},       # 0 kg CO2 per km
    },
    "energy": {
        "electricity": {"kwh": 0.4},  # 0.4 kg CO2 per kWh
        "natural_gas": {"m3": 2.0},   # 2.0 kg CO2 per m³
        "heating_oil": {"l": 2.7},    # 2.7 kg CO2 per liter
    },
    "food": {
        "beef": {"kg": 27.0},         # 27 kg CO2 per kg
        "pork": {"kg": 12.0},         # 12 kg CO2 per kg
        "chicken": {"kg": 6.9},       # 6.9 kg CO2 per kg
        "fish": {"kg": 6.0},          # 6 kg CO2 per kg
        "dairy": {"kg": 3.2},         # 3.2 kg CO2 per kg
        "vegetables": {"kg": 2.0},    # 2 kg CO2 per kg
    },
    "waste": {
        "general": {"kg": 0.5},       # 0.5 kg CO2 per kg
        "recycling": {"kg": 0.1},     # 0.1 kg CO2 per kg
        "compost": {"kg": 0.0},       # 0 kg CO2 per kg
    }
}


def calculate_co2_equivalent(category: str, activity: str, amount: float, unit: str) -> float:
    """
    Calculate CO2 equivalent for a given activity
    
    Args:
        category: Category of emission (transportation, energy, food, waste)
        activity: Specific activity (car_drive, electricity, etc.)
        amount: Amount of activity
        unit: Unit of measurement
        
    Returns:
        CO2 equivalent in kg
    """
    try:
        factor = EMISSION_FACTORS[category][activity][unit]
        return round(amount * factor, 2)
    except KeyError:
        # Default factor if not found
        return round(amount * 0.1, 2)


def get_emission_categories() -> Dict[str, Any]:
    """Get all available emission categories and their activities"""
    return {
        category: {
            "activities": list(activities.keys()),
            "units": list(set(
                unit for activity_units in activities.values() 
                for unit in activity_units.keys()
            ))
        }
        for category, activities in EMISSION_FACTORS.items()
    }


def calculate_monthly_totals(emissions: list) -> Dict[str, float]:
    """
    Calculate monthly emission totals from a list of emissions
    
    Args:
        emissions: List of emission dictionaries with date and co2_equivalent
        
    Returns:
        Dictionary with month keys and total emissions
    """
    monthly_totals = {}
    
    for emission in emissions:
        # Assuming date is in format "YYYY-MM-DD" or datetime object
        if isinstance(emission.get('date'), str):
            month_key = emission['date'][:7]  # "YYYY-MM"
        else:
            month_key = emission['date'].strftime("%Y-%m")
            
        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + emission.get('co2_equivalent', 0)
    
    return monthly_totals


def calculate_category_totals(emissions: list) -> Dict[str, float]:
    """
    Calculate emission totals by category
    
    Args:
        emissions: List of emission dictionaries with category and co2_equivalent
        
    Returns:
        Dictionary with category keys and total emissions
    """
    category_totals = {}
    
    for emission in emissions:
        category = emission.get('category', 'other')
        category_totals[category] = category_totals.get(category, 0) + emission.get('co2_equivalent', 0)
    
    return category_totals


def generate_reduction_suggestions(emissions: list) -> list:
    """
    Generate personalized reduction suggestions based on user's emissions
    
    Args:
        emissions: List of user's emission data
        
    Returns:
        List of suggestion dictionaries
    """
    category_totals = calculate_category_totals(emissions)
    suggestions = []
    
    # Find highest emission category
    if category_totals:
        highest_category = max(category_totals, key=category_totals.get)
        highest_amount = category_totals[highest_category]
        
        if highest_category == "transportation" and highest_amount > 50:
            suggestions.append({
                "category": "transportation",
                "title": "Reduce Car Usage",
                "description": "Consider using public transportation, biking, or walking for short trips",
                "potential_reduction": "20-40%",
                "priority": "high"
            })
        
        if highest_category == "energy" and highest_amount > 30:
            suggestions.append({
                "category": "energy",
                "title": "Energy Efficiency",
                "description": "Switch to LED bulbs and consider renewable energy sources",
                "potential_reduction": "15-25%",
                "priority": "medium"
            })
        
        if highest_category == "food" and highest_amount > 20:
            suggestions.append({
                "category": "food",
                "title": "Dietary Changes",
                "description": "Reduce meat consumption and choose locally sourced food",
                "potential_reduction": "10-30%",
                "priority": "medium"
            })
    
    return suggestions
