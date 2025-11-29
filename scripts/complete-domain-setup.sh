#!/bin/bash

# CarbonTrack Domain Setup - Automated SSL & DNS Configuration
# Run this AFTER you've purchased carbontrack.com in Route53
# Usage: ./complete-domain-setup.sh

set -e

DOMAIN_NAME="carbontracksystem.com"
CLOUDFRONT_ID="EUKA4HQFK6MC"
CLOUDFRONT_DOMAIN="d2z2og1o0b9esb.cloudfront.net"
REGION="us-east-1"

echo "🚀 CarbonTrack Domain Setup Automation"
echo "======================================="
echo ""
echo "Domain: ${DOMAIN_NAME}"
echo "CloudFront: ${CLOUDFRONT_DOMAIN}"
echo ""

# Step 1: Check if domain is registered
echo "📋 Step 1: Checking domain registration status..."
DOMAIN_STATUS=$(aws route53domains get-domain-detail --domain-name "${DOMAIN_NAME}" --query 'StatusList[0]' --output text 2>/dev/null || echo "NOT_FOUND")

if [ "$DOMAIN_STATUS" = "NOT_FOUND" ]; then
    echo "❌ Domain not registered yet!"
    echo ""
    echo "Please complete these steps first:"
    echo "1. Go to: https://console.aws.amazon.com/route53/home#DomainRegistration:"
    echo "2. Register: ${DOMAIN_NAME}"
    echo "3. Verify your email"
    echo "4. Wait for domain registration to complete (10-15 min)"
    echo "5. Run this script again"
    exit 1
fi

echo "✅ Domain registered: ${DOMAIN_NAME}"
echo ""

# Step 2: Get Hosted Zone ID
echo "📋 Step 2: Finding Route53 hosted zone..."
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones --query "HostedZones[?Name=='${DOMAIN_NAME}.'].Id" --output text 2>/dev/null | cut -d'/' -f3)

if [ -z "$HOSTED_ZONE_ID" ]; then
    echo "❌ No hosted zone found for ${DOMAIN_NAME}"
    echo "Wait a few minutes for domain registration to complete, then try again."
    exit 1
fi

echo "✅ Found hosted zone: ${HOSTED_ZONE_ID}"
echo ""

# Step 3: Request SSL Certificate
echo "📋 Step 3: Requesting SSL certificate..."
CERT_ARN=$(aws acm list-certificates --region ${REGION} --query "CertificateSummaryList[?DomainName=='${DOMAIN_NAME}'].CertificateArn" --output text 2>/dev/null)

if [ -z "$CERT_ARN" ]; then
    echo "   Creating new certificate..."
    CERT_ARN=$(aws acm request-certificate \
        --domain-name "${DOMAIN_NAME}" \
        --subject-alternative-names "*.${DOMAIN_NAME}" \
        --validation-method DNS \
        --region ${REGION} \
        --query 'CertificateArn' \
        --output text)
    
    echo "✅ Certificate requested: ${CERT_ARN}"
    echo ""
    
    # Wait a moment for certificate to be created
    sleep 5
    
    # Step 4: Get validation records and create in Route53
    echo "📋 Step 4: Creating DNS validation records..."
    
    VALIDATION_RECORDS=$(aws acm describe-certificate \
        --certificate-arn "${CERT_ARN}" \
        --region ${REGION} \
        --query 'Certificate.DomainValidationOptions[*].ResourceRecord' \
        --output json)
    
    # Parse and create validation records
    echo "$VALIDATION_RECORDS" | jq -c '.[]' | while read record; do
        VALIDATION_NAME=$(echo "$record" | jq -r '.Name')
        VALIDATION_VALUE=$(echo "$record" | jq -r '.Value')
        
        # Create validation record
        cat > /tmp/validation-record.json << EOF
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "${VALIDATION_NAME}",
      "Type": "CNAME",
      "TTL": 300,
      "ResourceRecords": [{"Value": "${VALIDATION_VALUE}"}]
    }
  }]
}
EOF
        
        aws route53 change-resource-record-sets \
            --hosted-zone-id "${HOSTED_ZONE_ID}" \
            --change-batch file:///tmp/validation-record.json > /dev/null
        
        echo "   ✅ Created validation record: ${VALIDATION_NAME}"
    done
    
    echo ""
    echo "⏳ Waiting for certificate validation (this may take 5-10 minutes)..."
    aws acm wait certificate-validated --certificate-arn "${CERT_ARN}" --region ${REGION}
    echo "✅ Certificate validated!"
else
    echo "✅ Certificate already exists: ${CERT_ARN}"
fi

echo ""

# Step 5: Update CloudFront distribution (manual step required)
echo "📋 Step 5: CloudFront configuration..."
echo ""
echo "⚠️  MANUAL STEP REQUIRED:"
echo ""
echo "1. Go to: https://console.aws.amazon.com/cloudfront/v3/home"
echo "2. Click distribution: ${CLOUDFRONT_ID}"
echo "3. Click 'Edit' button"
echo "4. Under 'Alternate domain names (CNAMEs)', add:"
echo "   - ${DOMAIN_NAME}"
echo "   - app.${DOMAIN_NAME}"
echo "5. Under 'Custom SSL certificate', select:"
echo "   ${CERT_ARN}"
echo "6. Click 'Save changes'"
echo ""
read -p "Press Enter when you've completed the CloudFront update..."

echo ""

# Step 6: Create DNS records
echo "📋 Step 6: Creating DNS records for CloudFront..."

# Create A record for root domain
cat > /tmp/dns-root.json << EOF
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "${DOMAIN_NAME}",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "Z2FDTNDATAQYW2",
        "DNSName": "${CLOUDFRONT_DOMAIN}",
        "EvaluateTargetHealth": false
      }
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id "${HOSTED_ZONE_ID}" \
    --change-batch file:///tmp/dns-root.json > /dev/null

echo "✅ Created A record: ${DOMAIN_NAME} → ${CLOUDFRONT_DOMAIN}"

# Create A record for app subdomain
cat > /tmp/dns-app.json << EOF
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "app.${DOMAIN_NAME}",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "Z2FDTNDATAQYW2",
        "DNSName": "${CLOUDFRONT_DOMAIN}",
        "EvaluateTargetHealth": false
      }
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id "${HOSTED_ZONE_ID}" \
    --change-batch file:///tmp/dns-app.json > /dev/null

echo "✅ Created A record: app.${DOMAIN_NAME} → ${CLOUDFRONT_DOMAIN}"

# Create A record for www subdomain
cat > /tmp/dns-www.json << EOF
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "www.${DOMAIN_NAME}",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "Z2FDTNDATAQYW2",
        "DNSName": "${CLOUDFRONT_DOMAIN}",
        "EvaluateTargetHealth": false
      }
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id "${HOSTED_ZONE_ID}" \
    --change-batch file:///tmp/dns-www.json > /dev/null

echo "✅ Created A record: www.${DOMAIN_NAME} → ${CLOUDFRONT_DOMAIN}"

echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo "Your domain is configured! DNS records created:"
echo "  ✅ ${DOMAIN_NAME} → CloudFront"
echo "  ✅ app.${DOMAIN_NAME} → CloudFront"
echo "  ✅ www.${DOMAIN_NAME} → CloudFront"
echo ""
echo "⏳ DNS propagation may take 5-15 minutes"
echo ""
echo "Test your domain:"
echo "  dig ${DOMAIN_NAME}"
echo "  curl -I https://${DOMAIN_NAME}"
echo ""
echo "Open in browser:"
echo "  https://${DOMAIN_NAME}"
echo "  https://app.${DOMAIN_NAME}"
echo ""
echo "🎊 Your CarbonTrack app is now live with custom domain!"
