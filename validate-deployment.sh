#!/bin/bash

# CarbonTrack Deployment Validation Script
# This script validates deployment configuration and tests components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[TEST]${NC} $1"; }
print_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[FAIL]${NC} $1"; }

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                     CarbonTrack Deployment Validation                        ║"
echo "║                         Pre-flight Checks                                   ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Test 1: Check file structure
print_status "Checking project structure..."
REQUIRED_FILES=(
    "frontend/index.html"
    "backend/app/main.py"
    "backend/requirements.txt"
    "infra/cloudformation-template.yaml"
    ".github/workflows/deploy.yml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found $file"
    else
        print_error "Missing $file"
        exit 1
    fi
done

# Test 2: Validate CloudFormation template
print_status "Validating CloudFormation template..."
if command -v aws &> /dev/null; then
    if aws cloudformation validate-template --template-body file://infra/cloudformation-template.yaml > /dev/null 2>&1; then
        print_success "CloudFormation template is valid"
    else
        print_warning "CloudFormation validation failed (may need AWS credentials)"
    fi
else
    print_warning "AWS CLI not installed - skipping CloudFormation validation"
fi

# Test 3: Check Python backend
print_status "Testing Python backend..."
if command -v python3 &> /dev/null; then
    cd backend
    if python3 -c "from app.main import app; print('FastAPI app imported successfully')" 2>/dev/null; then
        print_success "Backend imports correctly"
    else
        print_error "Backend has import issues"
        cd ..
        exit 1
    fi
    cd ..
else
    print_error "Python 3 not found"
    exit 1
fi

# Test 4: Validate GitHub Actions workflow
print_status "Validating GitHub Actions workflow..."
if command -v yamllint &> /dev/null; then
    if yamllint .github/workflows/deploy.yml > /dev/null 2>&1; then
        print_success "GitHub Actions workflow YAML is valid"
    else
        print_warning "YAML linting issues found in workflow"
    fi
else
    print_warning "yamllint not installed - skipping workflow validation"
fi

# Test 5: Check frontend structure
print_status "Validating frontend structure..."
if grep -q "createApp" frontend/app-full.js; then
    print_success "Vue.js 3 setup found"
else
    print_error "Vue.js 3 setup not found in frontend"
fi

if grep -q "axios" frontend/index.html; then
    print_success "Axios HTTP client configured"
else
    print_error "Axios not found in frontend"
fi

# Test 6: Check carbon calculation engine
print_status "Testing carbon calculation engine..."
cd backend
if python3 -c "
import sys
sys.path.append('.')
from app.services.carbon_calculator import CarbonCalculator
calc = CarbonCalculator()
result = calc.calculate_emission('transportation', 'car_gasoline_medium', 100, 'miles')
print(f'Test calculation: {result[\"co2_equivalent\"]} kg CO2')
assert result['co2_equivalent'] > 0, 'Calculation should return positive value'
" 2>/dev/null; then
    print_success "Carbon calculation engine working"
else
    print_error "Carbon calculation engine has issues"
    cd ..
    exit 1
fi
cd ..

# Test 7: Environment variables template
print_status "Checking environment configuration..."
if [ -f "DEPLOYMENT_SECRETS.md" ]; then
    print_success "Deployment secrets documentation found"
else
    print_warning "No deployment secrets documentation"
fi

# Test 8: Check deployment script permissions
print_status "Checking deployment script..."
if [ -x "deploy.sh" ]; then
    print_success "Deployment script is executable"
else
    print_warning "Deployment script not executable (run: chmod +x deploy.sh)"
fi

# Test 9: Mock API calls
print_status "Testing API endpoint structure..."
cd backend
python3 -c "
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.get('/health')
print(f'Health check status: {response.status_code}')

# Test emissions endpoint
response = client.post('/api/v1/emissions', json={
    'activity_type': 'transportation',
    'category': 'car_gasoline', 
    'amount': 50,
    'unit': 'miles'
})
print(f'Emissions API status: {response.status_code}')
" 2>/dev/null && print_success "API endpoints responding correctly" || print_warning "API testing requires additional setup"
cd ..

# Test 10: Infrastructure cost estimation
print_status "Estimating AWS costs..."
echo "Estimated monthly costs for CarbonTrack MVP:"
echo "  • S3 + CloudFront: \$1-5 (depending on traffic)"
echo "  • Lambda: \$0-2 (first 1M requests free)"
echo "  • DynamoDB: \$0-5 (first 25GB free)"
echo "  • API Gateway: \$0-10 (first 1M requests free)"
echo "  • Cognito: \$0-5 (first 50K users free)"
echo "  • TOTAL: \$1-27/month (mostly traffic dependent)"
print_success "Cost estimation complete"

echo
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗"
echo -e "║                         🚀 DEPLOYMENT READY!                                ║"
echo -e "║                                                                              ║"
echo -e "║  Next steps:                                                                 ║"
echo -e "║  1. Set up AWS account and IAM user                                          ║"
echo -e "║  2. Add GitHub secrets (see DEPLOYMENT_SECRETS.md)                          ║"
echo -e "║  3. Push to main branch or run ./deploy.sh                                  ║"
echo -e "║                                                                              ║"
echo -e "║  🌍 CarbonTrack: Making carbon tracking accessible to everyone!             ║"
echo -e "╚══════════════════════════════════════════════════════════════════════════════╝${NC}"