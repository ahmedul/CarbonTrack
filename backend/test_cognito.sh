#!/bin/bash

# AWS Cognito Testing Script for CarbonTrack API
# Make sure your FastAPI server is running on http://localhost:8000

BASE_URL="http://localhost:8000/api/v1"
EMAIL="test$(date +%s)@example.com"  # Unique email for each test
PASSWORD="TempPassword123!"
NAME="Test User"

echo "🧪 Starting AWS Cognito Integration Tests"
echo "========================================"
echo "Base URL: $BASE_URL"
echo "Test Email: $EMAIL"
echo ""

# Step 1: Register User
echo "📝 Step 1: Registering new user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"name\": \"$NAME\"
  }")

echo "Registration Response:"
echo $REGISTER_RESPONSE | jq '.' 2>/dev/null || echo $REGISTER_RESPONSE
echo ""

# Extract user_id if available
USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.user_id // empty' 2>/dev/null)
if [ ! -z "$USER_ID" ]; then
    echo "✅ User registered successfully with ID: $USER_ID"
else
    echo "❌ Registration failed or user_id not found"
fi
echo ""

# Step 2: Manual confirmation step
echo "📧 Step 2: Email Confirmation Required"
echo "Check your email ($EMAIL) for the confirmation code from AWS Cognito"
echo "Then run the confirmation command manually:"
echo ""
echo "curl -X POST \"$BASE_URL/auth/confirm\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"email\": \"$EMAIL\", \"confirmation_code\": \"YOUR_CODE_HERE\"}'"
echo ""

# Step 3: Login (will work after confirmation)
echo "🔐 Step 3: Login (run after email confirmation)"
echo "curl -X POST \"$BASE_URL/auth/login\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}'"
echo ""

# Step 4: Test protected endpoint
echo "🛡️  Step 4: Test protected endpoint (run after login)"
echo "Replace YOUR_ACCESS_TOKEN with the token from login response:"
echo ""
echo "curl -X GET \"$BASE_URL/carbon-emissions/\" \\"
echo "  -H \"Authorization: Bearer YOUR_ACCESS_TOKEN\""
echo ""

echo "🎯 Testing completed! Follow the manual steps above to complete the flow."
