#!/bin/bash

# Create DynamoDB tables for CSRD Compliance Module
# Run this script to set up the database schema

set -e

REGION="eu-central-1"
ENVIRONMENT="prod"

echo "🗄️  Creating DynamoDB Tables for CSRD Module"
echo "=============================================="
echo ""
echo "Region: ${REGION}"
echo "Environment: ${ENVIRONMENT}"
echo ""

# Table 1: CSRD Reports
echo "📋 Creating carbontrack-csrd-reports table..."

aws dynamodb create-table \
    --table-name carbontrack-csrd-reports-${ENVIRONMENT} \
    --attribute-definitions \
        AttributeName=report_id,AttributeType=S \
        AttributeName=company_id,AttributeType=S \
        AttributeName=reporting_year,AttributeType=N \
        AttributeName=created_at,AttributeType=S \
    --key-schema \
        AttributeName=report_id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=CompanyYearIndex,KeySchema=[{AttributeName=company_id,KeyType=HASH},{AttributeName=reporting_year,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
        "IndexName=CompanyCreatedIndex,KeySchema=[{AttributeName=company_id,KeyType=HASH},{AttributeName=created_at,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region ${REGION} \
    --tags Key=Project,Value=CarbonTrack Key=Feature,Value=CSRD Key=Environment,Value=${ENVIRONMENT} \
    2>/dev/null || echo "  ℹ️  Table may already exist"

echo "✅ carbontrack-csrd-reports-${ENVIRONMENT} created"
echo ""

# Table 2: CSRD Audit Trail
echo "📋 Creating carbontrack-csrd-audit-trail table..."

aws dynamodb create-table \
    --table-name carbontrack-csrd-audit-trail-${ENVIRONMENT} \
    --attribute-definitions \
        AttributeName=entry_id,AttributeType=S \
        AttributeName=report_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=entry_id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=ReportTimeIndex,KeySchema=[{AttributeName=report_id,KeyType=HASH},{AttributeName=timestamp,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region ${REGION} \
    --tags Key=Project,Value=CarbonTrack Key=Feature,Value=CSRD Key=Environment,Value=${ENVIRONMENT} \
    2>/dev/null || echo "  ℹ️  Table may already exist"

echo "✅ carbontrack-csrd-audit-trail-${ENVIRONMENT} created"
echo ""

# Table 3: CSRD Metrics History (for trend analysis)
echo "📋 Creating carbontrack-csrd-metrics-history table..."

aws dynamodb create-table \
    --table-name carbontrack-csrd-metrics-history-${ENVIRONMENT} \
    --attribute-definitions \
        AttributeName=metric_id,AttributeType=S \
        AttributeName=company_id,AttributeType=S \
        AttributeName=date,AttributeType=S \
    --key-schema \
        AttributeName=metric_id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=CompanyDateIndex,KeySchema=[{AttributeName=company_id,KeyType=HASH},{AttributeName=date,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region ${REGION} \
    --tags Key=Project,Value=CarbonTrack Key=Feature,Value=CSRD Key=Environment,Value=${ENVIRONMENT} \
    2>/dev/null || echo "  ℹ️  Table may already exist"

echo "✅ carbontrack-csrd-metrics-history-${ENVIRONMENT} created"
echo ""

# Wait for tables to be active
echo "⏳ Waiting for tables to become active..."
sleep 5

# Verify tables
echo ""
echo "🔍 Verifying tables..."
for table in "carbontrack-csrd-reports-${ENVIRONMENT}" "carbontrack-csrd-audit-trail-${ENVIRONMENT}" "carbontrack-csrd-metrics-history-${ENVIRONMENT}"; do
    STATUS=$(aws dynamodb describe-table --table-name "$table" --region ${REGION} --query 'Table.TableStatus' --output text 2>/dev/null || echo "NOT_FOUND")
    if [ "$STATUS" = "ACTIVE" ]; then
        echo "  ✅ $table: ACTIVE"
    else
        echo "  ⏳ $table: $STATUS"
    fi
done

echo ""
echo "🎉 DynamoDB tables created successfully!"
echo ""
echo "📊 Table Summary:"
echo "  • carbontrack-csrd-reports-${ENVIRONMENT}"
echo "    - Primary Key: report_id"
echo "    - GSI: CompanyYearIndex (company_id, reporting_year)"
echo "    - GSI: CompanyCreatedIndex (company_id, created_at)"
echo ""
echo "  • carbontrack-csrd-audit-trail-${ENVIRONMENT}"
echo "    - Primary Key: entry_id"
echo "    - GSI: ReportTimeIndex (report_id, timestamp)"
echo ""
echo "  • carbontrack-csrd-metrics-history-${ENVIRONMENT}"
echo "    - Primary Key: metric_id"
echo "    - GSI: CompanyDateIndex (company_id, date)"
echo ""
echo "💡 Next steps:"
echo "  1. Update Lambda execution role with DynamoDB permissions"
echo "  2. Deploy updated backend with database integration"
echo "  3. Test CSRD endpoints with real data"
