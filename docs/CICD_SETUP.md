# CI/CD Setup Guide - MediSecure Microservices

This guide will help you configure the complete CI/CD pipeline for automated deployment.

## 📋 Overview

Your CI/CD pipeline automatically:
- ✅ Builds 4 Docker images when you push code
- ✅ Runs tests (unit + integration)
- ✅ Deploys to DEV on `develop` branch
- ✅ Deploys to STAGING on `main` branch  
- ✅ Deploys to PRODUCTION manually (requires approval)
- ✅ Scans for security vulnerabilities

## 🔧 Step 1: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

### Required Secrets

Click **"New repository secret"** and add each of these:

#### Development Environment
```
Name: DEV_HOST
Value: dev.medisecure.local (or your dev server IP)

Name: DEV_USER
Value: deploy (or your SSH user)

Name: DEV_SSH_KEY
Value: (paste your private SSH key - see below)
```

#### Staging Environment
```
Name: STAGING_HOST
Value: staging.medisecure.local (or your staging server IP)

Name: STAGING_USER
Value: deploy

Name: STAGING_SSH_KEY
Value: (paste your private SSH key)
```

#### Production Environment
```
Name: PROD_HOST
Value: medisecure.com (or your production server)

Name: PROD_USER
Value: deploy

Name: PROD_SSH_KEY
Value: (paste your private SSH key)
```

### How to Generate SSH Keys

```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy

# Copy the PUBLIC key to your servers
ssh-copy-id -i ~/.ssh/github_deploy.pub deploy@dev.medisecure.local
ssh-copy-id -i ~/.ssh/github_deploy.pub deploy@staging.medisecure.local
ssh-copy-id -i ~/.ssh/github_deploy.pub deploy@medisecure.com

# Copy the PRIVATE key content for GitHub Secrets
cat ~/.ssh/github_deploy
# Copy the entire output (including -----BEGIN and -----END lines)
```

## 🌍 Step 2: Configure GitHub Environments

Go to **Settings** → **Environments**

### Create Development Environment

1. Click **"New environment"**
2. Name: `development`
3. **No protection rules** (auto-deploy)
4. Click **"Configure environment"**

### Create Staging Environment

1. Click **"New environment"**
2. Name: `staging`
3. **No protection rules** (auto-deploy)
4. Click **"Configure environment"**

### Create Production Environment

1. Click **"New environment"**
2. Name: `production`
3. **Add protection rules:**
   - ☑️ **Required reviewers**: Add 2 reviewers (team members)
   - ☑️ **Wait timer**: 5 minutes
   - ☑️ **Deployment branches**: Only `main` branch
4. Click **"Save protection rules"**

## 🖥️ Step 3: Prepare Your Servers

### On Each Server (DEV, STAGING, PROD)

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker deploy

# 2. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Create deployment directory
sudo mkdir -p /opt/medisecure
sudo chown deploy:deploy /opt/medisecure
cd /opt/medisecure

# 4. Clone repository
git clone https://github.com/Coussecousse/esi-projet-fil-rouge.git .

# 5. Copy environment files
cp kubernetes/secrets-databases.yaml.example kubernetes/secrets-databases.yaml
cp kubernetes/secrets-infrastructure.yaml.example kubernetes/secrets-infrastructure.yaml

# Edit secrets with production values
nano kubernetes/secrets-databases.yaml
nano kubernetes/secrets-infrastructure.yaml

# 6. Make scripts executable
chmod +x *.sh
chmod +x kong/configure-kong.sh

# 7. Test manual deployment
./start-microservices.sh
```

## 🚀 Step 4: Test Your CI/CD Pipeline

### Test DEV Deployment

```bash
# On your local machine
git checkout develop
git add .
git commit -m "test: trigger DEV deployment"
git push origin develop
```

**What happens:**
1. GitHub Actions builds all services
2. Runs tests
3. Deploys automatically to DEV server
4. Runs health checks

**Monitor:** Go to GitHub → **Actions** tab → Watch the workflow

### Test STAGING Deployment

```bash
# Merge develop to main
git checkout main
git merge develop
git push origin main
```

**What happens:**
1. Builds and tests
2. Deploys automatically to STAGING server
3. Runs smoke tests

### Test PRODUCTION Deployment

1. Go to GitHub → **Actions** tab
2. Click **"CI/CD Pipeline - Microservices"**
3. Click **"Run workflow"**
4. Select `production` environment
5. Click **"Run workflow"**
6. **Wait for reviewer approval** (if configured)
7. Deployment proceeds after approval

## 📊 Step 5: Verify Deployments

### Check Deployment Status

```bash
# SSH to your server
ssh deploy@dev.medisecure.local

# Check running services
cd /opt/medisecure
docker-compose -f compose.yml ps

# View logs
docker-compose -f compose.yml logs -f

# Test health
curl http://localhost:8000/api/appointments
```

### Check URLs

**Development:**
- Frontend: http://dev.medisecure.local:3000/
- API: http://dev.medisecure.local:8000/api/*
- Keycloak: http://dev.medisecure.local:8180/auth/

**Staging:**
- Frontend: http://staging.medisecure.local:3000/
- API: http://staging.medisecure.local:8000/api/*

**Production:**
- Frontend: https://medisecure.com/
- API: https://medisecure.com:8000/api/*

## 🔄 Typical Workflow

### For Feature Development

```bash
# 1. Create feature branch
git checkout develop
git pull
git checkout -b feature/new-feature

# 2. Make changes
# ... edit code ...

# 3. Commit and push
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# 4. Create Pull Request to develop
# - Go to GitHub → Pull Requests → New PR
# - Base: develop, Compare: feature/new-feature

# 5. After PR approval & merge → Auto deploys to DEV
```

### For Release to Production

```bash
# 1. Test on DEV (auto from develop branch)
git checkout develop
git push origin develop
# → Deploys to DEV automatically

# 2. Deploy to STAGING
git checkout main
git merge develop
git push origin main
# → Deploys to STAGING automatically

# 3. Test on STAGING
# - Verify all features work
# - Run manual tests

# 4. Deploy to PRODUCTION (manual)
# - Go to GitHub Actions
# - Run workflow with "production" environment
# - Get approval from reviewers
# - Deployment proceeds
```

## 🛡️ Security Features

Your pipeline includes:

- ✅ **Trivy Security Scan**: Scans for vulnerabilities in dependencies
- ✅ **SARIF Upload**: Results visible in GitHub Security tab
- ✅ **Production Backup**: Database backed up before each prod deployment
- ✅ **Rollback**: Automatic rollback if health checks fail
- ✅ **Secrets Management**: All credentials stored securely in GitHub Secrets

## 📈 Monitoring

### View Pipeline Status

- GitHub Actions tab shows all runs
- Green ✓ = Success
- Red ✗ = Failed
- Yellow ⏸ = Waiting for approval

### Check Logs

```bash
# On server
cd /opt/medisecure
docker-compose -f compose.yml logs -f service-patient
docker-compose -f compose.yml logs -f kong
```

### Health Checks

```bash
# Local test script
./test-microservices.sh

# Or manual
curl http://localhost:8000/api/appointments
curl http://localhost:8000/api/patients
curl http://localhost:8000/api/documents
curl http://localhost:8000/api/billing
```

## 🆘 Troubleshooting

### Pipeline Fails at Build

**Check:** Service Dockerfile syntax
```bash
cd services/service-patient
docker build -t test .
```

### Pipeline Fails at Deploy

**Check:** SSH connection
```bash
ssh deploy@dev.medisecure.local
# If this fails, check:
# - SSH key is correct in GitHub Secrets
# - Server is accessible
# - User has permissions
```

### Health Check Fails

**Check:** Services on server
```bash
ssh deploy@dev.medisecure.local
cd /opt/medisecure
docker-compose -f compose.yml ps
./test-microservices.sh
```

### Kong Configuration Fails

**Check:** Kong is running
```bash
docker ps | grep kong
docker logs kong
curl http://localhost:8888/
```

## 📚 Additional Resources

- **Pipeline File:** `.github/workflows/microservices-cicd.yml`
- **Scripts:** `start-microservices.sh`, `test-microservices.sh`
- **Documentation:** `docs/CICD_MICROSERVICES.md`

## ✅ Checklist

Before going live, verify:

- [ ] All GitHub Secrets configured (DEV, STAGING, PROD)
- [ ] All GitHub Environments created (development, staging, production)
- [ ] Production environment has required reviewers
- [ ] SSH keys generated and deployed to servers
- [ ] Servers have Docker + Docker Compose installed
- [ ] Repository cloned on all servers at `/opt/medisecure`
- [ ] Scripts are executable (`chmod +x *.sh`)
- [ ] Test deployment to DEV works
- [ ] Test deployment to STAGING works
- [ ] Production reviewers configured

## 🎉 You're Ready!

Your CI/CD pipeline is now configured. Every push will automatically build, test, and deploy based on the branch.

**Next steps:**
1. Make a test commit to `develop` branch
2. Watch it deploy to DEV automatically
3. Merge to `main` to deploy to STAGING
4. Use manual workflow for PRODUCTION deployments
