# 🏥 MediSecure - Healthcare Management Platform

**Version**: 2.0.0  
**Status**: HDS-Compliant Production Ready  
**Architecture**: Microservices  
**License**: Proprietary

Professional healthcare data management platform with microservices architecture, HDS compliance, and advanced security features.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Security & Compliance](#security--compliance)
- [Development](#development)
- [Deployment](#deployment)
- [Support](#support)

---

## 🎯 Overview

MediSecure is a comprehensive healthcare management platform designed for French hospitals and medical centers. The platform handles:

- **Patient Management** - Complete patient records and medical history
- **Appointment Scheduling** - Advanced booking system with conflict resolution
- **Document Management** - Secure storage of medical documents (DICOM, PDF, images)
- **Billing & Invoicing** - Automated billing with CPAM/AMO integration

### Key Features

✅ **HDS Certified** - Hébergement de Données de Santé compliant  
✅ **GDPR/RGPD** - Full compliance with data protection regulations  
✅ **Microservices** - Scalable, independent services  
✅ **High Availability** - Load balancing, auto-scaling, fault tolerance  
✅ **Security First** - OAuth2/OIDC, encryption at rest and in transit  
✅ **API Gateway** - Centralized authentication and rate limiting via Kong  
✅ **Audit Logging** - Complete traceability of all operations  

---

## 🏗️ Architecture

### Microservices Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         Kong API Gateway                      │
│                         (Port 8000)                           │
└──────────┬────────────────┬────────────────┬─────────────┬───┘
           │                │                │             │
    ┌──────▼──────┐  ┌─────▼──────┐  ┌──────▼──────┐  ┌──▼────────┐
    │   Patient   │  │   RDV      │  │  Documents  │  │  Billing  │
    │   Service   │  │  Service   │  │   Service   │  │  Service  │
    │  (Django)   │  │  (Flask)   │  │  (FastAPI)  │  │ (FastAPI) │
    │   :8001     │  │   :8002    │  │    :8003    │  │   :8004   │
    └──────┬──────┘  └─────┬──────┘  └──────┬──────┘  └──┬────────┘
           │               │                │             │
    ┌──────▼──────┐  ┌─────▼──────┐  ┌──────▼──────┐  ┌──▼────────┐
    │ PostgreSQL  │  │  MongoDB   │  │   MinIO     │  │  MariaDB  │
    │     15      │  │     7      │  │  (S3 API)   │  │   10.11   │
    └─────────────┘  └────────────┘  └─────────────┘  └───────────┘
```

### Infrastructure Components

| Component | Purpose | Port | Technology |
|-----------|---------|------|------------|
| **Kong** | API Gateway | 8000, 8001 | Kong 3.x |
| **Keycloak** | IAM/SSO | 8180 | Keycloak 23.x |
| **RabbitMQ** | Message Queue | 5672, 15672 | RabbitMQ 3.12 |
| **Redis** | Shared Cache | 6379 | Redis 7 |
| **HAProxy** | Load Balancer | 80, 443 | HAProxy 2.8 |
| **Prometheus** | Metrics | 9090 | Prometheus |
| **Grafana** | Monitoring | 3000 | Grafana |

---

## 🚀 Quick Start

### Prerequisites

- **Docker** 24.0+ & **Docker Compose** 2.20+
- **Git** 2.40+
- **Python** 3.11+
- **Node.js** 18+ (for frontend)
- **Kubernetes** 1.28+ (for production)
- 8GB RAM minimum, 16GB recommended

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/Coussecousse/esi-projet-fil-rouge.git
cd esi-projet-fil-rouge

# 2. Create environment file
cp .env.example .env
# Edit .env with your configuration

# 3. Start all services
./scripts/local/start.sh

# 4. Initialize databases
./scripts/local/init-databases.sh

# 5. Access the platform
# Frontend: http://localhost:5173
# API Gateway: http://localhost:8000
# Keycloak: http://localhost:8180
```

### Running Tests

```bash
# Run all unit tests
./scripts/local/test.sh

# Run specific service tests
cd services/service-patient && pytest
cd services/service-rdv && pytest
```

---

## 📚 Documentation

### Architecture Documentation

Located in `docs/architecture/`:

- [`architecture_complete.md`](docs/architecture/architecture_complete.md) - Complete system architecture
- [`architecture_backend.md`](docs/architecture/architecture_backend.md) - Backend microservices details
- [`architecture_frontend.md`](docs/architecture/architecture_frontend.md) - Frontend React SPA
- [`MICROSERVICES_ARCHITECTURE.md`](docs/architecture/MICROSERVICES_ARCHITECTURE.md) - Microservices design patterns
- [`structure_projet_medisecure.md`](docs/architecture/structure_projet_medisecure.md) - Project structure

### Deployment Documentation

Located in `docs/deployment/`:

- [`CICD.md`](docs/deployment/CICD.md) - **Complete CI/CD Guide** (Git Flow, GitHub Actions, deployment procedures)
- [`CICD_SETUP.md`](docs/deployment/CICD_SETUP.md) - CI/CD setup instructions
- [`INFRASTRUCTURE_COMPLETE.md`](docs/deployment/INFRASTRUCTURE_COMPLETE.md) - Infrastructure setup

### Guides

Located in `docs/guides/`:

- [`QUICKSTART.md`](docs/guides/QUICKSTART.md) - Quick start guide
- [`README_MICROSERVICES.md`](docs/guides/README_MICROSERVICES.md) - Microservices usage guide

### Scripts Documentation

- [`scripts/backup/README.md`](scripts/backup/README.md) - Backup/restore procedures (HDS compliant)

---

## 📁 Project Structure

```
medisecure/
├── README.md                          # This file
├── compose.yml                        # Docker Compose orchestration
├── package.json                       # Node.js dependencies
│
├── docs/                              # 📖 All documentation
│   ├── architecture/                  # Architecture diagrams & specs
│   ├── deployment/                    # Deployment & CI/CD guides
│   ├── guides/                        # User & developer guides
│   └── presentation_projet.html       # Project presentation
│
├── scripts/                           # 🔧 Operational scripts
│   ├── backup/                        # Backup/restore (HDS compliant)
│   │   ├── backup.sh                  # Database backup
│   │   ├── verify-backup.sh           # Integrity verification
│   │   ├── restore-backup.sh          # Disaster recovery
│   │   └── README.md                  # Backup documentation
│   ├── deployment/                    # Deployment automation
│   │   ├── check-cicd-setup.sh        # CI/CD validation
│   │   ├── check-server-health.sh     # Health checks
│   │   └── generate-secrets.sh        # Secret generation
│   ├── kubernetes/                    # Kubernetes operations
│   │   ├── deploy-k8s.sh              # K8s deployment
│   │   └── generate-k8s-secrets.sh    # K8s secrets
│   └── local/                         # Local development
│       ├── start.sh                   # Start all services
│       ├── test.sh                    # Run tests
│       ├── init-databases.sh          # Database initialization
│       └── setup-monitoring.sh        # Monitoring setup
│
├── infrastructure/                    # 🏗️ Infrastructure configs
│   ├── kong/                          # Kong API Gateway
│   │   ├── configure-kong.sh          # Kong configuration
│   │   └── init-konga-db.sh           # Konga DB setup
│   ├── haproxy/                       # HAProxy load balancer
│   │   ├── haproxy.cfg                # HAProxy config
│   │   └── haproxy-microservices.cfg/ # Microservices routing
│   ├── keycloak/                      # Keycloak IAM
│   │   └── medisecure-realm.json      # Realm configuration
│   └── monitoring/                    # Prometheus & Grafana
│
├── kubernetes/                        # ☸️ Kubernetes manifests
│   ├── *-deployment.yaml              # Service deployments
│   ├── *-service.yaml                 # Service definitions
│   ├── *-statefulset.yaml             # StatefulSets (DBs)
│   ├── hpa-*.yaml                     # Horizontal Pod Autoscalers
│   ├── ingress.yaml                   # Ingress rules
│   ├── networkpolicy.yaml             # Network policies
│   └── secrets-*.yaml.example         # Secret templates
│
├── .github/workflows/                 # 🔄 GitHub Actions CI/CD
│   └── github-cicd.yml                # Main pipeline (7 stages)
│
├── medisecure-backend/                # 🐍 Django monolith (legacy)
├── medisecure-frontend/               # ⚛️ React SPA frontend
│
└── services/                          # 🔬 Microservices
    ├── service-patient/               # Patient management (Django)
    ├── service-rdv/                   # Appointments (Flask)
    ├── service-documents/             # Documents (FastAPI)
    └── service-facturation/           # Billing (FastAPI)
```

---

## 💻 Technology Stack

### Backend Services

| Service | Framework | Database | Language | Features |
|---------|-----------|----------|----------|----------|
| **Patient** | Django 4.2 | PostgreSQL 15 | Python 3.11 | ORM, Admin, REST API |
| **RDV** | Flask 3.0 | MongoDB 7 | Python 3.11 | Lightweight, async |
| **Documents** | FastAPI 0.104 | MinIO (S3) | Python 3.11 | Async, DICOM support |
| **Facturation** | FastAPI 0.104 | MariaDB 10.11 | Python 3.11 | Billing, invoicing |

### Frontend

- **React** 18.2 - Component-based UI
- **TypeScript** 5.0 - Type safety
- **TailwindCSS** 3.3 - Utility-first styling
- **Vite** 4.4 - Fast build tool
- **React Router** 6.15 - Client-side routing

### Infrastructure

- **Docker** 24.0 - Containerization
- **Kubernetes** 1.28 - Orchestration
- **Kong** 3.x - API Gateway
- **Keycloak** 23.x - Identity & Access Management
- **RabbitMQ** 3.12 - Message broker
- **Redis** 7 - In-memory cache
- **HAProxy** 2.8 - Load balancing
- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboards

### CI/CD

- **GitHub Actions** - Automated pipelines
- **Docker Compose** - Local development
- **TruffleHog** - Secret scanning
- **Trivy** - Container vulnerability scanning
- **SonarQube** - Code quality (planned)

---

## 🔒 Security & Compliance

### HDS Compliance (Hébergement de Données de Santé)

✅ **Traceability** - Complete audit logs for all operations  
✅ **Integrity** - SHA256 checksums for all backups  
✅ **Availability** - 99.9% uptime with HA configuration  
✅ **Retention** - 30-day backup retention for production  
✅ **Encryption** - TLS 1.3 in transit, AES-256 at rest  

### Security Measures

- **Authentication**: OAuth2/OIDC via Keycloak
- **Authorization**: RBAC (Role-Based Access Control)
- **Network**: NetworkPolicies, TLS certificates
- **Secrets**: Kubernetes Secrets, encrypted at rest
- **Vulnerability Scanning**: Trivy for container images
- **Secret Scanning**: TruffleHog for code repositories
- **Rate Limiting**: Kong API Gateway
- **DDoS Protection**: HAProxy + Cloudflare

### GDPR/RGPD Compliance

- Right to access (export patient data)
- Right to erasure (anonymization)
- Data minimization
- Consent management
- Breach notification procedures

---

## 👨‍💻 Development

### Git Flow Strategy

```
feature/* ──────────┐
bugfix/*  ────────┐ │
                  ▼ ▼
              develop (DEV auto-deploy)
                  │
                  ▼
                main (STAGING auto-deploy)
                  │
                  ▼
             production (Manual deploy + 2 reviewers)
```

### Branch Naming Convention

- `feature/<ticket>-<description>` - New features
- `bugfix/<ticket>-<description>` - Bug fixes
- `hotfix/<ticket>-<description>` - Critical production fixes
- `release/<version>` - Release preparation

### Commit Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Example**:
```
feat(patient): Add DICOM image upload

- Implement multipart file upload
- Add DICOM validation
- Update API documentation

Closes #123
```

### Development Workflow

1. Create feature branch from `develop`
2. Implement changes with tests
3. Run local tests: `./scripts/local/test.sh`
4. Push and create Pull Request to `develop`
5. Wait for CI checks (tests, security, linting)
6. Get code review approval
7. Merge to `develop` → auto-deploys to DEV
8. When stable, merge `develop` → `main` → auto-deploys to STAGING
9. Manual deployment to PRODUCTION with 2 reviewers

---

## 🚀 Deployment

### Environments

| Environment | Branch | Auto-Deploy | Approvals | URL |
|-------------|--------|-------------|-----------|-----|
| **DEV** | `develop` | ✅ Yes | None | `dev.medisecure.internal` |
| **STAGING** | `main` | ✅ Yes | None | `staging.medisecure.health` |
| **PRODUCTION** | `production` tag | ❌ Manual | 2 reviewers | `medisecure.health` |

### Deployment Process

#### DEV Environment
```bash
# Automatically deployed on push to develop
git push origin develop
```

#### STAGING Environment
```bash
# Merge develop to main
git checkout main
git merge develop
git push origin main
```

#### PRODUCTION Environment
```bash
# 1. Create production tag
git tag -a v2.0.0 -m "Release v2.0.0"
git push origin v2.0.0

# 2. Trigger manual deployment via GitHub Actions
# 3. Wait for 2 reviewer approvals
# 4. Deployment proceeds with pre-backup
```

### Kubernetes Deployment

```bash
# Deploy to Kubernetes cluster
./scripts/kubernetes/deploy-k8s.sh production

# Generate secrets
./scripts/kubernetes/generate-k8s-secrets.sh

# Apply manifests
kubectl apply -k kubernetes/
```

### Rollback Procedure

```bash
# Automatic rollback on deployment failure
# Manual rollback:
./scripts/backup/restore-backup.sh production latest
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```bash
# Application
ENVIRONMENT=development
DEBUG=true

# Databases
POSTGRES_PASSWORD=changeme
MONGO_ROOT_PASSWORD=changeme
MARIADB_ROOT_PASSWORD=changeme
REDIS_PASSWORD=changeme

# Keycloak
KEYCLOAK_ADMIN_PASSWORD=changeme

# Kong
KONG_ADMIN_TOKEN=changeme

# MinIO
MINIO_ROOT_PASSWORD=changeme

# Security
JWT_SECRET_KEY=generate-secure-random-key
```

### Secrets Management

```bash
# Generate secure secrets
./scripts/deployment/generate-secrets.sh

# For Kubernetes
./scripts/kubernetes/generate-k8s-secrets.sh
```

---

## 📊 Monitoring

### Prometheus Metrics

Access: `http://localhost:9090`

- Request rate, latency, errors (RED metrics)
- Resource usage (CPU, memory, disk)
- Database connections, query performance
- Message queue depth

### Grafana Dashboards

Access: `http://localhost:3000`

- System overview
- Service-specific metrics
- Database performance
- Alert management

### Health Checks

```bash
# Check all services
./scripts/deployment/check-server-health.sh

# Individual service health
curl http://localhost:8001/health  # Patient
curl http://localhost:8002/health  # RDV
curl http://localhost:8003/health  # Documents
curl http://localhost:8004/health  # Facturation
```

---

## 🧪 Testing

### Unit Tests

```bash
# All services
./scripts/local/test.sh

# Specific service
cd services/service-patient
pytest tests/ -v --cov=app
```

### Integration Tests

```bash
# Run integration test suite
docker compose -f compose.test.yml up --abort-on-container-exit
```

### Load Testing

```bash
# Using k6 (planned)
k6 run tests/load/scenario.js
```

---

## 🐛 Troubleshooting

### Common Issues

**Services won't start**:
```bash
# Check logs
docker compose logs <service-name>

# Restart specific service
docker compose restart <service-name>
```

**Database connection errors**:
```bash
# Verify databases are running
docker compose ps

# Check database logs
docker compose logs postgres
docker compose logs mongodb
```

**Port conflicts**:
```bash
# Find process using port
sudo lsof -i :8000

# Kill process
kill -9 <PID>
```

### Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f service-patient

# Deployment logs
tail -f /var/log/medisecure/deployments.log
```

---

## 📞 Support

### Team

- **Product Owner**: [Name]
- **Tech Lead**: [Name]
- **DevOps**: [Name]
- **Security Officer**: [Name]

### Resources

- **Repository**: https://github.com/Coussecousse/esi-projet-fil-rouge
- **Wiki**: https://github.com/Coussecousse/esi-projet-fil-rouge/wiki
- **Issues**: https://github.com/Coussecousse/esi-projet-fil-rouge/issues
- **CI/CD**: https://github.com/Coussecousse/esi-projet-fil-rouge/actions

### Communication

- **Slack**: `#medisecure-dev`
- **Email**: dev@medisecure.health
- **On-call**: PagerDuty rotation

---

## 📄 License

**Proprietary** - All rights reserved.  
This software is the property of MediSecure SAS.  
Unauthorized copying, distribution, or modification is strictly prohibited.

---

## 🙏 Acknowledgments

Built with ❤️ by the MediSecure Team

- French healthcare standards (FHIR, DMP compatibility)
- HDS certification consultants
- Open-source community

---

**Last Updated**: December 5, 2025  
**Version**: 2.0.0  
**Status**: Production Ready
