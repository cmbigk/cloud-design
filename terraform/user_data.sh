#!/bin/bash
# Log execution to /var/log/user-data.log
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "Starting K3s Installation"

# Ensure system is updated
apt-get update -y

# Download and install K3s
# We use the public IP for tls-san so we can retrieve kubeconfig and connect remotely
export PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
curl -sfL https://get.k3s.io | sh -s - server \
  --write-kubeconfig-mode 644 \
  --tls-san $PUBLIC_IP

# Wait for K3s to be ready
sleep 15
kubectl get nodes

echo "K3s installation complete. You can retrieve the kubeconfig from /etc/rancher/k3s/k3s.yaml"
