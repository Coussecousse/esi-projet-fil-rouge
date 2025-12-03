#!/bin/bash

echo "==========================================="
echo "Initialisation des Bases de Données"
echo "==========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Attendre que les conteneurs soient prêts
echo "⏳ Attente du démarrage des bases de données..."
sleep 5

# PostgreSQL - Service Patient
echo ""
echo "📊 PostgreSQL (Service Patient)..."
docker exec medisecure-db psql -U medisecure_user -d medisecure_patients << 'EOF'
-- Vérification de la connexion
SELECT 'PostgreSQL est prêt!' as status;
\dt
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PostgreSQL initialisé${NC}"
else
    echo -e "${RED}✗ Erreur PostgreSQL${NC}"
fi

# MongoDB - Service RDV
echo ""
echo "📊 MongoDB (Service RDV)..."
docker exec medisecure-mongodb mongo -u mongo_admin -p mongo_password --authenticationDatabase admin << 'EOF'
use medisecure_appointments
db.appointments.countDocuments()
print("MongoDB est prêt!")
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ MongoDB initialisé${NC}"
else
    echo -e "${RED}✗ Erreur MongoDB${NC}"
fi

# MariaDB - Service Facturation
echo ""
echo "📊 MariaDB (Service Facturation)..."
docker exec medisecure-mariadb mysql -u mariadb_user -pmariadb_password medisecure_billing << 'EOF'
SELECT 'MariaDB est prêt!' as status;
SHOW TABLES;
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ MariaDB initialisé${NC}"
else
    echo -e "${RED}✗ Erreur MariaDB${NC}"
fi

# MinIO - Créer le bucket pour les documents
echo ""
echo "📊 MinIO (Service Documents)..."
docker exec medisecure-minio mc alias set myminio http://localhost:9000 minio_admin minio_password 2>/dev/null
docker exec medisecure-minio mc mb myminio/medical-documents 2>/dev/null || echo "Bucket 'medical-documents' existe déjà"
docker exec medisecure-minio mc anonymous set download myminio/medical-documents 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ MinIO initialisé${NC}"
else
    echo -e "${RED}✗ Erreur MinIO${NC}"
fi

# Redis - Test
echo ""
echo "📊 Redis (Cache)..."
docker exec medisecure-redis redis-cli -a redis_password PING 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Redis initialisé${NC}"
else
    echo -e "${RED}✗ Erreur Redis${NC}"
fi

echo ""
echo "==========================================="
echo -e "${GREEN}✓ Initialisation terminée${NC}"
echo "==========================================="
