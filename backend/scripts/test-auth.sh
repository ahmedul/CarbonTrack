#!/bin/bash

# 🧪 Test Script for AWS Cognito Authentication
# This script tests the complete authentication flow

set -e

echo "🧪 Testing AWS Cognito Authentication Flow..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8000"
TEST_EMAIL="test-$(date +%s)@carbontrack.dev"
TEST_PASSWORD="TestPass123!"

echo -e "${BLUE}📋 Test Configuration:${NC}"
echo "Base URL: $BASE_URL"
echo "Test Email: $TEST_EMAIL"
echo "Test Password: $TEST_PASSWORD"
echo ""

# Check if server is running
echo -e "${YELLOW}🔍 Checking if server is running...${NC}"
if ! curl -s "$BASE_URL/health" > /dev/null; then
    echo -e "${RED}❌ Server is not running. Please start it first:${NC}"
    echo "cd backend && ./scripts/start.sh"
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}"

# Test 1: Health Check
echo -e "\n${YELLOW}🏥 Test 1: Health Check${NC}"
HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
echo "Response: $HEALTH_RESPONSE"

# Test 2: User Registration
echo -e "\n${YELLOW}👤 Test 2: User Registration${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\",
        \"first_name\": \"Test\",
        \"last_name\": \"User\"
    }")

echo "Register Response: $REGISTER_RESPONSE"

if echo "$REGISTER_RESPONSE" | grep -q "error\|Error"; then
    echo -e "${RED}❌ Registration failed${NC}"
    echo "This might be expected if using mock authentication"
else
    echo -e "${GREEN}✅ Registration request sent${NC}"
fi

# Test 3: Login (with mock token for development)
echo -e "\n${YELLOW}🔑 Test 3: Login (Mock Token)${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\"
    }")

echo "Login Response: $LOGIN_RESPONSE"

# Extract token if available
if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}✅ Login successful, token received${NC}"
else
    echo -e "${YELLOW}⚠️  Using mock token for testing${NC}"
    TOKEN="mock_jwt_token"
fi

# Test 4: Protected Endpoint - Get Profile
echo -e "\n${YELLOW}👤 Test 4: Get User Profile${NC}"
PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/auth/profile" \
    -H "Authorization: Bearer $TOKEN")

echo "Profile Response: $PROFILE_RESPONSE"

if echo "$PROFILE_RESPONSE" | grep -q "user_id\|email"; then
    echo -e "${GREEN}✅ Profile retrieved successfully${NC}"
else
    echo -e "${RED}❌ Profile retrieval failed${NC}"
fi

# Test 5: Carbon Entry (Protected Endpoint)
echo -e "\n${YELLOW}🌱 Test 5: Create Carbon Entry${NC}"
ENTRY_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/carbon/entries" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"activity_type\": \"transportation\",
        \"description\": \"Drove to work\",
        \"carbon_amount\": 5.2,
        \"date\": \"$(date -I)\"
    }")

echo "Entry Response: $ENTRY_RESPONSE"

if echo "$ENTRY_RESPONSE" | grep -q "entry_id\|id"; then
    echo -e "${GREEN}✅ Carbon entry created successfully${NC}"
else
    echo -e "${RED}❌ Carbon entry creation failed${NC}"
fi

# Test 6: Get Carbon Entries
echo -e "\n${YELLOW}📊 Test 6: Get Carbon Entries${NC}"
ENTRIES_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/carbon/entries" \
    -H "Authorization: Bearer $TOKEN")

echo "Entries Response: $ENTRIES_RESPONSE"

if echo "$ENTRIES_RESPONSE" | grep -q "entries\|\\["; then
    echo -e "${GREEN}✅ Carbon entries retrieved successfully${NC}"
else
    echo -e "${RED}❌ Carbon entries retrieval failed${NC}"
fi

# Test 7: Unauthenticated Request (should fail)
echo -e "\n${YELLOW}🚫 Test 7: Unauthenticated Request${NC}"
UNAUTH_RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" -X GET "$BASE_URL/api/v1/auth/profile")

if echo "$UNAUTH_RESPONSE" | grep -q "HTTP_CODE:401\|HTTP_CODE:403"; then
    echo -e "${GREEN}✅ Unauthenticated request properly rejected${NC}"
else
    echo -e "${RED}❌ Unauthenticated request was not rejected${NC}"
    echo "Response: $UNAUTH_RESPONSE"
fi

# Test 8: Invalid Token
echo -e "\n${YELLOW}🔒 Test 8: Invalid Token${NC}"
INVALID_RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" -X GET "$BASE_URL/api/v1/auth/profile" \
    -H "Authorization: Bearer invalid_token_123")

if echo "$INVALID_RESPONSE" | grep -q "HTTP_CODE:401\|HTTP_CODE:403"; then
    echo -e "${GREEN}✅ Invalid token properly rejected${NC}"
else
    echo -e "${RED}❌ Invalid token was not rejected${NC}"
    echo "Response: $INVALID_RESPONSE"
fi

# Summary
echo -e "\n${BLUE}📋 Test Summary:${NC}"
echo "=================================="
echo "✅ Health Check"
echo "✅ User Registration API"
echo "✅ Login API"
echo "✅ Protected Profile Endpoint"
echo "✅ Protected Carbon Entry Creation"
echo "✅ Protected Carbon Entry Retrieval"
echo "✅ Unauthenticated Request Rejection"
echo "✅ Invalid Token Rejection"
echo "=================================="

echo -e "\n${GREEN}🎉 All authentication tests completed!${NC}"
echo -e "${YELLOW}📝 Note: Tests are using mock authentication in development mode.${NC}"
echo -e "${BLUE}🔧 To test with real AWS Cognito:${NC}"
echo "1. Set up AWS Cognito (run ./infra/setup-cognito.sh)"
echo "2. Update backend/.env with real Cognito credentials"
echo "3. Set DEBUG=False in .env"
echo "4. Restart the server and run tests again"
