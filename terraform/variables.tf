variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 Instance Type (t3.micro is free tier eligible, t3.small is recommended for >1GB workloads)"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "SSH Key Pair name. Leave empty if you don't have one and will use EC2 Instance Connect."
  type        = string
  default     = ""
}
