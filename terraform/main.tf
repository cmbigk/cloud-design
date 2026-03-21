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

# -----------------
# Networking (VPC)
# -----------------
resource "aws_vpc" "k3s_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "cloud-design-vpc"
  }
}

resource "aws_subnet" "k3s_subnet_public" {
  vpc_id                  = aws_vpc.k3s_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "cloud-design-public-subnet"
  }
}

resource "aws_internet_gateway" "k3s_igw" {
  vpc_id = aws_vpc.k3s_vpc.id

  tags = {
    Name = "cloud-design-igw"
  }
}

resource "aws_route_table" "k3s_rt_public" {
  vpc_id = aws_vpc.k3s_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.k3s_igw.id
  }

  tags = {
    Name = "cloud-design-rt-public"
  }
}

resource "aws_route_table_association" "k3s_rta_public" {
  subnet_id      = aws_subnet.k3s_subnet_public.id
  route_table_id = aws_route_table.k3s_rt_public.id
}

# -----------------
# Security Groups
# -----------------
resource "aws_security_group" "k3s_sg" {
  name        = "k3s-node-sg"
  description = "Allow SSH, HTTP, HTTPS, and API access"
  vpc_id      = aws_vpc.k3s_vpc.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Kube API"
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "cloud-design-sg"
  }
}

# -----------------
# IAM Role (ECR Pull)
# -----------------
resource "aws_iam_role" "k3s_ec2_role" {
  name = "k3s_ec2_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecr_read" {
  role       = aws_iam_role.k3s_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "k3s_ec2_profile" {
  name = "k3s_ec2_profile"
  role = aws_iam_role.k3s_ec2_role.name
}
