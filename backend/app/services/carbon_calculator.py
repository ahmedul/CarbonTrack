"""
Carbon footprint calculation engine with scientific emission factors

This module provides accurate CO2 equivalent calculations for various activities
based on established emission factors from research institutions and government agencies.

Sources:
- EPA Emission Factors Hub
- IPCC Guidelines for National Greenhouse Gas Inventories
- DEFRA UK Government GHG Conversion Factors
- EIA Energy Information Administration
- Academic research papers on lifecycle carbon assessments
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class EmissionUnit(Enum):
    """Standard units for emission calculations"""
    KG_CO2E = "kg_co2e"  # Kilograms of CO2 equivalent
    GRAMS_CO2E = "g_co2e"  # Grams of CO2 equivalent
    TONNES_CO2E = "t_co2e"  # Tonnes of CO2 equivalent

class Region(Enum):
    """Regional variations for calculations"""
    US_AVERAGE = "us_average"
    EU_AVERAGE = "eu_average" 
    UK = "uk"
    CANADA = "canada"
    AUSTRALIA = "australia"
    GLOBAL_AVERAGE = "global_average"

class CarbonCalculator:
    """
    Comprehensive carbon footprint calculator with scientifically-based emission factors
    """
    
    def __init__(self, region: Region = Region.US_AVERAGE):
        self.region = region
        self._load_emission_factors()
    
    def _load_emission_factors(self):
        """Load emission factors based on region and activity type"""
        
        # Transportation emission factors (kg CO2e per unit)
        self.transportation_factors = {
            # Personal Vehicles (kg CO2e per km)
            "car_gasoline_small": Decimal("0.151"),     # Small gasoline car
            "car_gasoline_medium": Decimal("0.192"),    # Medium gasoline car
            "car_gasoline_large": Decimal("0.251"),     # Large gasoline car/SUV
            "car_diesel_small": Decimal("0.142"),       # Small diesel car
            "car_diesel_medium": Decimal("0.171"),      # Medium diesel car
            "car_hybrid": Decimal("0.109"),             # Hybrid vehicle
            "car_electric": self._get_electric_car_factor(),  # Region-dependent
            "motorcycle": Decimal("0.103"),             # Average motorcycle
            
            # Public Transportation (kg CO2e per km per passenger)
            "bus_city": Decimal("0.089"),               # City bus
            "bus_coach": Decimal("0.027"),              # Long distance coach
            "train_local": Decimal("0.041"),            # Local/commuter train
            "train_intercity": Decimal("0.035"),        # Intercity train
            "metro_subway": Decimal("0.028"),           # Metro/subway
            
            # Aviation (kg CO2e per km per passenger)
            "flight_domestic_short": Decimal("0.255"),   # <500km
            "flight_domestic_medium": Decimal("0.195"),  # 500-1500km  
            "flight_international": Decimal("0.150"),    # >1500km
            "flight_first_class": Decimal("0.390"),      # First class multiplier
            
            # Other Transport
            "taxi": Decimal("0.211"),                   # Taxi ride
            "ferry": Decimal("0.113"),                  # Ferry per km
            "cruise_ship": Decimal("0.435"),            # Cruise ship per km
        }
        
        # Energy emission factors (kg CO2e per unit)
        self.energy_factors = {
            # Electricity (kg CO2e per kWh) - varies significantly by region
            "electricity": self._get_electricity_factor(),
            
            # Natural Gas (kg CO2e per unit)
            "natural_gas_therms": Decimal("5.3"),       # per therm
            "natural_gas_kwh": Decimal("0.184"),        # per kWh
            "natural_gas_m3": Decimal("1.91"),          # per cubic meter
            
            # Heating Oil & Propane
            "heating_oil_liters": Decimal("2.52"),      # per liter
            "heating_oil_gallons": Decimal("9.54"),     # per gallon
            "propane_liters": Decimal("1.51"),          # per liter  
            "propane_gallons": Decimal("5.72"),         # per gallon
            
            # Coal
            "coal_kg": Decimal("2.42"),                 # per kg
            "coal_tons": Decimal("2420"),               # per short ton
            
            # Wood/Biomass (considered carbon neutral but not zero)
            "wood_kg": Decimal("0.01"),                 # per kg (processing/transport)
        }
        
        # Food emission factors (kg CO2e per kg of food)
        self.food_factors = {
            # Meat & Animal Products
            "beef": Decimal("60.0"),                    # Highest impact
            "lamb": Decimal("39.2"),
            "pork": Decimal("12.1"),
            "chicken": Decimal("9.9"),
            "turkey": Decimal("10.9"),
            "fish_farmed": Decimal("13.6"),
            "fish_wild": Decimal("2.9"),
            "shellfish": Decimal("11.0"),
            
            # Dairy
            "milk": Decimal("3.2"),                     # per liter
            "cheese": Decimal("13.5"),
            "butter": Decimal("23.8"),
            "yogurt": Decimal("2.2"),
            "eggs": Decimal("4.2"),
            
            # Plant-based
            "rice": Decimal("4.0"),                     # High due to methane
            "wheat": Decimal("1.4"),
            "potatoes": Decimal("0.46"),
            "vegetables_root": Decimal("0.43"),
            "vegetables_leafy": Decimal("2.0"),         # Often greenhouse grown
            "fruits_local": Decimal("1.1"),
            "fruits_tropical": Decimal("1.9"),          # Transport emissions
            "nuts": Decimal("0.26"),
            "legumes": Decimal("0.43"),
            
            # Processed Foods
            "bread": Decimal("1.6"),
            "pasta": Decimal("1.4"),
            "coffee": Decimal("16.9"),                  # per kg beans
            "tea": Decimal("7.0"),                      # per kg leaves
            "chocolate": Decimal("18.7"),
            "sugar": Decimal("3.2"),
            "vegetable_oil": Decimal("3.1"),
            
            # Beverages
            "beer": Decimal("0.89"),                    # per liter
            "wine": Decimal("1.79"),                    # per liter
            "spirits": Decimal("3.48"),                 # per liter
        }
        
        # Waste emission factors (kg CO2e per kg of waste)
        self.waste_factors = {
            # Disposal Methods
            "landfill_mixed": Decimal("0.57"),          # Mixed waste to landfill
            "landfill_food": Decimal("0.77"),           # Food waste (methane)
            "landfill_paper": Decimal("1.84"),          # Paper waste
            "incineration": Decimal("0.41"),            # Waste incineration
            
            # Recycling (negative = carbon savings)
            "recycling_paper": Decimal("-0.89"),       # Paper recycling saves carbon
            "recycling_plastic": Decimal("-1.83"),     # Plastic recycling
            "recycling_aluminum": Decimal("-8.94"),    # Aluminum - huge savings
            "recycling_glass": Decimal("-0.31"),       # Glass recycling
            "recycling_steel": Decimal("-2.07"),       # Steel recycling
            
            # Composting
            "composting_food": Decimal("-0.26"),       # Composting saves vs landfill
            "composting_yard": Decimal("-0.15"),       # Yard waste composting
            
            # Material Production (if not recycled)
            "paper_new": Decimal("1.04"),              # New paper production
            "plastic_new": Decimal("3.79"),            # New plastic production
            "aluminum_new": Decimal("11.46"),          # New aluminum production
            "glass_new": Decimal("0.85"),              # New glass production
        }
    
    def _get_electricity_factor(self) -> Decimal:
        """Get electricity emission factor based on region"""
        electricity_factors = {
            Region.US_AVERAGE: Decimal("0.401"),        # US average grid mix
            Region.EU_AVERAGE: Decimal("0.276"),        # EU average (more renewable)
            Region.UK: Decimal("0.233"),                # UK grid (renewable + nuclear)
            Region.CANADA: Decimal("0.130"),            # Canada (hydro-heavy)
            Region.AUSTRALIA: Decimal("0.81"),          # Australia (coal-heavy)
            Region.GLOBAL_AVERAGE: Decimal("0.475"),    # Global average
        }
        return electricity_factors.get(self.region, electricity_factors[Region.GLOBAL_AVERAGE])
    
    def _get_electric_car_factor(self) -> Decimal:
        """Calculate electric car emissions based on regional electricity grid"""
        # Electric car efficiency: ~0.3 kWh per km average
        electricity_per_km = Decimal("0.3")
        grid_factor = self._get_electricity_factor()
        return electricity_per_km * grid_factor
    
    def calculate_transportation(self, activity: str, amount: Decimal, unit: str) -> Tuple[Decimal, str]:
        """
        Calculate CO2 emissions for transportation activities
        
        Args:
            activity: Transportation type (e.g., "car_gasoline_medium")
            amount: Amount of activity
            unit: Unit of measurement ("km", "miles", "hours")
            
        Returns:
            Tuple of (co2_equivalent_kg, calculation_details)
        """
        try:
            # Convert miles to km if needed
            if unit.lower() in ["miles", "mile", "mi"]:
                amount = amount * Decimal("1.60934")  # miles to km
                unit = "km"
            
            # Get emission factor
            if activity not in self.transportation_factors:
                logger.warning(f"Unknown transportation activity: {activity}")
                activity = "car_gasoline_medium"  # Default fallback
            
            factor = self.transportation_factors[activity]
            co2_equivalent = amount * factor
            
            details = f"{activity}: {amount} {unit} × {factor} kg CO₂e/{unit} = {co2_equivalent} kg CO₂e"
            
            return co2_equivalent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), details
            
        except Exception as e:
            logger.error(f"Transportation calculation error: {e}")
            # Fallback calculation
            return Decimal("5.0"), "Error in calculation, using fallback: 5.0 kg CO₂e"
    
    def calculate_energy(self, activity: str, amount: Decimal, unit: str) -> Tuple[Decimal, str]:
        """
        Calculate CO2 emissions for energy consumption
        
        Args:
            activity: Energy type (e.g., "electricity", "natural_gas_therms")
            amount: Amount consumed
            unit: Unit of measurement ("kwh", "therms", "liters", etc.)
            
        Returns:
            Tuple of (co2_equivalent_kg, calculation_details)
        """
        try:
            # Normalize unit naming
            unit_lower = unit.lower()
            activity_key = f"{activity}_{unit_lower}" if activity in ["natural_gas", "heating_oil", "propane"] else activity
            
            # Handle electricity specifically
            if activity == "electricity":
                if unit_lower in ["kwh", "kilowatt_hours", "kw_hours"]:
                    factor = self.energy_factors["electricity"]
                else:
                    raise ValueError(f"Unsupported electricity unit: {unit}")
            else:
                if activity_key not in self.energy_factors:
                    logger.warning(f"Unknown energy activity: {activity_key}")
                    factor = Decimal("0.5")  # Generic fallback
                else:
                    factor = self.energy_factors[activity_key]
            
            co2_equivalent = amount * factor
            details = f"{activity}: {amount} {unit} × {factor} kg CO₂e/{unit} = {co2_equivalent} kg CO₂e"
            
            return co2_equivalent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), details
            
        except Exception as e:
            logger.error(f"Energy calculation error: {e}")
            return Decimal("2.0"), "Error in calculation, using fallback: 2.0 kg CO₂e"
    
    def calculate_food(self, activity: str, amount: Decimal, unit: str) -> Tuple[Decimal, str]:
        """
        Calculate CO2 emissions for food consumption
        
        Args:
            activity: Food type (e.g., "beef", "chicken", "vegetables_leafy")
            amount: Amount consumed
            unit: Unit of measurement ("kg", "lbs", "servings")
            
        Returns:
            Tuple of (co2_equivalent_kg, calculation_details)
        """
        try:
            # Convert pounds to kg if needed
            if unit.lower() in ["lbs", "lb", "pounds", "pound"]:
                amount = amount * Decimal("0.453592")  # lbs to kg
                unit = "kg"
            
            # Convert servings to approximate kg (rough estimates)
            elif unit.lower() in ["serving", "servings", "portion", "portions"]:
                serving_weights = {
                    "beef": 0.113, "lamb": 0.113, "pork": 0.113,  # 4 oz meat serving
                    "chicken": 0.113, "turkey": 0.113, "fish_farmed": 0.113, "fish_wild": 0.113,
                    "milk": 0.25, "cheese": 0.03, "eggs": 0.05,  # Standard dairy servings
                    "rice": 0.08, "pasta": 0.08, "bread": 0.03,  # Grain servings
                }
                weight_per_serving = serving_weights.get(activity, 0.1)  # 100g default
                amount = amount * Decimal(str(weight_per_serving))
                unit = "kg"
            
            # Get emission factor
            if activity not in self.food_factors:
                logger.warning(f"Unknown food activity: {activity}")
                activity = "chicken"  # Default to moderate-impact protein
            
            factor = self.food_factors[activity]
            co2_equivalent = amount * factor
            
            details = f"{activity}: {amount} {unit} × {factor} kg CO₂e/{unit} = {co2_equivalent} kg CO₂e"
            
            return co2_equivalent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), details
            
        except Exception as e:
            logger.error(f"Food calculation error: {e}")
            return Decimal("1.0"), "Error in calculation, using fallback: 1.0 kg CO₂e"
    
    def calculate_waste(self, activity: str, amount: Decimal, unit: str) -> Tuple[Decimal, str]:
        """
        Calculate CO2 emissions for waste disposal/recycling
        
        Args:
            activity: Waste type/method (e.g., "landfill_mixed", "recycling_paper")
            amount: Amount of waste
            unit: Unit of measurement ("kg", "lbs")
            
        Returns:
            Tuple of (co2_equivalent_kg, calculation_details)
        """
        try:
            # Convert pounds to kg if needed
            if unit.lower() in ["lbs", "lb", "pounds", "pound"]:
                amount = amount * Decimal("0.453592")
                unit = "kg"
            
            # Get emission factor
            if activity not in self.waste_factors:
                logger.warning(f"Unknown waste activity: {activity}")
                activity = "landfill_mixed"  # Default fallback
            
            factor = self.waste_factors[activity]
            co2_equivalent = amount * factor
            
            # Handle negative emissions (carbon savings from recycling)
            impact_type = "saves" if co2_equivalent < 0 else "emits"
            abs_co2 = abs(co2_equivalent)
            
            details = f"{activity}: {amount} {unit} × {factor} kg CO₂e/{unit} = {impact_type} {abs_co2} kg CO₂e"
            
            return co2_equivalent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), details
            
        except Exception as e:
            logger.error(f"Waste calculation error: {e}")
            return Decimal("0.5"), "Error in calculation, using fallback: 0.5 kg CO₂e"
    
    def calculate_emission(self, category: str, activity: str, amount: float, unit: str) -> Dict[str, any]:
        """
        Main calculation method - routes to appropriate category calculator
        
        Args:
            category: Emission category ("transportation", "energy", "food", "waste")
            activity: Specific activity within category
            amount: Amount of activity
            unit: Unit of measurement
            
        Returns:
            Dict with co2_equivalent, calculation_details, emission_factor
        """
        try:
            amount_decimal = Decimal(str(amount))
            
            if category.lower() == "transportation":
                co2_equivalent, details = self.calculate_transportation(activity, amount_decimal, unit)
            elif category.lower() == "energy":
                co2_equivalent, details = self.calculate_energy(activity, amount_decimal, unit)
            elif category.lower() == "food":
                co2_equivalent, details = self.calculate_food(activity, amount_decimal, unit)
            elif category.lower() == "waste":
                co2_equivalent, details = self.calculate_waste(activity, amount_decimal, unit)
            else:
                logger.warning(f"Unknown category: {category}")
                co2_equivalent = amount_decimal * Decimal("0.5")  # Generic fallback
                details = f"Unknown category {category}, using generic factor: 0.5 kg CO₂e per unit"
            
            return {
                "co2_equivalent": float(co2_equivalent),
                "calculation_details": details,
                "emission_factor": float(co2_equivalent / amount_decimal) if amount_decimal != 0 else 0.0,
                "region": self.region.value
            }
            
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return {
                "co2_equivalent": 1.0,
                "calculation_details": f"Calculation error: {str(e)}",
                "emission_factor": 1.0,
                "region": self.region.value
            }


# Global calculator instance
calculator = CarbonCalculator(region=Region.US_AVERAGE)


def calculate_carbon_footprint(category: str, activity: str, amount: float, unit: str, region: str = "us_average") -> Dict[str, any]:
    """
    Convenience function for calculating carbon footprint
    
    Args:
        category: Emission category
        activity: Specific activity
        amount: Amount of activity
        unit: Unit of measurement
        region: Regional variation (optional)
    
    Returns:
        Dictionary with calculation results
    """
    # Create calculator with specified region if different from default
    if region != "us_average":
        try:
            region_enum = Region(region)
            calc = CarbonCalculator(region=region_enum)
        except ValueError:
            logger.warning(f"Unknown region {region}, using default US average")
            calc = calculator
    else:
        calc = calculator
    
    return calc.calculate_emission(category, activity, amount, unit)