#!/bin/bash
# Deployment script for Civo

set -e

echo "🚀 Starting Axiom API deployment to Civo..."

# Check if required tools are installed
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl is required but not installed. Aborting." >&2; exit 1; }

# Build Docker image
echo "📦 Building Docker image..."
docker build -t axiom-api:latest .

# Check if we're deploying to Kubernetes
if kubectl cluster-info &>/dev/null; then
    echo "✅ Kubernetes cluster detected"
    
    # Create namespace if it doesn't exist
    kubectl create namespace axiom --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply Kubernetes manifests
    echo "📋 Applying Kubernetes manifests..."
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    
    # Wait for deployment
    echo "⏳ Waiting for deployment to be ready..."
    kubectl rollout status deployment/axiom-api -n axiom || kubectl rollout status deployment/axiom-api
    
    echo "✅ Deployment complete!"
    echo ""
    echo "📊 Check status with:"
    echo "   kubectl get pods -l app=axiom-api"
    echo "   kubectl get services axiom-api-service"
    echo ""
    echo "📝 View logs with:"
    echo "   kubectl logs -l app=axiom-api -f"
else
    echo "⚠️  No Kubernetes cluster detected. Image built successfully."
    echo "   To deploy, configure kubectl and run:"
    echo "   kubectl apply -f k8s/"
fi

