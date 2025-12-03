#!/bin/bash
# Kong API Gateway Configuration Script
# Configures routes for all microservices

set -e

KONG_ADMIN_URL="http://localhost:8888"

echo "🔧 Configuring Kong API Gateway..."
echo "=================================="

# Wait for Kong to be ready
echo "⏳ Waiting for Kong Admin API..."
until curl -s -o /dev/null -w "%{http_code}" $KONG_ADMIN_URL/status | grep -q "200"; do
    echo "   Kong not ready yet, waiting..."
    sleep 5
done
echo "✅ Kong is ready!"

# Create Services and Routes for each microservice

echo ""
echo "📝 Creating Patient Service..."
curl -i -X POST $KONG_ADMIN_URL/services/ \
  --data "name=patient-service" \
  --data "url=http://service-patient:8001"

curl -i -X POST $KONG_ADMIN_URL/services/patient-service/routes \
  --data "paths[]=/api/patients" \
  --data "strip_path=false"

echo ""
echo "📝 Creating Appointment Service..."
curl -i -X POST $KONG_ADMIN_URL/services/ \
  --data "name=appointment-service" \
  --data "url=http://service-rdv:8002"

curl -i -X POST $KONG_ADMIN_URL/services/appointment-service/routes \
  --data "paths[]=/api/appointments" \
  --data "strip_path=false"

echo ""
echo "📝 Creating Documents Service..."
curl -i -X POST $KONG_ADMIN_URL/services/ \
  --data "name=documents-service" \
  --data "url=http://service-documents:8003"

curl -i -X POST $KONG_ADMIN_URL/services/documents-service/routes \
  --data "paths[]=/api/documents" \
  --data "strip_path=false"

echo ""
echo "📝 Creating Billing Service..."
curl -i -X POST $KONG_ADMIN_URL/services/ \
  --data "name=billing-service" \
  --data "url=http://service-facturation:8004"

curl -i -X POST $KONG_ADMIN_URL/services/billing-service/routes \
  --data "paths[]=/api/billing" \
  --data "strip_path=false"

curl -i -X POST $KONG_ADMIN_URL/services/billing-service/routes \
  --data "paths[]=/api/invoices" \
  --data "strip_path=false"

echo ""
echo "✅ Kong configuration complete!"
echo ""
echo "📊 Configured Services:"
curl -s $KONG_ADMIN_URL/services/ | grep -o '"name":"[^"]*"' || echo "Services configured"

echo ""
echo "🌐 Your API Gateway is ready at:"
echo "   - Kong Proxy: http://localhost:8000"
echo "   - Kong Admin: http://localhost:8888"
echo ""
echo "Example API calls:"
echo "   curl http://localhost:8000/api/appointments"
echo "   curl http://localhost:8000/api/patients"
echo "   curl http://localhost:8000/api/documents"
echo "   curl http://localhost:8000/api/billing"
