# Kubernetes - MediSecure Microservices

Configuration Kubernetes sécurisée pour le déploiement de MediSecure.

## 🔒 Sécurité

### Génération des secrets

**NE JAMAIS commiter des secrets en clair !**

```bash
# Générer des secrets sécurisés
cd infrastructure/kubernetes
./generate-secrets.sh

# Appliquer les secrets
kubectl apply -f 00-secrets.yaml
```

### Bonnes pratiques implémentées

✅ **Secrets Management**
- Utilisation de Kubernetes Secrets
- Encodage base64
- Script de génération automatique
- `.gitignore` configuré

✅ **Pod Security**
- `runAsNonRoot: true`
- `readOnlyRootFilesystem: true`
- Capabilities drop ALL
- SecurityContext stricte
- Seccomp profile

✅ **Network Security**
- NetworkPolicies configurées
- Ingress/Egress rules strictes
- Isolation des microservices

✅ **Resource Management**
- Requests et Limits définis
- HPA (Horizontal Pod Autoscaler)
- PodDisruptionBudget

✅ **High Availability**
- 3 replicas par service
- Pod Anti-Affinity
- Health checks (liveness/readiness)

## 📦 Services déployés

- `service-patient` (Port 8000) - PostgreSQL
- `service-rdv` (Port 8000) - MongoDB
- `service-documents` (Port 8000) - MinIO
- `service-billing` (Port 8000) - MariaDB

## 🚀 Déploiement

```bash
# 1. Créer le namespace
kubectl apply -f 00-secrets.yaml  # Contient aussi le namespace

# 2. Déployer les bases de données
kubectl apply -f postgres-pv-pvc.yaml
kubectl apply -f mongodb-statefulset.yaml
kubectl apply -f mariadb-statefulset.yaml
kubectl apply -f minio-statefulset.yaml

# 3. Déployer l'infrastructure
kubectl apply -f redis-statefulset.yaml
kubectl apply -f rabbitmq-statefulset.yaml
kubectl apply -f keycloak-deployment.yaml
kubectl apply -f kong-deployment.yaml

# 4. Déployer les microservices
kubectl apply -f service-patient-deployment.yaml
kubectl apply -f service-rdv-deployment.yaml
kubectl apply -f service-documents-deployment.yaml
kubectl apply -f service-billing-deployment.yaml

# 5. Déployer le frontend
kubectl apply -f frontend-deployment.yaml

# 6. Configurer l'ingress
kubectl apply -f ingress.yaml

# 7. Activer le monitoring
kubectl apply -f monitoring-prometheus.yaml
kubectl apply -f monitoring-grafana.yaml

# 8. Configurer l'autoscaling
kubectl apply -f hpa-*.yaml

# 9. Appliquer les NetworkPolicies
kubectl apply -f networkpolicy.yaml
```

## 🔍 Vérification

```bash
# Vérifier les pods
kubectl get pods -n medisecure

# Vérifier les secrets
kubectl get secrets -n medisecure

# Vérifier les services
kubectl get svc -n medisecure

# Logs d'un service
kubectl logs -f deployment/service-patient -n medisecure

# Port-forward pour tests
kubectl port-forward svc/service-patient 8001:8000 -n medisecure
```

## 🔐 Production

### Gestionnaires de secrets recommandés

1. **Sealed Secrets** (Bitnami)
   ```bash
   kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/controller.yaml
   ```

2. **External Secrets Operator**
   - Intégration avec AWS Secrets Manager, Azure Key Vault, GCP Secret Manager

3. **HashiCorp Vault**
   - Gestion centralisée des secrets
   - Rotation automatique

### Certificats TLS

```bash
# Générer un certificat auto-signé (dev)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=medisecure.local"

# Créer le secret TLS
kubectl create secret tls tls-cert \
  --cert=tls.crt \
  --key=tls.key \
  -n medisecure
```

Pour production, utilisez Let's Encrypt avec cert-manager:
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

## 📊 Monitoring

- **Prometheus**: http://prometheus.medisecure.local
- **Grafana**: http://grafana.medisecure.local
- **Dashboards**: Préconfigurésen production avec métriques de santé

## ⚠️ Important

- **Jamais de secrets en clair** dans les fichiers versionnés
- **Rotation régulière** des secrets (90 jours max)
- **Audits de sécurité** réguliers
- **Backups chiffrés** des secrets
- **RBAC** activé et configuré
- **Conformité RGPD/HDS** pour données médicales
