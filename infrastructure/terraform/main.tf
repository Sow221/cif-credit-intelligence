terraform {
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

# ---------------------------------------------------------------------------
# S3 : stockage des artefacts ML (.joblib) et des rapports de drift
# ---------------------------------------------------------------------------
resource "aws_s3_bucket" "cif_models" {
  bucket = var.models_bucket_name
  tags = {
    project = "cif-credit-intelligence"
  }
}

resource "aws_s3_bucket_versioning" "cif_models" {
  bucket = aws_s3_bucket.cif_models.id
  versioning_configuration {
    status = "Enabled"
  }
}

# ---------------------------------------------------------------------------
# RDS PostgreSQL (Free Tier) - base de donnees managée
# ---------------------------------------------------------------------------
resource "aws_db_subnet_group" "cif" {
  name       = "cif-db-subnet"
  subnet_ids = var.subnet_ids
}

resource "aws_db_instance" "cif_postgres" {
  identifier = "cif-credit-postgres"
  engine     = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  storage_type = "gp2"

  db_name              = var.db_name
  username             = var.db_username
  password             = var.db_password
  db_subnet_group_name = aws_db_subnet_group.cif.name
  skip_final_snapshot  = true

  vpc_security_group_ids = [aws_security_group.cif_db.id]

  backup_retention_period = 7

  tags = { project = "cif-credit-intelligence" }
}

# ---------------------------------------------------------------------------
# EC2 t2.micro (Free Tier) - serveur principal (Docker, API, MLflow)
# ---------------------------------------------------------------------------
resource "aws_security_group" "cif_web" {
  name        = "cif-web-sg"
  description = "Acces web + SSH vers le serveur CIF"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "cif_db" {
  name        = "cif-db-sg"
  description = "Acces PostgreSQL depuis le serveur web uniquement"

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.cif_web.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "cif_web" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t2.micro"
  vpc_security_group_ids = [aws_security_group.cif_web.id]
  subnet_id              = var.subnet_ids[0]
  key_name               = var.key_name

  user_data = <<-EOF
    #!/bin/bash
    set -e
    apt-get update
    apt-get install -y docker.io docker-compose-v2
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ubuntu
    EOF

  tags = {
    Name    = "cif-credit-production"
    project = "cif-credit-intelligence"
  }
}

# ---------------------------------------------------------------------------
# ECR : registre d'images Docker (Free Tier)
# ---------------------------------------------------------------------------
resource "aws_ecr_repository" "cif_backend" {
  name = "cif-backend"
}
resource "aws_ecr_repository" "cif_frontend" {
  name = "cif-frontend"
}
