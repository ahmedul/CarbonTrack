#!/usr/bin/env python3
"""
Test Database Scripts
====================

Simple test script to validate our database seed scripts
without requiring actual AWS/DynamoDB connection.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_carbon_activities_script():
    """Test the carbon activities seed script structure"""
    try:
        from scripts.seed_carbon_activities import get_carbon_activities_data, convert_to_dynamodb_item
        
        print("🧪 Testing Carbon Activities Script...")
        
        # Get the data
        activities = get_carbon_activities_data()
        print(f"✅ Retrieved {len(activities)} carbon activities")
        
        # Test a few conversions
        test_count = 5
        for i, activity in enumerate(activities[:test_count]):
            convert_to_dynamodb_item(activity)  # Test conversion works
            print(f"✅ Activity {i+1}: {activity['name']} -> DynamoDB format OK")
        
        # Show categories breakdown
        categories = {}
        for activity in activities:
            cat = activity['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📊 Categories breakdown:")
        for cat, count in categories.items():
            print(f"   {cat}: {count} activities")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing carbon activities: {e}")
        return False

def test_sample_emissions_script():
    """Test the sample emissions seed script structure"""
    try:
        from scripts.seed_sample_emissions import get_demo_emissions_data, get_sample_emissions_data, convert_emission_to_dynamodb_item
        
        print("\n🧪 Testing Sample Emissions Script...")
        
        # Get demo data
        demo_emissions = get_demo_emissions_data()
        print(f"✅ Retrieved {len(demo_emissions)} demo emissions")
        
        # Get sample data
        sample_emissions = get_sample_emissions_data()
        print(f"✅ Retrieved {len(sample_emissions)} sample emissions")
        
        # Test conversions
        all_emissions = demo_emissions + sample_emissions
        for i, emission in enumerate(all_emissions[:3]):
            convert_emission_to_dynamodb_item(emission)  # Test conversion works
            print(f"✅ Emission {i+1}: {emission['activity_name']} -> DynamoDB format OK")
        
        # Show totals
        total_co2 = sum(float(e['co2_equivalent']) for e in all_emissions)
        print(f"\n📊 Total sample CO2 equivalent: {total_co2:.2f} kg")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing sample emissions: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 CarbonTrack Database Scripts Test")
    print("=" * 50)
    
    success_count = 0
    
    # Test carbon activities
    if test_carbon_activities_script():
        success_count += 1
    
    # Test sample emissions
    if test_sample_emissions_script():
        success_count += 1
    
    print("\n📊 Test Results:")
    print(f"   ✅ Passed: {success_count}/2 tests")
    
    if success_count == 2:
        print("\n🎉 All tests passed! Database scripts are ready.")
        print("\nNext steps:")
        print("1. Set up AWS credentials or local DynamoDB")
        print("2. Run: python scripts/seed_carbon_activities.py")
        print("3. Run: python scripts/seed_sample_emissions.py")
        print("4. Test backend API endpoints")
        return 0
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())