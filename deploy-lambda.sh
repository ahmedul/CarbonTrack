#!/bin/bash

# Quick Lambda Deployment for CSRD Module
# Deploys backend code to existing carbontrack-api Lambda function

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
LAMBDA_FUNCTION="carbontrack-api"
REGION="eu-central-1"
BACKEND_DIR="backend"
DEPLOYMENT_DIR="${BACKEND_DIR}/deployment"

print_status "🚀 Deploying CSRD Module to Lambda..."
echo "=========================================="
echo "Function: ${LAMBDA_FUNCTION}"
echo "Region: ${REGION}"
echo ""

# Check AWS credentials
print_status "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS CLI not configured. Run 'aws configure' first."
    exit 1
fi
print_success "AWS credentials valid"

# Navigate to backend directory
cd "${BACKEND_DIR}"

# Copy latest code to deployment directory
print_status "Copying latest application code..."
cp -f main.py deployment/
cp -f auth.py deployment/
cp -f config.py deployment/
cp -f middleware.py deployment/
mkdir -p deployment/app
cp -rf app/* deployment/app/
print_success "Code copied to deployment directory"

# Create combined API server file
print_status "Creating Lambda handler..."
cat > deployment/combined_api_server.py << 'EOF'
"""
CarbonTrack API Server - Lambda Handler
Includes CSRD Compliance Module
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Import routers
from app.api.v1.api import api_router
from middleware import setup_middleware

# Create FastAPI app
app = FastAPI(
    title="CarbonTrack API",
    description="Carbon Footprint Tracking and CSRD Compliance Platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Setup middleware
setup_middleware(app)

# CORS configuration for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://carbontracksystem.com",
        "https://app.carbontracksystem.com",
        "https://d3hqxe4zq6k4wl.cloudfront.net",
        "http://localhost:3000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CarbonTrack API",
        "version": "2.0.0",
        "features": ["carbon-tracking", "csrd-compliance"]
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CarbonTrack API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }

# Create Lambda handler
handler = Mangum(app)
EOF

print_success "Lambda handler created"

# Create deployment package
print_status "Creating deployment package..."
cd deployment

# Remove old zip if exists
rm -f lambda-deployment.zip

# Create zip with all files and dependencies
print_status "Packaging application and dependencies..."
zip -r9 lambda-deployment.zip . \
    -x "*.pyc" \
    -x "__pycache__/*" \
    -x "*/__pycache__/*" \
    -x "*/*/__pycache__/*" \
    -x "carbontrack-lambda.zip" \
    -x "requirements.txt" \
    -x ".DS_Store" \
    > /dev/null

PACKAGE_SIZE=$(du -h lambda-deployment.zip | cut -f1)
print_success "Deployment package created: ${PACKAGE_SIZE}"

# Upload to Lambda
print_status "Uploading to Lambda function: ${LAMBDA_FUNCTION}..."
aws lambda update-function-code \
    --function-name ${LAMBDA_FUNCTION} \
    --zip-file fileb://lambda-deployment.zip \
    --region ${REGION} \
    --output json > /tmp/lambda-update.json

if [ $? -eq 0 ]; then
    print_success "Lambda function updated successfully!"
    
    # Wait for function to be active
    print_status "Waiting for function to be active..."
    aws lambda wait function-updated \
        --function-name ${LAMBDA_FUNCTION} \
        --region ${REGION}
    
    print_success "Function is now active"
    
    # Get function details
    LAST_MODIFIED=$(jq -r '.LastModified' /tmp/lambda-update.json)
    CODE_SIZE=$(jq -r '.CodeSize' /tmp/lambda-update.json)
    CODE_SIZE_MB=$(echo "scale=2; ${CODE_SIZE}/1024/1024" | bc)
    
    echo ""
    echo "=========================================="
    print_success "🎉 CSRD Module Deployed Successfully!"
    echo "=========================================="
    echo "Function: ${LAMBDA_FUNCTION}"
    echo "Region: ${REGION}"
    echo "Last Modified: ${LAST_MODIFIED}"
    echo "Code Size: ${CODE_SIZE_MB} MB"
    echo ""
    echo "CSRD Endpoints now available at:"
    echo "  https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/standards"
    echo "  https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/deadline-calendar"
    echo "  https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports"
    echo ""
    print_status "Testing endpoint..."
else
    print_error "Failed to update Lambda function"
    exit 1
fi

cd ../..

# Test the deployment
print_status "Testing CSRD standards endpoint..."
RESPONSE=$(curl -s "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/standards")

if echo "$RESPONSE" | grep -q "E1\|ESRS"; then
    print_success "✅ CSRD endpoints are live and responding!"
    echo ""
    echo "Sample standards:"
    echo "$RESPONSE" | jq -r '.[0:2] | .[] | "  - \(.code): \(.name)"' 2>/dev/null || echo "$RESPONSE"
else
    print_warning "Endpoint deployed but response unexpected:"
    echo "$RESPONSE"
fi

echo ""
print_success "Deployment complete! 🚀"
echo ""
echo "Next steps:"
echo "  1. Test authenticated endpoints with your token"
echo "  2. Create a test CSRD report"
echo "  3. Build the CSRD frontend UI"
echo ""
