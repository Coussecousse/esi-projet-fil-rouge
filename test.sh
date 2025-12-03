#!/bin/bash

echo "==========================================="
echo "Test des Microservices MediSecure"
echo "==========================================="
echo ""

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de test d'un service
test_service() {
    local service_name=$1
    local url=$2
    local port=$3
    
    echo -n "Test $service_name (port $port)... "
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        return 1
    fi
}

echo "1. Vérification des conteneurs Docker..."
echo "----------------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep medisecure

echo ""
echo "2. Test des services via ports directs..."
echo "----------------------------------------"
test_service "Service Patient (Django)" "http://localhost:8001/admin/" 8001
test_service "Service RDV (Flask)" "http://localhost:8002/health" 8002
test_service "Service Documents (FastAPI)" "http://localhost:8003/docs" 8003
test_service "Service Facturation (FastAPI)" "http://localhost:8004/health" 8004

echo ""
echo "3. Test des bases de données..."
echo "----------------------------------------"
echo -n "PostgreSQL (Patient)... "
if docker exec medisecure-db pg_isready -U medisecure_user > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi

echo -n "MongoDB (RDV)... "
if docker exec medisecure-mongodb mongo --eval "db.adminCommand('ping')" --quiet > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    # Try alternative for MongoDB 4.4
    if docker exec medisecure-mongodb mongo --eval "print('pong')" --quiet > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ FAIL${NC}"
    fi
fi

echo -n "MariaDB (Facturation)... "
if docker exec medisecure-mariadb mysqladmin ping -h localhost -u root -pmariadb_root_password > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi

echo ""
echo "4. Test de l'infrastructure..."
echo "----------------------------------------"
echo -n "Redis (port 6380)... "
if redis-cli -h localhost -p 6380 ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAIL${NC} (utiliser: redis-cli -h localhost -p 6380 ping)"
fi
test_service "MinIO" "http://localhost:9000/minio/health/live" 9000
test_service "Keycloak" "http://localhost:8180/auth/" 8180
test_service "RabbitMQ Management" "http://localhost:15672/" 15672

echo ""
echo "5. Test de l'API Gateway (Kong)..."
echo "----------------------------------------"
echo -n "Kong Gateway (8000)... "
STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/appointments)
if [ "$STATUS" = "404" ] || [ "$STATUS" = "302" ] || [ "$STATUS" = "200" ]; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAIL (status: $STATUS)${NC}"
fi
echo -n "Route /api/appointments... "
STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/appointments)
if [ "$STATUS" = "404" ] || [ "$STATUS" = "302" ] || [ "$STATUS" = "200" ]; then
    echo -e "${GREEN}✓ OK (status: $STATUS)${NC}"
else
    echo -e "${YELLOW}⚠ Service non prêt (status: $STATUS)${NC}"
fi

echo ""
echo "==========================================="
echo "Résumé des URLs importantes:"
echo "==========================================="
echo "Application:"
echo "  - Frontend:      http://localhost:3000/"
echo ""
echo "Via API Gateway (Kong):"
echo "  - Patients:      http://localhost:8000/api/patients"
echo "  - Appointments:  http://localhost:8000/api/appointments"
echo "  - Documents:     http://localhost:8000/api/documents"
echo "  - Billing:       http://localhost:8000/api/billing"
echo ""
echo "Admin & Management:"
echo "  - Keycloak:      http://localhost:8180/auth/ (admin/admin)"
echo "  - Kong Admin:    http://localhost:8888/"
echo "  - RabbitMQ:      http://localhost:15672/ (rabbitmq_user/rabbitmq_password)"
echo "  - MinIO Console: http://localhost:9001/ (minio_admin/minio_password)"
echo "  - pgAdmin:       http://localhost:5050/ (admin@medisecure.com/admin)"
echo ""
