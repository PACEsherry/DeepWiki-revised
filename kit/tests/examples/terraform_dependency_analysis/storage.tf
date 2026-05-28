# Storage resources including S3 buckets and EFS file systems

# Application data bucket
resource "aws_s3_bucket" "app_data" {
  bucket = "${var.project_name}-app-data-${random_id.bucket_suffix.hex}"

  tags = {
    Name = "${var.project_name}-app-data"
  }
}

resource "aws_s3_bucket_versioning" "app_data_versioning" {
  bucket = aws_s3_bucket.app_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "app_data_encryption" {
  bucket = aws_s3_bucket.app_data.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.app.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# Logging bucket
resource "aws_s3_bucket" "logs" {
  count  = var.enable_logging_bucket ? 1 : 0
  bucket = "${var.project_name}-logs-${random_id.bucket_suffix.hex}"

  tags = {
    Name = "${var.project_name}-logs"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "logs_lifecycle" {
  count  = var.enable_logging_bucket ? 1 : 0
  bucket = aws_s3_bucket.logs[0].id

  rule {
    id     = "log-rotation"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}

# EFS file system for shared application files
resource "aws_efs_file_system" "app_files" {
  encrypted  = true
  kms_key_id = aws_kms_key.app.arn

  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }

  tags = {
    Name = "${var.project_name}-app-files"
  }
}

resource "aws_efs_mount_target" "app_files" {
  count           = length(var.private_subnet_cidrs)
  file_system_id  = aws_efs_file_system.app_files.id
  subnet_id       = aws_subnet.private[count.index].id
  security_groups = [aws_security_group.efs.id]
}

resource "aws_security_group" "efs" {
  name        = "${var.project_name}-efs-sg"
  description = "Security group for EFS mount points"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "NFS from web servers"
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-efs-sg"
  }
}

# Random ID for unique bucket names
resource "random_id" "bucket_suffix" {
  byte_length = 4
}
