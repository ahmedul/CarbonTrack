#!/bin/bash

# 🔐 AWS Cognito Setup Script for CarbonTrack
# This script creates the necessary AWS Cognito infrastructure

set -e

echo "🌱 Setting up AWS Cognito for CarbonTrack..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
POOL_NAME="CarbonTrack-Users"
CLIENT_NAME="CarbonTrack-Client"
REGION="eu-central-1"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS CLI is not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Current AWS Identity:${NC}"
aws sts get-caller-identity

echo -e "\n${YELLOW}🔧 Creating Cognito User Pool...${NC}"

# Create User Pool
USER_POOL_OUTPUT=$(aws cognito-idp create-user-pool \
    --pool-name "$POOL_NAME" \
    --policies '{
        "PasswordPolicy": {
            "MinimumLength": 8,
            "RequireUppercase": true,
            "RequireLowercase": true,
            "RequireNumbers": true,
            "RequireSymbols": false
        }
    }' \
    --auto-verified-attributes email \
    --username-attributes email \
    --verification-message-template '{
        "DefaultEmailOption": "CONFIRM_WITH_CODE",
        "EmailSubject": "Welcome to CarbonTrack - Verify your email",
        "EmailMessage": "Welcome to CarbonTrack! Your verification code is {####}"
    }' \
    --admin-create-user-config '{
        "AllowAdminCreateUserOnly": false,
        "InviteMessageTemplate": {
            "EmailSubject": "Welcome to CarbonTrack",
            "EmailMessage": "Welcome to CarbonTrack! Your username is {username} and temporary password is {####}"
        }
    }' \
    --region "$REGION")

USER_POOL_ID=$(echo "$USER_POOL_OUTPUT" | jq -r '.UserPool.Id')
echo -e "${GREEN}✅ User Pool created: $USER_POOL_ID${NC}"

echo -e "\n${YELLOW}🔧 Creating User Pool Client...${NC}"

# Create User Pool Client
CLIENT_OUTPUT=$(aws cognito-idp create-user-pool-client \
    --user-pool-id "$USER_POOL_ID" \
    --client-name "$CLIENT_NAME" \
    --generate-secret \
    --explicit-auth-flows ALLOW_ADMIN_USER_PASSWORD_AUTH ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH \
    --supported-identity-providers COGNITO \
    --read-attributes email \
    --write-attributes email \
    --region "$REGION")

CLIENT_ID=$(echo "$CLIENT_OUTPUT" | jq -r '.UserPoolClient.ClientId')
CLIENT_SECRET=$(echo "$CLIENT_OUTPUT" | jq -r '.UserPoolClient.ClientSecret')

echo -e "${GREEN}✅ User Pool Client created: $CLIENT_ID${NC}"

echo -e "\n${YELLOW}🔧 Creating User Pool Domain...${NC}"

# Create a domain for hosted UI (optional but useful)
DOMAIN_NAME="carbontrack-$(date +%s)"
aws cognito-idp create-user-pool-domain \
    --domain "$DOMAIN_NAME" \
    --user-pool-id "$USER_POOL_ID" \
    --region "$REGION" || echo -e "${YELLOW}⚠️  Domain creation failed (might already exist)${NC}"

echo -e "\n${GREEN}🎉 AWS Cognito setup completed!${NC}"
echo -e "\n${BLUE}📋 Configuration Details:${NC}"
echo "----------------------------------------"
echo "AWS_REGION=$REGION"
echo "COGNITO_USER_POOL_ID=$USER_POOL_ID"
echo "COGNITO_CLIENT_ID=$CLIENT_ID"
echo "COGNITO_CLIENT_SECRET=$CLIENT_SECRET"
echo "COGNITO_DOMAIN=$DOMAIN_NAME.auth.$REGION.amazoncognito.com"
echo "----------------------------------------"

echo -e "\n${YELLOW}📝 Next Steps:${NC}"
echo "1. Update your .env file with the above values"
echo "2. Restart your FastAPI server"
echo "3. Test the authentication endpoints"

# Save configuration to a file
cat > ../backend/aws-cognito-config.txt << EOF
# AWS Cognito Configuration for CarbonTrack
# Generated on $(date)

AWS_REGION=$REGION
COGNITO_USER_POOL_ID=$USER_POOL_ID
COGNITO_CLIENT_ID=$CLIENT_ID
COGNITO_CLIENT_SECRET=$CLIENT_SECRET
COGNITO_DOMAIN=$DOMAIN_NAME.auth.$REGION.amazoncognito.com

# Copy these values to your .env file
EOF

echo -e "\n${GREEN}💾 Configuration saved to backend/aws-cognito-config.txt${NC}"
echo -e "${BLUE}🔗 Hosted UI URL: https://$DOMAIN_NAME.auth.$REGION.amazoncognito.com/login?client_id=$CLIENT_ID&response_type=code&scope=email+openid&redirect_uri=http://localhost:8000/callback${NC}"
