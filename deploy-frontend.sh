#!/bin/bash

# CarbonTrack Frontend Deployment Script
# This script ensures the correct file structure is maintained:
# - Landing page at root (/)
# - App files in /app/ subdirectory

set -e

echo "🚀 CarbonTrack Frontend Deployment"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
S3_BUCKET="carbontrack-frontend-production"
CLOUDFRONT_ID="EUKA4HQFK6MC"

echo ""
echo "📋 Deployment Structure:"
echo "  / (root)        → Landing page (frontend/index.html)"
echo "  /app/           → Application files (frontend/app/*)"
echo ""

# Step 1: Deploy landing page to root
echo -e "${YELLOW}Step 1: Deploying landing page to root...${NC}"
aws s3 cp frontend/index.html s3://$S3_BUCKET/index.html \
    --cache-control "max-age=300" \
    --content-type "text/html"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Landing page deployed${NC}"
else
    echo -e "${RED}✗ Landing page deployment failed${NC}"
    exit 1
fi

# Step 2: Deploy app files to /app/
echo -e "${YELLOW}Step 2: Deploying app files to /app/...${NC}"
aws s3 sync frontend/app/ s3://$S3_BUCKET/app/ \
    --exclude "*.md" \
    --exclude "test*.html" \
    --exclude "debug.html" \
    --exclude "*.pyc" \
    --exclude "__pycache__/*" \
    --cache-control "no-cache" \
    --delete

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ App files deployed${NC}"
else
    echo -e "${RED}✗ App deployment failed${NC}"
    exit 1
fi

# Step 3: Invalidate CloudFront cache
echo -e "${YELLOW}Step 3: Invalidating CloudFront cache...${NC}"
INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id $CLOUDFRONT_ID \
    --paths "/" "/index.html" "/app/*" \
    --query "Invalidation.Id" \
    --output text)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Cache invalidation created: $INVALIDATION_ID${NC}"
else
    echo -e "${RED}✗ Cache invalidation failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=================================="
echo "✅ Deployment Complete!"
echo "==================================${NC}"
echo ""
echo "URLs:"
echo "  Landing page: https://carbontracksystem.com"
echo "  App:          https://carbontracksystem.com/app/"
echo ""
echo "Note: CloudFront cache invalidation in progress (~2-3 minutes)"
echo ""
