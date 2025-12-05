# Architecture Complète MediSecure

## 📊 Vue d'ensemble de l'infrastructure

```
                                    Internet
                                       |
                                    HAProxy (Load Balancer)
                               Port 80/443/8404 (stats)
                                       |
                    +------------------+------------------+
                    |                                     |
                Frontend                              Backend API
              (React/Vite)                           (FastAPI)
             3 replicas (HPA)                      3 replicas (HPA)
                    |                                     |
                    |          +--------------------------|---------------------------+
                    |          |          |               |              |            |
                    |     PostgreSQL  MongoDB        MinIO         MariaDB      RabbitMQ    Redis
                    |     (Patients)    (RDV)     (Documents)  (Facturation)   (Queue)   (Cache)
                    |     1 replica   3 replicas   4 replicas    3 replicas   3 replicas 3 replicas
                    |          |          |               |              |            |
                    +----------+----------+---------------+--------------+------------+
                                                  |
                                        Monitoring & Observability
                                    Prometheus + Grafana + Exporters
```

## 🗄️ Base de données (4 systèmes)

### 1. PostgreSQL 13
- **Utilisation**: Base de données du service Patient
- **Réplication**: 1 instance (possibilité de scaling)
- **Stockage**: PersistentVolume
- **Port**: 5432
- **Tables principales**: 
  - `patients` (données personnelles, dossiers médicaux)
  - `users` (médecins, administrateurs, personnel)
  - `medical_records` (métadonnées des documents)

### 2. MongoDB 4.4
- **Utilisation**: Base de données du service RDV (Rendez-vous)
- **Réplication**: StatefulSet 3 replicas (Replica Set)
- **Stockage**: 10Gi par replica
- **Port**: 27017
- **Collections principales**:
  - `appointments` (rendez-vous)
  - `calendars` (disponibilités médecins)
  - `appointment_history` (historique)

### 3. MinIO (Object Storage)
- **Utilisation**: Stockage d'objets volumineux (documents médicaux, imagerie)
- **Réplication**: StatefulSet 4 nodes (mode distribué)
- **Stockage**: 20Gi par node (80Gi total)
- **Ports**: 9000 (API), 9001 (Console)
- **Buckets**:
  - `medisecure-documents` (documents patients)
  - `medisecure-images` (imagerie médicale)

### 4. MariaDB 10.5
- **Utilisation**: Base de données pour le service Facturation
- **Réplication**: StatefulSet 3 replicas
- **Stockage**: 10Gi par replica
- **Port**: 3306
- **Tables principales**:
  - `invoices` (factures)
  - `payments` (paiements)
  - `billing_items` (lignes de facturation)

## 🚀 Infrastructure & Réseau (3 systèmes)

### 1. RabbitMQ 3.8
- **Utilisation**: Gestion des files d'attente (messagerie asynchrone)
- **Réplication**: StatefulSet 3 nodes (cluster)
- **Stockage**: 5Gi par node
- **Ports**: 5672 (AMQP), 15672 (Management UI)
- **Use cases**:
  - Envoi d'emails asynchrones (confirmation RDV, rappels)
  - Notifications push
  - Génération de rapports en background
  - Traitement de documents volumineux
  - Export de données

### 2. Redis 6.0
- **Utilisation**: Cache et stockage de données en mémoire rapide
- **Réplication**: StatefulSet 3 replicas (Redis Sentinel)
- **Stockage**: 2Gi par replica
- **Port**: 6379
- **Use cases**:
  - Cache de sessions utilisateur
  - Cache de requêtes fréquentes (liste patients, statistiques)
  - Rate limiting (limitation du nombre de requêtes)
  - Token blacklist (révocation de tokens JWT)
  - Cache de résultats de recherche
  - Stockage temporaire de données

### 3. HAProxy 2.4
- **Utilisation**: Répartition de la charge et gestion du trafic réseau
- **Réplication**: Deployment 2 replicas
- **Ports**: 80 (HTTP), 443 (HTTPS), 8404 (Stats)
- **Fonctionnalités**:
  - Load balancing Round Robin
  - Health checks sur backend/frontend
  - Routing intelligent (/api → backend, / → frontend)
  - SSL/TLS termination
  - Rate limiting
  - Compression
  - Stats en temps réel

## 📊 Monitoring & Observabilité

### Prometheus
- **Utilisation**: Collecte de métriques temps réel
- **Scraping**: Toutes les applications et bases de données
- **Rétention**: Configurable (défaut 15 jours)
- **Port**: 9090
- **Métriques collectées**:
  - CPU, Memory, Disk I/O
  - Latence des requêtes HTTP
  - Taux d'erreurs
  - Nombre de connexions actives
  - Queue depth (RabbitMQ)
  - Cache hit rate (Redis)

### Grafana
- **Utilisation**: Visualisation des métriques et dashboards
- **Port**: 3000
- **Dashboards recommandés**:
  - Kubernetes cluster monitoring (ID: 315)
  - Pod metrics (ID: 6417)
  - Node exporter (ID: 1860)
  - Redis dashboard (ID: 11835)
  - RabbitMQ dashboard (ID: 10991)
  - HAProxy dashboard (ID: 2428)

### Exporters
- **Redis Exporter**: Métriques Redis pour Prometheus
- **RabbitMQ Prometheus Plugin**: Métriques RabbitMQ intégrées
- **HAProxy Stats**: Métriques HAProxy natives

## 🔐 Sécurité & Réseau

### Network Policies
- **Isolation réseau** entre services
- **Principe du moindre privilège**: Chaque service ne peut communiquer qu'avec ce dont il a besoin
- **Policies configurées**:
  - Frontend → Backend uniquement
  - Backend → Toutes les bases de données
  - Bases de données → Isolées, accessibles uniquement par Backend
  - HAProxy → Backend et Frontend
  - RabbitMQ → Clustering interne + Backend

### Secrets Management
- **Kubernetes Secrets** pour toutes les credentials
- **3 fichiers de secrets**:
  - `secrets.yaml`: PostgreSQL, JWT
  - `secrets-databases.yaml`: MongoDB, MinIO, MariaDB
  - `secrets-infrastructure.yaml`: RabbitMQ, Redis
- **⚠️ Jamais commités sur Git** (fichiers .example fournis)

### TLS/SSL
- **Ingress** avec support TLS (Let's Encrypt)
- **HAProxy** pour SSL termination
- **Cert-Manager** pour renouvellement automatique

## 🔄 Haute Disponibilité & Résilience

### Stratégies de déploiement
- **RollingUpdate** avec `maxUnavailable: 0` (zero downtime)
- **Pod Anti-Affinity**: Distribution des pods sur différents nodes
- **Health Checks**: Liveness, Readiness, Startup probes sur tous les services

### Auto-Scaling
- **HPA** configuré pour Backend et Frontend
  - Min: 3 replicas
  - Max: 10 replicas
  - Triggers: 70% CPU, 80% Memory
  - Scale up rapide, scale down progressif

### Pod Disruption Budgets
- **Backend**: Minimum 2 pods disponibles
- **Frontend**: Minimum 2 pods disponibles
- **MongoDB**: Minimum 2 instances
- **MinIO**: Minimum 3 nodes
- **MariaDB**: Minimum 2 instances
- **RabbitMQ**: Minimum 2 nodes
- **Redis**: Minimum 2 instances
- **HAProxy**: Minimum 1 instance

### Backups
- **CronJobs automatiques**:
  - PostgreSQL: Tous les jours à 2h00
  - MongoDB: Tous les jours à 3h00
  - Rétention: 7 jours
- **PVC dédié** de 50Gi pour les backups

## 📈 Ressources & Capacité

### Ressources totales minimales requises

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit | Replicas | Total CPU | Total Memory |
|---------|-------------|-----------|----------------|--------------|----------|-----------|--------------|
| Frontend | 100m | 200m | 128Mi | 256Mi | 3 | 300m | 384Mi |
| Backend | 250m | 500m | 256Mi | 512Mi | 3 | 750m | 768Mi |
| HAProxy | 100m | 500m | 128Mi | 256Mi | 2 | 200m | 256Mi |
| PostgreSQL | 250m | 500m | 256Mi | 512Mi | 1 | 250m | 256Mi |
| MongoDB | 500m | 1000m | 512Mi | 1Gi | 3 | 1500m | 1536Mi |
| MinIO | 500m | 1000m | 512Mi | 2Gi | 4 | 2000m | 2048Mi |
| MariaDB | 500m | 1000m | 512Mi | 1Gi | 3 | 1500m | 1536Mi |
| RabbitMQ | 500m | 1000m | 512Mi | 1Gi | 3 | 1500m | 1536Mi |
| Redis | 250m | 500m | 256Mi | 1Gi | 3 | 750m | 768Mi |
| Prometheus | 500m | 1000m | 512Mi | 1Gi | 1 | 500m | 512Mi |
| Grafana | 250m | 500m | 256Mi | 512Mi | 1 | 250m | 256Mi |
| **TOTAL** | | | | | **27** | **~9.5 CPU** | **~10Gi RAM** |

### Stockage total requis
- **Bases de données**: 80Gi (10Gi PostgreSQL + 30Gi MongoDB + 80Gi MinIO + 30Gi MariaDB)
- **Message Queue**: 15Gi (RabbitMQ)
- **Cache**: 6Gi (Redis)
- **Backups**: 50Gi
- **Logs & Monitoring**: 10Gi
- **Total estimé**: ~250Gi

## 🎯 SLA & Performance

### Objectifs de disponibilité
- **SLA cible**: 99.9% (8h43min downtime/an maximum)
- **RPO** (Recovery Point Objective): 24h (backups quotidiens)
- **RTO** (Recovery Time Objective): < 1h

### Performances attendues
- **Latence API**: < 200ms (p95)
- **Throughput**: 1000+ req/s
- **Cache hit rate**: > 80% (Redis)
- **Message processing**: 100+ msg/s (RabbitMQ)

## 📝 Use Cases Asynchrones (RabbitMQ)

### 1. Envoi d'emails
```
Patient crée RDV → Event dans RabbitMQ → Worker envoie email confirmation
```

### 2. Notifications
```
Nouveau document → Event dans RabbitMQ → Worker envoie notification push
```

### 3. Génération de rapports
```
Admin demande rapport → Event dans RabbitMQ → Worker génère PDF → Stockage MinIO
```

### 4. Traitement d'images médicales
```
Upload IRM → Event dans RabbitMQ → Worker compresse/optimise → Stockage MinIO
```

## 🔄 Flux de données typique

### Création d'un rendez-vous
1. **Frontend** → HAProxy → **Backend** (POST /api/appointments)
2. **Backend** vérifie dans **Redis** si patient en cache
3. Si non en cache, **Backend** → **PostgreSQL** (données patient)
4. **Backend** stocke résultat dans **Redis** (cache)
5. **Backend** → **MongoDB** (création du RDV)
6. **Backend** → **RabbitMQ** (event "RDV créé")
7. **Worker RabbitMQ** → Envoi email confirmation
8. **Backend** → **Frontend** (réponse HTTP)

### Consultation d'un dossier médical
1. **Frontend** → HAProxy → **Backend** (GET /api/patients/{id}/medical-record)
2. **Backend** vérifie **Redis** (cache)
3. Si non en cache:
   - **Backend** → **PostgreSQL** (métadonnées documents)
   - **Backend** → **MinIO** (URLs signées pour téléchargement)
4. **Backend** stocke dans **Redis** (TTL 5 minutes)
5. **Backend** → **Frontend** (réponse avec URLs)

## 🚀 Déploiement

### Docker Compose (Développement local)
```bash
docker-compose up -d
```
**Services accessibles**:
- Frontend: http://localhost:3001
- Backend: http://localhost:8000
- HAProxy: http://localhost:80 (et stats sur :8404/stats)
- RabbitMQ Management: http://localhost:15672
- Redis: localhost:6379

### Kubernetes (Production)
```bash
# Ordre complet dans README-HA.md
kubectl apply -f secrets*.yaml
kubectl apply -f *-pv-pvc.yaml
kubectl apply -f *-statefulset.yaml
kubectl apply -f *-service.yaml
kubectl apply -f *-deployment.yaml
kubectl apply -f hpa-*.yaml
kubectl apply -f poddisruptionbudget.yaml
kubectl apply -f networkpolicy.yaml
kubectl apply -f ingress.yaml
```

## 📚 Documentation
- **README-HA.md**: Documentation complète Kubernetes HA
- **TODO.md**: Liste des tâches restantes
- **haproxy/haproxy.cfg**: Configuration HAProxy
- **kubernetes/**: Tous les manifests K8s

---

**Architecture mise à jour**: 2025-11-21  
**Version**: 2.0 - Full Stack avec Infrastructure Complète  
**Conformité**: 99.9% SLA avec 4 DB + RabbitMQ + Redis + HAProxy + Monitoring
