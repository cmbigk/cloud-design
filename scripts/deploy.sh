#!/bin/bash
set -e

INSTANCE_ID="i-013ffb92b552e158a"
PUBLIC_IP="51.21.222.216"
REGION="eu-north-1"
AZ="${REGION}a"

echo "Generating temporary SSH key..."
ssh-keygen -t ed25519 -f /tmp/k3s_key -N "" -q || true

echo "Pushing SSH key via EC2 Instance Connect..."
aws ec2-instance-connect send-ssh-public-key \
  --instance-id $INSTANCE_ID \
  --availability-zone $AZ \
  --instance-os-user ubuntu \
  --ssh-public-key file:///tmp/k3s_key.pub

echo "Retrieving kubeconfig..."
ssh -i /tmp/k3s_key -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP "sudo cat /etc/rancher/k3s/k3s.yaml" > ../kubeconfig/k3s.yaml

echo "Updating kubeconfig with public IP..."
sed -i.bak "s/127.0.0.1/$PUBLIC_IP/g" ../kubeconfig/k3s.yaml

export KUBECONFIG=$(pwd)/../kubeconfig/k3s.yaml

echo "Testing kubectl connection..."
kubectl get nodes

echo "Applying Kubernetes manifests..."
kubectl apply -f ../k8s/

echo "Waiting for pods to be ready..."
sleep 15
kubectl get pods

echo "Deployment finished! You can manage it locally using: export KUBECONFIG=$(pwd)/../kubeconfig/k3s.yaml"
