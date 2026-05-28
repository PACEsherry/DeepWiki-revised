variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "terraform-analyzer-demo"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for the private subnets"
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "db_subnet_cidrs" {
  description = "CIDR blocks for the database subnets"
  type        = list(string)
  default     = ["10.0.5.0/24", "10.0.6.0/24"]
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.small"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "appdb"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "dbadmin"
}

# In a real scenario, you would use a secret manager or pass this as a parameter
variable "db_password" {
  description = "Database master password"
  type        = string
  default     = "YourPwdShouldBeDynamic!"
  sensitive   = true
}

# Domain configuration
variable "domain_name" {
  description = "Main domain name for the application"
  type        = string
  default     = "example.com"
}

# Bucket configuration
variable "enable_logging_bucket" {
  description = "Whether to create an S3 bucket for logs"
  type        = bool
  default     = true
}

# Auto scaling configuration
variable "min_size" {
  description = "Minimum size for the auto scaling group"
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum size for the auto scaling group"
  type        = number
  default     = 5
}

variable "desired_capacity" {
  description = "Desired capacity for the auto scaling group"
  type        = number
  default     = 2
}
