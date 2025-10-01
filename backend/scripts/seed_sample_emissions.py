#!/usr/bin/env python3
"""
Sample Emissions Data Migration Script
=====================================

This script creates sample user emissions data in DynamoDB based on the 
static data currently in the frontend JavaScript files.

This provides initial data for demo users and testing.

Usage:
    python scripts/seed_sample_emissions.py
"""

import boto3
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Any
import uuid

# DynamoDB configuration
EMISSIONS_TABLE = "carbontrack-emissions"
USERS_TABLE = "carbontrack-users" 
REGION = "us-east-1"

# Demo user IDs
DEMO_USER_ID = "demo-user"
ADMIN_USER_ID = "admin-user"

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

def create_emissions_table(dynamodb):
    """Create the emissions table if it doesn't exist"""
    try:
        table_definition = {
            'TableName': EMISSIONS_TABLE,
            'KeySchema': [
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'entry_id', 
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            'AttributeDefinitions': [
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'entry_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'emission_date',
                    'AttributeType': 'S'
                }
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'UserDateIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'emission_date',
                            'KeyType': 'RANGE'
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
        print(f"✅ Created table: {EMISSIONS_TABLE}")
        
        # Wait for table to be created
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=EMISSIONS_TABLE)
        print(f"✅ Table {EMISSIONS_TABLE} is now active")
        
    except dynamodb.exceptions.ResourceInUseException:
        print(f"ℹ️  Table {EMISSIONS_TABLE} already exists")
    except Exception as e:
        print(f"❌ Error creating table: {e}")

def get_demo_emissions_data() -> List[Dict[str, Any]]:
    """
    Demo emissions data from frontend JavaScript (loadDemoEmissions method)
    """
    return [
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'transportation',
            'activity': 'trans_flight_international',
            'activity_name': 'Flight to London',
            'amount': Decimal('150.5'),
            'unit': 'kg',
            'emission_date': '2025-09-25',
            'description': 'Business trip to London',
            'co2_equivalent': Decimal('150.5')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'transportation', 
            'activity': 'trans_car_gasoline_medium',
            'activity_name': 'Car commute',
            'amount': Decimal('25.4'),
            'unit': 'kg',
            'emission_date': '2025-09-24',
            'description': 'Daily commute to office',
            'co2_equivalent': Decimal('25.4')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'energy',
            'activity': 'energy_electricity_us_avg',
            'activity_name': 'Home electricity',
            'amount': Decimal('45.2'),
            'unit': 'kg', 
            'emission_date': '2025-09-23',
            'description': 'Monthly electricity bill',
            'co2_equivalent': Decimal('45.2')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'food',
            'activity': 'food_beef',
            'activity_name': 'Restaurant dining',
            'amount': Decimal('12.1'),
            'unit': 'kg',
            'emission_date': '2025-09-22', 
            'description': 'Dinner at steakhouse',
            'co2_equivalent': Decimal('12.1')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'transportation',
            'activity': 'trans_car_gasoline_small',
            'activity_name': 'Uber rides',
            'amount': Decimal('8.7'),
            'unit': 'kg',
            'emission_date': '2025-09-21',
            'description': 'City transportation', 
            'co2_equivalent': Decimal('8.7')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'energy',
            'activity': 'energy_electricity_us_avg', 
            'activity_name': 'Office electricity',
            'amount': Decimal('23.8'),
            'unit': 'kg',
            'emission_date': '2025-09-20',
            'description': 'Workspace energy consumption',
            'co2_equivalent': Decimal('23.8')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'food',
            'activity': 'food_vegetables_other',
            'activity_name': 'Grocery shopping',
            'amount': Decimal('15.2'),
            'unit': 'kg',
            'emission_date': '2025-09-19',
            'description': 'Weekly groceries',
            'co2_equivalent': Decimal('15.2')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'waste',
            'activity': 'waste_recycling_paper',
            'activity_name': 'Recycling credit',
            'amount': Decimal('-2.1'),
            'unit': 'kg',
            'emission_date': '2025-09-18',
            'description': 'Paper and plastic recycling',
            'co2_equivalent': Decimal('-2.1')
        }
    ]

def get_sample_emissions_data() -> List[Dict[str, Any]]:
    """
    Sample emissions data from frontend JavaScript (createSampleData method)
    """
    return [
        # Transportation - using real activity names and accurate calculations
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'transportation',
            'activity': 'trans_car_gasoline_medium',
            'activity_name': 'Car drive downtown',
            'amount': Decimal('25'),
            'unit': 'km',
            'emission_date': '2025-09-20',
            'description': 'Drive to downtown for meeting',
            'co2_equivalent': Decimal('4.8')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'transportation',
            'activity': 'trans_flight_domestic_short',
            'activity_name': 'Business flight',
            'amount': Decimal('320'),
            'unit': 'km',
            'emission_date': '2025-09-18',
            'description': 'Business trip to nearby city',
            'co2_equivalent': Decimal('81.6')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'transportation',
            'activity': 'trans_train_local',
            'activity_name': 'Train commute',
            'amount': Decimal('45'),
            'unit': 'km',
            'emission_date': '2025-09-17',
            'description': 'Train commute to office',
            'co2_equivalent': Decimal('1.85')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'transportation',
            'activity': 'trans_bus_city',
            'activity_name': 'Bus ride',
            'amount': Decimal('12'),
            'unit': 'km',
            'emission_date': '2025-09-16',
            'description': 'Bus to shopping center',
            'co2_equivalent': Decimal('1.07')
        },
        # Energy - with realistic consumption patterns
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'energy',
            'activity': 'energy_electricity_us_avg',
            'activity_name': 'Monthly electricity',
            'amount': Decimal('450'),
            'unit': 'kWh',
            'emission_date': '2025-09-15',
            'description': 'Monthly home electricity bill',
            'co2_equivalent': Decimal('180.45')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'energy',
            'activity': 'energy_natural_gas_heating',
            'activity_name': 'Home heating',
            'amount': Decimal('8'),
            'unit': 'therms',
            'emission_date': '2025-09-14',
            'description': 'Home heating and hot water',
            'co2_equivalent': Decimal('42.4')
        },
        # Food - with different impact levels
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'food',
            'activity': 'food_beef',
            'activity_name': 'Beef meal',
            'amount': Decimal('0.3'),
            'unit': 'kg',
            'emission_date': '2025-09-13',
            'description': 'Beef burger for lunch',
            'co2_equivalent': Decimal('18.0')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'food',
            'activity': 'food_chicken',
            'activity_name': 'Chicken dinner',
            'amount': Decimal('0.5'),
            'unit': 'kg',
            'emission_date': '2025-09-12',
            'description': 'Chicken dinner',
            'co2_equivalent': Decimal('4.95')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'food',
            'activity': 'food_vegetables_root',
            'activity_name': 'Vegetables',
            'amount': Decimal('2'),
            'unit': 'kg',
            'emission_date': '2025-09-11',
            'description': 'Weekly vegetable shopping',
            'co2_equivalent': Decimal('0.86')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'food',
            'activity': 'food_milk',
            'activity_name': 'Milk purchase',
            'amount': Decimal('2'),
            'unit': 'liters',
            'emission_date': '2025-09-10',
            'description': 'Weekly milk purchase',
            'co2_equivalent': Decimal('6.4')
        },
        # Waste - showing both emissions and savings
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'waste',
            'activity': 'waste_recycling_aluminum',
            'activity_name': 'Aluminum recycling',
            'amount': Decimal('0.5'),
            'unit': 'kg',
            'emission_date': '2025-09-09',
            'description': 'Aluminum cans recycling',
            'co2_equivalent': Decimal('-4.47')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'waste',
            'activity': 'waste_recycling_paper',
            'activity_name': 'Paper recycling',
            'amount': Decimal('3'),
            'unit': 'kg',
            'emission_date': '2025-09-08',
            'description': 'Weekly paper recycling',
            'co2_equivalent': Decimal('-2.67')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'waste',
            'activity': 'waste_landfill_mixed',
            'activity_name': 'Household waste',
            'amount': Decimal('5'),
            'unit': 'kg',
            'emission_date': '2025-09-07',
            'description': 'General household waste',
            'co2_equivalent': Decimal('2.85')
        },
        {
            'user_id': DEMO_USER_ID,
            'entry_id': str(uuid.uuid4()),
            'category': 'waste',
            'activity': 'waste_composting_food',
            'activity_name': 'Food composting',
            'amount': Decimal('2'),
            'unit': 'kg',
            'emission_date': '2025-09-06',
            'description': 'Food waste composting',
            'co2_equivalent': Decimal('-0.52')
        }
    ]

def convert_emission_to_dynamodb_item(emission: Dict[str, Any]) -> Dict[str, Any]:
    """Convert emission dict to DynamoDB item format"""
    item = {}
    for key, value in emission.items():
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
    
    return item

def seed_emissions(dynamodb):
    """Seed the database with sample emissions"""
    
    # Get both demo and sample data
    demo_emissions = get_demo_emissions_data()
    sample_emissions = get_sample_emissions_data()
    
    all_emissions = demo_emissions + sample_emissions
    
    print(f"🌱 Seeding {len(all_emissions)} sample emissions...")
    
    success_count = 0
    error_count = 0
    
    for emission in all_emissions:
        try:
            item = convert_emission_to_dynamodb_item(emission)
            
            dynamodb.put_item(
                TableName=EMISSIONS_TABLE,
                Item=item
            )
            
            success_count += 1
            print(f"✅ Added: {emission['activity_name']} ({emission['co2_equivalent']} kg CO2)")
            
        except Exception as e:
            error_count += 1
            print(f"❌ Error adding {emission['activity_name']}: {e}")
    
    print("\n📊 Seeding complete:")
    print(f"   ✅ Success: {success_count} emissions")
    print(f"   ❌ Errors: {error_count} emissions")
    print(f"   📝 Total: {len(all_emissions)} emissions processed")

def main():
    """Main function"""
    print("📊 CarbonTrack Sample Emissions Seeding")
    print("=" * 50)
    
    try:
        dynamodb = get_dynamodb_client()
        print("📡 Connected to DynamoDB")
        
        # Create table
        create_emissions_table(dynamodb)
        
        # Seed emissions
        seed_emissions(dynamodb)
        
        print("\n🎉 Sample emissions seeding completed successfully!")
        print("\nNext steps:")
        print("1. Test the emissions API endpoints")
        print("2. Verify data appears correctly in frontend")
        print("3. Update chart data to use real emissions")
        
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())