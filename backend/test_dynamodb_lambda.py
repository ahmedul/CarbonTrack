"""
Lambda function to test DynamoDB read/write operations for CarbonTrack
This function validates that all tables are working correctly
"""

import json
import boto3
from datetime import datetime
from decimal import Decimal
import uuid

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')

# Table references
users_table = dynamodb.Table('carbontrack-users')
entries_table = dynamodb.Table('carbontrack-entries')
goals_table = dynamodb.Table('carbontrack-goals')
achievements_table = dynamodb.Table('carbontrack-achievements')


def lambda_handler(event, context):
    """
    Test Lambda function for DynamoDB operations
    Tests all CRUD operations across all tables
    """
    
    test_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "tests": []
    }
    
    # Generate test user ID
    test_user_id = f"test-user-{int(datetime.utcnow().timestamp())}"
    
    try:
        # ====================
        # TEST 1: Users Table
        # ====================
        print("Testing Users table...")
        
        # CREATE user
        user_item = {
            'userId': test_user_id,
            'email': f'{test_user_id}@carbontrack.dev',
            'full_name': f'Test User {test_user_id[-10:]}',
            'preferred_units': {
                'distance': 'km',
                'energy': 'kWh',
                'weight': 'kg'
            },
            'total_emissions': Decimal('0'),
            'current_month_emissions': Decimal('0'),
            'entries_count': 0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'last_active': datetime.utcnow().isoformat()
        }
        
        users_table.put_item(Item=user_item)
        test_results["tests"].append({
            "test": "CREATE User",
            "status": "PASS",
            "user_id": test_user_id
        })
        
        # READ user
        response = users_table.get_item(Key={'userId': test_user_id})
        if 'Item' in response:
            test_results["tests"].append({
                "test": "READ User",
                "status": "PASS",
                "data": response['Item']['email']
            })
        else:
            test_results["tests"].append({
                "test": "READ User",
                "status": "FAIL",
                "error": "User not found"
            })
        
        # ====================
        # TEST 2: Carbon Entries Table
        # ====================
        print("Testing Carbon Entries table...")
        
        # CREATE carbon emission entry
        emission_timestamp = datetime.utcnow().isoformat()
        emission_item = {
            'userId': test_user_id,
            'timestamp': emission_timestamp,
            'entry_id': str(uuid.uuid4()),
            'date': datetime.utcnow().date().isoformat(),
            'category': 'transportation',
            'activity': 'car_drive',
            'amount': Decimal('25.5'),
            'unit': 'km',
            'description': 'Test drive for Lambda validation',
            'co2_equivalent': Decimal('5.1'),
            'created_at': emission_timestamp,
            'updated_at': emission_timestamp
        }
        
        entries_table.put_item(Item=emission_item)
        test_results["tests"].append({
            "test": "CREATE Carbon Entry",
            "status": "PASS",
            "timestamp": emission_timestamp
        })
        
        # READ carbon emission entries
        response = entries_table.query(
            KeyConditionExpression='userId = :user_id',
            ExpressionAttributeValues={':user_id': test_user_id}
        )
        
        if response['Items']:
            test_results["tests"].append({
                "test": "READ Carbon Entries",
                "status": "PASS",
                "count": len(response['Items'])
            })
        else:
            test_results["tests"].append({
                "test": "READ Carbon Entries",
                "status": "FAIL",
                "error": "No entries found"
            })
        
        # ====================
        # TEST 3: Goals Table
        # ====================
        print("Testing Goals table...")
        
        # CREATE goal
        goal_id = str(uuid.uuid4())
        goal_item = {
            'userId': test_user_id,
            'goalId': goal_id,
            'category': 'transportation',
            'target_amount': Decimal('100.0'),
            'target_period': 'monthly',
            'description': 'Test goal for Lambda validation',
            'current_amount': Decimal('0'),
            'is_active': True,
            'is_achieved': False,
            'start_date': datetime.utcnow().date().isoformat(),
            'end_date': (datetime.utcnow().date().replace(day=28)).isoformat(),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        goals_table.put_item(Item=goal_item)
        test_results["tests"].append({
            "test": "CREATE Goal",
            "status": "PASS",
            "goal_id": goal_id
        })
        
        # READ goals
        response = goals_table.query(
            KeyConditionExpression='userId = :user_id',
            ExpressionAttributeValues={':user_id': test_user_id}
        )
        
        if response['Items']:
            test_results["tests"].append({
                "test": "READ Goals",
                "status": "PASS",
                "count": len(response['Items'])
            })
        else:
            test_results["tests"].append({
                "test": "READ Goals",
                "status": "FAIL",
                "error": "No goals found"
            })
        
        # ====================
        # TEST 4: Achievements Table
        # ====================
        print("Testing Achievements table...")
        
        # CREATE achievement
        achievement_id = str(uuid.uuid4())
        achievement_item = {
            'userId': test_user_id,
            'achievementId': achievement_id,
            'title': 'First Entry',
            'description': 'Created your first carbon footprint entry',
            'category': 'milestone',
            'requirement_type': 'entries',
            'requirement_value': Decimal('1'),
            'current_progress': Decimal('1'),
            'is_unlocked': True,
            'unlocked_date': datetime.utcnow().isoformat(),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        achievements_table.put_item(Item=achievement_item)
        test_results["tests"].append({
            "test": "CREATE Achievement",
            "status": "PASS",
            "achievement_id": achievement_id
        })
        
        # READ achievements
        response = achievements_table.query(
            KeyConditionExpression='userId = :user_id',
            ExpressionAttributeValues={':user_id': test_user_id}
        )
        
        if response['Items']:
            test_results["tests"].append({
                "test": "READ Achievements",
                "status": "PASS",
                "count": len(response['Items'])
            })
        else:
            test_results["tests"].append({
                "test": "READ Achievements",
                "status": "FAIL",
                "error": "No achievements found"
            })
        
        # ====================
        # TEST 5: UPDATE Operations
        # ====================
        print("Testing UPDATE operations...")
        
        # UPDATE user stats
        users_table.update_item(
            Key={'userId': test_user_id},
            UpdateExpression='ADD total_emissions :co2, entries_count :one',
            ExpressionAttributeValues={
                ':co2': Decimal('5.1'),
                ':one': 1
            }
        )
        
        test_results["tests"].append({
            "test": "UPDATE User Stats",
            "status": "PASS"
        })
        
        # ====================
        # TEST 6: DELETE Operations (Cleanup)
        # ====================
        print("Testing DELETE operations (cleanup)...")
        
        # Delete test data
        entries_table.delete_item(Key={'userId': test_user_id, 'timestamp': emission_timestamp})
        goals_table.delete_item(Key={'userId': test_user_id, 'goalId': goal_id})
        achievements_table.delete_item(Key={'userId': test_user_id, 'achievementId': achievement_id})
        users_table.delete_item(Key={'userId': test_user_id})
        
        test_results["tests"].append({
            "test": "DELETE Test Data",
            "status": "PASS"
        })
        
        # Calculate success rate
        passed_tests = len([t for t in test_results["tests"] if t["status"] == "PASS"])
        total_tests = len(test_results["tests"])
        
        test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": f"{(passed_tests/total_tests)*100:.1f}%",
            "overall_status": "PASS" if passed_tests == total_tests else "FAIL"
        }
        
        print(f"Tests completed: {passed_tests}/{total_tests} passed")
        
    except Exception as e:
        test_results["tests"].append({
            "test": "EXCEPTION",
            "status": "FAIL",
            "error": str(e)
        })
        
        test_results["summary"] = {
            "overall_status": "FAIL",
            "error": str(e)
        }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(test_results, default=str)
    }


# For local testing
if __name__ == "__main__":
    result = lambda_handler({}, {})
    print(json.dumps(json.loads(result['body']), indent=2))
