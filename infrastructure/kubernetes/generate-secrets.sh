#!/bin/bash

# Script de génération de secrets sécurisés pour Kubernetes
# Usage: ./generate-secrets.sh

set -e

echo "==================================="
echo "Génération des secrets sécurisés"
echo "==================================="
echo ""

# Fonction pour générer un mot de passe aléatoire
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# Fonction pour encoder en base64
encode_base64() {
    echo -n "$1" | base64 | tr -d '\n'
}

# Génération des mots de passe
POSTGRES_PASSWORD=$(generate_password)
MONGO_PASSWORD=$(generate_password)
MARIADB_ROOT_PASSWORD=$(generate_password)
MARIADB_PASSWORD=$(generate_password)
MINIO_PASSWORD=$(generate_password)$(generate_password) # 64 chars for MinIO
REDIS_PASSWORD=$(generate_password)
RABBITMQ_PASSWORD=$(generate_password)
KEYCLOAK_ADMIN_PASSWORD=$(generate_password)
KEYCLOAK_DB_PASSWORD=$(generate_password)
KONG_DB_PASSWORD=$(generate_password)
JWT_SECRET=$(generate_password)$(generate_password) # 64 chars for JWT
ENCRYPTION_KEY=$(generate_password)
API_KEY=$(generate_password)

echo "Génération du fichier 00-secrets.yaml..."

cat > 00-secrets.yaml <<EOF
# ⚠️  GENERATED FILE - DO NOT COMMIT TO GIT!
# Generated on: $(date)
# 
# IMPORTANT: Ajoutez ce fichier à .gitignore
# IMPORTANT: Utilisez un gestionnaire de secrets en production (Vault, Sealed Secrets)

---
apiVersion: v1
kind: Namespace
metadata:
  name: medisecure
  labels:
    name: medisecure
    security: high

---
# PostgreSQL (Service Patient)
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: medisecure
type: Opaque
data:
  POSTGRES_USER: $(encode_base64 "medisecure_user")
  POSTGRES_PASSWORD: $(encode_base64 "$POSTGRES_PASSWORD")
  POSTGRES_DB: $(encode_base64 "medisecure_patients")

---
# MongoDB (Service RDV)
apiVersion: v1
kind: Secret
metadata:
  name: mongodb-secret
  namespace: medisecure
type: Opaque
data:
  MONGO_ROOT_USERNAME: $(encode_base64 "medisecure_admin")
  MONGO_ROOT_PASSWORD: $(encode_base64 "$MONGO_PASSWORD")

---
# MariaDB (Service Billing)
apiVersion: v1
kind: Secret
metadata:
  name: mariadb-secret
  namespace: medisecure
type: Opaque
data:
  MYSQL_ROOT_PASSWORD: $(encode_base64 "$MARIADB_ROOT_PASSWORD")
  MYSQL_USER: $(encode_base64 "medisecure_billing")
  MYSQL_PASSWORD: $(encode_base64 "$MARIADB_PASSWORD")
  MYSQL_DATABASE: $(encode_base64 "medisecure_billing")

---
# MinIO (Service Documents)
apiVersion: v1
kind: Secret
metadata:
  name: minio-secret
  namespace: medisecure
type: Opaque
data:
  MINIO_ROOT_USER: $(encode_base64 "medisecure_admin")
  MINIO_ROOT_PASSWORD: $(encode_base64 "$MINIO_PASSWORD")

---
# Redis (Cache)
apiVersion: v1
kind: Secret
metadata:
  name: redis-secret
  namespace: medisecure
type: Opaque
data:
  REDIS_PASSWORD: $(encode_base64 "$REDIS_PASSWORD")

---
# RabbitMQ (Message Queue)
apiVersion: v1
kind: Secret
metadata:
  name: rabbitmq-secret
  namespace: medisecure
type: Opaque
data:
  RABBITMQ_DEFAULT_USER: $(encode_base64 "medisecure")
  RABBITMQ_DEFAULT_PASS: $(encode_base64 "$RABBITMQ_PASSWORD")

---
# Keycloak (Authentication)
apiVersion: v1
kind: Secret
metadata:
  name: keycloak-secret
  namespace: medisecure
type: Opaque
data:
  KEYCLOAK_ADMIN: $(encode_base64 "admin")
  KEYCLOAK_ADMIN_PASSWORD: $(encode_base64 "$KEYCLOAK_ADMIN_PASSWORD")
  KC_DB_USERNAME: $(encode_base64 "keycloak_user")
  KC_DB_PASSWORD: $(encode_base64 "$KEYCLOAK_DB_PASSWORD")

---
# Kong (API Gateway)
apiVersion: v1
kind: Secret
metadata:
  name: kong-secret
  namespace: medisecure
type: Opaque
data:
  KONG_PG_USER: $(encode_base64 "kong")
  KONG_PG_PASSWORD: $(encode_base64 "$KONG_DB_PASSWORD")

---
# Application Secrets
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: medisecure
type: Opaque
data:
  JWT_SECRET_KEY: $(encode_base64 "$JWT_SECRET")
  ENCRYPTION_KEY: $(encode_base64 "$ENCRYPTION_KEY")
  INTERNAL_API_KEY: $(encode_base64 "$API_KEY")
EOF

echo ""
echo "✅ Fichier 00-secrets.yaml généré avec succès!"
echo ""
echo "📝 Sauvegardez ces informations dans un gestionnaire de mots de passe sécurisé:"
echo ""
echo "PostgreSQL Password:       $POSTGRES_PASSWORD"
echo "MongoDB Password:          $MONGO_PASSWORD"
echo "MariaDB Root Password:     $MARIADB_ROOT_PASSWORD"
echo "MariaDB Password:          $MARIADB_PASSWORD"
echo "MinIO Password:            $MINIO_PASSWORD"
echo "Redis Password:            $REDIS_PASSWORD"
echo "RabbitMQ Password:         $RABBITMQ_PASSWORD"
echo "Keycloak Admin Password:   $KEYCLOAK_ADMIN_PASSWORD"
echo "Keycloak DB Password:      $KEYCLOAK_DB_PASSWORD"
echo "Kong DB Password:          $KONG_DB_PASSWORD"
echo "JWT Secret:                $JWT_SECRET"
echo "Encryption Key:            $ENCRYPTION_KEY"
echo "Internal API Key:          $API_KEY"
echo ""
echo "⚠️  IMPORTANT:"
echo "1. Ajoutez '00-secrets.yaml' au .gitignore"
echo "2. Ne partagez jamais ces secrets via des canaux non sécurisés"
echo "3. En production, utilisez un gestionnaire de secrets (Vault, Sealed Secrets, etc.)"
echo ""
echo "Pour appliquer les secrets:"
echo "  kubectl apply -f 00-secrets.yaml"
echo ""
