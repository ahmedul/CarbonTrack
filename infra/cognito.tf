# AWS Cognito Infrastructure for CarbonTrack
# This Terraform configuration creates the necessary AWS Cognito resources

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "carbontrack"
}

# Cognito User Pool
resource "aws_cognito_user_pool" "main" {
  name = "${var.project_name}-users"

  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }

  # Auto verified attributes
  auto_verified_attributes = ["email"]

  # Username attributes
  username_attributes = ["email"]

  # Email verification
  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    default_email_subject = "Welcome to CarbonTrack - Verify your email"
    default_email_message = "Welcome to CarbonTrack! Your verification code is {####}"
  }

  # Admin create user config
  admin_create_user_config {
    allow_admin_create_user_only = false
    invite_message_template {
      email_subject = "Welcome to CarbonTrack"
      email_message = "Welcome to CarbonTrack! Your username is {username} and temporary password is {####}"
    }
  }

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  tags = {
    Name        = "${var.project_name}-user-pool"
    Environment = "development"
    Project     = "CarbonTrack"
  }
}

# Cognito User Pool Client
resource "aws_cognito_user_pool_client" "main" {
  name         = "${var.project_name}-client"
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret = true

  # Auth flows
  explicit_auth_flows = [
    "ADMIN_NO_SRP_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]

  # Supported identity providers
  supported_identity_providers = ["COGNITO"]

  # Attributes
  read_attributes  = ["email"]
  write_attributes = ["email"]

  # Token validity
  access_token_validity  = 60    # 1 hour
  id_token_validity      = 60    # 1 hour  
  refresh_token_validity = 30    # 30 days

  # Prevent user existence errors
  prevent_user_existence_errors = "ENABLED"
}

# Cognito User Pool Domain
resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${var.project_name}-${random_string.domain_suffix.result}"
  user_pool_id = aws_cognito_user_pool.main.id
}

# Random string for unique domain
resource "random_string" "domain_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Outputs
output "user_pool_id" {
  description = "ID of the Cognito user pool"
  value       = aws_cognito_user_pool.main.id
}

output "user_pool_client_id" {
  description = "ID of the Cognito user pool client"
  value       = aws_cognito_user_pool_client.main.id
}

output "user_pool_client_secret" {
  description = "Secret of the Cognito user pool client"
  value       = aws_cognito_user_pool_client.main.client_secret
  sensitive   = true
}

output "user_pool_domain" {
  description = "Domain of the Cognito user pool"
  value       = aws_cognito_user_pool_domain.main.domain
}

output "hosted_ui_url" {
  description = "URL for the Cognito hosted UI"
  value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${var.aws_region}.amazoncognito.com"
}

output "env_configuration" {
  description = "Environment variables for .env file"
  value = <<EOF
# AWS Cognito Configuration
AWS_REGION=${var.aws_region}
COGNITO_USER_POOL_ID=${aws_cognito_user_pool.main.id}
COGNITO_CLIENT_ID=${aws_cognito_user_pool_client.main.id}
COGNITO_CLIENT_SECRET=${aws_cognito_user_pool_client.main.client_secret}
COGNITO_DOMAIN=${aws_cognito_user_pool_domain.main.domain}.auth.${var.aws_region}.amazoncognito.com
EOF
}
