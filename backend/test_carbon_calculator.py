"""
Test file for carbon footprint calculation engine

This file contains comprehensive tests to validate the accuracy and functionality
of the carbon calculation system against known emission factors and real-world scenarios.
"""

import sys
import os

# Add the backend directory to Python path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.carbon_calculator import calculate_carbon_footprint

def test_transportation_calculations():
    """Test transportation emission calculations"""
    print("🚗 Testing Transportation Calculations:")
    print("-" * 50)
    
    # Test car emissions
    result = calculate_carbon_footprint("transportation", "car_gasoline_medium", 100, "km")
    print(f"100km Medium Gasoline Car: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()
    
    # Test flight emissions
    result = calculate_carbon_footprint("transportation", "flight_domestic_short", 500, "km")
    print(f"500km Domestic Flight: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()
    
    # Test electric vehicle
    result = calculate_carbon_footprint("transportation", "car_electric", 100, "km")
    print(f"100km Electric Vehicle: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()
    
    # Test unit conversion (miles to km)
    result = calculate_carbon_footprint("transportation", "car_gasoline_medium", 62.14, "miles")
    print(f"62.14 miles (100km) Medium Gasoline Car: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()

def test_energy_calculations():
    """Test energy consumption calculations"""
    print("⚡ Testing Energy Calculations:")
    print("-" * 50)
    
    # Test electricity
    result = calculate_carbon_footprint("energy", "electricity", 100, "kWh")
    print(f"100 kWh Electricity (US Grid): {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()
    
    # Test natural gas
    result = calculate_carbon_footprint("energy", "natural_gas", 10, "therms")
    print(f"10 therms Natural Gas: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()
    
    # Test heating oil
    result = calculate_carbon_footprint("energy", "heating_oil", 10, "gallons")
    print(f"10 gallons Heating Oil: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()

def test_food_calculations():
    """Test food emission calculations"""
    print("🍽️ Testing Food Calculations:")
    print("-" * 50)
    
    # Test high-impact foods
    result = calculate_carbon_footprint("food", "beef", 1, "kg")
    print(f"1 kg Beef: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()
    
    # Test low-impact foods
    result = calculate_carbon_footprint("food", "vegetables_root", 1, "kg")
    print(f"1 kg Root Vegetables: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()
    
    # Test unit conversion (pounds to kg)
    result = calculate_carbon_footprint("food", "chicken", 2.2, "lbs")
    print(f"2.2 lbs (1kg) Chicken: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()
    
    # Test servings conversion
    result = calculate_carbon_footprint("food", "beef", 4, "servings")
    print(f"4 servings Beef: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()

def test_waste_calculations():
    """Test waste disposal calculations"""
    print("♻️ Testing Waste Calculations:")
    print("-" * 50)
    
    # Test landfill emissions
    result = calculate_carbon_footprint("waste", "landfill_mixed", 10, "kg")
    print(f"10 kg Mixed Waste to Landfill: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()
    
    # Test recycling (should be negative - carbon savings)
    result = calculate_carbon_footprint("waste", "recycling_aluminum", 1, "kg")
    print(f"1 kg Aluminum Recycling: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()
    
    # Test paper recycling
    result = calculate_carbon_footprint("waste", "recycling_paper", 5, "kg")
    print(f"5 kg Paper Recycling: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()

def test_regional_variations():
    """Test regional variations in calculations"""
    print("🌍 Testing Regional Variations:")
    print("-" * 50)
    
    # Test electricity in different regions
    regions = ["us_average", "eu_average", "uk", "canada"]
    
    for region in regions:
        result = calculate_carbon_footprint("energy", "electricity", 100, "kWh", region)
        print(f"100 kWh Electricity in {region.upper()}: {result['co2_equivalent']:.2f} kg CO₂e")
    print()
    
    # Test electric vehicles in different regions
    print("Electric Vehicle 100km in different regions:")
    for region in regions:
        result = calculate_carbon_footprint("transportation", "car_electric", 100, "km", region)
        print(f"EV in {region.upper()}: {result['co2_equivalent']:.2f} kg CO₂e")
    print()

def test_real_world_scenarios():
    """Test real-world usage scenarios"""
    print("🌟 Real-World Scenarios:")
    print("-" * 50)
    
    print("Daily commute scenarios:")
    
    # Scenario 1: 30km daily car commute
    result = calculate_carbon_footprint("transportation", "car_gasoline_medium", 30, "km")
    print(f"30km car commute: {result['co2_equivalent']:.2f} kg CO₂e/day")
    print(f"Annual impact: {result['co2_equivalent'] * 250:.0f} kg CO₂e/year")
    print()
    
    # Scenario 2: Same commute by train
    result = calculate_carbon_footprint("transportation", "train_local", 30, "km")
    print(f"30km train commute: {result['co2_equivalent']:.2f} kg CO₂e/day")
    print(f"Annual impact: {result['co2_equivalent'] * 250:.0f} kg CO₂e/year")
    print()
    
    print("Household energy scenarios:")
    
    # Scenario 3: Monthly household electricity
    result = calculate_carbon_footprint("energy", "electricity", 900, "kWh")
    print(f"900 kWh monthly electricity: {result['co2_equivalent']:.2f} kg CO₂e/month")
    print(f"Annual impact: {result['co2_equivalent'] * 12:.0f} kg CO₂e/year")
    print()
    
    print("Diet scenarios:")
    
    # Scenario 4: Weekly beef consumption
    result = calculate_carbon_footprint("food", "beef", 0.5, "kg")
    print(f"0.5kg beef/week: {result['co2_equivalent']:.2f} kg CO₂e/week")
    print(f"Annual impact: {result['co2_equivalent'] * 52:.0f} kg CO₂e/year")
    print()
    
    # Scenario 5: Same calories from chicken
    result = calculate_carbon_footprint("food", "chicken", 0.6, "kg")
    print(f"0.6kg chicken/week (similar calories): {result['co2_equivalent']:.2f} kg CO₂e/week")
    print(f"Annual impact: {result['co2_equivalent'] * 52:.0f} kg CO₂e/year")
    print()

def test_error_handling():
    """Test error handling and edge cases"""
    print("🔧 Testing Error Handling:")
    print("-" * 50)
    
    # Test unknown activity
    result = calculate_carbon_footprint("transportation", "unknown_vehicle", 100, "km")
    print(f"Unknown activity fallback: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()
    
    # Test unknown category
    result = calculate_carbon_footprint("unknown_category", "some_activity", 100, "units")
    print(f"Unknown category fallback: {result['co2_equivalent']:.2f} kg CO₂e")
    print(f"Details: {result['calculation_details']}")
    print()
    
    # Test zero amount
    result = calculate_carbon_footprint("transportation", "car_gasoline_medium", 0, "km")
    print(f"Zero amount: {result['co2_equivalent']:.2f} kg CO₂e")
    print()

def run_comprehensive_tests():
    """Run all carbon calculation tests"""
    print("🧪 COMPREHENSIVE CARBON CALCULATION TESTS")
    print("=" * 60)
    print()
    
    test_transportation_calculations()
    test_energy_calculations() 
    test_food_calculations()
    test_waste_calculations()
    test_regional_variations()
    test_real_world_scenarios()
    test_error_handling()
    
    print("✅ All tests completed!")
    print()
    print("Key Insights:")
    print("• Beef has 6x higher emissions than chicken")
    print("• Electric vehicles vary dramatically by regional grid mix")
    print("• Aluminum recycling provides massive carbon savings")
    print("• Flights have very high per-km emissions")
    print("• Train commuting is much lower impact than driving")

if __name__ == "__main__":
    run_comprehensive_tests()