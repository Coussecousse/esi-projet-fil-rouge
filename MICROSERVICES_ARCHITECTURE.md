# Architecture Microservices - MediSecure

## Vue d'ensemble

Le projet MediSecure a été divisé en 4 microservices indépendants, chacun utilisant une technologie adaptée à ses besoins spécifiques.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        HAProxy (Port 80)                     │
│                    Load Balancer & Router                    │
└────────┬──────────┬──────────┬──────────┬───────────────────┘
         │          │          │          │
    ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌──▼─────┐
    │Service │ │Service │ │Service │ │Service │
    │  RDV   │ │Patient │ │Docs    │ │Billing │
    │:8001   │ │:8002   │ │:8003   │ │:8004   │
    └────┬───┘ └───┬────┘ └───┬────┘ └──┬─────┘
         │         │          │         │
    ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌──▼─────┐
    │MongoDB │ │Postgres│ │ MinIO  │ │MariaDB │
    │:27017  │ │:5432   │ │:9000   │ │:3306   │
    └────────┘ └────────┘ └────────┘ └────────┘
         │         │          │         │
         └─────────┴──────────┴─────────┘
                   │
         ┌─────────▼─────────┐
         │  Redis + RabbitMQ │
         │  (Cache + Queue)  │
         └───────────────────┘
```

## Microservices

### 1. Service RDV (Rendez-vous)
- **Technologie**: Flask 2.0 + Python 3.9
- **Port**: 8001 (interne: 5000)
- **Base de données**: MongoDB
- **Responsabilités**:
  - Gestion des rendez-vous
  - Disponibilités des médecins
  - Notifications de rappel
- **Endpoints**:
  - `GET /api/appointments` - Liste des rendez-vous
  - `POST /api/appointments` - Créer un rendez-vous
  - `GET /api/appointments/{id}` - Détails d'un rendez-vous
  - `PUT /api/appointments/{id}` - Modifier un rendez-vous
  - `DELETE /api/appointments/{id}` - Annuler un rendez-vous

### 2. Service Patient
- **Technologie**: Django 2.2 + Python 3.7
- **Port**: 8002 (interne: 8000)
- **Base de données**: PostgreSQL
- **Responsabilités**:
  - Gestion des informations patients
  - Dossiers médicaux
  - Historique médical
- **Endpoints**:
  - `GET /api/patients` - Liste des patients
  - `POST /api/patients` - Créer un patient
  - `GET /api/patients/{id}` - Détails d'un patient
  - `PUT /api/patients/{id}` - Modifier un patient
  - `DELETE /api/patients/{id}` - Supprimer un patient

### 3. Service Documents
- **Technologie**: .NET Core 3.1 (C#)
- **Port**: 8003 (interne: 5000)
- **Stockage**: MinIO (S3-compatible)
- **Responsabilités**:
  - Upload de documents médicaux
  - Génération de PDFs
  - Gestion des fichiers
- **Endpoints**:
  - `GET /api/documents` - Liste des documents
  - `POST /api/documents` - Upload un document
  - `GET /api/documents/{id}` - Télécharger un document
  - `DELETE /api/documents/{id}` - Supprimer un document

### 4. Service Facturation
- **Technologie**: FastAPI + Python 3.8
- **Port**: 8004 (interne: 8000)
- **Base de données**: MariaDB
- **Responsabilités**:
  - Gestion des factures
  - Paiements
  - Rapports financiers
- **Endpoints**:
  - `GET /api/invoices` - Liste des factures
  - `POST /api/invoices` - Créer une facture
  - `GET /api/invoices/{id}` - Détails d'une facture
  - `PUT /api/invoices/{id}` - Modifier une facture
  - `POST /api/invoices/{id}/pay` - Payer une facture

## Infrastructure partagée

### Redis
- **Rôle**: Cache distribué
- **Port**: 6379
- **Utilisateurs**: 
  - RDV: Database 0
  - Patient: Database 1
  - Facturation: Database 2

### RabbitMQ
- **Rôle**: Message broker
- **Ports**: 5672 (AMQP), 15672 (Management UI)
- **Utilisateurs**: Tous les services
- **Cas d'usage**:
  - Notifications asynchrones
  - Events entre services
  - Intégration de systèmes externes

### HAProxy
- **Rôle**: Load balancer et API Gateway
- **Port**: 80 (HTTP), 443 (HTTPS), 8404 (Stats)
- **Routing**:
  - `/api/appointments/*` → Service RDV
  - `/api/patients/*` → Service Patient
  - `/api/documents/*` → Service Documents
  - `/api/invoices/*` ou `/api/billing/*` → Service Facturation
  - `/*` → Frontend React

## Bases de données

| Service | Database | Type | Port | Réplication |
|---------|----------|------|------|-------------|
| RDV | MongoDB | NoSQL | 27017 | 3 replicas |
| Patient | PostgreSQL | SQL | 5432 | 1 primary |
| Documents | MinIO | Object Storage | 9000 | 4 nodes |
| Facturation | MariaDB | SQL | 3306 | 3 replicas |

## Communication inter-services

Les services communiquent de deux façons :

1. **Synchrone** (HTTP REST):
   - Via HAProxy pour les appels externes
   - Directement pour les appels internes
   
2. **Asynchrone** (RabbitMQ):
   - Events de création/modification
   - Notifications
   - Tâches en arrière-plan

## Déploiement

### Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# Logs d'un service spécifique
docker-compose logs -f service-rdv

# Arrêter tous les services
docker-compose down
```

### Kubernetes

Chaque service dispose de:
- **Deployment**: 3-10 replicas avec HPA
- **Service**: ClusterIP pour communication interne
- **Ingress**: Routing par HAProxy
- **ConfigMap**: Configuration
- **Secret**: Credentials

```bash
# Déployer tous les services
kubectl apply -f kubernetes/

# Scaler un service
kubectl scale deployment service-rdv --replicas=5

# Voir les pods
kubectl get pods -l app=service-rdv
```

## Monitoring

- **Prometheus**: Métriques de tous les services
- **Grafana**: Dashboards et alertes
- **HAProxy Stats**: Page de stats sur le port 8404

## Avantages de cette architecture

1. **Isolation**: Chaque service peut être développé, testé et déployé indépendamment
2. **Scaling**: Chaque service scale selon ses besoins propres
3. **Technologies adaptées**: Chaque service utilise la meilleure technologie pour son cas d'usage
4. **Résilience**: La panne d'un service n'affecte pas les autres
5. **Équipes autonomes**: Chaque équipe peut travailler sur son service

## Évolutions futures

- [ ] API Gateway avec authentification centralisée
- [ ] Service Mesh (Istio) pour le monitoring avancé
- [ ] Event Sourcing avec Kafka
- [ ] Circuit Breaker pattern
- [ ] Distributed tracing avec Jaeger
