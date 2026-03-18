## Deploying the Solution on AWS

Based on the project requirements in [task/project.md](cci:7://file:///Users/markus.amberla/Documents/cloud-devops/cloud-design/task/project.md:0:0-0:0) and the evaluation criteria in [task/audit.md](cci:7://file:///Users/markus.amberla/Documents/cloud-devops/cloud-design/task/audit.md:0:0-0:0), you need to set up an architecture that is scalable, secure, and uses Terraform for Infrastructure as Code, while remaining **as cheap as possible**. 

The project mentions 6 main services: `api-gateway`, `inventory-app`, `billing-app`, `inventory-db` (Postgres), `billing-db` (Postgres), and `rabbit-queue` (RabbitMQ).

Here are the primary approaches on AWS compared by cost and ease of setup:

### 1. The "True" Free Tier Route: Single EC2 Instance with K3s
Since you've already built this with K3s (local master/worker), the easiest and lowest-cost migration is to simply run your K3s cluster on a single AWS EC2 instance. 
- **How it works:** You use Terraform to provision a single `t2.micro` or `t3.micro` EC2 instance (which gives you 750 free hours/month in the Free Tier), install K3s on it via a startup script (user data), and deploy your existing Kubernetes manifests directly on the instance.
- **Cost:** **~$0/month** initially. If 1GB of RAM on a `-micro` instance isn't enough to run 6 containers (2x Postgres and RabbitMQ can be memory-heavy), you might need to upgrade to a `t3.small` (2GB RAM) which would cost about ~$15/month or ~$5/month if configured as an EC2 Spot Instance.
- **Ease of Setup:** **Easiest**. You can re-use 99% of your existing Kubernetes manifests. The only AWS piece is the Terraform code for the EC2 node, VPC, Security Groups, and maybe an API gateway / ALB for traffic entry.

### 2. The Native AWS Managed Route: ECS with EC2 Capacity (Recommended for Learning)
The documentation explicitly mentions using "AWS ECS or EKS" as an orchestration tool. If you want to use native AWS services without a massive bill, ECS backed by EC2 is the way to go. 
- **How it works:** Instead of deploying Kubernetes, you package your apps into Docker images, push them to AWS ECR, and create **ECS Task Definitions** for each service. Then, you tell ECS to deploy those tasks on a Free Tier EC2 instance.
- **Cost:** **~$0/month**. You only pay for the underlying EC2 instance, not for the ECS control plane. Like option 1, if you run out of memory with a `t2.micro`, upgrading to a `t3.small` Spot Instance will cost around $5/month. You may also fall into the free tier for the Application Load Balancer (ALB).
- **Ease of Setup:** **Medium**. You have a lot of new Terraform to write: ECS Clusters, Task Definitions, ECS Services, IAM execution roles, Target Groups, pushing to ECR (Elastic Container Registry), and ALB listeners. However, this is significantly more "AWS-native" and a great learning point for an AWS DevOps portfolio.

### 3. The Serverless Route: ECS with Fargate
Fargate is similar to ECS but removes the need to manage EC2 instances altogether. You just say "run this container with 0.25 vCPU and 0.5 GB RAM" and AWS finds a place for it.
- **Cost:** **Expensive ($20-$40/month)**. There is NO Free Tier for Fargate. You pay per second for every vCPU and GB allocated. 6 tiny containers running 24/7 will rack up a bill relatively fast.
- **Ease of Setup:** **Medium/Hard**. Same Terraform requirements as ECS with EC2, but you don't need to configure EC2 Auto Scaling groups or capacity providers.

### 4. The Managed Kubernetes Route: AWS EKS
EKS is AWS’s fully managed Kubernetes control plane. It's essentially the enterprise version of K3s.
- **Cost:** **Very Expensive ($75+/month)**. AWS charges **$0.10 per hour** just to keep the Kubernetes control plane running, which equals about `$73/month`. This is before you even provision the EC2 nodes to run the containers themselves. This approach completely defeats the goal of being cost-effective for a personal project.
- **Ease of Setup:** **Hard**. EKS has a steeper learning curve, especially with the IAM integration and the heavy Terraform modules required to glue the VPC, Control Plane, and Node Groups together.

### Summary Recommendation
I recommend **Option 2: ECS with EC2 Spot Instances** if you want to heavily focus on the "AWS Native" aspect, or **Option 1: Single EC2 with K3s** if you want to reuse your current Kubernetes experience and finish quickly while staying as cheap as possible.

**Important Note on Cost Management:**
Since you must run two PostgreSQL databases and a RabbitMQ queue alongside three apps, you are likely going to struggle squeezing all of that into a 1GB `t2.micro` or `t3.micro`. If you get Out-Of-Memory (OOM) errors where your containers keep dying:
1. Try utilizing EC2 **Spot Instances** (e.g., `t3.small` or `t3.medium`). You can use a `t3.small` spot instance for roughly $5/month. This ensures you satisfy the project requirement of remaining within a "reasonable cost range".
2. Remember to destroy your infrastructure with `terraform destroy` when you aren't actively developing or presenting the solution to stop costs entirely!