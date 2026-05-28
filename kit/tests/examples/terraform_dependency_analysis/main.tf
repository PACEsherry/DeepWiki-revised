# Main Terraform configuration file
# Sets up AWS provider and basic infrastructure

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# VPC and networking are defined in network.tf
# S3 and storage components are defined in storage.tf
# Compute resources are defined in compute.tf
# Database resources are defined in database.tf
# Security components are defined in security.tf
# Outputs are defined in outputs.tf
