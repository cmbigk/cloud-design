#!/bin/bash
set -e

REGION="eu-north-1"
ACCOUNT_ID="361990119373"
ECR_URL="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

echo "Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URL

# Mapping of ECR Repo Name -> Source Directory
SERVICES=(
  "api-gateway:gateway"
  "inventory-app:inventory"
  "billing-app:billing"
  "inventory-db:inventory-db"
  "billing-db:billing-db"
  "rabbit-queue:rabbit-queue"
)

for entry in "${SERVICES[@]}"; do
    REPO_NAME="${entry%:*}"
    DIR_NAME="${entry#*:}"
    
    echo "========================================="
    echo "Building $REPO_NAME from src/$DIR_NAME..."
    echo "========================================="
    # Ensure they are built for AMD64 so they run properly on the t3.small EC2
    docker build --platform linux/amd64 -t $REPO_NAME ../src/$DIR_NAME
    
    echo "Tagging $REPO_NAME..."
    docker tag $REPO_NAME:latest $ECR_URL/$REPO_NAME:latest
    
    echo "Pushing $REPO_NAME to ECR..."
    docker push $ECR_URL/$REPO_NAME:latest
done

echo "All images built and pushed successfully!"
