#!/bin/bash

# CarbonTrack Production Deployment Script
# This script automates the complete deployment of CarbonTrack to AWS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="carbontrack-production"
REGION="us-east-1"
DOMAIN_NAME="carbontrack.com"  # Change this to your domain
CERTIFICATE_ARN=""  # Will be set from AWS Certificate Manager
ENVIRONMENT="production"

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is configured
check_aws_cli() {
    print_status "Checking AWS CLI configuration..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "AWS CLI is configured"
}

# Validate domain and certificate
validate_domain_certificate() {
    print_status "Validating domain and SSL certificate..."
    
    # Check if certificate exists for the domain
    CERTIFICATE_ARN=$(aws acm list-certificates \
        --region us-east-1 \
        --query "CertificateSummary[?DomainName=='${DOMAIN_NAME}'].CertificateArn" \
        --output text 2>/dev/null || echo "")
    
    if [ -z "$CERTIFICATE_ARN" ]; then
        print_warning "No SSL certificate found for ${DOMAIN_NAME}"
        print_status "You can either:"
        echo "  1. Create a certificate in AWS Certificate Manager (ACM) for ${DOMAIN_NAME}"
        echo "  2. Use the default CloudFront domain (not recommended for production)"
        
        read -p "Do you want to continue without custom domain? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Deployment cancelled. Please create an SSL certificate in ACM first."
            exit 1
        fi
        
        # Use a placeholder certificate ARN
        CERTIFICATE_ARN="arn:aws:acm:us-east-1:123456789012:certificate/placeholder"
        print_warning "Using placeholder certificate. CloudFront will use default domain."
    else
        print_success "Found SSL certificate: ${CERTIFICATE_ARN}"
    fi
}

# Create S3 bucket for deployment artifacts
create_deployment_bucket() {
    print_status "Creating S3 bucket for deployment artifacts..."
    
    DEPLOYMENT_BUCKET="carbontrack-deployment-artifacts-$(date +%s)"
    
    if aws s3 mb s3://${DEPLOYMENT_BUCKET} --region ${REGION}; then
        print_success "Created deployment bucket: ${DEPLOYMENT_BUCKET}"
    else
        print_error "Failed to create deployment bucket"
        exit 1
    fi
}

# Package Lambda function
package_lambda() {
    print_status "Packaging Lambda function..."
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    
    # Copy backend files
    cp -r backend/* ${TEMP_DIR}/
    
    # Install dependencies
    cd ${TEMP_DIR}
    pip install -r requirements.txt -t .
    
    # Create Lambda deployment package
    zip -r lambda-deployment.zip . -x "requirements.txt" "__pycache__/*" "*.pyc"
    
    # Upload to S3
    aws s3 cp lambda-deployment.zip s3://${DEPLOYMENT_BUCKET}/lambda-deployment.zip
    
    print_success "Lambda package uploaded to S3"
    
    # Cleanup
    cd - > /dev/null
    rm -rf ${TEMP_DIR}
}

# Deploy CloudFormation stack
deploy_infrastructure() {
    print_status "Deploying CloudFormation stack..."
    
    aws cloudformation deploy \
        --template-file infra/cloudformation-template.yaml \
        --stack-name ${STACK_NAME} \
        --parameter-overrides \
            DomainName=${DOMAIN_NAME} \
            CertificateArn=${CERTIFICATE_ARN} \
            Environment=${ENVIRONMENT} \
        --capabilities CAPABILITY_NAMED_IAM \
        --region ${REGION}
    
    if [ $? -eq 0 ]; then
        print_success "CloudFormation stack deployed successfully"
    else
        print_error "Failed to deploy CloudFormation stack"
        exit 1
    fi
}

# Update Lambda function code
update_lambda_code() {
    print_status "Updating Lambda function code..."
    
    # Get the Lambda function name from CloudFormation outputs
    LAMBDA_FUNCTION_NAME=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --query "Stacks[0].Outputs[?OutputKey=='BackendLambdaName'].OutputValue" \
        --output text \
        --region ${REGION} 2>/dev/null || echo "carbontrack-api-${ENVIRONMENT}")
    
    # Update function code
    aws lambda update-function-code \
        --function-name ${LAMBDA_FUNCTION_NAME} \
        --s3-bucket ${DEPLOYMENT_BUCKET} \
        --s3-key lambda-deployment.zip \
        --region ${REGION}
    
    print_success "Lambda function code updated"
}

# Build and deploy frontend
deploy_frontend() {
    print_status "Building and deploying frontend..."
    
    # Get the S3 bucket name and API URL from CloudFormation outputs
    FRONTEND_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --query "Stacks[0].Outputs[?OutputKey=='FrontendBucket'].OutputValue" \
        --output text \
        --region ${REGION})
    
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --query "Stacks[0].Outputs[?OutputKey=='ApiGatewayURL'].OutputValue" \
        --output text \
        --region ${REGION})
    
    if [ -z "$FRONTEND_BUCKET" ] || [ -z "$API_URL" ]; then
        print_error "Failed to get CloudFormation outputs"
        exit 1
    fi
    
    # Create temporary directory for build
    BUILD_DIR=$(mktemp -d)
    cp -r frontend/* ${BUILD_DIR}/
    
    # Replace API URL in frontend files
    cd ${BUILD_DIR}
    if [ -f "index.html" ]; then
        sed -i "s|http://localhost:8000|${API_URL}|g" index.html
        sed -i "s|API_BASE_URL = 'http://localhost:8000'|API_BASE_URL = '${API_URL}'|g" index.html
    fi
    
    # Sync to S3
    aws s3 sync . s3://${FRONTEND_BUCKET} \
        --delete \
        --cache-control "public, max-age=31536000" \
        --exclude "*.html" \
        --region ${REGION}
    
    # Upload HTML files with shorter cache
    aws s3 sync . s3://${FRONTEND_BUCKET} \
        --cache-control "public, max-age=0, must-revalidate" \
        --include "*.html" \
        --region ${REGION}
    
    print_success "Frontend deployed to S3"
    
    # Invalidate CloudFront cache
    CLOUDFRONT_DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" \
        --output text \
        --region ${REGION})
    
    if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
        print_status "Invalidating CloudFront cache..."
        aws cloudfront create-invalidation \
            --distribution-id ${CLOUDFRONT_DISTRIBUTION_ID} \
            --paths "/*" > /dev/null
        print_success "CloudFront cache invalidated"
    fi
    
    # Cleanup
    cd - > /dev/null
    rm -rf ${BUILD_DIR}
}

# Get deployment URLs
get_deployment_info() {
    print_status "Getting deployment information..."
    
    # Get CloudFormation outputs
    STACK_OUTPUTS=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --query "Stacks[0].Outputs" \
        --output json \
        --region ${REGION})
    
    FRONTEND_URL=$(echo ${STACK_OUTPUTS} | jq -r '.[] | select(.OutputKey=="FrontendURL") | .OutputValue')
    CUSTOM_DOMAIN_URL=$(echo ${STACK_OUTPUTS} | jq -r '.[] | select(.OutputKey=="CustomDomainURL") | .OutputValue')
    API_URL=$(echo ${STACK_OUTPUTS} | jq -r '.[] | select(.OutputKey=="ApiGatewayURL") | .OutputValue')
    USER_POOL_ID=$(echo ${STACK_OUTPUTS} | jq -r '.[] | select(.OutputKey=="UserPoolId") | .OutputValue')
    USER_POOL_CLIENT_ID=$(echo ${STACK_OUTPUTS} | jq -r '.[] | select(.OutputKey=="UserPoolClientId") | .OutputValue')
    
    echo
    print_success "🚀 CarbonTrack Deployment Complete!"
    echo "=================================================="
    echo -e "${GREEN}Frontend URLs:${NC}"
    echo -e "  CloudFront: ${FRONTEND_URL}"
    if [ ! -z "$CUSTOM_DOMAIN_URL" ] && [ "$CUSTOM_DOMAIN_URL" != "null" ]; then
        echo -e "  Custom Domain: ${CUSTOM_DOMAIN_URL}"
    fi
    echo
    echo -e "${GREEN}API Endpoint:${NC}"
    echo -e "  ${API_URL}"
    echo
    echo -e "${GREEN}Authentication:${NC}"
    echo -e "  User Pool ID: ${USER_POOL_ID}"
    echo -e "  Client ID: ${USER_POOL_CLIENT_ID}"
    echo "=================================================="
    echo
}

# Cleanup deployment artifacts
cleanup() {
    print_status "Cleaning up deployment artifacts..."
    
    if [ ! -z "$DEPLOYMENT_BUCKET" ]; then
        aws s3 rb s3://${DEPLOYMENT_BUCKET} --force
        print_success "Deployment bucket cleaned up"
    fi
}

# Main deployment flow
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                          CarbonTrack Production Deploy                       ║"
    echo "║                      Carbon Footprint Tracking SaaS                         ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_status "Starting CarbonTrack production deployment..."
    print_status "Domain: ${DOMAIN_NAME}"
    print_status "Region: ${REGION}"
    print_status "Environment: ${ENVIRONMENT}"
    echo
    
    # Deployment steps
    check_aws_cli
    validate_domain_certificate
    create_deployment_bucket
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    package_lambda
    deploy_infrastructure
    update_lambda_code
    deploy_frontend
    get_deployment_info
    
    print_success "🎉 Deployment completed successfully!"
}

# Handle script interruption
trap 'print_error "Deployment interrupted"; cleanup; exit 1' INT TERM

# Run main function
main "$@"