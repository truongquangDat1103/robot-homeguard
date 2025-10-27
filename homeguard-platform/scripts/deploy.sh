#!/bin/bash

set -e

echo "🚀 Starting HomeGuard Platform Deployment..."

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | xargs)
fi

# Check required variables
if [ -z "$DOCKER_USERNAME" ]; then
    echo "❌ Error: DOCKER_USERNAME not set"
    exit 1
fi

# Build and push Docker images
echo "📦 Building Docker images..."
docker compose -f docker-compose.prod.yml build

echo "⬆️  Pushing images to Docker Hub..."
docker push $DOCKER_USERNAME/homeguard-api:latest
docker push $DOCKER_USERNAME/homeguard-web:latest

# Deploy to Kubernetes
echo "☸️  Deploying to Kubernetes..."

# Apply secrets and config
kubectl apply -f infrastructure/kubernetes/secrets.yaml
kubectl apply -f infrastructure/kubernetes/configmap.yaml

# Deploy services
kubectl apply -f infrastructure/kubernetes/api-deployment.yaml
kubectl apply -f infrastructure/kubernetes/web-deployment.yaml
kubectl apply -f infrastructure/kubernetes/ingress.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl rollout status deployment/homeguard-api
kubectl rollout status deployment/homeguard-web

# Check status
echo "✅ Deployment complete!"
echo ""
echo "📊 Deployment status:"
kubectl get pods -l app=homeguard-api
kubectl get pods -l app=homeguard-web
kubectl get svc
kubectl get ingress

echo ""
echo "🎉 HomeGuard Platform deployed successfully!"