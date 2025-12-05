#!/bin/bash
# deploy-k8s.sh - Deploy MediSecure to Kubernetes

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying MediSecure to Kubernetes...${NC}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl is not installed or not in PATH${NC}"
    exit 1
fi

# Check if we're connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ Not connected to a Kubernetes cluster${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Connected to Kubernetes cluster${NC}"

# Check if secrets have been generated
if grep -q "CHANGE_ME_IN_PRODUCTION" kubernetes/secrets.yaml; then
    echo -e "${YELLOW}⚠️  Warning: Default secrets detected!${NC}"
    echo "For production, run: ./generate-k8s-secrets.sh"
    read -p "Continue with default secrets? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please run ./generate-k8s-secrets.sh first"
        exit 1
    fi
fi

echo -e "${GREEN}📝 Applying Kubernetes manifests...${NC}"

# Deploy in order
echo "1. Applying secrets..."
kubectl apply -f kubernetes/secrets.yaml

echo "2. Applying storage..."
kubectl apply -f kubernetes/postgres-pv-pvc.yaml
kubectl apply -f kubernetes/pgadmin-pv-pvc.yaml
kubectl apply -f kubernetes/medisecure-init-sql-configmap.yaml

echo "3. Applying database..."
kubectl apply -f kubernetes/db-deployment.yml
kubectl apply -f kubernetes/db-service.yaml

echo "4. Waiting for database to be ready..."
kubectl wait --for=condition=ready pod -l app=medisecure-db --timeout=300s

echo "5. Applying backend..."
kubectl apply -f kubernetes/backend-deployment.yml
kubectl apply -f kubernetes/backend-service.yaml

echo "6. Applying frontend..."
kubectl apply -f kubernetes/frontend-deployment.yaml
kubectl apply -f kubernetes/frontend-service.yaml

echo "7. Applying pgAdmin (optional)..."
kubectl apply -f kubernetes/pgadmin-deployment.yml
kubectl apply -f kubernetes/pgadmin-service.yaml

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "${GREEN}🔍 Checking deployment status:${NC}"
kubectl get pods
echo ""
echo -e "${GREEN}📋 Services:${NC}"
kubectl get services
echo ""
echo -e "${GREEN}🌐 Access your services:${NC}"

# Check if running on minikube
if kubectl config current-context | grep -q minikube; then
    echo "Frontend: minikube service frontend-service"
    echo "Backend: minikube service backend-service"
    echo "pgAdmin: minikube service pgadmin-service"
else
    echo "Frontend: kubectl port-forward svc/frontend-service 3000:80"
    echo "Backend: kubectl port-forward svc/backend-service 8000:8000"
    echo "pgAdmin: kubectl port-forward svc/pgadmin-service 5050:80"
fi

echo ""
echo -e "${YELLOW}📊 Monitor deployment:${NC}"
echo "kubectl get pods -w"
echo "kubectl logs -f deployment/backend-deployment"
echo ""