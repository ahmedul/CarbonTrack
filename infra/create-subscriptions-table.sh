#!/bin/bash

# Create DynamoDB table for subscriptions
# Run this script to set up the subscription management table

set -e

REGION="eu-central-1"
ENVIRONMENT="prod"

echo "🗄️  Creating DynamoDB Table for Subscriptions"
echo "=============================================="
echo ""
echo "Region: ${REGION}"
echo "Environment: ${ENVIRONMENT}"
echo ""

# Table: Subscriptions
echo "📋 Creating carbontrack-subscriptions table..."

aws dynamodb create-table \
    --table-name carbontrack-subscriptions-${ENVIRONMENT} \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=tier,AttributeType=S \
        AttributeName=created_at,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=TierIndex,KeySchema=[{AttributeName=tier,KeyType=HASH},{AttributeName=created_at,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region ${REGION} \
    --tags Key=Project,Value=CarbonTrack Key=Feature,Value=Subscriptions Key=Environment,Value=${ENVIRONMENT} \
    2>/dev/null || echo "  ℹ️  Table may already exist"

echo "✅ carbontrack-subscriptions-${ENVIRONMENT} created"
echo ""

# Wait for table to be active
echo "⏳ Waiting for table to become active..."
sleep 5

# Verify table
echo ""
echo "🔍 Verifying table..."
STATUS=$(aws dynamodb describe-table --table-name "carbontrack-subscriptions-${ENVIRONMENT}" --region ${REGION} --query 'Table.TableStatus' --output text 2>/dev/null || echo "NOT_FOUND")
if [ "$STATUS" = "ACTIVE" ]; then
    echo "  ✅ carbontrack-subscriptions-${ENVIRONMENT}: ACTIVE"
else
    echo "  ⏳ carbontrack-subscriptions-${ENVIRONMENT}: $STATUS"
fi

echo ""
echo "🎉 Subscriptions table created successfully!"
echo ""
echo "📊 Table Summary:"
echo "  • carbontrack-subscriptions-${ENVIRONMENT}"
echo "    - Primary Key: user_id"
echo "    - GSI: TierIndex (tier, created_at)"
echo ""
echo "💡 Subscription Tiers:"
echo "  • FREE: Basic tracking (no CSRD access)"
echo "  • PROFESSIONAL: \$49/month (CSRD access, single entity, 3 users)"
echo "  • BUSINESS: \$149/month (Multi-entity up to 5, API access, 10 users)"
echo "  • ENTERPRISE: \$499/month (Unlimited entities, white-label, SSO, dedicated support)"
