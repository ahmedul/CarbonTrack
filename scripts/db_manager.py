#!/usr/bin/env python3
"""
CarbonTrack Database Manager
A simple CLI tool to interact with DynamoDB tables
"""

import boto3
from datetime import datetime
from botocore.exceptions import ClientError

class CarbonTrackDBManager:
    def __init__(self, region='us-east-1'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.users_table = self.dynamodb.Table('carbontrack-users-production')
        self.emissions_table = self.dynamodb.Table('carbontrack-emissions-production')
    
    def list_all_users(self):
        """List all users in the database"""
        try:
            response = self.users_table.scan()
            users = response.get('Items', [])
            
            print(f"\n=== USERS TABLE ({len(users)} records) ===")
            if not users:
                print("No users found.")
                return
                
            for user in users:
                print(f"User ID: {user.get('user_id', 'N/A')}")
                print(f"Email: {user.get('email', 'N/A')}")
                print(f"Created: {user.get('created_at', 'N/A')}")
                print("-" * 40)
        except ClientError as e:
            print(f"Error scanning users table: {e}")
    
    def list_all_emissions(self):
        """List all emissions records"""
        try:
            response = self.emissions_table.scan()
            emissions = response.get('Items', [])
            
            print(f"\n=== EMISSIONS TABLE ({len(emissions)} records) ===")
            if not emissions:
                print("No emissions records found.")
                return
                
            for emission in emissions:
                print(f"Record ID: {emission.get('record_id', 'N/A')}")
                print(f"User ID: {emission.get('user_id', 'N/A')}")
                print(f"Activity: {emission.get('activity_type', 'N/A')}")
                print(f"CO2 (kg): {emission.get('co2_kg', 'N/A')}")
                print(f"Date: {emission.get('date', 'N/A')}")
                print("-" * 40)
        except ClientError as e:
            print(f"Error scanning emissions table: {e}")
    
    def add_sample_user(self, user_id=None, email=None):
        """Add a sample user for testing"""
        if not user_id:
            user_id = f"user_{int(datetime.now().timestamp())}"
        if not email:
            email = f"{user_id}@example.com"
        
        try:
            self.users_table.put_item(
                Item={
                    'user_id': user_id,
                    'email': email,
                    'created_at': datetime.now().isoformat(),
                    'subscription_type': 'free'
                }
            )
            print(f"✅ Added sample user: {user_id} ({email})")
        except ClientError as e:
            print(f"❌ Error adding user: {e}")
    
    def add_sample_emission(self, user_id=None):
        """Add a sample emission record"""
        if not user_id:
            # Get first user or create one
            response = self.users_table.scan(Limit=1)
            users = response.get('Items', [])
            if users:
                user_id = users[0]['user_id']
            else:
                user_id = "sample_user"
                self.add_sample_user(user_id)
        
        record_id = f"emission_{int(datetime.now().timestamp())}"
        
        try:
            self.emissions_table.put_item(
                Item={
                    'record_id': record_id,
                    'user_id': user_id,
                    'activity_type': 'transportation',
                    'description': 'Car trip to office',
                    'co2_kg': 2.5,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'created_at': datetime.now().isoformat()
                }
            )
            print(f"✅ Added sample emission record: {record_id}")
        except ClientError as e:
            print(f"❌ Error adding emission: {e}")
    
    def get_table_info(self):
        """Display table information"""
        try:
            users_info = self.users_table.table_status
            emissions_info = self.emissions_table.table_status
            
            print("\n=== TABLE STATUS ===")
            print(f"Users Table: {users_info}")
            print(f"Emissions Table: {emissions_info}")
            
            # Get item counts
            users_count = self.users_table.scan(Select='COUNT')['Count']
            emissions_count = self.emissions_table.scan(Select='COUNT')['Count']
            
            print("\n=== RECORD COUNTS ===")
            print(f"Users: {users_count}")
            print(f"Emissions: {emissions_count}")
            
        except ClientError as e:
            print(f"Error getting table info: {e}")

def main():
    db = CarbonTrackDBManager()
    
    while True:
        print("\n" + "="*50)
        print("🌱 CarbonTrack Database Manager")
        print("="*50)
        print("1. View table information")
        print("2. List all users")
        print("3. List all emissions")
        print("4. Add sample user")
        print("5. Add sample emission")
        print("6. Add sample data (user + emission)")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == '0':
            print("Goodbye! 👋")
            break
        elif choice == '1':
            db.get_table_info()
        elif choice == '2':
            db.list_all_users()
        elif choice == '3':
            db.list_all_emissions()
        elif choice == '4':
            user_id = input("Enter user ID (or press Enter for auto-generated): ").strip()
            email = input("Enter email (or press Enter for auto-generated): ").strip()
            db.add_sample_user(user_id if user_id else None, email if email else None)
        elif choice == '5':
            user_id = input("Enter user ID (or press Enter to use existing user): ").strip()
            db.add_sample_emission(user_id if user_id else None)
        elif choice == '6':
            print("Adding sample user and emission...")
            db.add_sample_user()
            db.add_sample_emission()
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()