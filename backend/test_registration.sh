#!/bin/bash

# Test script for CarbonTrack user registration

echo "🚀 Testing CarbonTrack User Registration..."
echo "==========================================="

# Test registration
echo "📝 Registering new user..."
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TempPassword123!",
    "full_name": "Test User"
  }' | jq '.'

echo ""
echo "✅ Registration request sent!"
echo ""
echo "🔍 To check if user was saved in Cognito, run:"
echo "aws cognito-idp list-users --user-pool-id eu-central-1_liszdknXy --region eu-central-1"
