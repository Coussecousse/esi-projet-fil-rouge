# MediSecure - Services Directory

Ce dossier contient les 4 microservices de l'application MediSecure.

## Structure

```
services/
├── service-rdv/          # Service Rendez-vous (Flask + MongoDB)
├── service-patient/      # Service Patient (Django + PostgreSQL)
├── service-documents/    # Service Documents (.NET + MinIO)
└── service-facturation/  # Service Facturation (FastAPI + MariaDB)
```

## Services

| Service | Technologie | Port | Database | Description |
|---------|-------------|------|----------|-------------|
| service-rdv | Flask 2.0 + Python 3.9 | 8001 | MongoDB | Gestion des rendez-vous |
| service-patient | Django 2.2 + Python 3.7 | 8002 | PostgreSQL | Gestion des patients |
| service-documents | .NET Core 3.1 | 8003 | MinIO | Gestion des documents |
| service-facturation | FastAPI + Python 3.8 | 8004 | MariaDB | Gestion de la facturation |

## Démarrage rapide

### Docker Compose (recommandé)

```bash
# Depuis la racine du projet
docker-compose up -d

# Vérifier que tous les services sont démarrés
docker-compose ps

# Logs d'un service spécifique
docker-compose logs -f service-rdv
```

### Développement local

Chaque service peut être lancé indépendamment :

```bash
# Service RDV
cd service-rdv && python app.py

# Service Patient
cd service-patient && python manage.py runserver

# Service Documents
cd service-documents && dotnet run

# Service Facturation
cd service-facturation && python app.py
```

## Accès aux services

- **Service RDV**: http://localhost:8001
- **Service Patient**: http://localhost:8002
- **Service Documents**: http://localhost:8003
- **Service Facturation**: http://localhost:8004
- **HAProxy (API Gateway)**: http://localhost
- **HAProxy Stats**: http://localhost:8404/stats

## Documentation

Consultez `MICROSERVICES_ARCHITECTURE.md` pour la documentation complète de l'architecture.
