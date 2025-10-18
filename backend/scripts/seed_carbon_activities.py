#!/usr/bin/env python3
"""
Carbon Activities Database Seed Script
=====================================

This script populates the DynamoDB with comprehensive carbon emission factors 
and activities for the CarbonTrack application.

Data sources:
- EPA emission factors
- DEFRA carbon factors  
- IPCC guidelines
- Scientific carbon footprint databases

Usage:
    python scripts/seed_carbon_activities.py
"""

import boto3
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Any

# DynamoDB configuration
TABLE_NAME = "carbontrack-activities"
REGION = "eu-central-1"

def get_dynamodb_client():
    """Get DynamoDB client"""
    try:
        # Try local DynamoDB first
        return boto3.client(
            'dynamodb',
            endpoint_url='http://localhost:8000',
            region_name=REGION,
            aws_access_key_id='fake',
            aws_secret_access_key='fake'
        )
    except Exception:
        # Fall back to AWS DynamoDB
        return boto3.client('dynamodb', region_name=REGION)

def create_activities_table(dynamodb):
    """Create the carbon activities table if it doesn't exist"""
    try:
        table_definition = {
            'TableName': TABLE_NAME,
            'KeySchema': [
                {
                    'AttributeName': 'activity_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            'AttributeDefinitions': [
                {
                    'AttributeName': 'activity_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'category',
                    'AttributeType': 'S'
                }
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'CategoryIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'category',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
        
        dynamodb.create_table(**table_definition)
        print(f"✅ Created table: {TABLE_NAME}")
        
        # Wait for table to be created
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=TABLE_NAME)
        print(f"✅ Table {TABLE_NAME} is now active")
        
    except dynamodb.exceptions.ResourceInUseException:
        print(f"ℹ️  Table {TABLE_NAME} already exists")
    except Exception as e:
        print(f"❌ Error creating table: {e}")

def get_carbon_activities_data() -> List[Dict[str, Any]]:
    """
    Comprehensive carbon activities database with emission factors
    Based on EPA, DEFRA, and IPCC data sources
    """
    return [
        # TRANSPORTATION ACTIVITIES
        {
            "activity_id": "trans_car_gasoline_small",
            "category": "transportation", 
            "name": "Car - Gasoline (Small)",
            "emission_factor": Decimal("0.192"),  # kg CO2 per km
            "unit": "km",
            "description": "Small gasoline car (e.g., Toyota Corolla, Honda Civic)",
            "source": "EPA 2023",
            "subcategory": "personal_vehicle"
        },
        {
            "activity_id": "trans_car_gasoline_medium", 
            "category": "transportation",
            "name": "Car - Gasoline (Medium)",
            "emission_factor": Decimal("0.251"), # kg CO2 per km
            "unit": "km", 
            "description": "Medium gasoline car (e.g., Toyota Camry, Honda Accord)",
            "source": "EPA 2023",
            "subcategory": "personal_vehicle"
        },
        {
            "activity_id": "trans_car_gasoline_large",
            "category": "transportation",
            "name": "Car - Gasoline (Large/SUV)", 
            "emission_factor": Decimal("0.342"), # kg CO2 per km
            "unit": "km",
            "description": "Large gasoline car or SUV (e.g., Ford F-150, Toyota Highlander)",
            "source": "EPA 2023", 
            "subcategory": "personal_vehicle"
        },
        {
            "activity_id": "trans_car_electric",
            "category": "transportation",
            "name": "Electric Vehicle",
            "emission_factor": Decimal("0.089"), # kg CO2 per km (avg US grid)
            "unit": "km",
            "description": "Electric vehicle (varies by local electricity grid)",
            "source": "EPA 2023",
            "subcategory": "personal_vehicle"
        },
        {
            "activity_id": "trans_car_hybrid",
            "category": "transportation", 
            "name": "Hybrid Vehicle",
            "emission_factor": Decimal("0.104"), # kg CO2 per km
            "unit": "km",
            "description": "Hybrid gasoline-electric vehicle (e.g., Toyota Prius)",
            "source": "EPA 2023",
            "subcategory": "personal_vehicle"
        },
        {
            "activity_id": "trans_motorcycle",
            "category": "transportation",
            "name": "Motorcycle", 
            "emission_factor": Decimal("0.103"), # kg CO2 per km
            "unit": "km",
            "description": "Average motorcycle or scooter",
            "source": "DEFRA 2023",
            "subcategory": "personal_vehicle"
        },
        {
            "activity_id": "trans_bus_city",
            "category": "transportation",
            "name": "City Bus",
            "emission_factor": Decimal("0.089"), # kg CO2 per km per passenger
            "unit": "km", 
            "description": "Urban public bus (per passenger)",
            "source": "DEFRA 2023",
            "subcategory": "public_transport"
        },
        {
            "activity_id": "trans_train_local",
            "category": "transportation",
            "name": "Local Train/Subway",
            "emission_factor": Decimal("0.041"), # kg CO2 per km per passenger
            "unit": "km",
            "description": "Urban rail, subway, or light rail (per passenger)", 
            "source": "DEFRA 2023",
            "subcategory": "public_transport"
        },
        {
            "activity_id": "trans_train_intercity",
            "category": "transportation", 
            "name": "Intercity Train",
            "emission_factor": Decimal("0.035"), # kg CO2 per km per passenger
            "unit": "km",
            "description": "Long-distance passenger train (per passenger)",
            "source": "DEFRA 2023",
            "subcategory": "public_transport"
        },
        {
            "activity_id": "trans_flight_domestic_short",
            "category": "transportation",
            "name": "Flight - Domestic Short (<500km)",
            "emission_factor": Decimal("0.255"), # kg CO2 per km per passenger
            "unit": "km",
            "description": "Domestic flight under 500km (per passenger)",
            "source": "DEFRA 2023", 
            "subcategory": "aviation"
        },
        {
            "activity_id": "trans_flight_domestic_long", 
            "category": "transportation",
            "name": "Flight - Domestic Long (>500km)",
            "emission_factor": Decimal("0.156"), # kg CO2 per km per passenger
            "unit": "km",
            "description": "Domestic flight over 500km (per passenger)",
            "source": "DEFRA 2023",
            "subcategory": "aviation"
        },
        {
            "activity_id": "trans_flight_international",
            "category": "transportation",
            "name": "Flight - International",
            "emission_factor": Decimal("0.195"), # kg CO2 per km per passenger  
            "unit": "km",
            "description": "International flight (per passenger)",
            "source": "DEFRA 2023",
            "subcategory": "aviation"
        },

        # ENERGY ACTIVITIES
        {
            "activity_id": "energy_electricity_us_avg",
            "category": "energy",
            "name": "Electricity - US Average",
            "emission_factor": Decimal("0.401"), # kg CO2 per kWh
            "unit": "kWh",
            "description": "US average electricity grid mix",
            "source": "EPA eGRID 2023",
            "subcategory": "electricity"
        },
        {
            "activity_id": "energy_electricity_coal",
            "category": "energy", 
            "name": "Electricity - Coal Dominated",
            "emission_factor": Decimal("0.820"), # kg CO2 per kWh
            "unit": "kWh",
            "description": "Electricity from coal-dominated grid",
            "source": "IPCC 2014",
            "subcategory": "electricity"
        },
        {
            "activity_id": "energy_electricity_natural_gas",
            "category": "energy",
            "name": "Electricity - Natural Gas",
            "emission_factor": Decimal("0.490"), # kg CO2 per kWh
            "unit": "kWh", 
            "description": "Electricity from natural gas power plants",
            "source": "IPCC 2014",
            "subcategory": "electricity"
        },
        {
            "activity_id": "energy_electricity_renewable",
            "category": "energy",
            "name": "Electricity - Renewable",
            "emission_factor": Decimal("0.024"), # kg CO2 per kWh
            "unit": "kWh",
            "description": "Electricity from renewable sources (wind, solar, hydro)",
            "source": "IPCC 2014", 
            "subcategory": "electricity"
        },
        {
            "activity_id": "energy_natural_gas_heating",
            "category": "energy",
            "name": "Natural Gas - Home Heating",
            "emission_factor": Decimal("5.3"), # kg CO2 per therm
            "unit": "therms",
            "description": "Natural gas for home heating and hot water",
            "source": "EPA 2023",
            "subcategory": "heating_fuel"
        },
        {
            "activity_id": "energy_heating_oil",
            "category": "energy",
            "name": "Heating Oil",
            "emission_factor": Decimal("10.15"), # kg CO2 per gallon
            "unit": "gallons",
            "description": "Home heating oil",
            "source": "EPA 2023", 
            "subcategory": "heating_fuel"
        },
        {
            "activity_id": "energy_propane", 
            "category": "energy",
            "name": "Propane",
            "emission_factor": Decimal("5.68"), # kg CO2 per gallon
            "unit": "gallons", 
            "description": "Propane for heating, cooking, or hot water",
            "source": "EPA 2023",
            "subcategory": "heating_fuel"
        },

        # FOOD ACTIVITIES  
        {
            "activity_id": "food_beef",
            "category": "food",
            "name": "Beef",
            "emission_factor": Decimal("60.0"), # kg CO2 per kg
            "unit": "kg",
            "description": "Fresh beef (average global production)",
            "source": "Poore & Nemecek 2018",
            "subcategory": "meat"
        },
        {
            "activity_id": "food_lamb",
            "category": "food", 
            "name": "Lamb",
            "emission_factor": Decimal("24.5"), # kg CO2 per kg
            "unit": "kg",
            "description": "Fresh lamb meat",
            "source": "Poore & Nemecek 2018",
            "subcategory": "meat"
        },
        {
            "activity_id": "food_pork",
            "category": "food",
            "name": "Pork", 
            "emission_factor": Decimal("7.6"), # kg CO2 per kg
            "unit": "kg",
            "description": "Fresh pork meat",
            "source": "Poore & Nemecek 2018", 
            "subcategory": "meat"
        },
        {
            "activity_id": "food_chicken",
            "category": "food",
            "name": "Chicken",
            "emission_factor": Decimal("9.9"), # kg CO2 per kg  
            "unit": "kg",
            "description": "Fresh chicken meat",
            "source": "Poore & Nemecek 2018",
            "subcategory": "meat"
        },
        {
            "activity_id": "food_fish_farmed",
            "category": "food",
            "name": "Fish - Farmed",
            "emission_factor": Decimal("13.6"), # kg CO2 per kg
            "unit": "kg",
            "description": "Farmed fish (average)",
            "source": "Poore & Nemecek 2018",
            "subcategory": "seafood"
        },
        {
            "activity_id": "food_fish_wild", 
            "category": "food",
            "name": "Fish - Wild Caught",
            "emission_factor": Decimal("1.9"), # kg CO2 per kg
            "unit": "kg",
            "description": "Wild-caught fish (average)",
            "source": "Poore & Nemecek 2018",
            "subcategory": "seafood"
        },
        {
            "activity_id": "food_milk",
            "category": "food",
            "name": "Milk", 
            "emission_factor": Decimal("3.2"), # kg CO2 per liter
            "unit": "liters",
            "description": "Fresh dairy milk",
            "source": "Poore & Nemecek 2018",
            "subcategory": "dairy"
        },
        {
            "activity_id": "food_cheese",
            "category": "food",
            "name": "Cheese",
            "emission_factor": Decimal("23.9"), # kg CO2 per kg
            "unit": "kg", 
            "description": "Hard cheese (average)",
            "source": "Poore & Nemecek 2018",
            "subcategory": "dairy"
        },
        {
            "activity_id": "food_eggs",
            "category": "food", 
            "name": "Eggs",
            "emission_factor": Decimal("4.7"), # kg CO2 per kg
            "unit": "kg",
            "description": "Chicken eggs",
            "source": "Poore & Nemecek 2018",
            "subcategory": "dairy"
        },
        {
            "activity_id": "food_rice",
            "category": "food",
            "name": "Rice",
            "emission_factor": Decimal("4.5"), # kg CO2 per kg
            "unit": "kg", 
            "description": "Rice (global average)",
            "source": "Poore & Nemecek 2018",
            "subcategory": "grains"
        },
        {
            "activity_id": "food_wheat_bread",
            "category": "food",
            "name": "Bread (Wheat)",
            "emission_factor": Decimal("1.6"), # kg CO2 per kg
            "unit": "kg",
            "description": "Wheat bread",
            "source": "Poore & Nemecek 2018",
            "subcategory": "grains"
        },
        {
            "activity_id": "food_vegetables_root",
            "category": "food",
            "name": "Root Vegetables", 
            "emission_factor": Decimal("0.43"), # kg CO2 per kg
            "unit": "kg",
            "description": "Root vegetables (potatoes, carrots, etc.)",
            "source": "Poore & Nemecek 2018",
            "subcategory": "vegetables"
        },
        {
            "activity_id": "food_vegetables_other",
            "category": "food",
            "name": "Other Vegetables",
            "emission_factor": Decimal("2.1"), # kg CO2 per kg
            "unit": "kg",
            "description": "Other vegetables (tomatoes, peppers, etc.)",
            "source": "Poore & Nemecek 2018", 
            "subcategory": "vegetables"
        },
        {
            "activity_id": "food_fruits",
            "category": "food",
            "name": "Fruits",
            "emission_factor": Decimal("1.1"), # kg CO2 per kg
            "unit": "kg", 
            "description": "Fresh fruits (average)",
            "source": "Poore & Nemecek 2018",
            "subcategory": "fruits"
        },
        {
            "activity_id": "food_nuts",
            "category": "food",
            "name": "Nuts",
            "emission_factor": Decimal("0.26"), # kg CO2 per kg
            "unit": "kg",
            "description": "Tree nuts (average)",
            "source": "Poore & Nemecek 2018",
            "subcategory": "proteins"
        },

        # WASTE ACTIVITIES
        {
            "activity_id": "waste_landfill_mixed",
            "category": "waste",
            "name": "Landfill - Mixed Waste", 
            "emission_factor": Decimal("0.57"), # kg CO2 per kg
            "unit": "kg",
            "description": "Mixed household waste to landfill",
            "source": "EPA WARM 2020",
            "subcategory": "disposal"
        },
        {
            "activity_id": "waste_incineration",
            "category": "waste",
            "name": "Incineration",
            "emission_factor": Decimal("0.037"), # kg CO2 per kg
            "unit": "kg",
            "description": "Waste incineration with energy recovery",
            "source": "EPA WARM 2020", 
            "subcategory": "disposal"
        },
        {
            "activity_id": "waste_recycling_paper",
            "category": "waste", 
            "name": "Recycling - Paper",
            "emission_factor": Decimal("-0.89"), # kg CO2 per kg (negative = savings)
            "unit": "kg",
            "description": "Paper and cardboard recycling (carbon savings)",
            "source": "EPA WARM 2020",
            "subcategory": "recycling"
        },
        {
            "activity_id": "waste_recycling_aluminum",
            "category": "waste",
            "name": "Recycling - Aluminum",
            "emission_factor": Decimal("-8.94"), # kg CO2 per kg (negative = savings)
            "unit": "kg", 
            "description": "Aluminum can recycling (carbon savings)",
            "source": "EPA WARM 2020",
            "subcategory": "recycling"
        },
        {
            "activity_id": "waste_recycling_plastic",
            "category": "waste",
            "name": "Recycling - Plastic",
            "emission_factor": Decimal("-1.36"), # kg CO2 per kg (negative = savings)
            "unit": "kg",
            "description": "Plastic bottle recycling (carbon savings)",
            "source": "EPA WARM 2020",
            "subcategory": "recycling" 
        },
        {
            "activity_id": "waste_composting_food",
            "category": "waste",
            "name": "Composting - Food Waste",
            "emission_factor": Decimal("-0.26"), # kg CO2 per kg (negative = savings)
            "unit": "kg",
            "description": "Food waste composting (carbon savings)",
            "source": "EPA WARM 2020",
            "subcategory": "composting"
        },
        {
            "activity_id": "waste_composting_yard",
            "category": "waste", 
            "name": "Composting - Yard Waste",
            "emission_factor": Decimal("-0.15"), # kg CO2 per kg (negative = savings)
            "unit": "kg",
            "description": "Yard waste composting (carbon savings)",
            "source": "EPA WARM 2020",
            "subcategory": "composting"
        }
    ]

def convert_to_dynamodb_item(activity: Dict[str, Any]) -> Dict[str, Any]:
    """Convert activity dict to DynamoDB item format"""
    item = {}
    for key, value in activity.items():
        if isinstance(value, str):
            item[key] = {'S': value}
        elif isinstance(value, Decimal):
            item[key] = {'N': str(value)}
        elif isinstance(value, (int, float)):
            item[key] = {'N': str(value)}
        elif isinstance(value, bool):
            item[key] = {'BOOL': value}
        else:
            item[key] = {'S': str(value)}
    
    # Add metadata
    item['created_at'] = {'S': datetime.utcnow().isoformat()}
    item['updated_at'] = {'S': datetime.utcnow().isoformat()}
    item['is_active'] = {'BOOL': True}
    
    return item

def seed_activities(dynamodb):
    """Seed the database with carbon activities"""
    activities = get_carbon_activities_data()
    
    print(f"🌱 Seeding {len(activities)} carbon activities...")
    
    success_count = 0
    error_count = 0
    
    for activity in activities:
        try:
            item = convert_to_dynamodb_item(activity)
            
            dynamodb.put_item(
                TableName=TABLE_NAME,
                Item=item,
                ConditionExpression='attribute_not_exists(activity_id)'  # Don't overwrite
            )
            
            success_count += 1
            print(f"✅ Added: {activity['name']} ({activity['category']})")
            
        except dynamodb.exceptions.ConditionalCheckFailedException:
            print(f"ℹ️  Skipped (already exists): {activity['name']}")
        except Exception as e:
            error_count += 1
            print(f"❌ Error adding {activity['name']}: {e}")
    
    print("\n📊 Seeding complete:")
    print(f"   ✅ Success: {success_count} activities")
    print(f"   ❌ Errors: {error_count} activities")
    print(f"   📝 Total: {len(activities)} activities processed")

def main():
    """Main function"""
    print("🌍 CarbonTrack Database Seeding")
    print("=" * 50)
    
    try:
        dynamodb = get_dynamodb_client()
        print("📡 Connected to DynamoDB")
        
        # Create table
        create_activities_table(dynamodb)
        
        # Seed activities
        seed_activities(dynamodb)
        
        print("\n🎉 Database seeding completed successfully!")
        print("\nNext steps:")
        print("1. Test the backend API endpoints")
        print("2. Update frontend to use real database")
        print("3. Remove static data fallbacks")
        
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())