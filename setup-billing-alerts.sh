#!/bin/bash

# CarbonTrack AWS Billing Alerts Setup
# Protects your €50 monthly budget

echo "🔔 Setting up AWS Billing Alerts for CarbonTrack"
echo "==============================================="

# Step 1: Enable billing alerts (run this first)
echo "1. Go to AWS Console → Billing Dashboard"
echo "2. Navigate to: Billing Preferences"
echo "3. Check: 'Receive Billing Alerts'"
echo "4. Save preferences"
echo ""

# Step 2: Create SNS topic for alerts
echo "Creating SNS topic for billing alerts..."
aws sns create-topic --name "CarbonTrack-Billing-Alerts"

# Get the topic ARN (you'll need this)
TOPIC_ARN=$(aws sns list-topics --query 'Topics[?contains(TopicArn, `CarbonTrack-Billing-Alerts`)].TopicArn' --output text)
echo "Topic ARN: $TOPIC_ARN"

# Step 3: Subscribe your email to notifications
echo ""
read -p "Enter your email address for billing alerts: " EMAIL
aws sns subscribe --topic-arn "$TOPIC_ARN" --protocol email --notification-endpoint "$EMAIL"

echo ""
echo "⚠️  Check your email and confirm the subscription!"
echo ""

# Step 4: Create CloudWatch billing alarms
echo "Creating CloudWatch billing alarms..."

# Alert at €40 (80% of budget)
aws cloudwatch put-metric-alarm \
    --alarm-name "CarbonTrack-Budget-80-Percent" \
    --alarm-description "Alert when CarbonTrack costs reach €40 (80% of €50 budget)" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 86400 \
    --threshold 40 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=Currency,Value=EUR \
    --evaluation-periods 1 \
    --alarm-actions "$TOPIC_ARN" \
    --unit None

# Alert at €45 (90% of budget) 
aws cloudwatch put-metric-alarm \
    --alarm-name "CarbonTrack-Budget-90-Percent" \
    --alarm-description "URGENT: CarbonTrack costs reach €45 (90% of €50 budget)" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 86400 \
    --threshold 45 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=Currency,Value=EUR \
    --evaluation-periods 1 \
    --alarm-actions "$TOPIC_ARN" \
    --unit None

# Critical alert at €50 (100% of budget)
aws cloudwatch put-metric-alarm \
    --alarm-name "CarbonTrack-Budget-EXCEEDED" \
    --alarm-description "CRITICAL: CarbonTrack costs EXCEED €50 budget!" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 86400 \
    --threshold 50 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=Currency,Value=EUR \
    --evaluation-periods 1 \
    --alarm-actions "$TOPIC_ARN" \
    --unit None

echo ""
echo "✅ Billing alerts configured successfully!"
echo ""
echo "🔔 You will receive email alerts at:"
echo "   • €40 (80% of budget) - Warning"
echo "   • €45 (90% of budget) - Urgent" 
echo "   • €50 (100% of budget) - Critical"
echo ""
echo "📊 Monitor your costs at: https://console.aws.amazon.com/billing/"