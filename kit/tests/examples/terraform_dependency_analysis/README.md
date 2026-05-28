# Terraform Dependency Analysis Demo

This example demonstrates how to use the Kit SDK's Terraform Dependency Analyzer to analyze, visualize, and understand complex infrastructure relationships in Terraform configurations.

## Overview

The demo includes:

1. A complex AWS infrastructure setup with multiple interdependent resources:
   - Networking (VPC, subnets, gateways, route tables)
   - Computing (EC2, Auto Scaling Groups, Load Balancers)
   - Storage (S3 buckets, EFS)
   - Databases (RDS, ElastiCache)
   - Security (Security Groups, IAM roles, KMS keys)
   - DNS (Route53, ACM certificates)

2. A Python script that uses Kit's `TerraformDependencyAnalyzer` to:
   - Build a comprehensive dependency graph
   - Identify circular dependencies
   - Generate visualizations
   - Create LLM-friendly context about the infrastructure
   - Analyze key resources and their relationships

## File Structure

- `main.tf` - Provider configuration and project structure
- `variables.tf` - Input variables for the infrastructure
- `network.tf` - VPC, subnets, gateways, and routing
- `compute.tf` - EC2, Auto Scaling, and Load Balancers
- `storage.tf` - S3 buckets and EFS resources
- `database.tf` - RDS PostgreSQL and ElastiCache Redis
- `security.tf` - Security groups and encryption keys
- `dns.tf` - Route53 and ACM certificates
- `outputs.tf` - Output values from the infrastructure
- `analyze_terraform_deps.py` - Demo script using Kit's TerraformDependencyAnalyzer

## Running the Demo

To run the demo and analyze the Terraform configuration:

```bash
# Create output directory
mkdir -p output

# Run basic analysis
python analyze_terraform_deps.py

# Run with visualization
python analyze_terraform_deps.py --visualize

# Generate LLM-friendly context
python analyze_terraform_deps.py --llm-context

# Export in different formats
python analyze_terraform_deps.py --format json
python analyze_terraform_deps.py --format graphml

# Run all options
python analyze_terraform_deps.py --visualize --llm-context --format dot
```

## Key Features Demonstrated

This demo showcases how Kit's TerraformDependencyAnalyzer can:

1. **Map Resource Relationships**: Identify which resources depend on others, both directly and indirectly.

2. **Detect Potential Issues**: Find circular dependencies that might cause deployment problems.

3. **Visualize Architecture**: Generate visual representations of your infrastructure.

4. **Generate Documentation**: Create LLM-friendly context that describes the infrastructure in natural language.

5. **Identify Central Components**: Find the most interconnected resources in your infrastructure.

## Implementation Details

The analyzer uses HCL parsing to extract dependencies from Terraform files and builds a graph representation of the infrastructure. It can identify dependencies through:

- Direct references (e.g., `aws_instance.example.id`)
- String interpolations (e.g., `"${aws_vpc.main.id}"`)
- Resource attributes (e.g., within a resource's configuration)

The demo infrastructure is designed to have realistic dependencies that showcase the analyzer's capabilities, including resource references across different files and modules.
