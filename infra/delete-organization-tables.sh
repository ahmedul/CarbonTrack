#!/bin/bash
# Script to delete all organization-related DynamoDB tables
# WARNING: This will permanently delete all data in these tables!

set -e

AWS_REGION="eu-central-1"

echo "WARNING: This will delete all organization tables and their data!"
echo "Region: $AWS_REGION"
echo ""

read -p "Are you sure you want to delete all organization tables? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Deletion cancelled."
    exit 0
fi

TABLES=(
    "carbontrack-organizations"
    "carbontrack-teams"
    "carbontrack-team-members"
    "carbontrack-team-goals"
    "carbontrack-challenges"
    "carbontrack-challenge-participants"
)

echo ""
echo "Deleting tables..."

for table in "${TABLES[@]}"; do
    echo "  Deleting $table..."
    aws dynamodb delete-table --table-name $table --region $AWS_REGION 2>/dev/null || echo "  (Table $table does not exist or already deleted)"
done

echo ""
echo "✓ All organization tables deleted"
echo ""
echo "To recreate tables, run:"
echo "  ./create-organization-tables.sh"
