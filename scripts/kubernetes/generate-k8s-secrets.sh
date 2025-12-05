#!/bin/bash
# generate-k8s-secrets.sh - Generate Kubernetes secrets for MediSecure

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to generate a random password (32 characters)
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# Function to generate JWT secret (64 characters)
generate_jwt_secret() {
    openssl rand -base64 64 | tr -d "=+/" | cut -c1-64
}

echo -e "${GREEN}🔐 Generating Kubernetes secrets for MediSecure...${NC}"
echo ""

# Check if secrets.yaml exists
if [ -f "kubernetes/secrets.yaml" ]; then
    echo -e "${YELLOW}⚠️  Warning: kubernetes/secrets.yaml already exists${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Generate new secrets
POSTGRES_PASSWORD=$(generate_password)
JWT_SECRET=$(generate_jwt_secret) 
PGADMIN_PASSWORD=$(generate_password)

echo -e "${GREEN}📝 Creating kubernetes/secrets.yaml...${NC}"

cat > kubernetes/secrets.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
stringData:
  POSTGRES_DB: "medisecure"
  POSTGRES_USER: "medisecure_user"
  POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
---
apiVersion: v1
kind: Secret
metadata:
  name: backend-secret
type: Opaque
stringData:
  JWT_SECRET_KEY: "${JWT_SECRET}"
  DATABASE_URL: "postgresql://medisecure_user:${POSTGRES_PASSWORD}@db-service:5432/medisecure"
---
apiVersion: v1
kind: Secret
metadata:
  name: pgadmin-secret
type: Opaque
stringData:
  PGADMIN_DEFAULT_EMAIL: "admin@medisecure.com"
  PGADMIN_DEFAULT_PASSWORD: "${PGLADMIN_PASSWORD}"
EOF

echo -e "${GREEN}✅ Kubernetes secrets generated successfully!${NC}"
echo ""
echo -e "${YELLOW}⚠️  Important Security Notes:${NC}"
echo "1. kubernetes/secrets.yaml contains sensitive credentials"
echo "2. Never commit this file to version control"
echo "3. Apply secrets before deploying other resources:"
echo "   ${GREEN}kubectl apply -f kubernetes/secrets.yaml${NC}"
echo ""
echo -e "${GREEN}🚀 Ready to deploy:${NC}"
echo "   kubectl apply -f kubernetes/"
echo ""