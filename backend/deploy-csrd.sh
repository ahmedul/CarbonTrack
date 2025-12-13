#!/bin/bash
# Quick deployment script for CSRD module to AWS Lambda
# This deploys from feature branch for testing before merge

set -e

echo "🚀 CarbonTrack CSRD Module Deployment"
echo "======================================"
echo ""

LAMBDA_FUNCTION="carbontrack-api"
REGION="eu-central-1"
DEPLOYMENT_DIR="deployment"

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the backend/ directory"
    exit 1
fi

echo "📦 Step 1: Cleaning previous deployment package..."
rm -rf $DEPLOYMENT_DIR
mkdir -p $DEPLOYMENT_DIR

echo ""
echo "📋 Step 2: Copying application code..."
cp -r app/ $DEPLOYMENT_DIR/
cp auth.py config.py middleware.py $DEPLOYMENT_DIR/ 2>/dev/null || true

echo ""
echo "📥 Step 3: Installing dependencies..."
pip install -r requirements.txt -t $DEPLOYMENT_DIR/ --quiet

echo ""
echo "🔧 Step 4: Creating Lambda handler..."
cat > $DEPLOYMENT_DIR/lambda_function.py << 'EOF'
import json
from mangum import Mangum
from app.main import app

# Mangum adapter for AWS Lambda
handler = Mangum(app)

def lambda_handler(event, context):
    return handler(event, context)
EOF

# Ensure mangum is installed
echo "📦 Installing mangum adapter..."
pip install mangum==0.17.0 -t $DEPLOYMENT_DIR/ --quiet

echo ""
echo "🗜️ Step 5: Creating deployment package..."
cd $DEPLOYMENT_DIR
zip -r ../lambda-deployment.zip . -q
cd ..

SIZE=$(du -h lambda-deployment.zip | cut -f1)
echo "   Package size: $SIZE"

echo ""
echo "☁️ Step 6: Deploying to AWS Lambda..."
echo "   Function: $LAMBDA_FUNCTION"
echo "   Region: $REGION"
echo ""

# Check if boto3 is available for Python deployment
if python3 -c "import boto3" 2>/dev/null; then
    echo "   Using Python boto3 for deployment (more reliable)..."
    python3 << PYTHON_EOF
import boto3
import sys

try:
    with open('lambda-deployment.zip', 'rb') as f:
        zip_content = f.read()
    
    client = boto3.client('lambda', region_name='$REGION')
    
    print("   Uploading function code...")
    response = client.update_function_code(
        FunctionName='$LAMBDA_FUNCTION',
        ZipFile=zip_content
    )
    
    print("")
    print("✅ Deployment successful!")
    print(f"   Function ARN: {response['FunctionArn']}")
    print(f"   Runtime: {response['Runtime']}")
    print(f"   Code Size: {response['CodeSize']} bytes")
    print(f"   Last Modified: {response['LastModified']}")
    
except Exception as e:
    print(f"❌ Deployment failed: {e}")
    sys.exit(1)
PYTHON_EOF
else
    echo "   Using AWS CLI for deployment..."
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION \
        --zip-file fileb://lambda-deployment.zip \
        --region $REGION
    
    echo ""
    echo "⏳ Waiting for function update to complete..."
    aws lambda wait function-updated \
        --function-name $LAMBDA_FUNCTION \
        --region $REGION
    
    echo "✅ Deployment successful!"
fi

echo ""
echo "🧪 Step 7: Testing CSRD endpoint..."
API_ENDPOINT="https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod"

# Test the CSRD standards endpoint (doesn't require auth)
echo "   Testing: GET $API_ENDPOINT/api/v1/csrd/standards"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" "$API_ENDPOINT/api/v1/csrd/standards")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ CSRD endpoint is live!"
    echo "   HTTP Status: $HTTP_CODE"
    echo "   Response preview:"
    echo "$BODY" | python3 -m json.tool | head -20
    echo "   ..."
else
    echo "⚠️  Endpoint returned HTTP $HTTP_CODE"
    echo "   Response: $BODY"
fi

echo ""
echo "=========================================="
echo "📊 Deployment Summary"
echo "=========================================="
echo "✅ CSRD module deployed to Lambda"
echo "✅ Function: $LAMBDA_FUNCTION ($REGION)"
echo "✅ API Endpoint: $API_ENDPOINT"
echo ""
echo "📝 CSRD Endpoints Available:"
echo "   GET  /api/v1/csrd/standards - List ESRS standards"
echo "   POST /api/v1/csrd/reports - Create new report"
echo "   GET  /api/v1/csrd/reports - List user reports"
echo "   PUT  /api/v1/csrd/reports/{id} - Update report"
echo "   POST /api/v1/csrd/reports/{id}/submit - Submit report"
echo "   GET  /api/v1/csrd/reports/{id}/export/pdf - Export PDF"
echo "   GET  /api/v1/csrd/reports/{id}/validate - Validate compliance"
echo ""
echo "🎯 Next Steps:"
echo "   1. Test endpoints with Postman or curl"
echo "   2. Build frontend CSRD UI components"
echo "   3. Perform end-to-end testing"
echo "   4. Merge feature/csrd-compliance-module to main"
echo ""
