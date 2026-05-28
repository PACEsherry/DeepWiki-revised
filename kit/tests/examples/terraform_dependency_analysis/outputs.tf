# Output values from the infrastructure

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnets" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnets" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "database_subnets" {
  description = "List of database subnet IDs"
  value       = aws_subnet.database[*].id
}

output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.app.dns_name
}

output "domain_name" {
  description = "Domain name of the application"
  value       = var.domain_name
}

output "bastion_public_ip" {
  description = "Public IP address of the bastion host"
  value       = aws_instance.bastion.public_ip
}

output "db_endpoint" {
  description = "Endpoint for the primary database"
  value       = aws_db_instance.main.endpoint
}

output "db_replica_endpoint" {
  description = "Endpoint for the database replica"
  value       = aws_db_instance.replica.endpoint
}

output "redis_endpoint" {
  description = "Endpoint for the Redis cluster"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "app_bucket_name" {
  description = "Name of the S3 bucket for application data"
  value       = aws_s3_bucket.app_data.bucket
}

output "logs_bucket_name" {
  description = "Name of the S3 bucket for logs"
  value       = var.enable_logging_bucket ? aws_s3_bucket.logs[0].bucket : "Logging bucket not enabled"
}
