#!/bin/bash

# Fix CarbonTrack Structure - Landing Page + App
# Deploys landing page at root and app at /app/

set -e

echo "🔧 Fixing CarbonTrack structure..."
echo "  - Landing page → / (root)"
echo "  - App with login → /app/"
echo ""

S3_BUCKET="carbontrack-frontend-production"
CLOUDFRONT_DIST="EUKA4HQFK6MC"
REGION="eu-central-1"

# 1. Upload landing page as root index.html
echo "📄 Deploying landing page to root..."
aws s3 cp landing.html s3://${S3_BUCKET}/index.html \
    --region ${REGION} \
    --cache-control "public, max-age=300, must-revalidate" \
    --content-type "text/html"

# 2. Upload app to /app/ directory
echo "🚀 Deploying app to /app/ directory..."
aws s3 cp frontend/index.html s3://${S3_BUCKET}/app/index.html \
    --region ${REGION} \
    --cache-control "public, max-age=0, must-revalidate" \
    --content-type "text/html"

aws s3 cp frontend/app-full.js s3://${S3_BUCKET}/app/app-full.js \
    --region ${REGION} \
    --cache-control "public, max-age=31536000"

aws s3 cp frontend/app.js s3://${S3_BUCKET}/app/app.js \
    --region ${REGION} \
    --cache-control "public, max-age=31536000"

# Upload CSRD module files
echo "🏢 Uploading CSRD Compliance Module..."
aws s3 cp frontend/csrd-dashboard.js s3://${S3_BUCKET}/app/csrd-dashboard.js \
    --region ${REGION} \
    --cache-control "public, max-age=31536000"

aws s3 cp frontend/csrd-dashboard.css s3://${S3_BUCKET}/app/csrd-dashboard.css \
    --region ${REGION} \
    --cache-control "public, max-age=31536000"

aws s3 cp frontend/subscription-gate.js s3://${S3_BUCKET}/app/subscription-gate.js \
    --region ${REGION} \
    --cache-control "public, max-age=31536000"

aws s3 cp frontend/subscription-gate.css s3://${S3_BUCKET}/app/subscription-gate.css \
    --region ${REGION} \
    --cache-control "public, max-age=31536000"

# 3. Copy assets if they exist
if [ -d "frontend/assets" ]; then
    echo "📦 Uploading assets..."
    aws s3 sync frontend/assets s3://${S3_BUCKET}/app/assets \
        --region ${REGION} \
        --cache-control "public, max-age=31536000"
fi

# 4. Invalidate CloudFront cache
echo "🔄 Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
    --distribution-id ${CLOUDFRONT_DIST} \
    --paths "/*" \
    --region us-east-1 > /dev/null

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Live URLs:"
echo "  Landing page: https://carbontracksystem.com/"
echo "  App (Login):  https://carbontracksystem.com/app/"
echo ""
echo "⏱️  Changes will propagate in 5-10 minutes"
