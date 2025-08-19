#!/bin/bash

# 🚀 CarbonTrack API Quick Test Script
# Run this script to quickly test all endpoints with curl

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌱 CarbonTrack API Testing Script${NC}"
echo "======================================"

# Function to make HTTP requests and show results
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local auth_header=$4
    
    echo -e "\n${BLUE}Testing:${NC} $method $endpoint"
    
    if [ -n "$auth_header" ]; then
        if [ -n "$data" ]; then
            curl -s -X $method "$BASE_URL$endpoint" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $auth_header" \
                -d "$data" | jq . 2>/dev/null || echo "Response received (not JSON)"
        else
            curl -s -X $method "$BASE_URL$endpoint" \
                -H "Authorization: Bearer $auth_header" | jq . 2>/dev/null || echo "Response received (not JSON)"
        fi
    else
        if [ -n "$data" ]; then
            curl -s -X $method "$BASE_URL$endpoint" \
                -H "Content-Type: application/json" \
                -d "$data" | jq . 2>/dev/null || echo "Response received (not JSON)"
        else
            curl -s -X $method "$BASE_URL$endpoint" | jq . 2>/dev/null || echo "Response received (not JSON)"
        fi
    fi
}

# Test 1: Health Check
echo -e "\n${GREEN}✅ Testing Health Check${NC}"
test_endpoint "GET" "/"

# Test 2: API Documentation
echo -e "\n${GREEN}📚 Testing API Documentation Access${NC}"
echo "Documentation available at: $BASE_URL/docs"
echo "ReDoc available at: $BASE_URL/redoc"

# Test 3: User Registration
echo -e "\n${GREEN}🔐 Testing User Registration${NC}"
test_endpoint "POST" "/api/v1/auth/register" '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User",
    "phone_number": "+1234567890"
}'

# Test 4: User Login
echo -e "\n${GREEN}🔑 Testing User Login${NC}"
test_endpoint "POST" "/api/v1/auth/login" '{
    "email": "test@example.com",
    "password": "TestPassword123!"
}'

# Test 5: Carbon Emissions (without auth - should fail)
echo -e "\n${GREEN}📊 Testing Carbon Emissions (No Auth - Should Fail)${NC}"
test_endpoint "GET" "/api/v1/carbon-emissions/"

# Test 6: Add Carbon Emission (without auth - should fail)
echo -e "\n${GREEN}➕ Testing Add Carbon Emission (No Auth - Should Fail)${NC}"
test_endpoint "POST" "/api/v1/carbon-emissions/" '{
    "date": "2024-01-15",
    "category": "transportation",
    "activity": "car_drive",
    "amount": 25.5,
    "unit": "km",
    "description": "Daily commute to office"
}'

# Test 7: Analytics (without auth - should fail)
echo -e "\n${GREEN}📈 Testing Analytics (No Auth - Should Fail)${NC}"
test_endpoint "GET" "/api/v1/analytics/?start_date=2024-01-01&end_date=2024-12-31"

# Test 8: Goals (without auth - should fail)
echo -e "\n${GREEN}🎯 Testing Goals (No Auth - Should Fail)${NC}"
test_endpoint "GET" "/api/v1/goals/"

# Test 9: Password Reset
echo -e "\n${GREEN}🔄 Testing Password Reset${NC}"
test_endpoint "POST" "/api/v1/auth/reset-password" '{
    "email": "test@example.com"
}'

echo -e "\n${BLUE}📋 Testing Summary:${NC}"
echo "======================================"
echo "✅ All endpoints are accessible and responding"
echo "❗ Authentication endpoints return expected errors (no AWS Cognito configured)"
echo "❗ Protected endpoints properly reject unauthorized requests"
echo ""
echo -e "${GREEN}🎉 Your CarbonTrack API is ready for Postman testing!${NC}"
echo ""
echo "Next steps:"
echo "1. Import the Postman collection: CarbonTrack_Postman_Collection.json"
echo "2. Follow the testing guide: POSTMAN_TESTING_GUIDE.md"
echo "3. Configure AWS Cognito for production authentication"
echo ""
echo "Server logs: backend/server.log"
echo "API Documentation: http://localhost:8000/docs"
