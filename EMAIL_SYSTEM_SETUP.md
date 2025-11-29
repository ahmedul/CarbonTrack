# Email System Setup Guide

## Overview
CarbonTrack uses AWS Simple Email Service (SES) for sending transactional and notification emails.

## Email Addresses

The following email addresses are configured:

- **noreply@carbontracksystem.com** - Automated emails (default sender)
- **support@carbontracksystem.com** - Customer support inquiries
- **hello@carbontracksystem.com** - General inquiries
- **beta@carbontracksystem.com** - Beta tester feedback

## Setup Steps

### 1. Verify Email Addresses

Run the setup script:

```bash
./scripts/setup-ses-emails.sh
```

This will:
- Verify all email addresses in AWS SES
- Send verification emails to each address
- Display current sending quota

### 2. Click Verification Links

**Important**: Check the inbox for each email address and click the verification link.

If you don't have access to these inboxes yet:
1. Set up email forwarding in Route53 or your email provider
2. Or temporarily verify a test email you control

### 3. Request Production Access

By default, SES is in **sandbox mode** with limits:
- ✅ Can send to verified addresses only
- ❌ Limit: 200 emails/day
- ❌ Rate: 1 email/second

**To remove limits**:

1. Go to AWS Console > Amazon SES
2. Navigate to **Account Dashboard**
3. Click **Request production access**
4. Fill out the form:
   - **Mail type**: Transactional
   - **Website URL**: https://carbontracksystem.com
   - **Use case**: "Sending transactional emails for carbon tracking SaaS app"
   - **Expected volume**: 1,000 emails/month (adjust based on users)
   - **Bounce/complaint handling**: "We monitor bounce and complaint rates"
5. Submit request
6. Wait for approval (usually 24-48 hours)

## Email Templates

### 1. Welcome Email
**Sent**: When new user registers
**From**: noreply@carbontracksystem.com
**Purpose**: Welcome user and guide getting started

```python
from app.email_service import email_service

await email_service.send_welcome_email(
    user_email="user@example.com",
    user_name="John Doe"
)
```

### 2. Beta Approval Email
**Sent**: When admin approves beta access
**From**: noreply@carbontracksystem.com
**Purpose**: Notify user of approved access

```python
await email_service.send_beta_approved_email(
    user_email="user@example.com",
    user_name="John Doe"
)
```

### 3. Activity Limit Warning
**Sent**: When user reaches 90% of activity limit
**From**: noreply@carbontracksystem.com
**Purpose**: Alert user before hitting limit

```python
await email_service.send_limit_warning_email(
    user_email="user@example.com",
    user_name="John Doe",
    current_count=90,
    limit=100
)
```

### 4. Monthly Report
**Sent**: Beginning of each month
**From**: noreply@carbontracksystem.com
**Purpose**: Summary of previous month's carbon footprint

```python
await email_service.send_monthly_report_email(
    user_email="user@example.com",
    user_name="John Doe",
    total_emissions=245.5,
    activities_count=32,
    top_category="Transportation"
)
```

## Email Service Usage

### Basic Email

```python
from app.email_service import email_service

result = await email_service.send_email(
    recipient="user@example.com",
    subject="Your Carbon Report",
    body_text="Plain text version",
    body_html="<h1>HTML version</h1>",
    sender="noreply@carbontracksystem.com"  # Optional, uses default
)

if result['success']:
    print(f"Email sent! MessageId: {result['message_id']}")
else:
    print(f"Failed: {result['error']}")
```

### Check Sending Quota

```python
quota = await email_service.get_send_quota()

if quota['success']:
    print(f"Max 24hr send: {quota['max_24_hour_send']}")
    print(f"Sent last 24hrs: {quota['sent_last_24_hours']}")
    print(f"Max send rate: {quota['max_send_rate']}/sec")
```

## Integration Points

### 1. User Registration
Add to registration flow:

```python
# In auth.py or user service
async def register_user(user_data):
    # ... create user ...
    
    # Send welcome email
    await email_service.send_welcome_email(
        user_email=user_data.email,
        user_name=user_data.full_name
    )
```

### 2. Admin Approval
Add to admin approval endpoint:

```python
async def approve_beta_user(user_id: str):
    # ... approve user ...
    
    # Send approval email
    user = await get_user(user_id)
    await email_service.send_beta_approved_email(
        user_email=user.email,
        user_name=user.full_name
    )
```

### 3. Activity Limit Check
Already integrated in `activity_service.py`:

```python
# Automatically triggers at 90% usage
if current_count >= ACTIVITY_LIMIT * 0.9:
    # Uncomment to enable email warning
    # await email_service.send_limit_warning_email(
    #     user_email, user_name, current_count, ACTIVITY_LIMIT
    # )
```

### 4. Monthly Reports (Scheduled)
Create Lambda function or cron job:

```python
import asyncio
from datetime import datetime

async def send_monthly_reports():
    """Run on 1st of each month"""
    users = await get_all_active_users()
    
    for user in users:
        # Calculate user's monthly stats
        stats = await calculate_monthly_stats(user.id)
        
        # Send report
        await email_service.send_monthly_report_email(
            user_email=user.email,
            user_name=user.full_name,
            total_emissions=stats['total_emissions'],
            activities_count=stats['activities_count'],
            top_category=stats['top_category']
        )
        
        # Rate limiting
        await asyncio.sleep(0.1)  # 10 emails/second max

# Schedule with AWS EventBridge or cron
# 0 0 1 * * - Run at midnight on 1st of month
```

## Monitoring & Debugging

### Check Email Sending Stats

```bash
# Via AWS CLI
aws ses get-send-statistics --region eu-central-1

# Via Python
quota = await email_service.get_send_quota()
print(quota)
```

### View Bounces and Complaints

```bash
# List suppressed addresses (bounces/complaints)
aws sesv2 list-suppressed-destinations --region eu-central-1

# Get specific address details
aws sesv2 get-suppressed-destination \
    --email-address bounced@example.com \
    --region eu-central-1
```

### Enable SNS Notifications

Set up notifications for bounces/complaints:

```bash
# Create SNS topic
aws sns create-topic \
    --name carbontrack-email-notifications \
    --region eu-central-1

# Subscribe email to topic
aws sns subscribe \
    --topic-arn arn:aws:sns:eu-central-1:ACCOUNT_ID:carbontrack-email-notifications \
    --protocol email \
    --notification-endpoint admin@carbontracksystem.com

# Configure SES to publish to SNS
aws ses set-identity-notification-topic \
    --identity carbontracksystem.com \
    --notification-type Bounce \
    --sns-topic arn:aws:sns:eu-central-1:ACCOUNT_ID:carbontrack-email-notifications \
    --region eu-central-1
```

## Best Practices

### 1. Handle Bounces
- Monitor bounce rate (should be <5%)
- Remove hard bounces from mailing list
- Investigate soft bounces

### 2. Unsubscribe Links
Add to all marketing emails:

```html
<p style="font-size: 12px; color: #666;">
    Don't want these emails? 
    <a href="https://carbontracksystem.com/unsubscribe?email={{email}}">Unsubscribe</a>
</p>
```

### 3. Rate Limiting
Respect SES limits:
- Sandbox: 1 email/second
- Production: Starts at 14 emails/second, can increase

```python
import asyncio

async def send_bulk_emails(recipients):
    for recipient in recipients:
        await email_service.send_email(...)
        await asyncio.sleep(0.1)  # 10 emails/second
```

### 4. Email Design
- Use responsive HTML templates
- Test on multiple email clients
- Include plain text version
- Keep under 100KB size

### 5. Deliverability
- Set up SPF, DKIM, DMARC records
- Warm up sending reputation gradually
- Monitor spam complaints (<0.1%)

## DNS Configuration

Verify these records exist in Route53:

```
# SPF Record (TXT)
carbontracksystem.com. TXT "v=spf1 include:amazonses.com ~all"

# DKIM Records (automatically added by SES)
# Check in SES console > Verified identities > carbontracksystem.com

# DMARC Record (TXT)
_dmarc.carbontracksystem.com. TXT "v=DMARC1; p=quarantine; rua=mailto:dmarc@carbontracksystem.com"
```

To verify:

```bash
# Check SPF
dig TXT carbontracksystem.com

# Check DKIM (get selector from SES console)
dig TXT [selector]._domainkey.carbontracksystem.com

# Check DMARC
dig TXT _dmarc.carbontracksystem.com
```

## Costs

AWS SES pricing:
- **First 62,000 emails/month**: FREE (if sent from EC2)
- **Additional emails**: $0.10 per 1,000 emails
- **Attachments**: $0.12 per GB

Example costs:
- 1,000 emails/month = FREE
- 10,000 emails/month = FREE
- 100,000 emails/month = ~$4

Very affordable compared to alternatives like SendGrid, Mailgun, etc.

## Testing

### Test Email Sending

```bash
# Test from command line
python3 << EOF
import asyncio
from backend.app.email_service import email_service

async def test():
    result = await email_service.send_email(
        recipient="your-email@example.com",
        subject="Test Email",
        body_text="This is a test email from CarbonTrack",
        body_html="<h1>This is a test email</h1><p>From CarbonTrack</p>"
    )
    print(result)

asyncio.run(test())
EOF
```

### Test All Templates

```bash
# Test welcome email
python3 -c "
import asyncio
from backend.app.email_service import email_service
asyncio.run(email_service.send_welcome_email('test@example.com', 'Test User'))
"

# Test beta approval
python3 -c "
import asyncio
from backend.app.email_service import email_service
asyncio.run(email_service.send_beta_approved_email('test@example.com', 'Test User'))
"

# Test limit warning
python3 -c "
import asyncio
from backend.app.email_service import email_service
asyncio.run(email_service.send_limit_warning_email('test@example.com', 'Test User', 90, 100))
"
```

## Troubleshooting

### Email not received?
1. Check spam folder
2. Verify email address in SES
3. Check SES sending quota
4. Verify sandbox mode restrictions
5. Check bounce/complaint lists

### "Email address not verified" error?
- Click verification link in email
- Or manually verify in SES console

### Rate limit errors?
- Add delays between sends
- Request rate increase from AWS
- Check daily sending quota

### Bounces?
- Hard bounce: Invalid email, remove from list
- Soft bounce: Temporary issue, retry later

## Next Steps

1. ✅ Run setup script: `./scripts/setup-ses-emails.sh`
2. ✅ Verify all email addresses (click links)
3. ✅ Request production access
4. ✅ Set up DNS records (SPF, DKIM, DMARC)
5. ✅ Enable SNS notifications
6. ✅ Test email sending
7. ✅ Integrate with application flows

## Support

For email-related issues:
- AWS SES Documentation: https://docs.aws.amazon.com/ses/
- AWS Support: https://console.aws.amazon.com/support/
- Email: support@carbontracksystem.com
