# Cloud-Design Microservices Project

This project deploys a highly scalable microservices architecture using the "True Free Tier" approach on AWS. It provisions AWS infrastructure via **Terraform** and orchestrates containerized applications using **K3s (Lightweight Kubernetes)** on a single AWS EC2 instance.

## Quick Links
- [Project Overview](task/project.md)
- [Technical Operations Guide](documentation/tech-guide.md)
- [Phase Completion Report](documentation/phase_completion_report.md)
- [AWS Implementation Approaches](documentation/aws_approaches.md)

## Application Architecture
The system consists of 6 interconnected microservices:
1. **API Gateway:** Entry point for all HTTP requests (Python/Flask backend using Waitress on port 3000).
2. **Inventory Application:** Manages movie details and queries via REST API.
3. **Billing Application:** Asynchronously processes incoming billing orders using RabbitMQ queue workers.
4. **Inventory Database:** PostgreSQL StatefulSet hosting the `movies_db`.
5. **Billing Database:** PostgreSQL StatefulSet hosting the `orders_db`.
6. **RabbitMQ Message Broker:** Facilitates event-driven architecture between the API Gateway and Billing Application.

## Prerequisites
Before you can run or modify this project, you must have the following tools installed locally:
- **AWS CLI:** Configured with your AWS account credentials (run `aws configure`).
- **Docker:** Running locally to build Linux AMD64 container images.
- **Terraform:** Used for Infrastructure as Code (IaC) deployment.
- **kubectl:** The Kubernetes command-line tool.

## Setup & Configuration

### 1. Configure AWS Region
By default, the Terraform code is configured to deploy to `eu-north-1`. You can change this within `terraform/variables.tf`:
```hcl
variable "aws_region" {
  default = "eu-north-1"
}
```

### 2. Provision AWS Infrastructure
The first step is standing up the underlying resources (VPC, Security Groups, ECR Registries, and the EC2 Spot Instance).
```bash
cd terraform
terraform init
terraform apply
```
After successful deployment, Terraform will output the `ec2_public_ip` and your private `ecr_repository_urls`.

### 3. Build & Push Docker Images
To push your applications securely to AWS ECR, execute the automated script:
```bash
./scripts/push_images.sh
```
*Note: This script automatically tags and cross-compiles your local images to `linux/amd64` to avoid architecture mismatches.*

### 4. Deploy Kubernetes Manifests
Run the deployment script to retrieve the private `kubeconfig` securely using EC2 Instance Connect and deploy all logic:
```bash
./scripts/deploy.sh
```

## Usage
Once the Kubernetes deployment completes, the API Gateway is exposed over the internet via the EC2 Public IP on port 80 (routed internally by the Traefik Ingress to port 3000).

### Movie Inventory (Synchronous Request)
**Retrieve all Movies:**
```bash
curl http://<EC2-PUBLIC-IP>/api/movies
```
**Add a Movie:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"title": "Inception", "director": "Christopher Nolan", "year": 2010}' \
  http://<EC2-PUBLIC-IP>/api/movies
```

### Billing Service (Asynchronous Event-Driven)
**Submit a Billing Order:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"user_id": 1, "number_of_items": 3, "total_amount": 45.50}' \
  http://<EC2-PUBLIC-IP>/api/billing
```
**Verify Processed Bills:**
```bash
curl http://<EC2-PUBLIC-IP>/api/billing
```

## Clean Up (Cost Savings)
When done, ensure you destroy the architecture to preserve your AWS limits and remaining credits.
```bash
cd terraform
terraform destroy
```