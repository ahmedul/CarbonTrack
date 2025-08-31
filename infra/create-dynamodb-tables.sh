#!/bin/bash

# DynamoDB Table Creation Script for CarbonTrack
# This script creates all required DynamoDB tables for the CarbonTrack application

set -e

echo "🚀 Creating DynamoDB tables for CarbonTrack..."
echo "================================================"

# Configuration
REGION="eu-central-1"
BILLING_MODE="PAY_PER_REQUEST"  # Good for development, can change to PROVISIONED for production

# Function to create table with error handling
create_table() {
    local table_name=$1
    local partition_key=$2
    local sort_key=$3
    local key_schema=""
    local attribute_definitions=""
    
    # Build key schema and attribute definitions
    key_schema="AttributeName=${partition_key},KeyType=HASH"
    attribute_definitions="AttributeName=${partition_key},AttributeType=S"
    
    if [ ! -z "$sort_key" ]; then
        key_schema="${key_schema} AttributeName=${sort_key},KeyType=RANGE"
        attribute_definitions="${attribute_definitions} AttributeName=${sort_key},AttributeType=S"
    fi
    
    echo "📝 Creating table: $table_name"
    
    # Check if table already exists
    if aws dynamodb describe-table --table-name "$table_name" --region "$REGION" >/dev/null 2>&1; then
        echo "⚠️  Table $table_name already exists, skipping..."
        return 0
    fi
    
    # Create the table
    aws dynamodb create-table \
        --table-name "$table_name" \
        --key-schema $key_schema \
        --attribute-definitions $attribute_definitions \
        --billing-mode "$BILLING_MODE" \
        --region "$REGION" \
        --output table
    
    if [ $? -eq 0 ]; then
        echo "✅ Table $table_name created successfully"
    else
        echo "❌ Failed to create table $table_name"
        exit 1
    fi
    
    echo ""
}

echo "Creating tables with the following configuration:"
echo "Region: $REGION"
echo "Billing Mode: $BILLING_MODE"
echo ""

# 1. Users table - Stores user profiles
# Partition Key: userId (String)
create_table "carbontrack-users" "userId"

# 2. CarbonData table - Stores carbon footprint entries
# Partition Key: userId (String)
# Sort Key: timestamp (String) - ISO datetime string for sorting by time
create_table "carbontrack-entries" "userId" "timestamp"

# 3. Goals table - Stores user carbon reduction goals
# Partition Key: userId (String)
# Sort Key: goalId (String)
create_table "carbontrack-goals" "userId" "goalId"

# 4. Achievements table - Stores user achievements
# Partition Key: userId (String)
# Sort Key: achievementId (String)
create_table "carbontrack-achievements" "userId" "achievementId"

echo "🎉 All DynamoDB tables created successfully!"
echo ""
echo "📊 Table Summary:"
echo "1. carbontrack-users (userId)"
echo "2. carbontrack-entries (userId, timestamp)"
echo "3. carbontrack-goals (userId, goalId)"
echo "4. carbontrack-achievements (userId, achievementId)"
echo ""
echo "🔗 Next steps:"
echo "1. Wait for tables to become ACTIVE"
echo "2. Run test Lambda function"
echo "3. Test read/write operations"
echo ""

# Wait for tables to become active
echo "⏳ Waiting for tables to become ACTIVE..."
aws dynamodb wait table-exists --table-name "carbontrack-users" --region "$REGION"
aws dynamodb wait table-exists --table-name "carbontrack-entries" --region "$REGION"
aws dynamodb wait table-exists --table-name "carbontrack-goals" --region "$REGION"
aws dynamodb wait table-exists --table-name "carbontrack-achievements" --region "$REGION"

echo "✅ All tables are now ACTIVE and ready for use!"
