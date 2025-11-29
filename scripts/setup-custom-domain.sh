#!/bin/bash

# CarbonTrack Custom Domain Setup Script
# Usage: ./setup-custom-domain.sh <domain-name>

set -e

DOMAIN_NAME="${1:-carbontrack.com}"
CLOUDFRONT_ID="EUKA4HQFK6MC"
CLOUDFRONT_DOMAIN="d2z2og1o0b9esb.cloudfront.net"
SUBDOMAIN="app"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN_NAME}"

echo "🌐 CarbonTrack Custom Domain Setup"
echo "=================================="
echo ""
echo "Domain: ${DOMAIN_NAME}"
echo "Subdomain: ${FULL_DOMAIN}"
echo "CloudFront: ${CLOUDFRONT_DOMAIN}"
echo ""

# Check if domain is available
echo "📋 Step 1: Checking domain availability..."
if aws route53domains check-domain-availability --domain-name "${DOMAIN_NAME}" --query 'Availability' --output text 2>/dev/null | grep -q "AVAILABLE"; then
    echo "✅ Domain ${DOMAIN_NAME} is available!"
    echo ""
    echo "💰 Price: ~\$12-13/year for .com domain"
    echo ""
    read -p "Do you want to register this domain? (yes/no): " REGISTER
    
    if [ "$REGISTER" = "yes" ]; then
        echo "⚠️  Manual step required:"
        echo "   Go to: https://console.aws.amazon.com/route53/home#DomainRegistration:"
        echo "   Search for: ${DOMAIN_NAME}"
        echo "   Complete registration with your details"
        echo ""
        read -p "Press Enter after registering the domain..."
    fi
else
    echo "ℹ️  Domain ${DOMAIN_NAME} is not available or already owned"
    echo "   Proceeding with DNS setup (assuming you own it)..."
fi

# Step 2: Request SSL Certificate
echo ""
echo "🔒 Step 2: Requesting SSL Certificate..."
echo "   Region: us-east-1 (required for CloudFront)"

CERT_ARN=$(aws acm request-certificate \
    --domain-name "${DOMAIN_NAME}" \
    --subject-alternative-names "*.${DOMAIN_NAME}" \
    --validation-method DNS \
    --region us-east-1 \
    --query 'CertificateArn' \
    --output text 2>/dev/null || echo "")

if [ -n "$CERT_ARN" ]; then
    echo "✅ Certificate requested: ${CERT_ARN}"
    echo ""
    echo "📋 Step 3: DNS Validation Required"
    echo ""
    echo "Get validation records:"
    echo "   aws acm describe-certificate --certificate-arn ${CERT_ARN} --region us-east-1"
    echo ""
    echo "⚠️  Manual step:"
    echo "   1. Copy the CNAME record from above command"
    echo "   2. Add it to your domain's DNS (Route53 or external registrar)"
    echo "   3. Wait 5-10 minutes for validation"
    echo ""
    
    # Try to create validation records in Route53 if hosted zone exists
    HOSTED_ZONE_ID=$(aws route53 list-hosted-zones --query "HostedZones[?Name=='${DOMAIN_NAME}.'].Id" --output text 2>/dev/null | cut -d'/' -f3 || echo "")
    
    if [ -n "$HOSTED_ZONE_ID" ]; then
        echo "✅ Found Route53 hosted zone: ${HOSTED_ZONE_ID}"
        echo "   Attempting automatic validation..."
        
        # Get validation records
        VALIDATION_JSON=$(aws acm describe-certificate \
            --certificate-arn "${CERT_ARN}" \
            --region us-east-1 \
            --query 'Certificate.DomainValidationOptions[0].ResourceRecord' \
            --output json)
        
        VALIDATION_NAME=$(echo "$VALIDATION_JSON" | jq -r '.Name')
        VALIDATION_VALUE=$(echo "$VALIDATION_JSON" | jq -r '.Value')
        
        # Create DNS record for validation
        cat > /tmp/route53-validation.json << EOFINNER
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "${VALIDATION_NAME}",
      "Type": "CNAME",
      "TTL": 300,
      "ResourceRecords": [{"Value": "${VALIDATION_VALUE}"}]
    }
  }]
}
EOFINNER
        
        aws route53 change-resource-record-sets \
            --hosted-zone-id "${HOSTED_ZONE_ID}" \
            --change-batch file:///tmp/route53-validation.json
        
        echo "✅ Validation record created in Route53"
        echo "   Waiting for certificate validation (this may take 5-10 minutes)..."
        
        aws acm wait certificate-validated --certificate-arn "${CERT_ARN}" --region us-east-1
        echo "✅ Certificate validated!"
    fi
else
    echo "ℹ️  Certificate may already exist. Listing certificates..."
    aws acm list-certificates --region us-east-1 --query 'CertificateSummaryList[*].[DomainName,CertificateArn,Status]' --output table
    echo ""
    read -p "Enter certificate ARN (or press Enter to skip): " CERT_ARN
fi

# Step 4: Update CloudFront with custom domain
if [ -n "$CERT_ARN" ]; then
    echo ""
    echo "☁️  Step 4: Adding domain to CloudFront..."
    echo ""
    echo "⚠️  Manual step required:"
    echo "   1. Go to: https://console.aws.amazon.com/cloudfront/v3/home"
    echo "   2. Click distribution: ${CLOUDFRONT_ID}"
    echo "   3. Click 'Edit' in Settings"
    echo "   4. Under 'Alternate domain names', add: ${FULL_DOMAIN}"
    echo "   5. Under 'Custom SSL certificate', select: ${CERT_ARN}"
    echo "   6. Click 'Save changes'"
    echo ""
    read -p "Press Enter after updating CloudFront..."
fi

# Step 5: Create DNS records
echo ""
echo "🌐 Step 5: Creating DNS Records..."

HOSTED_ZONE_ID=$(aws route53 list-hosted-zones --query "HostedZones[?Name=='${DOMAIN_NAME}.'].Id" --output text 2>/dev/null | cut -d'/' -f3 || echo "")

if [ -n "$HOSTED_ZONE_ID" ]; then
    echo "✅ Found Route53 hosted zone: ${HOSTED_ZONE_ID}"
    
    # Create A record for subdomain pointing to CloudFront
    cat > /tmp/route53-cloudfront.json << EOFINNER
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "${FULL_DOMAIN}",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "Z2FDTNDATAQYW2",
        "DNSName": "${CLOUDFRONT_DOMAIN}",
        "EvaluateTargetHealth": false
      }
    }
  }]
}
EOFINNER
    
    aws route53 change-resource-record-sets \
        --hosted-zone-id "${HOSTED_ZONE_ID}" \
        --change-batch file:///tmp/route53-cloudfront.json
    
    echo "✅ DNS record created: ${FULL_DOMAIN} → ${CLOUDFRONT_DOMAIN}"
else
    echo "⚠️  No Route53 hosted zone found"
    echo ""
    echo "Manual DNS setup required:"
    echo "   Add this CNAME record in your domain registrar:"
    echo ""
    echo "   Type:  A (Alias) or CNAME"
    echo "   Name:  ${SUBDOMAIN}"
    echo "   Value: ${CLOUDFRONT_DOMAIN}"
    echo "   TTL:   300"
    echo ""
fi

# Step 6: Test
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Your domain: https://${FULL_DOMAIN}"
echo ""
echo "⏳ DNS propagation may take 5-15 minutes"
echo ""
echo "Test with:"
echo "   dig ${FULL_DOMAIN}"
echo "   curl -I https://${FULL_DOMAIN}"
echo ""
echo "Open in browser:"
echo "   https://${FULL_DOMAIN}"
echo ""
