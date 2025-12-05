#!/bin/bash

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════╗
║                                               ║
║          MediSecure Microservices             ║
║          Démarrage Complet                    ║
║                                               ║
╚═══════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker n'est pas installé${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose n'est pas installé${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker est installé${NC}"
echo ""

# Vérifier si des conteneurs existent déjà
existing=$(docker ps -a --filter "name=medisecure-" --format "{{.Names}}" | wc -l)
if [ $existing -gt 0 ]; then
    echo -e "${YELLOW}⚠ Des conteneurs MediSecure existent déjà${NC}"
    read -p "Voulez-vous les arrêter et reconstruire ? (o/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        echo "🗑️  Nettoyage des conteneurs existants..."
        docker-compose -f compose.yml down
    fi
fi

# Build et démarrage
echo ""
echo "🔨 Build des images Docker..."
docker-compose -f compose.yml build

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Erreur lors du build${NC}"
    exit 1
fi

echo ""
echo "🚀 Démarrage des services..."
docker-compose -f compose.yml up -d

# Configure Kong
echo ""
echo "🔧 Configuration de Kong API Gateway..."
sleep 5
./kong/configure-kong.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Erreur lors du démarrage${NC}"
    exit 1
fi

# Attendre que les services soient prêts
echo ""
echo "⏳ Attente du démarrage complet..."
sleep 10

# Initialiser les bases de données
echo ""
echo "💾 Initialisation des bases de données..."
./init-databases.sh

# Tests de santé
echo ""
echo "🏥 Vérification de la santé des services..."
./test-microservices.sh

echo ""
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════╗
║                                               ║
║          ✓ Démarrage terminé !                ║
║                                               ║
╚═══════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${GREEN}🌐 URLs disponibles :${NC}"
echo ""
echo "  🌐 Application :"
echo "     • Frontend:             http://localhost:3000/"
echo "     • Kong API Gateway:     http://localhost:8000/api/*"
echo ""
echo "  📦 Services via Kong :"
echo "     • API Patients:         http://localhost:8000/api/patients"
echo "     • API Appointments:     http://localhost:8000/api/appointments"
echo "     • API Documents:        http://localhost:8000/api/documents"
echo "     • API Billing:          http://localhost:8000/api/billing"
echo ""
echo "  🔐 Admin & Management :"
echo "     • Keycloak (Auth):      http://localhost:8180/auth/"
echo "     • Kong Admin:           http://localhost:8888/"
echo "     • RabbitMQ:             http://localhost:15672/"
echo "     • MinIO Console:        http://localhost:9001/"
echo "     • pgAdmin:              http://localhost:5050/"
echo ""
echo -e "${YELLOW}📝 Commandes utiles :${NC}"
echo "  • Logs:        docker-compose -f compose.yml logs -f"
echo "  • Status:      docker-compose -f compose.yml ps"
echo "  • Arrêt:       docker-compose -f compose.yml down"
echo "  • Redémarrage: docker-compose -f compose.yml restart"
echo ""
