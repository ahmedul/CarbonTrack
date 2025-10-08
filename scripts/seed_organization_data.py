#!/usr/bin/env python3
"""
Seed script to populate local DynamoDB with sample organization data
This creates a complete organization structure for testing
"""

import boto3
import uuid
from datetime import datetime, timedelta
import sys

# Local DynamoDB configuration
DYNAMODB_ENDPOINT = "http://localhost:8000"
REGION = "us-east-1"

# Initialize DynamoDB client
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=DYNAMODB_ENDPOINT,
    region_name=REGION,
    aws_access_key_id='fakeAccessKey',  # Local DynamoDB doesn't validate credentials
    aws_secret_access_key='fakeSecretKey'
)

def generate_id(prefix):
    """Generate a unique ID with a prefix"""
    return f"{prefix}_{uuid.uuid4()}"

def iso_timestamp(days_ago=0):
    """Generate ISO timestamp"""
    return (datetime.now() - timedelta(days=days_ago)).isoformat()

def create_organizations():
    """Create sample organizations"""
    table = dynamodb.Table('carbontrack-organizations')
    
    organizations = [
        {
            'organization_id': generate_id('org'),
            'name': 'TechCorp Industries',
            'industry': 'Technology',
            'size': 'large',
            'subscription_tier': 'enterprise',
            'admin_user_id': 'user_admin_techcorp',
            'settings': {
                'carbon_budget': 500000,  # kg CO2/year
                'reporting_frequency': 'monthly',
                'features_enabled': ['bulk_import', 'challenges', 'advanced_reports'],
                'branding': {
                    'logo_url': 'https://example.com/techcorp-logo.png',
                    'primary_color': '#0066CC',
                    'custom_domain': 'carbon.techcorp.com'
                }
            },
            'billing': {
                'plan': 'enterprise',
                'seats': 500,
                'renewal_date': iso_timestamp(-180)
            },
            'metadata': {
                'industry_average_per_employee': 4.2,
                'headquarters': 'San Francisco, CA'
            },
            'created_at': iso_timestamp(365),
            'updated_at': iso_timestamp(5),
            'status': 'active'
        },
        {
            'organization_id': generate_id('org'),
            'name': 'GreenEnergy Solutions',
            'industry': 'Energy',
            'size': 'medium',
            'subscription_tier': 'professional',
            'admin_user_id': 'user_admin_greenenergy',
            'settings': {
                'carbon_budget': 100000,
                'reporting_frequency': 'quarterly',
                'features_enabled': ['challenges', 'reports'],
                'branding': {
                    'logo_url': 'https://example.com/greenenergy-logo.png',
                    'primary_color': '#22AA55',
                    'custom_domain': ''
                }
            },
            'billing': {
                'plan': 'professional',
                'seats': 150,
                'renewal_date': iso_timestamp(-90)
            },
            'metadata': {
                'industry_average_per_employee': 3.1,
                'headquarters': 'Austin, TX'
            },
            'created_at': iso_timestamp(180),
            'updated_at': iso_timestamp(2),
            'status': 'active'
        }
    ]
    
    print("Creating organizations...")
    org_ids = []
    for org in organizations:
        table.put_item(Item=org)
        org_ids.append((org['organization_id'], org['admin_user_id'], org['name']))
        print(f"  ✓ Created: {org['name']} ({org['organization_id']})")
    
    return org_ids

def create_teams(org_ids):
    """Create sample teams/departments"""
    table = dynamodb.Table('carbontrack-teams')
    
    # TechCorp teams
    techcorp_id, techcorp_admin, _ = org_ids[0]
    techcorp_teams = [
        {
            'team_id': generate_id('team'),
            'organization_id': techcorp_id,
            'name': 'Engineering',
            'description': 'Product development and infrastructure teams',
            'parent_team_id': '',
            'team_lead_user_id': 'user_lead_eng',
            'settings': {
                'carbon_budget': 150000,
                'goal_period': 'quarterly',
                'visibility': 'org_only'
            },
            'stats': {
                'member_count': 120,
                'total_emissions': 45230.5,
                'average_per_member': 376.92,
                'last_calculated': iso_timestamp(0)
            },
            'created_at': iso_timestamp(300),
            'updated_at': iso_timestamp(1),
            'status': 'active'
        },
        {
            'team_id': generate_id('team'),
            'organization_id': techcorp_id,
            'name': 'Sales & Marketing',
            'description': 'Customer acquisition and brand teams',
            'parent_team_id': '',
            'team_lead_user_id': 'user_lead_sales',
            'settings': {
                'carbon_budget': 200000,
                'goal_period': 'monthly',
                'visibility': 'org_only'
            },
            'stats': {
                'member_count': 80,
                'total_emissions': 78450.2,
                'average_per_member': 980.63,
                'last_calculated': iso_timestamp(0)
            },
            'created_at': iso_timestamp(300),
            'updated_at': iso_timestamp(1),
            'status': 'active'
        },
        {
            'team_id': generate_id('team'),
            'organization_id': techcorp_id,
            'name': 'Operations',
            'description': 'Facilities, HR, and admin teams',
            'parent_team_id': '',
            'team_lead_user_id': 'user_lead_ops',
            'settings': {
                'carbon_budget': 100000,
                'goal_period': 'quarterly',
                'visibility': 'org_only'
            },
            'stats': {
                'member_count': 50,
                'total_emissions': 23450.8,
                'average_per_member': 469.02,
                'last_calculated': iso_timestamp(0)
            },
            'created_at': iso_timestamp(300),
            'updated_at': iso_timestamp(1),
            'status': 'active'
        }
    ]
    
    # GreenEnergy teams
    greenenergy_id, greenenergy_admin, _ = org_ids[1]
    greenenergy_teams = [
        {
            'team_id': generate_id('team'),
            'organization_id': greenenergy_id,
            'name': 'Field Operations',
            'description': 'On-site installation and maintenance',
            'parent_team_id': '',
            'team_lead_user_id': 'user_lead_field',
            'settings': {
                'carbon_budget': 60000,
                'goal_period': 'monthly',
                'visibility': 'org_only'
            },
            'stats': {
                'member_count': 45,
                'total_emissions': 18234.5,
                'average_per_member': 405.21,
                'last_calculated': iso_timestamp(0)
            },
            'created_at': iso_timestamp(150),
            'updated_at': iso_timestamp(1),
            'status': 'active'
        },
        {
            'team_id': generate_id('team'),
            'organization_id': greenenergy_id,
            'name': 'Corporate',
            'description': 'Office staff and management',
            'parent_team_id': '',
            'team_lead_user_id': 'user_lead_corporate',
            'settings': {
                'carbon_budget': 40000,
                'goal_period': 'quarterly',
                'visibility': 'org_only'
            },
            'stats': {
                'member_count': 30,
                'total_emissions': 10345.2,
                'average_per_member': 344.84,
                'last_calculated': iso_timestamp(0)
            },
            'created_at': iso_timestamp(150),
            'updated_at': iso_timestamp(1),
            'status': 'active'
        }
    ]
    
    all_teams = techcorp_teams + greenenergy_teams
    
    print("\nCreating teams...")
    team_ids = []
    for team in all_teams:
        table.put_item(Item=team)
        team_ids.append((team['team_id'], team['organization_id'], team['name']))
        print(f"  ✓ Created: {team['name']} ({team['team_id']})")
    
    return team_ids

def create_users_and_memberships(org_ids, team_ids):
    """Create sample users and team memberships"""
    users_table = dynamodb.Table('carbontrack-users')
    members_table = dynamodb.Table('carbontrack-team-members')
    
    users = []
    memberships = []
    
    # Create admin users
    for org_id, admin_id, org_name in org_ids:
        user = {
            'user_id': admin_id,
            'email': f"admin@{org_name.lower().replace(' ', '')}.com",
            'name': f"{org_name} Admin",
            'password_hash': 'hashed_password_here',  # In real app, properly hash
            'status': 'active',
            'role': 'admin',
            'organization_id': org_id,
            'organization_role': 'owner',
            'teams': [],
            'department': 'Management',
            'employee_id': 'EMP001',
            'org_joined_at': iso_timestamp(365),
            'created_at': iso_timestamp(365),
            'updated_at': iso_timestamp(1)
        }
        users.append(user)
    
    # Create team leads and members
    team_user_count = 0
    for team_id, org_id, team_name in team_ids:
        # Team lead
        lead_id = f"user_lead_{team_name.lower().replace(' & ', '_').replace(' ', '_')}"
        lead_user = {
            'user_id': lead_id,
            'email': f"{lead_id}@example.com",
            'name': f"{team_name} Lead",
            'password_hash': 'hashed_password_here',
            'status': 'active',
            'role': 'user',
            'organization_id': org_id,
            'organization_role': 'manager',
            'teams': [team_id],
            'department': team_name,
            'employee_id': f'EMP{1000 + team_user_count}',
            'org_joined_at': iso_timestamp(200),
            'created_at': iso_timestamp(200),
            'updated_at': iso_timestamp(1)
        }
        users.append(lead_user)
        
        # Lead membership
        memberships.append({
            'team_id': team_id,
            'user_id': lead_id,
            'organization_id': org_id,
            'role': 'team_lead',
            'permissions': ['view_reports', 'add_members', 'set_goals', 'add_emissions'],
            'joined_at': iso_timestamp(200),
            'invited_by': 'admin',
            'status': 'active'
        })
        
        # Create 3-5 regular members per team
        num_members = 4
        for i in range(num_members):
            member_id = f"user_member_{team_id}_{i}"
            member = {
                'user_id': member_id,
                'email': f"{member_id}@example.com",
                'name': f"{team_name} Member {i+1}",
                'password_hash': 'hashed_password_here',
                'status': 'active',
                'role': 'user',
                'organization_id': org_id,
                'organization_role': 'member',
                'teams': [team_id],
                'department': team_name,
                'employee_id': f'EMP{2000 + team_user_count + i}',
                'org_joined_at': iso_timestamp(150),
                'created_at': iso_timestamp(150),
                'updated_at': iso_timestamp(1)
            }
            users.append(member)
            
            memberships.append({
                'team_id': team_id,
                'user_id': member_id,
                'organization_id': org_id,
                'role': 'member',
                'permissions': ['view_reports', 'add_emissions'],
                'joined_at': iso_timestamp(150),
                'invited_by': lead_id,
                'status': 'active'
            })
        
        team_user_count += num_members + 1
    
    print("\nCreating users...")
    for user in users:
        users_table.put_item(Item=user)
        print(f"  ✓ Created user: {user['email']}")
    
    print("\nCreating team memberships...")
    for membership in memberships:
        members_table.put_item(Item=membership)
        print(f"  ✓ Added {membership['user_id']} to {membership['team_id']}")
    
    return users

def create_team_goals(team_ids):
    """Create sample team goals"""
    table = dynamodb.Table('carbontrack-team-goals')
    
    goals = []
    
    for team_id, org_id, team_name in team_ids:
        # Current quarter goal
        goal = {
            'goal_id': generate_id('goal'),
            'team_id': team_id,
            'organization_id': org_id,
            'goal_type': 'reduction',
            'target_value': 10000,  # 10% reduction
            'baseline_value': 100000,
            'period': 'quarterly',
            'start_date': iso_timestamp(60),
            'end_date': iso_timestamp(-30),
            'status': 'active',
            'progress': {
                'current_value': 92000,
                'percentage': 8.0,
                'last_updated': iso_timestamp(0),
                'on_track': True
            },
            'created_by': f'user_lead_{team_name.lower().replace(" & ", "_").replace(" ", "_")}',
            'created_at': iso_timestamp(65),
            'updated_at': iso_timestamp(0)
        }
        goals.append(goal)
    
    print("\nCreating team goals...")
    for goal in goals:
        table.put_item(Item=goal)
        print(f"  ✓ Created goal for team {goal['team_id']}")
    
    return goals

def create_challenges(org_ids):
    """Create sample challenges"""
    challenges_table = dynamodb.Table('carbontrack-challenges')
    participants_table = dynamodb.Table('carbontrack-challenge-participants')
    
    org_id, _, org_name = org_ids[0]  # TechCorp
    
    challenge = {
        'challenge_id': generate_id('challenge'),
        'organization_id': org_id,
        'name': 'Q4 2024 Carbon Reduction Challenge',
        'description': 'Teams compete to achieve the highest percentage reduction in carbon emissions',
        'challenge_type': 'reduction_race',
        'rules': {
            'measurement': 'percentage_reduction',
            'duration_days': 90,
            'min_participants': 2,
            'categories': ['all']
        },
        'prizes': [
            {'rank': 1, 'description': 'Team Lunch & Recognition', 'value': '$500'},
            {'rank': 2, 'description': 'Coffee Shop Gift Cards', 'value': '$200'},
            {'rank': 3, 'description': 'Sustainability Books', 'value': '$100'}
        ],
        'start_date': iso_timestamp(30),
        'end_date': iso_timestamp(-60),
        'status': 'active',
        'created_by': org_ids[0][1],  # Admin user
        'created_at': iso_timestamp(35)
    }
    
    print("\nCreating challenges...")
    challenges_table.put_item(Item=challenge)
    print(f"  ✓ Created: {challenge['name']}")
    
    # Add participants (teams)
    participants = [
        {
            'challenge_id': challenge['challenge_id'],
            'participant_id': 'team_eng',
            'participant_type': 'team',
            'team_id': 'team_eng',
            'organization_id': org_id,
            'stats': {
                'baseline_emissions': 50000,
                'current_emissions': 42000,
                'reduction_amount': 8000,
                'reduction_percentage': 16.0,
                'rank': 1,
                'last_updated': iso_timestamp(0)
            },
            'joined_at': iso_timestamp(30),
            'status': 'active'
        }
    ]
    
    print("\nCreating challenge participants...")
    for participant in participants:
        participants_table.put_item(Item=participant)
        print(f"  ✓ Added participant: {participant['participant_id']}")
    
    return [challenge]

def main():
    """Main seeding function"""
    print("=" * 60)
    print("CarbonTrack Local DynamoDB Seeding Script")
    print("=" * 60)
    print()
    
    try:
        # Test connection
        dynamodb.meta.client.list_tables()
        print("✓ Connected to local DynamoDB")
        print()
        
        # Seed data
        org_ids = create_organizations()
        team_ids = create_teams(org_ids)
        users = create_users_and_memberships(org_ids, team_ids)
        goals = create_team_goals(team_ids)
        challenges = create_challenges(org_ids)
        
        print()
        print("=" * 60)
        print("✓ Seeding complete!")
        print("=" * 60)
        print()
        print("Created:")
        print(f"  - {len(org_ids)} organizations")
        print(f"  - {len(team_ids)} teams")
        print(f"  - {len(users)} users")
        print(f"  - {len(goals)} team goals")
        print(f"  - {len(challenges)} challenges")
        print()
        print("Test credentials:")
        for org_id, admin_id, org_name in org_ids:
            print(f"  - {org_name}: admin@{org_name.lower().replace(' ', '')}.com")
        print()
        print("Next steps:")
        print("  1. Configure backend to use local DynamoDB endpoint")
        print("  2. Start backend server")
        print("  3. Test organization APIs with Postman/curl")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure DynamoDB Local is running:")
        print("  docker ps | grep dynamodb-local")
        print("\nOr start it with:")
        print("  ./infra/setup-local-dynamodb.sh")
        sys.exit(1)

if __name__ == "__main__":
    main()
