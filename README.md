# MediSecure

Plateforme de gestion des dossiers médicaux et des rendez-vous pour établissements de santé.

## Architecture Microservices

- **service-patient**: Gestion des patients et dossiers (PostgreSQL) - Port 8001
- **service-rdv**: Gestion des rendez-vous (MongoDB) - Port 8002
- **service-documents**: Stockage et gestion des documents médicaux (MinIO) - Port 8003
- **service-billing**: Gestion de la facturation (MariaDB) - Port 8004
- **frontend**: Interface utilisateur React/TypeScript - Port 3000

## Infrastructure

- **Kong**: API Gateway
- **Keycloak**: Authentification et autorisation
- **HAProxy**: Load balancer
- **Redis**: Cache distribué
- **RabbitMQ**: Message broker
- **Prometheus + Grafana**: Monitoring

## Démarrage

```bash
# Lancer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down
```

## Accès

- Frontend: http://localhost:80
- API Gateway (Kong): http://localhost:8000
- Keycloak: http://localhost:8080
- RabbitMQ Management: http://localhost:15672
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090
- MinIO Console: http://localhost:9001

## Développement

Voir `.env.example` pour la configuration des variables d'environnement.

```bash
# Backend
cd medisecure-backend
pip install -r requirements.txt
uvicorn api.main:app --reload

# Frontend
cd medisecure-frontend
npm install
npm run dev
```
