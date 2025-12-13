#!/bin/bash
# Deploy full CarbonTrack API with CSRD module using Lambda Layer
# This deployment includes all features + CSRD compliance module

set -e

echo "🚀 CarbonTrack Full API Deployment (with CSRD)"
echo "==============================================="
echo ""

LAMBDA_FUNCTION="carbontrack-api"
REGION="eu-central-1"
DEPLOYMENT_DIR="deployment-full"
S3_BUCKET="carbontrack-lambda-deploy-temp"

# Get CSRD Layer ARN
if [ -f "csrd-layer-arn.txt" ]; then
    CSRD_LAYER_ARN=$(cat csrd-layer-arn.txt)
    echo "📌 Using CSRD Layer: $CSRD_LAYER_ARN"
else
    echo "❌ Error: CSRD layer not found. Run create-csrd-layer.sh first"
    exit 1
fi

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the backend/ directory"
    exit 1
fi

echo ""
echo "📦 Step 1: Cleaning previous deployment..."
rm -rf $DEPLOYMENT_DIR
mkdir -p $DEPLOYMENT_DIR

echo ""
echo "📋 Step 2: Uncommenting CSRD imports in main.py..."
# Create a temporary version with CSRD enabled
cp main.py $DEPLOYMENT_DIR/main.py
sed -i 's/# import csrd  # Temporarily disabled/import csrd/' $DEPLOYMENT_DIR/main.py
sed -i 's/# app.include_router(csrd.router)  # Temporarily disabled/app.include_router(csrd.router)/' $DEPLOYMENT_DIR/main.py

# Copy other core files
cp auth.py config.py middleware.py csrd.py $DEPLOYMENT_DIR/ 2>/dev/null || true

# Copy app directory (includes CSRD module)
cp -r app/ $DEPLOYMENT_DIR/

echo ""
echo "📥 Step 3: Installing core dependencies (CSRD deps in layer)..."
# Create requirements WITHOUT CSRD deps (they're in the layer)
cat > /tmp/requirements-with-layer.txt << 'EOF'
# Core API
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# AWS
boto3==1.34.0
botocore==1.34.0
mangum==0.17.0

# Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# HTTP
httpx==0.27.0

# Utilities
python-dateutil==2.8.2
EOF

pip install -r /tmp/requirements-with-layer.txt -t $DEPLOYMENT_DIR/ --quiet

echo ""
echo "🗜️ Step 4: Creating deployment package..."
cd $DEPLOYMENT_DIR
zip -r ../lambda-full.zip . -q
cd ..

SIZE=$(du -h lambda-full.zip | cut -f1)
echo "   Package size: $SIZE"

echo ""
echo "☁️ Step 5: Uploading to S3..."
aws s3 cp lambda-full.zip s3://$S3_BUCKET/lambda-full.zip

echo ""
echo "🚀 Step 6: Deploying Lambda code..."
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION \
    --s3-bucket $S3_BUCKET \
    --s3-key lambda-full.zip \
    --region $REGION \
    --publish > /tmp/lambda-deploy.json

echo ""
echo "🔗 Step 7: Attaching CSRD Layer to Lambda..."
aws lambda update-function-configuration \
    --function-name $LAMBDA_FUNCTION \
    --layers $CSRD_LAYER_ARN \
    --region $REGION > /tmp/lambda-config.json

VERSION=$(cat /tmp/lambda-deploy.json | grep '"Version"' | head -1 | cut -d'"' -f4)
CODE_SIZE=$(cat /tmp/lambda-deploy.json | grep '"CodeSize"' | head -1 | cut -d':' -f2 | tr -d ' ,')

echo ""
echo "✅ Full API Deployment Complete!"
echo ""
echo "📊 Deployment Summary:"
echo "   ✅ Core API endpoints (auth, carbon, users, goals, achievements)"
echo "   ✅ Recommendations & Gamification"
echo "   ✅ Admin & Subscription management"
echo "   ✅ CSRD Compliance Module (19 endpoints)"
echo "   ✅ PDF Generation (via Layer)"
echo "   ✅ XBRL Export (via Layer)"
echo ""
echo "📦 Package Details:"
echo "   Lambda Code Size: $CODE_SIZE bytes ($SIZE)"
echo "   Lambda Version: $VERSION"
echo "   CSRD Layer: $CSRD_LAYER_ARN"
echo ""
echo "🧪 Test CSRD endpoints:"
echo "   curl https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports"
echo ""
