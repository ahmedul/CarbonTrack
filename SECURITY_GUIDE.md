# GitHub Repository Security Guide
# Prevent Unauthorized Deployments & Protect Secrets

## 🚫 **Critical Files to NEVER Commit**

Create `.gitignore` to prevent accidentally committing sensitive data:

```gitignore
# AWS Credentials
*.pem
*.key
aws-credentials.txt
.aws/

# Environment Files
.env
.env.local
.env.production
.env.staging
config/secrets.json

# Deployment Artifacts
lambda-package/
dist/
build/
*.zip

# IDE & OS Files
.vscode/settings.json
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary Files
tmp/
temp/
*.tmp

# Database Files
*.db
*.sqlite

# API Keys & Tokens
api-keys.txt
tokens.json
secrets/
```

## 🔐 **GitHub Repository Security Settings**

### 1. **Repository Visibility**
```
✅ Private Repository (Recommended for production)
❌ Public Repository (Only for open-source projects)
```

### 2. **Branch Protection Rules**
```yaml
Branch: main
Settings:
  ✅ Require pull request reviews before merging
  ✅ Require status checks to pass before merging
  ✅ Require branches to be up to date before merging
  ✅ Include administrators (even you must follow rules)
  ✅ Restrict pushes that create files larger than 100MB
```

### 3. **GitHub Actions Security**
```yaml
Actions Permissions:
  ✅ Allow actions created by GitHub
  ✅ Allow actions by Marketplace verified creators
  ❌ Allow all actions (security risk)

Workflow Permissions:
  ✅ Restrict token permissions to minimum required
  ✅ Require approval for workflows from outside contributors
```

### 4. **Secret Management**
```
Repository Settings → Secrets and Variables → Actions

Required Secrets (NEVER commit these):
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY  
- DOMAIN_NAME
- SSL_CERTIFICATE_ARN
- ALERT_EMAIL
- SLACK_WEBHOOK (optional)
```

## 🛡️ **Multi-Layer Security Strategy**

### **Layer 1: Environment-Based Deployments**
```yaml
# Only deploy from specific branches
on:
  push:
    branches: [ main ]  # Only main branch can deploy
  workflow_dispatch:    # Manual deployment only
    inputs:
      confirm:
        description: 'Type "DEPLOY" to confirm'
        required: true
        
jobs:
  deploy:
    if: github.ref == 'refs/heads/main' && github.event.inputs.confirm == 'DEPLOY'
```

### **Layer 2: AWS Resource Tagging & Monitoring**
```yaml
# All resources tagged with deployment info
Tags:
  - Key: DeployedBy
    Value: !Ref AWS::AccountId
  - Key: GitCommit  
    Value: !Ref GitCommitHash
  - Key: Environment
    Value: !Ref Environment
  - Key: CostCenter
    Value: CarbonTrack-Production
```

### **Layer 3: IAM User Restrictions**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RestrictToSpecificStack",
      "Effect": "Allow", 
      "Action": ["cloudformation:*"],
      "Resource": "arn:aws:cloudformation:*:*:stack/carbontrack-*/*"
    },
    {
      "Sid": "PreventRootAccess",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:userid": "root"
        }
      }
    }
  ]
}
```

## 🔒 **Secure Deployment Configuration**

### **1. Environment-Specific Config Files**

#### `config/production.env.template`
```bash
# Template file - copy to production.env and fill values
AWS_REGION=us-east-1
DOMAIN_NAME=your-domain.com
ENVIRONMENT=production
ALERT_EMAIL=your-email@domain.com

# Never commit the actual .env file!
```

#### `config/local.env.template`
```bash
# Local development template
AWS_REGION=us-east-1
ENVIRONMENT=local
API_BASE_URL=http://localhost:8000
```

### **2. Secure GitHub Actions Workflow**
```yaml
name: Secure Production Deploy

on:
  workflow_dispatch:  # Manual deployment only
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production
      confirm_deploy:
        description: 'Type "CONFIRMED" to deploy'
        required: true

jobs:
  security-check:
    runs-on: ubuntu-latest
    steps:
    - name: Verify deployment confirmation
      if: github.event.inputs.confirm_deploy != 'CONFIRMED'
      run: |
        echo "❌ Deployment not confirmed"
        exit 1
        
    - name: Verify authorized user
      run: |
        authorized_users=("your-github-username" "trusted-dev-username")
        if [[ ! " ${authorized_users[@]} " =~ " ${GITHUB_ACTOR} " ]]; then
          echo "❌ Unauthorized deployment attempt by: ${GITHUB_ACTOR}"
          exit 1
        fi
        
  deploy:
    needs: security-check
    environment: ${{ github.event.inputs.environment }}
    runs-on: ubuntu-latest
    steps:
    - name: Deploy with approval
      run: echo "Deploying to ${{ github.event.inputs.environment }}"
```

### **3. AWS CloudFormation Security**
```yaml
# Add deployment safeguards to CloudFormation
Parameters:
  DeploymentConfirmation:
    Type: String
    Description: Type "DEPLOY-CONFIRMED" to proceed
    AllowedValues: [DEPLOY-CONFIRMED]
    
  AllowedDeployerEmail:
    Type: String
    Description: Email of authorized deployer
    
Conditions:
  IsAuthorizedDeployment: !Equals [!Ref DeploymentConfirmation, "DEPLOY-CONFIRMED"]
  
Resources:
  # All resources only created if confirmed
  FrontendBucket:
    Type: AWS::S3::Bucket
    Condition: IsAuthorizedDeployment
    Properties: ...
```

## 🚨 **Security Monitoring & Alerts**

### **1. CloudTrail for API Monitoring**
```yaml
CloudTrail:
  Type: AWS::CloudTrail::Trail
  Properties:
    TrailName: CarbonTrack-Security-Audit
    S3BucketName: !Ref SecurityAuditBucket
    IncludeGlobalServiceEvents: true
    IsLogging: true
    EventSelectors:
      - ReadWriteType: All
        IncludeManagementEvents: true
        DataResources:
          - Type: AWS::S3::Object
            Values: ["arn:aws:s3:::carbontrack-*/*"]
```

### **2. Security Alert System**
```python
# Lambda function to monitor unauthorized access
import boto3
import json

def security_monitor(event, context):
    # Check for unusual API calls
    unusual_patterns = [
        'root account usage',
        'unauthorized region access', 
        'budget exceeded',
        'mass resource deletion'
    ]
    
    for record in event['Records']:
        if any(pattern in record['eventName'].lower() for pattern in unusual_patterns):
            send_security_alert({
                'severity': 'HIGH',
                'event': record['eventName'],
                'user': record['userIdentity']['userName'],
                'timestamp': record['eventTime']
            })
```

## 📋 **Security Checklist for Deployment**

### **Before Each Deployment:**
- [ ] Verify no secrets in git history: `git log --all --grep="password\|key\|secret"`
- [ ] Check .gitignore covers all sensitive files
- [ ] Confirm GitHub repository is private
- [ ] Validate only authorized users have access
- [ ] Review AWS billing alerts are active
- [ ] Test deployment in staging first

### **After Each Deployment:**
- [ ] Rotate AWS access keys (monthly)
- [ ] Review CloudTrail logs for unusual activity
- [ ] Monitor cost dashboard
- [ ] Verify all endpoints require authentication
- [ ] Test security headers and HTTPS enforcement

### **Monthly Security Review:**
- [ ] Audit GitHub collaborators
- [ ] Review AWS IAM users and roles
- [ ] Check for unused resources (cost + security)
- [ ] Update dependencies for security patches
- [ ] Review AWS CloudTrail logs
- [ ] Test backup and recovery procedures

## 🚩 **Red Flags to Watch For**

### **Indicators of Compromise:**
```
❌ Unexpected AWS bills
❌ Resources in unknown regions
❌ Unknown IAM users or roles
❌ Suspicious API Gateway traffic
❌ Lambda functions with unusual runtimes
❌ S3 buckets with public access
❌ GitHub repository suddenly public
```

### **Immediate Response Plan:**
1. **Rotate all AWS credentials immediately**
2. **Disable compromised IAM users**
3. **Review CloudTrail for unauthorized actions**
4. **Check billing for unexpected charges**
5. **Enable AWS GuardDuty for threat detection**
6. **Contact AWS support if needed**

This security framework ensures your CarbonTrack deployment is protected against unauthorized access and accidental exposure of sensitive data!