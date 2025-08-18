# 🔐 AWS Cognito Setup Guide for CarbonTrack

This guide walks you through setting up AWS Cognito authentication for the CarbonTrack backend.

## 📋 Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured (`aws configure`)
- Terraform installed (optional, for IaC approach)

## 🚀 Option 1: Quick Setup with AWS CLI Script

### 1. Run the Setup Script

```bash
cd infra
./setup-cognito.sh
```

This script will:
- Create a Cognito User Pool
- Create a User Pool Client with secret
- Set up email verification
- Create a custom domain for hosted UI
- Generate configuration for your .env file

### 2. Update Backend Configuration

Copy the generated values to your backend `.env` file:

```bash
# Copy the generated configuration
cp aws-cognito-config.txt ../backend/.env.cognito
```

Then update your `backend/.env` file with the values from the output.

## 🏗️ Option 2: Infrastructure as Code with Terraform

### 1. Initialize Terraform

```bash
cd infra
terraform init
```

### 2. Plan the Infrastructure

```bash
terraform plan
```

### 3. Apply the Configuration

```bash
terraform apply
```

### 4. Get the Configuration

```bash
terraform output -raw env_configuration >> ../backend/.env.cognito
```

## 🔧 Backend Configuration

Update your `backend/.env` file with the Cognito values:

```env
# AWS Cognito Configuration (replace with your actual values)
AWS_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_CLIENT_ID=your_actual_client_id
COGNITO_CLIENT_SECRET=your_actual_client_secret
COGNITO_DOMAIN=carbontrack-xxxxx.auth.us-east-1.amazoncognito.com

# AWS Credentials (for development)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

## 🧪 Testing the Setup

### 1. Start the Backend Server

```bash
cd backend
./scripts/start.sh
```

### 2. Test User Registration

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "TestPass123",
       "first_name": "Test",
       "last_name": "User"
     }'
```

### 3. Check Email for Verification Code

Check the email inbox for the verification code, then confirm:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/confirm" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "confirmation_code": "123456"
     }'
```

### 4. Test Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "TestPass123"
     }'
```

## 🌐 Hosted UI Testing

You can also test using the Cognito Hosted UI:

1. Visit the hosted UI URL (provided in the script output)
2. Register a new user
3. Verify email
4. Log in

Example URL format:
```
https://carbontrack-xxxxx.auth.us-east-1.amazoncognito.com/login?client_id=your_client_id&response_type=code&scope=email+openid&redirect_uri=http://localhost:8000/callback
```

## 🔍 Verification Steps

To verify everything is working:

1. ✅ User Pool created in AWS Console
2. ✅ User Pool Client configured with secret
3. ✅ Backend can connect to Cognito (no auth errors in logs)
4. ✅ User registration creates user in Cognito
5. ✅ Email verification works
6. ✅ Login returns valid JWT tokens
7. ✅ Protected endpoints accept valid tokens

## 🛠️ Troubleshooting

### Common Issues:

1. **"AWS credentials not found"**
   - Run `aws configure` to set up credentials
   - Ensure IAM user has Cognito permissions

2. **"User pool domain already exists"**
   - Choose a different domain name in the script
   - Or use the existing domain

3. **"Invalid client_secret"**
   - Regenerate client secret in AWS Console
   - Update .env file with new secret

4. **Email not sending**
   - Check AWS SES configuration
   - Verify email sending limits

### Debug Commands:

```bash
# Test AWS connection
aws sts get-caller-identity

# List Cognito User Pools
aws cognito-idp list-user-pools --max-items 10

# Check backend logs
tail -f backend/server.log
```

## 🗑️ Cleanup (Optional)

To remove the AWS resources:

### Using Terraform:
```bash
cd infra
terraform destroy
```

### Using AWS CLI:
```bash
# Delete User Pool (this deletes everything)
aws cognito-idp delete-user-pool --user-pool-id your_pool_id
```

## 📚 Additional Resources

- [AWS Cognito Documentation](https://docs.aws.amazon.com/cognito/)
- [FastAPI Authentication Guide](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Token Debugging](https://jwt.io/)

---

✅ **Once completed, your AWS Cognito authentication will be fully operational!**
