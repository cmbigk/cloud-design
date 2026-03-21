output "ec2_public_ip" {
  description = "Public IP address of the K3s EC2 instance"
  value       = aws_instance.k3s_node.public_ip
}

output "ecr_repository_urls" {
  description = "URLs of the provisioned ECR repositories"
  value       = { for k, v in aws_ecr_repository.app_repos : k => v.repository_url }
}
