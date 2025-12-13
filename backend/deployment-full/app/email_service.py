"""
Email service using AWS SES for CarbonTrack
Handles sending emails for notifications, alerts, and communications
"""

import boto3
from botocore.exceptions import ClientError
from typing import List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails via AWS SES"""
    
    def __init__(self, region_name: str = "eu-central-1"):
        """
        Initialize AWS SES client
        
        Args:
            region_name: AWS region for SES (default: eu-central-1)
        """
        self.ses_client = boto3.client('ses', region_name=region_name)
        self.sender_email = "noreply@carbontracksystem.com"
        self.support_email = "support@carbontracksystem.com"
        
    def send_email(
        self,
        recipient: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        sender: Optional[str] = None
    ) -> dict:
        """
        Send an email via AWS SES
        
        Args:
            recipient: Email address of recipient
            subject: Email subject line
            body_text: Plain text body
            body_html: HTML body (optional)
            sender: Sender email (default: noreply@carbontracksystem.com)
            
        Returns:
            dict: Response from SES
        """
        if sender is None:
            sender = self.sender_email
            
        try:
            message = {
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Text': {'Data': body_text, 'Charset': 'UTF-8'}}
            }
            
            if body_html:
                message['Body']['Html'] = {'Data': body_html, 'Charset': 'UTF-8'}
            
            response = self.ses_client.send_email(
                Source=sender,
                Destination={'ToAddresses': [recipient]},
                Message=message
            )
            
            logger.info(f"Email sent successfully to {recipient}. MessageId: {response['MessageId']}")
            return {
                'success': True,
                'message_id': response['MessageId'],
                'recipient': recipient
            }
            
        except ClientError as e:
            logger.error(f"Failed to send email to {recipient}: {e.response['Error']['Message']}")
            return {
                'success': False,
                'error': e.response['Error']['Message'],
                'recipient': recipient
            }
    
    def send_welcome_email(self, user_email: str, user_name: str) -> dict:
        """Send welcome email to new user"""
        subject = "Welcome to CarbonTrack! 🌍"
        
        body_text = f"""
Hi {user_name},

Welcome to CarbonTrack!

We're excited to have you join our community of environmentally conscious individuals 
working towards a more sustainable future.

Getting Started:
1. Log in to your account at https://carbontracksystem.com
2. Add your first carbon emission entry
3. Explore personalized recommendations
4. Track your progress on the dashboard

Need Help?
Visit our support page or reply to this email.

Best regards,
The CarbonTrack Team

---
CarbonTrack - Track Your Carbon Footprint
https://carbontracksystem.com
"""
        
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); 
                   color: white; padding: 30px; text-align: center; border-radius: 10px; }}
        .content {{ background: #f9fafb; padding: 30px; margin: 20px 0; border-radius: 10px; }}
        .button {{ background: #2563eb; color: white; padding: 12px 30px; 
                   text-decoration: none; border-radius: 8px; display: inline-block; 
                   margin: 10px 0; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; }}
        .feature {{ margin: 15px 0; padding: 10px; background: white; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 Welcome to CarbonTrack!</h1>
        </div>
        
        <div class="content">
            <h2>Hi {user_name},</h2>
            
            <p>We're excited to have you join our community of environmentally conscious 
            individuals working towards a more sustainable future.</p>
            
            <h3>🚀 Getting Started</h3>
            
            <div class="feature">
                <strong>1️⃣ Add Your First Entry</strong><br>
                Track your carbon footprint across transportation, energy, food, and waste.
            </div>
            
            <div class="feature">
                <strong>2️⃣ Get Recommendations</strong><br>
                Receive personalized suggestions to reduce your environmental impact.
            </div>
            
            <div class="feature">
                <strong>3️⃣ Track Progress</strong><br>
                Monitor your carbon reduction journey with visual dashboards.
            </div>
            
            <div class="feature">
                <strong>4️⃣ Earn Achievements</strong><br>
                Complete challenges and climb the leaderboards!
            </div>
            
            <center>
                <a href="https://carbontracksystem.com" class="button">
                    Go to Dashboard →
                </a>
            </center>
        </div>
        
        <div class="footer">
            <p>Need help? Reply to this email or visit our support page.</p>
            <p>CarbonTrack - Track Your Carbon Footprint<br>
            <a href="https://carbontracksystem.com">carbontracksystem.com</a></p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(user_email, subject, body_text, body_html)
    
    def send_beta_approved_email(self, user_email: str, user_name: str) -> dict:
        """Send email when beta access is approved"""
        subject = "Your CarbonTrack Beta Access is Approved! 🎉"
        
        body_text = f"""
Hi {user_name},

Great news! Your CarbonTrack beta access has been approved.

You can now log in and start tracking your carbon footprint:
https://carbontracksystem.com

As a beta tester, you'll receive:
• Lifetime FREE premium access
• Direct input on feature development
• Early access to new features
• Beta community membership

Your feedback is invaluable in helping us build the best carbon tracking platform possible.

Welcome aboard!

Best regards,
The CarbonTrack Team
"""
        
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                   color: white; padding: 30px; text-align: center; border-radius: 10px; }}
        .content {{ background: #f0fdf4; padding: 30px; margin: 20px 0; border-radius: 10px; }}
        .button {{ background: #10b981; color: white; padding: 12px 30px; 
                   text-decoration: none; border-radius: 8px; display: inline-block; }}
        .perk {{ margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #10b981; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 You're Approved!</h1>
        </div>
        
        <div class="content">
            <h2>Hi {user_name},</h2>
            
            <p><strong>Great news!</strong> Your CarbonTrack beta access has been approved.</p>
            
            <h3>🎁 Your Beta Perks:</h3>
            <div class="perk">✅ Lifetime FREE premium access</div>
            <div class="perk">💬 Direct input on feature development</div>
            <div class="perk">🚀 Early access to new features</div>
            <div class="perk">👥 Beta community membership</div>
            
            <center>
                <a href="https://carbontracksystem.com" class="button">
                    Start Tracking →
                </a>
            </center>
            
            <p style="margin-top: 20px;">Your feedback is invaluable in helping us build 
            the best carbon tracking platform possible. Welcome aboard!</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(user_email, subject, body_text, body_html)
    
    def send_limit_warning_email(self, user_email: str, user_name: str, current_count: int, limit: int) -> dict:
        """Send email when user approaches activity limit"""
        subject = "⚠️ Approaching Activity Limit"
        
        remaining = limit - current_count
        
        body_text = f"""
Hi {user_name},

You're approaching your monthly activity limit.

Current Activities: {current_count}/{limit}
Remaining: {remaining}

To continue tracking after reaching the limit, you can:
1. Wait until next month (limit resets)
2. Upgrade to premium for unlimited activities
3. Delete old activities to free up space

Questions? Contact us at {self.support_email}

Best regards,
The CarbonTrack Team
"""
        
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                   color: white; padding: 30px; text-align: center; border-radius: 10px; }}
        .content {{ background: #fffbeb; padding: 30px; margin: 20px 0; border-radius: 10px; }}
        .stats {{ background: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .progress-bar {{ background: #e5e7eb; height: 20px; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ background: #f59e0b; height: 100%; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Activity Limit Warning</h1>
        </div>
        
        <div class="content">
            <h2>Hi {user_name},</h2>
            
            <p>You're approaching your monthly activity limit.</p>
            
            <div class="stats">
                <h3>{current_count} / {limit} Activities</h3>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(current_count/limit)*100}%"></div>
                </div>
                <p style="margin-top: 10px;"><strong>{remaining} remaining</strong></p>
            </div>
            
            <h3 style="margin-top: 30px;">What's Next?</h3>
            <p>To continue tracking after reaching the limit:</p>
            <ul>
                <li>Wait until next month (limit resets automatically)</li>
                <li>Upgrade to premium for unlimited activities</li>
                <li>Delete old activities to free up space</li>
            </ul>
            
            <p>Questions? Contact us at <a href="mailto:{self.support_email}">{self.support_email}</a></p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(user_email, subject, body_text, body_html)
    
    def send_monthly_report_email(
        self,
        user_email: str,
        user_name: str,
        total_emissions: float,
        activities_count: int,
        top_category: str
    ) -> dict:
        """Send monthly carbon footprint report"""
        subject = f"Your Monthly Carbon Report - {datetime.now().strftime('%B %Y')}"
        
        body_text = f"""
Hi {user_name},

Here's your carbon footprint report for {datetime.now().strftime('%B %Y')}:

📊 Total Emissions: {total_emissions:.2f} kg CO₂
📈 Activities Logged: {activities_count}
🔥 Top Category: {top_category}

View your detailed dashboard: https://carbontracksystem.com/dashboard

Keep up the great work tracking your environmental impact!

Best regards,
The CarbonTrack Team
"""
        
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); 
                   color: white; padding: 30px; text-align: center; border-radius: 10px; }}
        .content {{ background: #f9fafb; padding: 30px; margin: 20px 0; border-radius: 10px; }}
        .stat-box {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; 
                      border-left: 4px solid #6366f1; }}
        .button {{ background: #6366f1; color: white; padding: 12px 30px; 
                   text-decoration: none; border-radius: 8px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Monthly Carbon Report</h1>
            <p>{datetime.now().strftime('%B %Y')}</p>
        </div>
        
        <div class="content">
            <h2>Hi {user_name},</h2>
            
            <p>Here's your carbon footprint summary for this month:</p>
            
            <div class="stat-box">
                <h3>🔥 Total Emissions</h3>
                <p style="font-size: 28px; font-weight: bold; color: #dc2626;">{total_emissions:.2f} kg CO₂</p>
            </div>
            
            <div class="stat-box">
                <h3>📈 Activities Logged</h3>
                <p style="font-size: 28px; font-weight: bold; color: #2563eb;">{activities_count}</p>
            </div>
            
            <div class="stat-box">
                <h3>🎯 Top Category</h3>
                <p style="font-size: 24px; font-weight: bold; color: #059669;">{top_category}</p>
            </div>
            
            <center style="margin-top: 30px;">
                <a href="https://carbontracksystem.com/dashboard" class="button">
                    View Detailed Dashboard →
                </a>
            </center>
            
            <p style="margin-top: 30px;">Keep up the great work tracking your environmental impact!</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(user_email, subject, body_text, body_html)
    
    def verify_email_address(self, email: str) -> dict:
        """
        Verify an email address in AWS SES (required for sending)
        
        Args:
            email: Email address to verify
            
        Returns:
            dict: Verification status
        """
        try:
            response = self.ses_client.verify_email_identity(EmailAddress=email)
            logger.info(f"Verification email sent to {email}")
            return {
                'success': True,
                'message': f'Verification email sent to {email}',
                'email': email
            }
        except ClientError as e:
            logger.error(f"Failed to verify email {email}: {e.response['Error']['Message']}")
            return {
                'success': False,
                'error': e.response['Error']['Message'],
                'email': email
            }
    
    def get_send_quota(self) -> dict:
        """Get current SES sending quota"""
        try:
            response = self.ses_client.get_send_quota()
            return {
                'success': True,
                'max_24_hour_send': response['Max24HourSend'],
                'max_send_rate': response['MaxSendRate'],
                'sent_last_24_hours': response['SentLast24Hours']
            }
        except ClientError as e:
            return {
                'success': False,
                'error': e.response['Error']['Message']
            }


# Singleton instance
email_service = EmailService()
