## Deploying the Solution on AWS

Based on the project requirements in `task/project.md` and the evaluation criteria in `task/audit.md`, you need to set up an architecture that is scalable, secure, and uses Terraform for Infrastructure as Code, while remaining **as cheap as possible**. 

The project mentions 6 main services: `api-gateway`, `inventory-app`, `billing-app`, `inventory-db` (Postgres), `billing-db` (Postgres), and `rabbit-queue` (RabbitMQ).

Here are the primary approaches on AWS compared by cost, ease of setup, and how they meet the project requirements.

---

### 1. The "True" Free Tier Route: Single EC2 Instance with K3s
Since you've already built this with K3s (local master/worker), the easiest and lowest-cost migration is to simply run your K3s cluster on a single AWS EC2 instance. 

* **How it works:** You use Terraform to provision a single `t2.micro` or `t3.micro` EC2 instance, install K3s on it via a startup script (user data), and deploy your existing Kubernetes manifests directly on the instance.
* **Cost:** **~$0/month** initially. Upgrading to a `t3.small` (2GB RAM) costs about ~$15/month or ~$5/month if configured as an EC2 Spot Instance.
* **Ease of Setup:** **Easiest**. Reuses your existing manifests.

#### Assessment against Project Requirements:
* **Auto-Scaling:** **Poor.** You are constrained to a single EC2 instance. Auto-scaling would require complex bash scripting logic to join new spot instances to the K3s cluster. You rely entirely on vertical scaling (choosing a larger instance size) rather than horizontal cloud scaling.
* **Monitoring & Logging:** You must deploy and manage your own open-source stack (Prometheus, Grafana, ELK) inside the K3s cluster since there's no native AWS integration. The infrastructure itself can be monitored at a basic VM level via CloudWatch.
* **Security & Encryption:** Network security is managed at the EC2 Security Group boundary, but internal pod communication relies on standard K3s networking. You will have to encrypt K3s secrets yourself. For managed authentication (Cognito) or HTTPS (ACM), you would still need to deploy an Application Load Balancer (ALB) in front of the EC2 instance, slightly increasing complexity.
* **Analyzing Resource Use:** You can view total EC2 CPU/RAM in CloudWatch but need Prometheus/Grafana inside K3s to track individual container usage against constraints.

---

### 2. The Native AWS Managed Route: ECS with EC2 Capacity (Recommended for Learning)
Instead of deploying Kubernetes, you write **ECS Task Definitions** for each microservice and use an ECS Capacity Provider mapping to an Auto Scaling Group of free-tier eligible EC2 instances.

* **How it works:** You package apps into Docker images, push them to AWS ECR, and let ECS orchestrate the containers onto your managed EC2 instances.
* **Cost:** **~$0/month**. You only pay for the underlying EC2 instance.
* **Ease of Setup:** **Medium**. Heavy Terraform lifting (ECS Clusters, Task Definitions, ECS Services, IAM execution roles, ALB setup).

#### Assessment against Project Requirements:
* **Auto-Scaling:** **Excellent.** ECS integrates flawlessly with AWS Auto Scaling. You can scale the ECS tasks dynamically based on CPU or memory thresholds, and when the tasks require more capacity, the EC2 Auto Scaling Group will spin up new EC2 instances automatically.
* **Monitoring & Logging:** **Excellent.** ECS pushes standard output container logs natively to AWS CloudWatch via the `awslogs` driver. No ELK stack required for basic compliance.
* **Security & Encryption:** **Excellent.** You assign specific **IAM Task Roles** to individual containers, providing tight, least-privilege AWS access. Environment variables can be encrypted cleanly using AWS System Manager Parameter Store or AWS Secrets Manager. Native integration with ALB makes implementing AWS Certificate Manager (ACM) for HTTPS and Amazon Cognito for API authentication very straightforward. You can also enforce placement in private VPC subnets.
* **Analyzing Resource Use:** CloudWatch provides out-of-the-box, service-level and cluster-level metrics for CPU and Memory, ensuring you can monitor if your Spot instances are sufficient.

---

### 3. The Serverless Route: ECS with Fargate
Fargate is similar to ECS but removes the underlying EC2 instances entirely. You define CPU/RAM limits for the task, and AWS runs it serverlessly.

* **Cost:** **Expensive ($20-$40/month)**. No Free Tier. You pay per second for every vCPU and GB allocated across all 6 services.
* **Ease of Setup:** **Medium/Hard**. Same Terraform requirements as ECS with EC2, minus the EC2 capacity providers.

#### Assessment against Project Requirements:
* **Auto-Scaling:** **Superb.** Scaling is purely horizontal down to the container level. Adding an instance of the billing API happens in seconds without worrying about underlying EC2 node capacity.
* **Monitoring & Logging:** Fully native CloudWatch integration. You can enable Container Insights to get deep operational analytics.
* **Security & Encryption:** **Supreme.** Every single Fargate task runs in isolated compute environments. The best security available natively. Complete alignment with VPC boundaries, KMS encryption, and IAM permissions.
* **Analyzing Resource Use:** Since you don't manage VMs, resource consumption metrics in CloudWatch tie directly back to the exact dollar amount you are spending, making cost-optimization highly transparent.

---

### 4. The Managed Kubernetes Route: AWS EKS
EKS is AWS’s fully managed Kubernetes control plane. It satisfies the documentation's suggestion to use Kubernetes orchestrators but at an enterprise price.

* **Cost:** **Very Expensive ($75+/month)**. $0.10 per hour just to keep the Kubernetes control plane running. 
* **Ease of Setup:** **Hard**. EKS has a steep learning curve, especially gluing together IAM roles, VPCs, and the Control Plane in Terraform.

#### Assessment against Project Requirements:
* **Auto-Scaling:** **Excellent.** Utilizes the Kubernetes Horizontal Pod Autoscaler (HPA) alongside Cluster Autoscaler or Karpenter for managing backend nodes.
* **Monitoring & Logging:** Compatible with CloudWatch Container Insights for EKS or standard Prometheus/Grafana operator stacks.
* **Security & Encryption:** **Enterprise-grade.** Offers KMS secrets encryption, IAM Roles for Service Accounts (IRSA) giving fine-grained AWS permissions to pods, and AWS VPC CNI for native IP addressing inside the cluster. Very easy to integrate with ALB Ingress Controllers for ACM/Cognito.
* **Analyzing Resource Use:** Provides the most granular detail available using the Kubernetes `metrics-server`, Prometheus, and CloudWatch metrics combined.

---

### Summary Recommendation
To fulfill the specific cloud project requirement of being **cost-effective** while maintaining **high availability, security, and using AWS tools**, **Option 2 (ECS with EC2 Capacity using Spot Instances)** is strongly recommended. It avoids the $70+ monthly EKS fee while heavily practicing native AWS infrastructure logic in Terraform (IAM, VPCs, ECS, CloudWatch, ALB, ECR). It makes auto-scaling, metrics, and secret encryption relatively seamless compared to a self-managed K3s cluster.

**Important Note on Cost Management:**
Since you must run two PostgreSQL databases and a RabbitMQ queue alongside three apps, you will struggle squeezing all of that into a 1GB `t2.micro` or `t3.micro`. If you get Out-Of-Memory (OOM) errors:
1. Try utilizing EC2 **Spot Instances** (e.g., `t3.small` or `t3.medium`). You can use a `t3.small` spot instance for roughly $5/month. 
2. Remember to destroy your infrastructure with `terraform destroy` when not actively developing.