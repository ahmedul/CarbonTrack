#!/bin/bash

# CarbonTrack Security Validation Script
# Run before each deployment to ensure no secrets are committed

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SECURITY_ISSUES=0

print_header() {
    echo -e "${BLUE}🔒 CarbonTrack Security Validation${NC}"
    echo "=================================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((SECURITY_ISSUES++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((SECURITY_ISSUES++))
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check 1: Scan for potential secrets in code
check_secrets_in_code() {
    print_info "Checking for potential secrets in codebase..."
    
    # Patterns that might indicate secrets
    SECRET_PATTERNS=(
        "password\s*=\s*['\"][^'\"]{8,}['\"]"
        "api_key\s*=\s*['\"][^'\"]{15,}['\"]"
        "secret\s*=\s*['\"][^'\"]{15,}['\"]"
        "token\s*=\s*['\"][^'\"]{15,}['\"]"
        "AKIA[0-9A-Z]{16}"  # AWS Access Key pattern
        "github_pat_[0-9a-zA-Z_]{82}"  # GitHub Personal Access Token
        "sk-[a-zA-Z0-9]{48}"  # OpenAI API Key pattern
    )
    
    found_secrets=false
    
    for pattern in "${SECRET_PATTERNS[@]}"; do
        if grep -r -E "$pattern" --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.venv --exclude-dir=virtualenv --exclude-dir=__pycache__ --exclude="*test*.py" --exclude="*example*" . 2>/dev/null; then
            found_secrets=true
        fi
    done
    
    if $found_secrets; then
        print_error "Potential secrets found in code! Review and remove before committing."
    else
        print_success "No hardcoded secrets detected"
    fi
}

# Check 2: Validate .gitignore exists and covers common secret files
check_gitignore() {
    print_info "Validating .gitignore configuration..."
    
    if [ ! -f ".gitignore" ]; then
        print_error ".gitignore file missing!"
        return
    fi
    
    # Critical patterns that should be in .gitignore
    REQUIRED_PATTERNS=(
        "\.env"
        "secrets"
        "api-keys"
        "\.pem"
        "\.key"
        "aws-credentials"
        "config.*\.json"
    )
    
    missing_patterns=()
    for pattern in "${REQUIRED_PATTERNS[@]}"; do
        if ! grep -q "$pattern" .gitignore; then
            missing_patterns+=("$pattern")
        fi
    done
    
    if [ ${#missing_patterns[@]} -eq 0 ]; then
        print_success ".gitignore properly configured"
    else
        print_warning ".gitignore missing patterns: ${missing_patterns[*]}"
    fi
}

# Check 3: Look for common secret files that shouldn't exist
check_secret_files() {
    print_info "Checking for secret files that shouldn't be committed..."
    
    SECRET_FILES=(
        ".env"
        ".env.production"
        "aws-credentials.txt"
        "api-keys.txt"
        "secrets.json"
        "config/production.json"
        "github-token.txt"
        "*.pem"
        "*.key"
    )
    
    found_files=()
    for file_pattern in "${SECRET_FILES[@]}"; do
        if ls $file_pattern 2>/dev/null | grep -q .; then
            found_files+=($file_pattern)
        fi
    done
    
    if [ ${#found_files[@]} -eq 0 ]; then
        print_success "No secret files found in repository"
    else
        print_error "Secret files detected: ${found_files[*]}"
        print_info "Add these to .gitignore and remove from repository"
    fi
}

# Check 4: Validate GitHub Actions workflow security
check_github_actions() {
    print_info "Validating GitHub Actions security..."
    
    workflow_file=".github/workflows/deploy.yml"
    
    if [ ! -f "$workflow_file" ]; then
        print_warning "GitHub Actions workflow file not found"
        return
    fi
    
    # Check for secure practices
    if grep -q "workflow_dispatch" "$workflow_file"; then
        print_success "Manual deployment trigger configured"
    else
        print_warning "Consider adding manual deployment trigger (workflow_dispatch)"
    fi
    
    if grep -q "secrets\." "$workflow_file"; then
        print_success "Secrets properly referenced from GitHub secrets"
    else
        print_warning "No GitHub secrets usage detected"
    fi
    
    # Check for hardcoded values that should be secrets
    if grep -E "(aws_access_key|aws_secret_key|api_key)" "$workflow_file" | grep -v "secrets\."; then
        print_error "Potential hardcoded credentials in GitHub Actions"
    fi
}

# Check 5: Validate CloudFormation security
check_cloudformation() {
    print_info "Validating CloudFormation security..."
    
    cf_template="infra/cloudformation-template.yaml"
    
    if [ ! -f "$cf_template" ]; then
        print_warning "CloudFormation template not found"
        return
    fi
    
    # Check for proper parameter usage instead of hardcoded values
    if grep -E "DomainName.*carbontrack\.com" "$cf_template" > /dev/null; then
        print_warning "Hardcoded domain name found in CloudFormation template"
    fi
    
    # Check for proper tagging
    if grep -q "Application.*CarbonTrack" "$cf_template"; then
        print_success "Resources properly tagged for cost tracking"
    else
        print_warning "Missing resource tags for cost monitoring"
    fi
}

# Check 6: Validate AWS cost controls
check_cost_controls() {
    print_info "Validating cost control measures..."
    
    cost_file="AWS_COST_ANALYSIS.md"
    monitoring_file="infra/cost-monitoring.yaml"
    
    if [ -f "$cost_file" ] && [ -f "$monitoring_file" ]; then
        print_success "Cost monitoring configuration present"
    else
        print_warning "Cost monitoring files missing"
    fi
    
    # Check if budget is set in monitoring file
    if [ -f "$monitoring_file" ] && grep -q "BudgetAmount" "$monitoring_file"; then
        print_success "Budget controls configured"
    else
        print_warning "Budget controls not found"
    fi
}

# Check 7: Repository access controls
check_repository_access() {
    print_info "Checking repository access controls..."
    
    # This would need GitHub API access to check properly
    # For now, provide guidance
    print_info "Manual verification needed:"
    print_info "  1. Repository is private: GitHub → Settings → General"
    print_info "  2. Branch protection enabled: GitHub → Settings → Branches"
    print_info "  3. Actions restricted: GitHub → Settings → Actions"
}

# Main execution
main() {
    print_header
    echo
    
    check_secrets_in_code
    echo
    check_gitignore
    echo
    check_secret_files
    echo
    check_github_actions
    echo
    check_cloudformation
    echo
    check_cost_controls
    echo
    check_repository_access
    echo
    
    # Final results
    echo "=================================="
    if [ $SECURITY_ISSUES -eq 0 ]; then
        print_success "🎉 All security checks passed!"
        print_info "Repository is ready for secure deployment"
        echo
        print_info "Next steps:"
        print_info "  1. Make repository private on GitHub"
        print_info "  2. Add required secrets to GitHub repository"
        print_info "  3. Enable branch protection on main branch"
        print_info "  4. Set up AWS billing alerts"
        exit 0
    else
        print_error "⚠️ Found $SECURITY_ISSUES security issues!"
        print_info "Please fix these issues before deploying to production"
        echo
        print_info "Common fixes:"
        print_info "  1. Move hardcoded values to environment variables"
        print_info "  2. Add sensitive files to .gitignore"
        print_info "  3. Use GitHub Secrets for credentials"
        print_info "  4. Review CloudFormation parameters"
        exit 1
    fi
}

# Run security check
main "$@"