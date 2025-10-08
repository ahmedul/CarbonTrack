#!/usr/bin/env python3
"""
Seed script to populate the carbontrack-emission-factors DynamoDB table
with comprehensive emission factor data for carbon footprint calculations.
"""

import boto3
import sys
from decimal import Decimal

# AWS Configuration
REGION = 'eu-central-1'
TABLE_NAME = 'carbontrack-emission-factors'

def get_emission_factors_data():
    """
    Comprehensive emission factors database
    All values are in kg CO2 equivalent per unit
    Sources: EPA, IPCC, UK DEFRA, European Environment Agency
    """
    return [
        # TRANSPORTATION - Per kilometer
        {
            'category': 'transportation',
            'activity': 'car_petrol_small',
            'emission_factor': Decimal('0.14'),
            'unit': 'km',
            'description': 'Small petrol car (< 1.4L)',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'car_petrol_medium',
            'emission_factor': Decimal('0.19'),
            'unit': 'km',
            'description': 'Medium petrol car (1.4-2.0L)',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'car_petrol_large',
            'emission_factor': Decimal('0.28'),
            'unit': 'km',
            'description': 'Large petrol car (> 2.0L)',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'car_diesel_small',
            'emission_factor': Decimal('0.13'),
            'unit': 'km',
            'description': 'Small diesel car (< 1.7L)',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'car_diesel_medium',
            'emission_factor': Decimal('0.17'),
            'unit': 'km',
            'description': 'Medium diesel car (1.7-2.0L)',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'car_diesel_large',
            'emission_factor': Decimal('0.24'),
            'unit': 'km',
            'description': 'Large diesel car (> 2.0L)',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'car_hybrid',
            'emission_factor': Decimal('0.11'),
            'unit': 'km',
            'description': 'Hybrid car',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'car_electric',
            'emission_factor': Decimal('0.05'),
            'unit': 'km',
            'description': 'Electric car (grid average)',
            'source': 'IEA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'motorcycle',
            'emission_factor': Decimal('0.10'),
            'unit': 'km',
            'description': 'Motorcycle (average)',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'bus',
            'emission_factor': Decimal('0.089'),
            'unit': 'km',
            'description': 'Local bus per passenger',
            'source': 'EPA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'train_national',
            'emission_factor': Decimal('0.041'),
            'unit': 'km',
            'description': 'National rail per passenger',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'train_international',
            'emission_factor': Decimal('0.006'),
            'unit': 'km',
            'description': 'International rail (Eurostar)',
            'source': 'UK DEFRA 2023',
            'region': 'Europe'
        },
        {
            'category': 'transportation',
            'activity': 'flight_domestic',
            'emission_factor': Decimal('0.255'),
            'unit': 'km',
            'description': 'Domestic flight per passenger',
            'source': 'ICAO Carbon Calculator',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'flight_short_haul',
            'emission_factor': Decimal('0.156'),
            'unit': 'km',
            'description': 'Short-haul flight (< 3700 km)',
            'source': 'ICAO Carbon Calculator',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'flight_long_haul',
            'emission_factor': Decimal('0.195'),
            'unit': 'km',
            'description': 'Long-haul flight (> 3700 km)',
            'source': 'ICAO Carbon Calculator',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'ferry',
            'emission_factor': Decimal('0.115'),
            'unit': 'km',
            'description': 'Ferry per passenger',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'transportation',
            'activity': 'bicycle',
            'emission_factor': Decimal('0.00'),
            'unit': 'km',
            'description': 'Bicycle (zero emissions)',
            'source': 'N/A',
            'region': 'Global'
        },
        {
            'category': 'transportation',
            'activity': 'walking',
            'emission_factor': Decimal('0.00'),
            'unit': 'km',
            'description': 'Walking (zero emissions)',
            'source': 'N/A',
            'region': 'Global'
        },
        
        # ENERGY - Per kWh or unit
        {
            'category': 'energy',
            'activity': 'electricity',
            'emission_factor': Decimal('0.475'),
            'unit': 'kWh',
            'description': 'Grid electricity (global average)',
            'source': 'IEA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'energy',
            'activity': 'electricity_renewable',
            'emission_factor': Decimal('0.02'),
            'unit': 'kWh',
            'description': 'Renewable electricity',
            'source': 'IPCC',
            'region': 'Global'
        },
        {
            'category': 'energy',
            'activity': 'natural_gas',
            'emission_factor': Decimal('0.203'),
            'unit': 'kWh',
            'description': 'Natural gas heating',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'energy',
            'activity': 'heating_oil',
            'emission_factor': Decimal('2.96'),
            'unit': 'liter',
            'description': 'Heating oil',
            'source': 'EPA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'energy',
            'activity': 'lpg',
            'emission_factor': Decimal('1.51'),
            'unit': 'liter',
            'description': 'LPG (Liquefied Petroleum Gas)',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'energy',
            'activity': 'coal',
            'emission_factor': Decimal('2.45'),
            'unit': 'kg',
            'description': 'Coal for heating',
            'source': 'IPCC',
            'region': 'Global Average'
        },
        {
            'category': 'energy',
            'activity': 'wood_pellets',
            'emission_factor': Decimal('0.39'),
            'unit': 'kg',
            'description': 'Wood pellets (biomass)',
            'source': 'UK DEFRA 2023',
            'region': 'Europe'
        },
        
        # FOOD - Per kilogram
        {
            'category': 'food',
            'activity': 'beef',
            'emission_factor': Decimal('27.0'),
            'unit': 'kg',
            'description': 'Beef meat',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'lamb',
            'emission_factor': Decimal('39.2'),
            'unit': 'kg',
            'description': 'Lamb meat',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'pork',
            'emission_factor': Decimal('12.1'),
            'unit': 'kg',
            'description': 'Pork meat',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'chicken',
            'emission_factor': Decimal('6.9'),
            'unit': 'kg',
            'description': 'Chicken meat',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'fish_farmed',
            'emission_factor': Decimal('5.1'),
            'unit': 'kg',
            'description': 'Farmed fish',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'fish_wild',
            'emission_factor': Decimal('2.9'),
            'unit': 'kg',
            'description': 'Wild-caught fish',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'cheese',
            'emission_factor': Decimal('13.5'),
            'unit': 'kg',
            'description': 'Cheese (dairy)',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'milk',
            'emission_factor': Decimal('1.9'),
            'unit': 'liter',
            'description': 'Cow milk',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'eggs',
            'emission_factor': Decimal('4.8'),
            'unit': 'kg',
            'description': 'Eggs',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'rice',
            'emission_factor': Decimal('4.0'),
            'unit': 'kg',
            'description': 'Rice',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'pasta',
            'emission_factor': Decimal('1.4'),
            'unit': 'kg',
            'description': 'Pasta/wheat products',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'bread',
            'emission_factor': Decimal('1.6'),
            'unit': 'kg',
            'description': 'Bread',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'vegetables',
            'emission_factor': Decimal('2.0'),
            'unit': 'kg',
            'description': 'Vegetables (average)',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'fruits',
            'emission_factor': Decimal('1.1'),
            'unit': 'kg',
            'description': 'Fruits (average)',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'legumes',
            'emission_factor': Decimal('0.9'),
            'unit': 'kg',
            'description': 'Legumes (beans, lentils)',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'nuts',
            'emission_factor': Decimal('2.3'),
            'unit': 'kg',
            'description': 'Nuts',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'tofu',
            'emission_factor': Decimal('3.0'),
            'unit': 'kg',
            'description': 'Tofu (soy products)',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'coffee',
            'emission_factor': Decimal('16.5'),
            'unit': 'kg',
            'description': 'Coffee beans',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        {
            'category': 'food',
            'activity': 'chocolate',
            'emission_factor': Decimal('19.0'),
            'unit': 'kg',
            'description': 'Chocolate/cocoa products',
            'source': 'Poore & Nemecek 2018',
            'region': 'Global Average'
        },
        
        # WASTE - Per kilogram
        {
            'category': 'waste',
            'activity': 'landfill',
            'emission_factor': Decimal('0.57'),
            'unit': 'kg',
            'description': 'Waste to landfill',
            'source': 'EPA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'waste',
            'activity': 'recycling_paper',
            'emission_factor': Decimal('-0.35'),
            'unit': 'kg',
            'description': 'Paper recycling (carbon saved)',
            'source': 'EPA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'waste',
            'activity': 'recycling_plastic',
            'emission_factor': Decimal('-0.15'),
            'unit': 'kg',
            'description': 'Plastic recycling (carbon saved)',
            'source': 'EPA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'waste',
            'activity': 'recycling_glass',
            'emission_factor': Decimal('-0.26'),
            'unit': 'kg',
            'description': 'Glass recycling (carbon saved)',
            'source': 'EPA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'waste',
            'activity': 'recycling_metal',
            'emission_factor': Decimal('-1.89'),
            'unit': 'kg',
            'description': 'Metal recycling (carbon saved)',
            'source': 'EPA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'waste',
            'activity': 'composting',
            'emission_factor': Decimal('-0.10'),
            'unit': 'kg',
            'description': 'Organic waste composting',
            'source': 'EPA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'waste',
            'activity': 'incineration',
            'emission_factor': Decimal('0.21'),
            'unit': 'kg',
            'description': 'Waste incineration',
            'source': 'EPA 2023',
            'region': 'Global Average'
        },
        
        # HOUSEHOLD & OTHER
        {
            'category': 'household',
            'activity': 'water_supply',
            'emission_factor': Decimal('0.344'),
            'unit': 'm3',
            'description': 'Water supply and treatment',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'household',
            'activity': 'sewage_treatment',
            'emission_factor': Decimal('0.709'),
            'unit': 'm3',
            'description': 'Sewage treatment',
            'source': 'UK DEFRA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'household',
            'activity': 'paper_product',
            'emission_factor': Decimal('1.3'),
            'unit': 'kg',
            'description': 'Paper products',
            'source': 'EPA 2023',
            'region': 'Global Average'
        },
        {
            'category': 'household',
            'activity': 'plastic_product',
            'emission_factor': Decimal('2.5'),
            'unit': 'kg',
            'description': 'Plastic products',
            'source': 'EPA 2023',
            'region': 'Global Average'
        },
    ]

def seed_emission_factors():
    """Seed the emission factors table with data"""
    try:
        dynamodb = boto3.client('dynamodb', region_name=REGION)
        
        # Wait for table to be active
        print(f"Checking if table {TABLE_NAME} is active...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=TABLE_NAME)
        
        data = get_emission_factors_data()
        print(f"\nSeeding {len(data)} emission factors to DynamoDB...")
        
        success_count = 0
        error_count = 0
        
        for item in data:
            try:
                dynamodb.put_item(
                    TableName=TABLE_NAME,
                    Item={
                        'category': {'S': item['category']},
                        'activity': {'S': item['activity']},
                        'emission_factor': {'N': str(item['emission_factor'])},
                        'unit': {'S': item['unit']},
                        'description': {'S': item['description']},
                        'source': {'S': item['source']},
                        'region': {'S': item['region']},
                    }
                )
                success_count += 1
                print(f"✓ Added: {item['category']}/{item['activity']} ({item['emission_factor']} kg CO2/{item['unit']})")
            except Exception as e:
                error_count += 1
                print(f"✗ Error adding {item['category']}/{item['activity']}: {str(e)}")
        
        print(f"\n{'='*60}")
        print(f"Seeding complete!")
        print(f"Successfully added: {success_count}")
        print(f"Errors: {error_count}")
        print(f"{'='*60}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"Error seeding emission factors: {str(e)}")
        return False

def verify_seed():
    """Verify the seeded data"""
    try:
        dynamodb = boto3.client('dynamodb', region_name=REGION)
        
        print("\nVerifying seeded data...")
        response = dynamodb.scan(
            TableName=TABLE_NAME,
            Select='COUNT'
        )
        
        count = response.get('Count', 0)
        print(f"Total items in table: {count}")
        
        # Sample some items
        if count > 0:
            print("\nSample emission factors:")
            response = dynamodb.scan(
                TableName=TABLE_NAME,
                Limit=5
            )
            
            for item in response.get('Items', []):
                category = item['category']['S']
                activity = item['activity']['S']
                factor = item['emission_factor']['N']
                unit = item['unit']['S']
                description = item['description']['S']
                print(f"  {category}/{activity}: {factor} kg CO2/{unit} - {description}")
        
        return True
        
    except Exception as e:
        print(f"Error verifying seed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CarbonTrack Emission Factors Seed Script")
    print("=" * 60)
    
    if seed_emission_factors():
        verify_seed()
        sys.exit(0)
    else:
        print("Seeding failed!")
        sys.exit(1)
