#!/bin/bash

##############################################################################
# AWS SES Email Setup Script
# Sets up email addresses for CarbonTrack email system
##############################################################################

set -e

REGION="eu-central-1"
DOMAIN="carbontracksystem.com"

echo "🔧 CarbonTrack - AWS SES Email Setup"
echo "===================================="
echo ""

# Email addresses to verify
EMAILS=(
    "noreply@${DOMAIN}"
    "support@${DOMAIN}"
    "hello@${DOMAIN}"
    "beta@${DOMAIN}"
)

echo "📧 Verifying email addresses in AWS SES..."
echo ""

for email in "${EMAILS[@]}"; do
    echo "Verifying: $email"
    
    aws ses verify-email-identity \
        --email-address "$email" \
        --region "$REGION" || echo "  ⚠️  Failed to verify $email (may already be verified)"
    
    echo "  ✅ Verification email sent to $email"
    echo ""
done

echo ""
echo "📋 Checking current SES sending quota..."
aws ses get-send-quota --region "$REGION"

echo ""
echo "📊 Listing verified email addresses..."
aws ses list-verified-email-addresses --region "$REGION"

echo ""
echo "============================================"
echo "✅ Email Setup Complete!"
echo "============================================"
echo ""
echo "📧 Verification emails have been sent to:"
for email in "${EMAILS[@]}"; do
    echo "   - $email"
done
echo ""
echo "⚠️  IMPORTANT: Check each inbox and click verification links!"
echo ""
echo "💡 Note: In SES sandbox mode:"
echo "   - Can only send to verified addresses"
echo "   - Limit of 200 emails/day, 1 email/second"
echo "   - Request production access to remove limits"
echo ""
echo "📖 To request production access:"
echo "   1. Go to AWS Console > SES > Account Dashboard"
echo "   2. Click 'Request production access'"
echo "   3. Fill out use case form"
echo "   4. Wait for approval (usually 24-48 hours)"
echo ""
