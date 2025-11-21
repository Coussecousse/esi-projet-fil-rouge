#!/bin/bash
# Script d'initialisation de Kong avec les routes vers les microservices

KONG_ADMIN_URL="http://localhost:8888"

echo "🔧 Configuration de Kong API Gateway..."

# Attendre que Kong soit prêt
echo "⏳ Attente de Kong..."
until curl -s ${KONG_ADMIN_URL}/status > /dev/null; do
  echo "Kong n'est pas encore prêt..."
  sleep 2
done
echo "✅ Kong est prêt!"

# 1. Créer le service RDV
echo "📝 Création du service RDV..."
curl -i -X POST ${KONG_ADMIN_URL}/services/ \
  --data "name=service-rdv" \
  --data "url=http://service-rdv:5000"

# Créer les routes pour RDV
curl -i -X POST ${KONG_ADMIN_URL}/services/service-rdv/routes \
  --data "paths[]=/api/appointments" \
  --data "strip_path=false"

curl -i -X POST ${KONG_ADMIN_URL}/services/service-rdv/routes \
  --data "paths[]=/api/auth" \
  --data "strip_path=false"

# 2. Créer le service Patient
echo "📝 Création du service Patient..."
curl -i -X POST ${KONG_ADMIN_URL}/services/ \
  --data "name=service-patient" \
  --data "url=http://service-patient:8000"

curl -i -X POST ${KONG_ADMIN_URL}/services/service-patient/routes \
  --data "paths[]=/api/patients" \
  --data "strip_path=false"

# 3. Créer le service Documents
echo "📝 Création du service Documents..."
curl -i -X POST ${KONG_ADMIN_URL}/services/ \
  --data "name=service-documents" \
  --data "url=http://service-documents:5000"

curl -i -X POST ${KONG_ADMIN_URL}/services/service-documents/routes \
  --data "paths[]=/api/documents" \
  --data "strip_path=false"

# 4. Créer le service Facturation
echo "📝 Création du service Facturation..."
curl -i -X POST ${KONG_ADMIN_URL}/services/ \
  --data "name=service-facturation" \
  --data "url=http://service-facturation:8000"

curl -i -X POST ${KONG_ADMIN_URL}/services/service-facturation/routes \
  --data "paths[]=/api/invoices" \
  --data "strip_path=false"

curl -i -X POST ${KONG_ADMIN_URL}/services/service-facturation/routes \
  --data "paths[]=/api/billing" \
  --data "strip_path=false"

# 5. Activer le plugin OIDC (Keycloak) pour tous les services
echo "🔐 Configuration de l'authentification Keycloak..."

# Plugin OIDC pour service-rdv
curl -i -X POST ${KONG_ADMIN_URL}/services/service-rdv/plugins \
  --data "name=oidc" \
  --data "config.client_id=service-rdv" \
  --data "config.client_secret=CHANGE_ME" \
  --data "config.discovery=http://medisecure-keycloak:8080/auth/realms/medisecure/.well-known/openid-configuration"

# Plugin OIDC pour service-patient
curl -i -X POST ${KONG_ADMIN_URL}/services/service-patient/plugins \
  --data "name=oidc" \
  --data "config.client_id=service-patient" \
  --data "config.client_secret=CHANGE_ME" \
  --data "config.discovery=http://medisecure-keycloak:8080/auth/realms/medisecure/.well-known/openid-configuration"

# Plugin OIDC pour service-documents
curl -i -X POST ${KONG_ADMIN_URL}/services/service-documents/plugins \
  --data "name=oidc" \
  --data "config.client_id=service-documents" \
  --data "config.client_secret=CHANGE_ME" \
  --data "config.discovery=http://medisecure-keycloak:8080/auth/realms/medisecure/.well-known/openid-configuration"

# Plugin OIDC pour service-facturation
curl -i -X POST ${KONG_ADMIN_URL}/services/service-facturation/plugins \
  --data "name=oidc" \
  --data "config.client_id=service-facturation" \
  --data "config.client_secret=CHANGE_ME" \
  --data "config.discovery=http://medisecure-keycloak:8080/auth/realms/medisecure/.well-known/openid-configuration"

# 6. Activer le Rate Limiting
echo "⏱️ Configuration du Rate Limiting..."
for service in service-rdv service-patient service-documents service-facturation; do
  curl -i -X POST ${KONG_ADMIN_URL}/services/${service}/plugins \
    --data "name=rate-limiting" \
    --data "config.minute=100" \
    --data "config.hour=1000"
done

# 7. Activer le CORS
echo "🌐 Configuration du CORS..."
for service in service-rdv service-patient service-documents service-facturation; do
  curl -i -X POST ${KONG_ADMIN_URL}/services/${service}/plugins \
    --data "name=cors" \
    --data "config.origins=*" \
    --data "config.methods=GET,POST,PUT,DELETE,PATCH,OPTIONS" \
    --data "config.headers=Accept,Authorization,Content-Type,X-Requested-With" \
    --data "config.credentials=true" \
    --data "config.max_age=3600"
done

# 8. Activer le Request/Response Logging
echo "📊 Configuration du Logging..."
for service in service-rdv service-patient service-documents service-facturation; do
  curl -i -X POST ${KONG_ADMIN_URL}/services/${service}/plugins \
    --data "name=http-log" \
    --data "config.http_endpoint=http://prometheus:9090/api/v1/write"
done

echo "✅ Configuration de Kong terminée!"
echo ""
echo "📋 Services configurés:"
echo "  - Service RDV: http://localhost:8000/api/appointments"
echo "  - Service Patient: http://localhost:8000/api/patients"
echo "  - Service Documents: http://localhost:8000/api/documents"
echo "  - Service Facturation: http://localhost:8000/api/invoices"
echo ""
echo "🔐 Authentification: Keycloak activé sur tous les services"
echo "⏱️ Rate Limiting: 100/minute, 1000/heure"
echo "🌐 CORS: Activé pour tous les domaines"
echo ""
echo "📚 Kong Admin API: http://localhost:8001"
