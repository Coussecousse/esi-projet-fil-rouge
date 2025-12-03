# MediSecure - Architecture Microservices

Plateforme de gestion médicale basée sur 4 microservices indépendants avec communication asynchrone.

## 🏗️ Architecture

```
                    ┌─────────────────┐
                    │  Kong :8000     │
                    │  API Gateway    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐        ┌────▼─────┐        ┌────▼─────┐        ┌────▼─────┐
   │ Patient  │        │   RDV    │        │Documents │        │ Billing  │
   │  :8001   │        │  :8002   │        │  :8003   │        │  :8004   │
   │  Django  │        │  Flask   │        │ FastAPI  │        │ FastAPI  │
   └────┬─────┘        └────┬─────┘        └────┬─────┘        └────┬─────┘
        │                   │                    │                    │
   ┌────▼─────┐        ┌────▼─────┐        ┌────▼─────┐        ┌────▼─────┐
   │PostgreSQL│        │ MongoDB  │        │  MinIO   │        │ MariaDB  │
   └──────────┘        └──────────┘        └──────────┘        └──────────┘
        
        ┌──────────────────────────────────────────────────────────┐
        │  Keycloak (OAuth/SSO) + RabbitMQ + Redis + Frontend :3000  │
        └──────────────────────────────────────────────────────────┘
```

### 4 Microservices

| Service | Tech | Database | Port | Description |
|---------|------|----------|------|-------------|
| **Patient** | Django | PostgreSQL | 8001 | Gestion patients |
| **RDV** | Flask | MongoDB | 8002 | Gestion rendez-vous |
| **Documents** | FastAPI | MinIO (S3) | 8003 | Stockage documents |
| **Facturation** | FastAPI | MariaDB | 8004 | Facturation & billing |

### Infrastructure Entreprise
- **Kong**: API Gateway avec plugins (rate-limiting, auth, etc.)
- **Keycloak**: OAuth2/SSO pour authentification centralisée
- **RabbitMQ**: Message queue pour communication asynchrone
- **Redis**: Cache distribué entre services
- **Frontend**: React application (port 3000)

## 🚀 Quick Start

### Démarrer l'environnement complet

```bash
# Clone
git clone https://github.com/Coussecousse/esi-projet-fil-rouge.git
cd esi-projet-fil-rouge

# Démarrer tous les microservices
./start-microservices.sh
# OU manuellement:
docker-compose -f compose.yml up -d

# Vérifier
docker-compose -f compose.yml ps
```

### Accès aux services

```bash
# Application Frontend
http://localhost:3000/

# API via Kong (port 8000)
curl http://localhost:8000/api/patients
curl http://localhost:8000/api/appointments
curl http://localhost:8000/api/documents
curl http://localhost:8000/api/billing

# Services individuels (direct)
curl http://localhost:8001/admin/            # Patient service
curl http://localhost:8002/health            # RDV service

# Interfaces de gestion
http://localhost:8180/auth/    # Keycloak (admin/admin)
http://localhost:8888/         # Kong Admin API
http://localhost:15672/        # RabbitMQ Management (rabbitmq_user/rabbitmq_password)
http://localhost:9001/         # MinIO Console (minio_admin/minio_password)
http://localhost:5050/         # pgAdmin (admin@medisecure.com/admin)
```

### Health Checks

```bash
curl http://localhost:8000/api/appointments  # Via Kong
curl http://localhost:8001/admin/            # Patient
curl http://localhost:8002/health            # RDV
curl http://localhost:8003/health            # Documents
curl http://localhost:8004/health            # Facturation
curl http://localhost:8180/auth/             # Keycloak
```

## 🔄 CI/CD Pipeline

Pipeline automatisé avec GitHub Actions pour build, test et déploiement.

```
Git Push → Build (4 services) → Test → Deploy (Dev/Staging/Prod)
```

### Déploiements

- **DEV**: Auto sur branche `develop`
- **STAGING**: Auto sur branche `main`
- **PRODUCTION**: Manuel via GitHub Actions UI (requiert approbation)

### Configuration

```bash
# 1. Configurer secrets GitHub
Settings → Secrets → Actions:
- DEV_HOST, DEV_USER, DEV_SSH_KEY
- STAGING_HOST, STAGING_USER, STAGING_SSH_KEY
- PROD_HOST, PROD_USER, PROD_SSH_KEY

# 2. Créer environments
Settings → Environments:
- development (auto)
- staging (auto)
- production (manual approval, 2 reviewers)

# 3. Push pour déclencher
git push origin develop  # → Deploy DEV
git push origin main     # → Deploy STAGING
```

Voir [docs/CICD_MICROSERVICES.md](docs/CICD_MICROSERVICES.md) pour détails complets.

## 🧪 Tests

```bash
# Tests complets
./start-microservices.sh
sleep 60
./test-microservices.sh

# OU manuellement:
docker-compose -f compose.yml up -d
sleep 60
curl http://localhost:8000/api/appointments
docker-compose -f compose.yml down
```

## 📚 Documentation

- **[CI/CD Pipeline](docs/CICD_MICROSERVICES.md)** - Configuration GitHub Actions
- **[Infrastructure](docs/INFRASTRUCTURE.md)** - Architecture détaillée
- **[Quick Start](docs/QUICK_START.md)** - Guide de démarrage

## 🛠️ Développement

### Ajouter une feature

```bash
# 1. Créer branche
git checkout -b feature/my-feature

# 2. Modifier service
cd services/service-patient
# ... modifications ...

# 3. Tester localement
docker-compose -f compose.yml up -d --build service-patient

# 4. Commit & Push
git commit -m "feat: nouvelle fonctionnalité"
git push origin feature/my-feature

# 5. Créer PR vers develop
# 6. Merge → Auto deploy DEV
```

### Structure des services

```
services/
├── service-patient/         # Django + PostgreSQL
│   ├── config/             # Django settings
│   ├── Dockerfile
│   └── requirements.txt
├── service-rdv/            # Flask + MongoDB
│   ├── app.py              # Flask API
│   ├── Dockerfile
│   └── requirements.txt
├── service-documents/      # FastAPI + MinIO
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
└── service-facturation/    # FastAPI + MariaDB
    ├── app.py
    ├── Dockerfile
    └── requirements.txt
```

## 📊 Monitoring

### Logs

```bash
# Tous les services
docker-compose -f compose.yml logs -f

# Service spécifique
docker-compose -f compose.yml logs -f service-patient

# Dernières 100 lignes
docker-compose -f compose.yml logs --tail=100
```

### Métriques

- **Kong Admin API**: http://localhost:8888/
  - Services configuration
  - Routes & plugins
  - API analytics

- **Keycloak**: http://localhost:8180/auth/
  - Users & authentication
  - OAuth2/SSO config
  - Security realms

- **RabbitMQ Management**: http://localhost:15672/
  - Queues
  - Messages
  - Consumers

## 🔒 Sécurité

- ✅ Services isolés avec bases dédiées
- ✅ Kong API Gateway avec plugins de sécurité
- ✅ Keycloak pour OAuth2/SSO centralisé
- ✅ Events asynchrones via RabbitMQ
- ✅ Cache Redis pour performance
- ✅ Health checks automatiques
- ✅ Scan sécurité Trivy dans CI/CD

## 📞 Troubleshooting

### Service ne démarre pas

```bash
# Voir logs
docker-compose -f compose.yml logs service-patient

# Rebuild
docker-compose -f compose.yml up -d --build service-patient
```

### Communication entre services échoue

```bash
# Vérifier network
docker network ls
docker network inspect kubernetes_medisecure-network

# Tester connectivité
docker exec service-patient curl service-rdv:8002/health

# Vérifier Kong routes
curl http://localhost:8888/services
curl http://localhost:8888/routes
```

### Base de données inaccessible

```bash
# Vérifier containers DB
docker-compose -f compose.yml ps | grep -E "medisecure-db|medisecure-mongodb|medisecure-mariadb"

# Logs DB
docker-compose -f compose.yml logs medisecure-db
docker-compose -f compose.yml logs medisecure-mongodb
docker-compose -f compose.yml logs medisecure-mariadb
```

## 🤝 Contributing

1. Fork le projet
2. Créer branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'feat: Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir Pull Request

## 📄 License

Ce projet est sous licence propriétaire - voir LICENSE pour détails.

---

**MediSecure** - Architecture Microservices Moderne
