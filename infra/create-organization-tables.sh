#!/bin/bash
# Script to create all DynamoDB tables for multi-tenant organization features
# Run this script to set up the database schema for B2B team tracking

set -e

AWS_REGION="eu-central-1"
BILLING_MODE="PAY_PER_REQUEST"  # Use on-demand pricing for flexible scaling

echo "Creating DynamoDB tables for CarbonTrack Organizations..."
echo "Region: $AWS_REGION"
echo "Billing Mode: $BILLING_MODE"
echo ""

# 1. Create Organizations Table
echo "Creating carbontrack-organizations table..."
aws dynamodb create-table \
    --table-name carbontrack-organizations \
    --attribute-definitions \
        AttributeName=organization_id,AttributeType=S \
        AttributeName=admin_user_id,AttributeType=S \
        AttributeName=created_at,AttributeType=S \
    --key-schema \
        AttributeName=organization_id,KeyType=HASH \
    --billing-mode $BILLING_MODE \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"AdminUserIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"admin_user_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"created_at\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {
                    \"ProjectionType\":\"ALL\"
                }
            }
        ]" \
    --region $AWS_REGION \
    --tags Key=Project,Value=CarbonTrack Key=Environment,Value=Production

echo "✓ Organizations table created"
echo ""

# 2. Create Teams Table
echo "Creating carbontrack-teams table..."
aws dynamodb create-table \
    --table-name carbontrack-teams \
    --attribute-definitions \
        AttributeName=team_id,AttributeType=S \
        AttributeName=organization_id,AttributeType=S \
        AttributeName=name,AttributeType=S \
        AttributeName=team_lead_user_id,AttributeType=S \
        AttributeName=created_at,AttributeType=S \
    --key-schema \
        AttributeName=team_id,KeyType=HASH \
    --billing-mode $BILLING_MODE \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"OrganizationTeamsIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"name\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {
                    \"ProjectionType\":\"ALL\"
                }
            },
            {
                \"IndexName\": \"TeamLeadIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"team_lead_user_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"created_at\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {
                    \"ProjectionType\":\"ALL\"
                }
            }
        ]" \
    --region $AWS_REGION \
    --tags Key=Project,Value=CarbonTrack Key=Environment,Value=Production

echo "✓ Teams table created"
echo ""

# 3. Create Team Members Table
echo "Creating carbontrack-team-members table..."
aws dynamodb create-table \
    --table-name carbontrack-team-members \
    --attribute-definitions \
        AttributeName=team_id,AttributeType=S \
        AttributeName=user_id,AttributeType=S \
        AttributeName=organization_id,AttributeType=S \
        AttributeName=joined_at,AttributeType=S \
    --key-schema \
        AttributeName=team_id,KeyType=HASH \
        AttributeName=user_id,KeyType=RANGE \
    --billing-mode $BILLING_MODE \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"UserTeamsIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"user_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {
                    \"ProjectionType\":\"ALL\"
                }
            },
            {
                \"IndexName\": \"OrganizationMembersIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"joined_at\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {
                    \"ProjectionType\":\"ALL\"
                }
            }
        ]" \
    --region $AWS_REGION \
    --tags Key=Project,Value=CarbonTrack Key=Environment,Value=Production

echo "✓ Team Members table created"
echo ""

# 4. Create Team Goals Table
echo "Creating carbontrack-team-goals table..."
aws dynamodb create-table \
    --table-name carbontrack-team-goals \
    --attribute-definitions \
        AttributeName=goal_id,AttributeType=S \
        AttributeName=team_id,AttributeType=S \
        AttributeName=organization_id,AttributeType=S \
        AttributeName=start_date,AttributeType=S \
        AttributeName=end_date,AttributeType=S \
    --key-schema \
        AttributeName=goal_id,KeyType=HASH \
    --billing-mode $BILLING_MODE \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"TeamGoalsIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"team_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"start_date\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {
                    \"ProjectionType\":\"ALL\"
                }
            },
            {
                \"IndexName\": \"OrganizationGoalsIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"end_date\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {
                    \"ProjectionType\":\"ALL\"
                }
            }
        ]" \
    --region $AWS_REGION \
    --tags Key=Project,Value=CarbonTrack Key=Environment,Value=Production

echo "✓ Team Goals table created"
echo ""

# 5. Create Challenges Table
echo "Creating carbontrack-challenges table..."
aws dynamodb create-table \
    --table-name carbontrack-challenges \
    --attribute-definitions \
        AttributeName=challenge_id,AttributeType=S \
        AttributeName=organization_id,AttributeType=S \
        AttributeName=status,AttributeType=S \
        AttributeName=start_date,AttributeType=S \
    --key-schema \
        AttributeName=challenge_id,KeyType=HASH \
    --billing-mode $BILLING_MODE \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"OrganizationChallengesIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"start_date\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {
                    \"ProjectionType\":\"ALL\"
                }
            },
            {
                \"IndexName\": \"StatusIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"status\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"start_date\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {
                    \"ProjectionType\":\"ALL\"
                }
            }
        ]" \
    --region $AWS_REGION \
    --tags Key=Project,Value=CarbonTrack Key=Environment,Value=Production

echo "✓ Challenges table created"
echo ""

# 6. Create Challenge Participants Table
echo "Creating carbontrack-challenge-participants table..."
aws dynamodb create-table \
    --table-name carbontrack-challenge-participants \
    --attribute-definitions \
        AttributeName=challenge_id,AttributeType=S \
        AttributeName=participant_id,AttributeType=S \
        AttributeName=organization_id,AttributeType=S \
        AttributeName=joined_at,AttributeType=S \
    --key-schema \
        AttributeName=challenge_id,KeyType=HASH \
        AttributeName=participant_id,KeyType=RANGE \
    --billing-mode $BILLING_MODE \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"ParticipantChallengesIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"participant_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"joined_at\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {
                    \"ProjectionType\":\"ALL\"
                }
            },
            {
                \"IndexName\": \"OrganizationParticipantsIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"challenge_id\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {
                    \"ProjectionType\":\"ALL\"
                }
            }
        ]" \
    --region $AWS_REGION \
    --tags Key=Project,Value=CarbonTrack Key=Environment,Value=Production

echo "✓ Challenge Participants table created"
echo ""

# Wait for all tables to become active
echo "Waiting for all tables to become active..."
TABLES=(
    "carbontrack-organizations"
    "carbontrack-teams"
    "carbontrack-team-members"
    "carbontrack-team-goals"
    "carbontrack-challenges"
    "carbontrack-challenge-participants"
)

for table in "${TABLES[@]}"; do
    echo "  Waiting for $table..."
    aws dynamodb wait table-exists --table-name $table --region $AWS_REGION
    echo "  ✓ $table is active"
done

echo ""
echo "=========================================="
echo "✓ All DynamoDB tables created successfully!"
echo "=========================================="
echo ""
echo "Tables created:"
for table in "${TABLES[@]}"; do
    echo "  - $table"
done
echo ""
echo "Next steps:"
echo "  1. Update backend API with organization endpoints"
echo "  2. Test locally with seed data"
echo "  3. Update frontend with organization dashboard"
echo ""
echo "To verify tables, run:"
echo "  aws dynamodb list-tables --region $AWS_REGION"
echo ""
echo "To delete all tables (if needed), run:"
echo "  ./delete-organization-tables.sh"
