# 🚀 Guide de Démarrage Rapide - Microservices MediSecure

## Architecture

4 microservices indépendants :
- **Service Patient** (Django + PostgreSQL) - Port 8001
- **Service RDV** (Flask + MongoDB) - Port 8002  
- **Service Documents** (FastAPI + MinIO) - Port 8003
- **Service Facturation** (FastAPI + MariaDB) - Port 8004

Infrastructure :
- **Kong** : API Gateway (port 8000, admin 8888)
- **Keycloak** : IAM/SSO (port 8180)
- **RabbitMQ** : Message Queue (port 5672, management 15672)
- **Redis** : Cache partagé (port 6380)
- **MinIO** : Stockage S3 (ports 9000-9001)

## 🏁 Démarrage Local

### 1. Lancer tous les services

```bash
./start-microservices.sh

# Manual :
# Build et démarrage
docker-compose -f compose.yml up -d --build

# Voir les logs
docker-compose -f compose.yml logs -f

# Status
docker-compose -f compose.yml ps
```

### 4. Initialiser les bases de données 
```bash
./init-databases.sh
```

### 3. Tester les services

```bash
./test-microservices.sh
```

### 4. Accéder aux services

**Via API Gateway (Kong)** :
```bash
# Patients
curl http://localhost:8000/api/patients

# Rendez-vous
curl http://localhost:8000/api/appointments

# Documents
curl http://localhost:8000/api/documents

# Facturation
curl http://localhost:8000/api/billing
```

**Application** :
- Frontend: http://localhost:3000/

**Interfaces de gestion** :
- Keycloak (Auth): http://localhost:8180/auth/ (admin/admin)
- Kong Admin: http://localhost:8888/
- RabbitMQ: http://localhost:15672/ (rabbitmq_user/rabbitmq_password)
- MinIO Console: http://localhost:9001/ (minio_admin/minio_password)
- pgAdmin: http://localhost:5050/ (admin@medisecure.com/admin)

## 🔧 Développement

### Build d'un seul service
### Build d'un seul service

```bash
docker-compose -f compose.yml build service-patient
docker-compose -f compose.yml up -d service-patient
```

### Voir les logs d'un service

```bash
docker-compose -f compose.yml logs -f service-patient
```

### Redémarrer un service

```bash
docker-compose -f compose.yml restart service-patient
```
### Shell dans un conteneur

```bash
docker exec -it medisecure-service-patient bash
```

## 🧪 Tests

### Tests locaux

```bash
# Service Patient (Django)
docker exec medisecure-service-patient python manage.py test

# Service RDV (Flask)
docker exec medisecure-service-rdv pytest

# Service Facturation (FastAPI)
docker exec medisecure-service-facturation pytest
```

## 📦 CI/CD GitHub Actions

### Configuration requise

Créer les secrets GitHub :

```bash
# Environnement DEV
DEV_HOST=dev.example.com
DEV_USER=deploy
DEV_SSH_KEY=<private_key>

# Environnement STAGING
STAGING_HOST=staging.example.com
STAGING_USER=deploy
STAGING_SSH_KEY=<private_key>

# Environnement PRODUCTION
PROD_HOST=prod.example.com
PROD_USER=deploy
PROD_SSH_KEY=<private_key>
```

### Déclenchement

Le pipeline s'exécute automatiquement :
- **develop** → build + deploy DEV
- **main** → build + deploy DEV + STAGING
- **production** → déploiement manuel vers PROD (avec validation)

### Étapes du pipeline

1. **Build** : Build des 4 services en parallèle
2. **Test** : Tests unitaires avec bases de données
3. **Deploy DEV** : Déploiement automatique
4. **Deploy STAGING** : Déploiement automatique (branche main)
5. **Deploy PROD** : Déploiement manuel avec validation
6. **Security Scan** : Scan Trivy des vulnérabilités

## 🛑 Arrêt des Services

```bash
# Arrêt propre
docker-compose -f compose.yml down

# Arrêt + suppression des volumes
docker-compose -f compose.yml down -v

# Nettoyage complet
docker-compose -f compose.yml down -v --rmi all
```

## 🐛 Dépannage

### Service ne démarre pas

```bash
# Vérifier les logs
docker-compose -f compose.yml logs service-patient

# Reconstruire
docker-compose -f compose.yml build --no-cache service-patient
docker-compose -f compose.yml up -d service-patient
```

### Base de données non accessible

```bash
# PostgreSQL
docker exec medisecure-db-patient psql -U patient_user -d patients_db

# MongoDB
docker exec medisecure-db-mongodb mongosh -u rdv_user -p rdv_pass

# MariaDB
docker exec medisecure-db-mariadb mysql -u billing_user -pbilling_pass billing_db
```

### Ports déjà utilisés

```bash
# Vérifier les ports
netstat -tulpn | grep -E '8000|8001|8002|8003|8004|8180'

# Modifier les ports dans compose.yml si nécessaire
```

## 📚 Documentation Complète

- [Architecture Microservices](./README_MICROSERVICES.md)
- [CI/CD Pipeline](./docs/CICD_MICROSERVICES.md)
- [Kong Configuration](./kong/configure-kong.sh)

## 🔐 Sécurité Production

**Avant le déploiement en production** :

1. ✅ Changer tous les mots de passe par défaut
2. ✅ Configurer HTTPS avec certificats SSL (Kong + Keycloak)
3. ✅ Configurer Keycloak pour OAuth2/SSO
4. ✅ Activer les plugins Kong (rate-limiting, auth, etc.)
5. ✅ Configurer les CORS correctement
6. ✅ Mettre en place les sauvegardes automatiques
7. ✅ Configurer le monitoring (Prometheus/Grafana)
8. ✅ Limiter les accès réseau avec NetworkPolicy

## 📊 Monitoring

```bash
# Health checks
curl http://localhost:8000/api/appointments  # Via Kong
curl http://localhost:3000/                  # Frontend
curl http://localhost:8180/auth/             # Keycloak

# Kong Admin API
curl http://localhost:8888/services

# Redis
redis-cli -h localhost -p 6380 ping

# RabbitMQ Management
open http://localhost:15672/                 # rabbitmq_user/rabbitmq_password

# MinIO Console
open http://localhost:9001/                  # minio_admin/minio_password
```
