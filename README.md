# Cloud-Design Project

This project implements a scalable microservices architecture on AWS using K3s.

## Quick Links
- [Project Overview](task/project.md)
- [Technical Guide](documentation/tech-guide.md)
- [AWS Implementation Approaches](documentation/aws_approaches.md)

## Components
- **API Gateway:** Entry point for all requests.
- **Inventory Service:** Manages movies and data persistence (PostgreSQL).
- **Billing Service:** Handles orders asynchronously using RabbitMQ and PostgreSQL.
- **Orchestration:** K3s running on a single AWS EC2 instance.
- **Infrastructure:** Provisioned natively via Terraform.

## Getting Started
To interact with the deployed cluster:
1. Ensure your AWS credentials are configured.
2. Run `./deploy.sh` to retrieve the latest `kubeconfig`.
3. Use `kubectl` commands to manage your pods (see the [Technical Guide](documentation/tech-guide.md)).