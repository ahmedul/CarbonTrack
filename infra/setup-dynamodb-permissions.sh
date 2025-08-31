#!/bin/bash

# Add DynamoDB permissions to the carbontrack-dev IAM user

echo "🔐 Adding DynamoDB permissions to carbontrack-dev user..."
echo "=========================================================="

# IAM policy for DynamoDB access
POLICY_NAME="CarbonTrackDynamoDBPolicy"
USER_NAME="carbontrack-dev"

# Create DynamoDB policy document
cat > /tmp/dynamodb-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:CreateTable",
                "dynamodb:DeleteTable",
                "dynamodb:DescribeTable",
                "dynamodb:ListTables",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:DescribeTimeToLive",
                "dynamodb:PutItem",
                "dynamodb:DescribeReservedCapacity",
                "dynamodb:DescribeReservedCapacityOfferings",
                "dynamodb:ListTagsOfResource",
                "dynamodb:DescribeStream",
                "dynamodb:GetRecords",
                "dynamodb:GetShardIterator",
                "dynamodb:DescribeStream",
                "dynamodb:ListStreams"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/carbontrack-*",
                "arn:aws:dynamodb:*:*:table/carbontrack-*/index/*",
                "arn:aws:dynamodb:*:*:table/carbontrack-*/stream/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:ListTables",
                "dynamodb:DescribeLimits"
            ],
            "Resource": "*"
        }
    ]
}
EOF

echo "📋 Creating DynamoDB policy..."

# Create the policy
POLICY_ARN=$(aws iam create-policy \
    --policy-name "$POLICY_NAME" \
    --policy-document file:///tmp/dynamodb-policy.json \
    --description "DynamoDB access policy for CarbonTrack application" \
    --query 'Policy.Arn' \
    --output text 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Policy created: $POLICY_ARN"
else
    # Policy might already exist, try to get its ARN
    POLICY_ARN=$(aws iam list-policies \
        --query "Policies[?PolicyName=='$POLICY_NAME'].Arn" \
        --output text)
    
    if [ ! -z "$POLICY_ARN" ]; then
        echo "ℹ️  Policy already exists: $POLICY_ARN"
    else
        echo "❌ Failed to create or find policy"
        exit 1
    fi
fi

echo "🔗 Attaching policy to user: $USER_NAME"

# Attach policy to user
aws iam attach-user-policy \
    --user-name "$USER_NAME" \
    --policy-arn "$POLICY_ARN"

if [ $? -eq 0 ]; then
    echo "✅ Policy attached successfully!"
else
    echo "❌ Failed to attach policy to user"
    exit 1
fi

# Clean up temporary file
rm -f /tmp/dynamodb-policy.json

echo ""
echo "🎉 DynamoDB permissions configured successfully!"
echo ""
echo "📋 Permissions granted:"
echo "  • Create/Delete DynamoDB tables"
echo "  • Read/Write data to carbontrack-* tables"
echo "  • Query and scan operations"
echo "  • Batch operations"
echo ""
echo "🚀 You can now run the table creation script:"
echo "  ./infra/create-dynamodb-tables.sh"
