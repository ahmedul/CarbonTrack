#!/usr/bin/env python3
"""
Direct AWS Cognito Test Script
Test user registration and authentication without the FastAPI server
"""

import boto3
import hmac
import hashlib
import base64
import sys
from botocore.exceptions import ClientError

# Load environment variables
sys.path.append('.')
from app.core.config import settings

def get_secret_hash(username: str, client_id: str, client_secret: str) -> str:
    """Generate secret hash for Cognito client"""
    message = username + client_id
    dig = hmac.new(
        str(client_secret).encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

def test_cognito_registration():
    """Test user registration with AWS Cognito"""
    print("🧪 Testing AWS Cognito User Registration...")
    
    # Initialize Cognito client
    client = boto3.client('cognito-idp', region_name=settings.aws_region)
    
    test_email = f"test-{int(__import__('time').time())}@carbontrack.dev"
    test_password = "TestPass123!"
    
    print(f"📧 Test Email: {test_email}")
    print(f"🔧 Region: {settings.aws_region}")
    print(f"🏊 User Pool ID: {settings.cognito_user_pool_id}")
    print(f"📱 Client ID: {settings.cognito_client_id}")
    
    try:
        # Create user
        client.admin_create_user(
            UserPoolId=settings.cognito_user_pool_id,
            Username=test_email,
            UserAttributes=[
                {'Name': 'email', 'Value': test_email},
                {'Name': 'name', 'Value': 'Test User'},
                {'Name': 'email_verified', 'Value': 'true'}
            ],
            TemporaryPassword=test_password,
            MessageAction='SUPPRESS'
        )
        
        print("✅ User created successfully!")
        
        # Set permanent password
        client.admin_set_user_password(
            UserPoolId=settings.cognito_user_pool_id,
            Username=test_email,
            Password=test_password,
            Permanent=True
        )
        
        print("✅ Password set successfully!")
        
        # Test authentication
        secret_hash = get_secret_hash(test_email, settings.cognito_client_id, settings.cognito_client_secret)
        
        auth_response = client.admin_initiate_auth(
            UserPoolId=settings.cognito_user_pool_id,
            ClientId=settings.cognito_client_id,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': test_email,
                'PASSWORD': test_password,
                'SECRET_HASH': secret_hash
            }
        )
        
        if 'AuthenticationResult' in auth_response:
            tokens = auth_response['AuthenticationResult']
            print("✅ Authentication successful!")
            print(f"🎫 Access Token: {tokens['AccessToken'][:50]}...")
            print(f"⏰ Expires in: {tokens['ExpiresIn']} seconds")
            
            # Clean up - delete test user
            client.admin_delete_user(
                UserPoolId=settings.cognito_user_pool_id,
                Username=test_email
            )
            print("🗑️ Test user cleaned up")
            
            return True
        else:
            print("❌ Authentication failed")
            return False
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ AWS Error ({error_code}): {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Direct AWS Cognito Test")
    print("=" * 50)
    
    # Check configuration
    print(f"✅ AWS Region: {settings.aws_region}")
    print(f"✅ User Pool ID: {settings.cognito_user_pool_id}")
    print(f"✅ Client ID: {settings.cognito_client_id}")
    print(f"✅ Debug Mode: {settings.debug}")
    print()
    
    success = test_cognito_registration()
    
    if success:
        print("\n🎉 AWS Cognito integration is working perfectly!")
        print("✅ User registration: PASSED")
        print("✅ Authentication: PASSED")
        print("✅ Token generation: PASSED")
    else:
        print("\n❌ AWS Cognito integration has issues")
        print("Please check your configuration")
