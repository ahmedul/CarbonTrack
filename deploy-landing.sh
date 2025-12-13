#!/bin/bash

# CarbonTrack Landing Page Deployment Script
# Deploys only the landing page (no CSRD features)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
S3_BUCKET="carbontrack-frontend-production"  # Your existing S3 bucket
CLOUDFRONT_DISTRIBUTION_ID="EUKA4HQFK6MC"  # Your existing CloudFront distribution
REGION="eu-central-1"

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

# Verify S3 bucket exists
verify_bucket() {
    print_status "Verifying S3 bucket exists..."
    
    if aws s3 ls s3://${S3_BUCKET} --region ${REGION} &> /dev/null; then
        print_success "S3 bucket found: ${S3_BUCKET}"
    else
        print_error "S3 bucket not found: ${S3_BUCKET}"
        print_error "Please update S3_BUCKET in this script with your actual bucket name"
        exit 1
    fi
}

# Deploy landing page
deploy_landing_page() {
    print_status "Deploying landing page to S3..."
    
    # Upload landing.html with cache control
    aws s3 cp landing.html s3://${S3_BUCKET}/landing.html \
        --region ${REGION} \
        --cache-control "public, max-age=300, must-revalidate" \
        --content-type "text/html"
    
    if [ $? -eq 0 ]; then
        print_success "Landing page uploaded successfully"
    else
        print_error "Failed to upload landing page"
        exit 1
    fi
}

# Optional: Deploy as index.html (root page)
deploy_as_root() {
    print_warning "Do you want to make the landing page your root page (index.html)?"
    echo "  Current: index.html redirects to app"
    echo "  New: landing.html becomes the homepage"
    read -p "Deploy landing page as homepage? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Backing up current index.html..."
        
        # Backup current index.html
        aws s3 cp s3://${S3_BUCKET}/index.html s3://${S3_BUCKET}/index.html.backup \
            --region ${REGION}
        
        # Deploy landing as index.html
        aws s3 cp landing.html s3://${S3_BUCKET}/index.html \
            --region ${REGION} \
            --cache-control "public, max-age=300, must-revalidate" \
            --content-type "text/html"
        
        print_success "Landing page deployed as homepage (index.html)"
        print_status "Original index.html backed up as index.html.backup"
    else
        print_status "Landing page deployed as /landing.html only"
        print_status "Access it at: https://carbontracksystem.com/landing.html"
    fi
}

# Invalidate CloudFront cache
invalidate_cloudfront() {
    print_status "Invalidating CloudFront cache..."
    
    INVALIDATION_PATHS="/landing.html"
    
    # Ask if deployed as root
    if aws s3 ls s3://${S3_BUCKET}/index.html.backup --region ${REGION} &> /dev/null; then
        INVALIDATION_PATHS="/landing.html /index.html"
    fi
    
    aws cloudfront create-invalidation \
        --distribution-id ${CLOUDFRONT_DISTRIBUTION_ID} \
        --paths ${INVALIDATION_PATHS} \
        --region us-east-1 \
        > /dev/null
    
    if [ $? -eq 0 ]; then
        print_success "CloudFront cache invalidated"
        print_status "Changes will be visible worldwide within 5-10 minutes"
    else
        print_warning "CloudFront invalidation failed, but files are uploaded"
        print_status "Cache will update naturally within 24 hours"
    fi
}

# Show deployment URLs
show_urls() {
    echo
    print_success "🚀 Landing Page Deployment Complete!"
    echo "=================================================="
    echo -e "${GREEN}Live URLs:${NC}"
    echo -e "  Landing Page: https://carbontracksystem.com/landing.html"
    
    if aws s3 ls s3://${S3_BUCKET}/index.html.backup --region ${REGION} &> /dev/null; then
        echo -e "  Homepage: https://carbontracksystem.com/"
        echo -e "  (Landing page is now the root)"
    fi
    
    echo -e "  App Domain: https://app.carbontracksystem.com"
    echo
    echo -e "${GREEN}CloudFront Distribution:${NC}"
    echo -e "  Distribution ID: ${CLOUDFRONT_DISTRIBUTION_ID}"
    echo -e "  Status: Cache invalidation in progress"
    echo "=================================================="
    echo
    print_status "Note: Changes may take 5-10 minutes to propagate globally"
}

# Main deployment flow
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    CarbonTrack Landing Page Deployment                       ║"
    echo "║                        (CSRD Features NOT Included)                          ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_status "Starting landing page deployment..."
    print_status "Target: ${S3_BUCKET}"
    print_status "Region: ${REGION}"
    echo
    
    # Deployment steps
    check_aws_cli
    verify_bucket
    deploy_landing_page
    deploy_as_root
    invalidate_cloudfront
    show_urls
    
    print_success "🎉 Landing page deployed successfully!"
    echo
    print_status "What's deployed:"
    echo "  ✅ Landing page with CSRD information"
    echo "  ✅ Pricing tables (all tiers)"
    echo "  ✅ Product roadmap"
    echo "  ✅ Professional marketing copy"
    echo
    print_status "What's NOT deployed:"
    echo "  ⏳ CSRD Compliance Module (backend)"
    echo "  ⏳ CSRD Frontend UI"
    echo "  ⏳ Premium feature gating"
    echo
    print_status "Next steps:"
    echo "  1. Visit https://carbontracksystem.com/landing.html"
    echo "  2. Test all sections and links"
    echo "  3. Continue CSRD development on feature branch"
    echo "  4. Deploy CSRD features after thorough testing"
}

# Handle script interruption
trap 'print_error "Deployment interrupted"; exit 1' INT TERM

# Check if landing.html exists
if [ ! -f "landing.html" ]; then
    print_error "landing.html not found in current directory"
    print_error "Please run this script from the CarbonTrack root directory"
    exit 1
fi

# Run main function
main "$@"
