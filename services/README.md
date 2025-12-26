# MediSecure - Services Directory

Ce dossier contient les 4 microservices indépendants de l'application MediSecure.

## Structure

Chaque service est un projet FastAPI autonome avec sa propre base de données :

```
services/
├── service-patient/       # Gestion des patients (PostgreSQL)
├── service-rdv/          # Gestion des rendez-vous (MongoDB)
├── service-documents/    # Gestion des documents (MinIO)
└── service-billing/      # Gestion de la facturation (MariaDB)
```

## Développement

Chaque service peut être développé et testé indépendamment :

```bash
cd services/service-patient
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8001
```

## Communication

Les services communiquent entre eux via :
- **RabbitMQ** : Messages asynchrones
- **Kong API Gateway** : Routage et orchestration
- **Redis** : Cache partagé

## Déploiement

Les services sont déployés via Docker Compose :
```bash
docker-compose up service-patient service-rdv service-documents service-billing
```
