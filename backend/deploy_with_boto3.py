#!/usr/bin/env python3
"""
Deploy Lambda function using boto3 (bypasses AWS CLI SSL issues)
"""

import boto3
import sys
import os

def deploy_lambda(zip_file_path, function_name='carbontrack-api', region='eu-central-1'):
    """Deploy Lambda function using boto3"""
    
    if not os.path.exists(zip_file_path):
        print(f"❌ Error: {zip_file_path} not found")
        return False
    
    print(f"📦 Reading deployment package: {zip_file_path}")
    with open(zip_file_path, 'rb') as f:
        zip_content = f.read()
    
    size_mb = len(zip_content) / (1024 * 1024)
    print(f"   Size: {size_mb:.2f} MB")
    
    print(f"\n🚀 Deploying to Lambda function: {function_name}")
    print(f"   Region: {region}")
    
    try:
        client = boto3.client('lambda', region_name=region)
        
        response = client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print(f"\n✅ Deployment successful!")
        print(f"   Function ARN: {response['FunctionArn']}")
        print(f"   Runtime: {response['Runtime']}")
        print(f"   Code Size: {response['CodeSize']} bytes")
        print(f"   Last Modified: {response['LastModified']}")
        print(f"   Status: {response['State']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        zip_file = sys.argv[1]
    else:
        zip_file = "lambda-update.zip"
    
    success = deploy_lambda(zip_file)
    sys.exit(0 if success else 1)
