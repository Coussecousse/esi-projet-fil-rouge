# CI/CD Pipeline - Architecture Microservices

## 📋 Vue d'Ensemble

Pipeline automatisé pour build, test et déploiement des 4 microservices vers 3 environnements.

```
┌─────────────┐
│  Git Push   │
└──────┬──────┘
       │
┌──────▼──────────────────────────────────┐
│  BUILD (4 services en parallèle)        │
│  - service-patient                      │
│  - service-rdv                          │
│  - service-documents                    │
│  - service-facturation                  │
└──────┬──────────────────────────────────┘
       │
┌──────▼──────────────────────────────────┐
│  TEST                                   │
│  - Tests unitaires                      │
│  - Tests d'intégration                  │
│  - Health checks                        │
└──────┬──────────────────────────────────┘
       │
       ├──► develop → DEV (auto)
       ├──► main → STAGING (auto)
       └──► manual → PRODUCTION (approval)
```

## 🔧 Configuration Requise

### Secrets GitHub

Configurez dans **Settings → Secrets and variables → Actions** :

**Development:**
```
DEV_HOST=dev.medisecure.local
DEV_USER=deploy
DEV_SSH_KEY=<private-key>
```

**Staging:**
```
STAGING_HOST=staging.medisecure.local
STAGING_USER=deploy
STAGING_SSH_KEY=<private-key>
```

**Production:**
```
PROD_HOST=medisecure.com
PROD_USER=deploy
PROD_SSH_KEY=<private-key>
```

### Environments GitHub

Créez dans **Settings → Environments** :

1. **development** - Protection: aucune
2. **staging** - Protection: aucune
3. **production** - Protection:
   - ✅ Required reviewers (2 minimum)
   - ✅ Wait timer: 5 minutes

## 🚀 Utilisation

### Déploiement Automatique

```bash
# Déployer sur DEV
git push origin develop

# Déployer sur STAGING
git push origin main
```

### Déploiement Production (Manuel)

1. Aller sur **Actions** → **CI/CD Pipeline - Microservices**
2. Cliquer **Run workflow**
3. Sélectionner `production`
4. Attendre approbation des reviewers
5. Déploiement automatique après validation

## 📊 Stages du Pipeline

### 1. Build (Parallèle)
- Build 4 images Docker (Patient, RDV, Documents, Facturation)
- Build Frontend React
- Push vers GitHub Container Registry (ghcr.io)
- Cache Docker layers

### 2. Test
- Tests unitaires par service
- Tests d'intégration avec docker-compose (compose.yml)
- Health checks automatiques (Kong, Keycloak, RabbitMQ, services)
- Configuration Kong API Gateway

### 3. Deploy
- **DEV**: Auto sur branche `develop`
- **STAGING**: Auto sur branche `main`
- **PRODUCTION**: Manuel uniquement, backup automatique avant déploiement

### 4. Security
- Scan Trivy pour vulnérabilités
- Upload résultats vers GitHub Security

## 🧪 Tester Localement

```bash
# Build tous les services
docker-compose -f compose.yml build

# Démarrer l'environnement complet
./start-microservices.sh
# OU manuellement:
docker-compose -f compose.yml up -d
sleep 60
./kong/configure-kong.sh

# Vérifier les services via Kong
curl http://localhost:8000/api/patients
curl http://localhost:8000/api/appointments
curl http://localhost:8000/api/documents
curl http://localhost:8000/api/billing

# Frontend
http://localhost:3000/

# Health check complet
./test-microservices.sh

# Arrêter
docker-compose -f compose.yml down
```

## 📈 Monitoring

### Kong Admin API
- URL: http://localhost:8888/
- API Gateway configuration et monitoring

### Keycloak
- URL: http://localhost:8180/auth/
- OAuth2/SSO authentication management

### RabbitMQ Management
- URL: http://localhost:15672/
- Message queue monitoring

### Logs
```bash
# Logs en temps réel
docker-compose -f compose.yml logs -f

# Logs d'un service spécifique
docker-compose -f compose.yml logs -f service-patient

# Logs Kong
docker-compose -f compose.yml logs -f kong
```

## 🔄 Workflow Complet

### Feature Development
```bash
# 1. Créer branche feature
git checkout -b feature/new-feature

# 2. Développer et commiter
git commit -m "feat: nouvelle fonctionnalité"

# 3. Push et créer PR vers develop
git push origin feature/new-feature

# 4. Merge PR → Auto deploy DEV
```

### Release
```bash
# 1. Merge develop → main
git checkout main
git merge develop

# 2. Push → Auto deploy STAGING
git push origin main

# 3. Tester sur staging
curl https://staging.medisecure.local/health

# 4. Deploy PRODUCTION (manuel via GitHub Actions UI)
```

## 🛡️ Sécurité

- ✅ Images scannées avec Trivy
- ✅ Secrets jamais en clair
- ✅ SSH keys pour déploiements
- ✅ Backup avant déploiement prod
- ✅ Rollback automatique si échec

## 📞 Troubleshooting

### Pipeline échoue au build
```bash
# Tester build localement
cd services/service-patient
docker build -t test-patient .

# OU avec docker-compose
docker-compose -f compose.yml build service-patient
```

### Déploiement échoue
```bash
# SSH sur serveur
ssh deploy@dev.medisecure.local

# Vérifier containers
docker ps

# Voir logs
docker-compose -f compose.yml logs

# Vérifier Kong configuration
curl http://localhost:8888/services
curl http://localhost:8888/routes
```

### Health check échoue
```bash
# Vérifier services individuellement
curl http://localhost:8001/admin/            # Patient
curl http://localhost:8002/health            # RDV
curl http://localhost:8003/health            # Documents
curl http://localhost:8004/health            # Facturation

# Vérifier infrastructure
curl http://localhost:8000/                  # Kong
curl http://localhost:8180/auth/             # Keycloak
curl http://localhost:15672/                 # RabbitMQ

# Tester via Kong
curl http://localhost:8000/api/appointments
```

## 🎯 Prochaines Étapes

1. Configurer les secrets GitHub
2. Créer les 3 environments
3. Tester pipeline sur branche develop
4. Valider déploiement staging
5. Approuver déploiement production
