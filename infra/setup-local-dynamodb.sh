#!/bin/bash
# Script to set up local DynamoDB for testing organization features
# This creates tables in DynamoDB Local (docker) for development

set -e

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

DYNAMODB_PORT=8000
DYNAMODB_LOCAL_ENDPOINT="http://localhost:$DYNAMODB_PORT"

echo "Setting up Local DynamoDB for CarbonTrack..."
echo "Endpoint: $DYNAMODB_LOCAL_ENDPOINT"
echo ""

# Check if DynamoDB Local container is already running
if docker ps | grep -q "dynamodb-local"; then
    echo "DynamoDB Local is already running"
else
    echo "Starting DynamoDB Local container..."
    docker run -d -p $DYNAMODB_PORT:8000 --name dynamodb-local amazon/dynamodb-local
    echo "✓ DynamoDB Local started on port $DYNAMODB_PORT"
    sleep 3
fi

echo ""
echo "Creating tables in local DynamoDB..."

# Helper function to create table
create_local_table() {
    local table_name=$1
    echo "  Creating $table_name..."
}

# 1. Create Organizations Table
create_local_table "carbontrack-organizations"
aws dynamodb create-table \
    --table-name carbontrack-organizations \
    --attribute-definitions \
        AttributeName=organization_id,AttributeType=S \
        AttributeName=admin_user_id,AttributeType=S \
        AttributeName=created_at,AttributeType=S \
    --key-schema \
        AttributeName=organization_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"AdminUserIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"admin_user_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"created_at\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            }
        ]" \
    --endpoint-url $DYNAMODB_LOCAL_ENDPOINT \
    --region us-east-1 > /dev/null

echo "  ✓ Organizations table created"

# 2. Create Teams Table
create_local_table "carbontrack-teams"
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
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"OrganizationTeamsIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"name\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            },
            {
                \"IndexName\": \"TeamLeadIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"team_lead_user_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"created_at\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            }
        ]" \
    --endpoint-url $DYNAMODB_LOCAL_ENDPOINT \
    --region us-east-1 > /dev/null

echo "  ✓ Teams table created"

# 3. Create Team Members Table
create_local_table "carbontrack-team-members"
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
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"UserTeamsIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"user_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            },
            {
                \"IndexName\": \"OrganizationMembersIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"joined_at\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            }
        ]" \
    --endpoint-url $DYNAMODB_LOCAL_ENDPOINT \
    --region us-east-1 > /dev/null

echo "  ✓ Team Members table created"

# 4. Create Team Goals Table
create_local_table "carbontrack-team-goals"
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
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"TeamGoalsIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"team_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"start_date\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            },
            {
                \"IndexName\": \"OrganizationGoalsIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"end_date\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            }
        ]" \
    --endpoint-url $DYNAMODB_LOCAL_ENDPOINT \
    --region us-east-1 > /dev/null

echo "  ✓ Team Goals table created"

# 5. Create Challenges Table
create_local_table "carbontrack-challenges"
aws dynamodb create-table \
    --table-name carbontrack-challenges \
    --attribute-definitions \
        AttributeName=challenge_id,AttributeType=S \
        AttributeName=organization_id,AttributeType=S \
        AttributeName=status,AttributeType=S \
        AttributeName=start_date,AttributeType=S \
    --key-schema \
        AttributeName=challenge_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"OrganizationChallengesIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"start_date\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            },
            {
                \"IndexName\": \"StatusIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"status\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"start_date\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            }
        ]" \
    --endpoint-url $DYNAMODB_LOCAL_ENDPOINT \
    --region us-east-1 > /dev/null

echo "  ✓ Challenges table created"

# 6. Create Challenge Participants Table
create_local_table "carbontrack-challenge-participants"
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
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"ParticipantChallengesIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"participant_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"joined_at\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            },
            {
                \"IndexName\": \"OrganizationParticipantsIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"challenge_id\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            }
        ]" \
    --endpoint-url $DYNAMODB_LOCAL_ENDPOINT \
    --region us-east-1 > /dev/null

echo "  ✓ Challenge Participants table created"

# Also create existing tables for full local testing
echo ""
echo "Creating existing CarbonTrack tables..."

# Users table
create_local_table "carbontrack-users"
aws dynamodb create-table \
    --table-name carbontrack-users \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=email,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"EmailIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"email\",\"KeyType\":\"HASH\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            }
        ]" \
    --endpoint-url $DYNAMODB_LOCAL_ENDPOINT \
    --region us-east-1 > /dev/null

echo "  ✓ Users table created"

# Emissions table
create_local_table "carbontrack-entries"
aws dynamodb create-table \
    --table-name carbontrack-entries \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=entry_id,AttributeType=S \
        AttributeName=organization_id,AttributeType=S \
        AttributeName=date,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=entry_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"OrganizationIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"organization_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"date\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            }
        ]" \
    --endpoint-url $DYNAMODB_LOCAL_ENDPOINT \
    --region us-east-1 > /dev/null

echo "  ✓ Entries table created"

echo ""
echo "=========================================="
echo "✓ Local DynamoDB setup complete!"
echo "=========================================="
echo ""
echo "Tables created in local DynamoDB:"
echo "  - carbontrack-organizations"
echo "  - carbontrack-teams"
echo "  - carbontrack-team-members"
echo "  - carbontrack-team-goals"
echo "  - carbontrack-challenges"
echo "  - carbontrack-challenge-participants"
echo "  - carbontrack-users"
echo "  - carbontrack-entries"
echo ""
echo "Endpoint: $DYNAMODB_LOCAL_ENDPOINT"
echo ""
echo "To list tables:"
echo "  aws dynamodb list-tables --endpoint-url $DYNAMODB_LOCAL_ENDPOINT --region us-east-1"
echo ""
echo "To stop DynamoDB Local:"
echo "  docker stop dynamodb-local"
echo ""
echo "To start it again:"
echo "  docker start dynamodb-local"
echo ""
echo "To remove the container:"
echo "  docker rm -f dynamodb-local"
echo ""
echo "Next steps:"
echo "  1. Run seed data script: python scripts/seed_organization_data.py"
echo "  2. Configure backend to use local endpoint"
echo "  3. Start backend server: cd backend && uvicorn combined_api_server:app --reload"
