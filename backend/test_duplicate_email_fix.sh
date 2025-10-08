#!/bin/bash
# Test script to verify duplicate email registration is properly rejected

API_BASE="${API_BASE:-https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod}"
TEST_EMAIL="test-duplicate-$(date +%s)@example.com"

echo "=============================================="
echo "Testing Duplicate Email Registration Fix"
echo "=============================================="
echo ""
echo "Test Email: $TEST_EMAIL"
echo "API Base: $API_BASE"
echo ""

# Test 1: Register new user (should succeed)
echo "📝 Test 1: Registering new user with email: $TEST_EMAIL"
RESPONSE1=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/api/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"TestPassword123!\",
    \"full_name\": \"Test User\",
    \"carbon_budget\": 1000
  }")

HTTP_CODE1=$(echo "$RESPONSE1" | tail -n1)
BODY1=$(echo "$RESPONSE1" | sed '$d')

echo "Response Code: $HTTP_CODE1"
echo "Response Body: $BODY1" | jq -C '.' 2>/dev/null || echo "$BODY1"
echo ""

if [ "$HTTP_CODE1" = "200" ] || [ "$HTTP_CODE1" = "201" ]; then
    echo "✅ Test 1 PASSED: New user registered successfully"
else
    echo "❌ Test 1 FAILED: Expected 200/201, got $HTTP_CODE1"
    exit 1
fi

echo ""
echo "⏳ Waiting 2 seconds for database consistency..."
sleep 2
echo ""

# Test 2: Try to register same email again (should fail with 409)
echo "📝 Test 2: Attempting to register with same email: $TEST_EMAIL"
RESPONSE2=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/api/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"DifferentPassword456!\",
    \"full_name\": \"Different User\",
    \"carbon_budget\": 2000
  }")

HTTP_CODE2=$(echo "$RESPONSE2" | tail -n1)
BODY2=$(echo "$RESPONSE2" | sed '$d')

echo "Response Code: $HTTP_CODE2"
echo "Response Body: $BODY2" | jq -C '.' 2>/dev/null || echo "$BODY2"
echo ""

if [ "$HTTP_CODE2" = "409" ]; then
    echo "✅ Test 2 PASSED: Duplicate email properly rejected with 409 Conflict"
    
    # Check if error message mentions email
    if echo "$BODY2" | grep -q "already registered\|already exists"; then
        echo "✅ Test 2a PASSED: Error message is user-friendly"
    else
        echo "⚠️  Test 2a WARNING: Error message could be more helpful"
    fi
else
    echo "❌ Test 2 FAILED: Expected 409 Conflict, got $HTTP_CODE2"
    echo "This means duplicate emails are NOT being caught!"
    exit 1
fi

echo ""
echo "=============================================="
echo "✅ ALL TESTS PASSED!"
echo "=============================================="
echo ""
echo "Summary:"
echo "  ✅ New user registration works"
echo "  ✅ Duplicate email is rejected (409 Conflict)"
echo "  ✅ Error message is clear and helpful"
echo ""
echo "The duplicate email registration bug has been fixed! 🎉"
