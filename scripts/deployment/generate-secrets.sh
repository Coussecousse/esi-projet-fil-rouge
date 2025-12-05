#!/bin/bash
# generate-secrets.sh - Generate all secrets for MediSecure platform

SECRETS_DIR="./secrets"
mkdir -p $SECRETS_DIR

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to generate a random password (32 characters)
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# Function to generate encryption key (64 hex characters for AES-256)
generate_encryption_key() {
    openssl rand -hex 32
}

echo "🔐 Generating secrets for MediSecure platform..."
echo ""

# Database passwords
echo "📊 Database passwords..."
echo $(generate_password) > $SECRETS_DIR/postgres_patients_password.txt
echo $(generate_password) > $SECRETS_DIR/mongo_appointments_password.txt
echo $(generate_password) > $SECRETS_DIR/mariadb_root_password.txt
echo $(generate_password) > $SECRETS_DIR/mariadb_billing_password.txt
echo $(generate_password) > $SECRETS_DIR/minio_root_password.txt
echo $(generate_password) > $SECRETS_DIR/keycloak_db_password.txt
echo $(generate_password) > $SECRETS_DIR/kong_db_password.txt

# Keycloak
echo "🔑 Keycloak secrets..."
echo $(generate_password) > $SECRETS_DIR/keycloak_admin_password.txt
echo $(generate_password) > $SECRETS_DIR/keycloak_patient_secret.txt
echo $(generate_password) > $SECRETS_DIR/keycloak_appointments_secret.txt
echo $(generate_password) > $SECRETS_DIR/keycloak_documents_secret.txt
echo $(generate_password) > $SECRETS_DIR/keycloak_billing_secret.txt

# Application secrets
echo "🔧 Application secrets..."
echo $(generate_password) > $SECRETS_DIR/django_secret_key.txt
echo $(generate_password) > $SECRETS_DIR/flask_secret_key.txt
echo $(generate_password) > $SECRETS_DIR/fastapi_secret_key.txt

# Infrastructure
echo "🏗️  Infrastructure secrets..."
echo $(generate_password) > $SECRETS_DIR/rabbitmq_password.txt
echo $(generate_password) > $SECRETS_DIR/grafana_admin_password.txt

# Encryption (HDS)
echo "🔒 Encryption keys (HDS compliance)..."
echo $(generate_encryption_key) > $SECRETS_DIR/encryption_master_key.txt

# Secure file permissions
chmod 600 $SECRETS_DIR/*.txt

echo ""
echo -e "${GREEN}✅ All secrets generated successfully!${NC}"
echo ""
echo -e "${YELLOW}⚠️  Important Security Notes:${NC}"
echo "1. These files contain sensitive credentials"
echo "2. Never commit secrets/* to version control"
echo "3. Store backup in secure encrypted vault"
echo "4. Rotate keys every 90 days for HDS compliance"
echo "5. Use proper secrets manager in production (Vault, AWS Secrets Manager)"
echo ""
echo "📋 Generated secret files:"
ls -lh $SECRETS_DIR/*.txt
