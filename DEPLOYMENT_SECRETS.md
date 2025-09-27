# GitHub Secrets Configuration for CarbonTrack

## Required Secrets for GitHub Actions

Add these secrets in your GitHub repository:
Settings → Secrets and variables → Actions → Repository secrets

### AWS Authentication
```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJa...
```
**How to get**: AWS IAM → Users → Create user with programmatic access

### Domain Configuration
```
DOMAIN_NAME=carbontrack.com
SSL_CERTIFICATE_ARN=arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012
```
**How to get**: AWS Certificate Manager → Request certificate → Copy ARN

### Environment Settings
```
ENVIRONMENT=production
PRODUCTION_API_URL=https://api.carbontrack.com
```

### CloudFront Configuration
```
CLOUDFRONT_DISTRIBUTION_ID=E1234567890123
```
**How to get**: After first deployment, from CloudFormation outputs

## AWS Permissions Required

### IAM Policy for Deployment User
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "s3:*",
        "lambda:*",
        "apigateway:*",
        "iam:*",
        "dynamodb:*",
        "cognito-idp:*",
        "cloudfront:*",
        "acm:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## Setup Steps

### 1. AWS Account Setup
1. Create AWS account
2. Create IAM user for deployment
3. Generate Access Key and Secret
4. Add permissions policy above

### 2. Domain Setup (Optional)
1. Purchase domain (Route 53 or external)
2. Request SSL certificate in us-east-1
3. Validate certificate ownership

### 3. GitHub Repository Setup
1. Fork/clone CarbonTrack repository
2. Add secrets listed above
3. Push to main branch to trigger deployment

### 4. First Deployment
```bash
# Local deployment option
./deploy.sh

# Or push to main branch for GitHub Actions
git push origin main
```

## Monitoring and Troubleshooting

### CloudWatch Logs
- Lambda function logs: `/aws/lambda/carbontrack-api-production`
- API Gateway logs: Enable in API Gateway console

### CloudFormation
- Stack events show deployment progress
- Failed deployments show specific error messages

### Common Issues
1. **Certificate not in us-east-1**: CloudFront requires certificates in us-east-1
2. **IAM permissions**: User needs full access for initial deployment
3. **S3 bucket naming**: Bucket names must be globally unique

## Security Best Practices

### Production Secrets
- Rotate access keys regularly
- Use IAM roles instead of users when possible
- Enable CloudTrail for API logging
- Enable GuardDuty for threat detection

### Application Security
- Enable WAF for API Gateway
- Use Cognito for authentication
- Encrypt data at rest (DynamoDB)
- Use HTTPS everywhere

## Cost Optimization

### Free Tier Resources
- DynamoDB: 25GB storage, 200M requests/month
- Lambda: 1M requests, 400K GB-seconds/month
- CloudFront: 50GB transfer, 2M requests/month
- S3: 5GB storage, 20K GET requests/month

### Monitoring Costs
- Set up billing alerts
- Use AWS Cost Explorer
- Tag resources for cost allocation
- Monitor usage in CloudWatch