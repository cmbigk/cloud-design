locals {
  repositories = [
    "api-gateway",
    "inventory-app",
    "billing-app",
    "inventory-db",
    "billing-db",
    "rabbit-queue"
  ]
}

resource "aws_ecr_repository" "app_repos" {
  for_each = toset(local.repositories)
  name     = each.key

  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "cloud-design-${each.key}"
  }
}
