# 🔒 SÉCURITÉ KUBERNETES - MediSecure

## ✅ Mesures de sécurité implémentées

### 1. Gestion des Secrets

#### ✅ Secrets Kubernetes
- **Fichier**: `00-secrets.yaml.example` (template)
- **Script**: `generate-secrets.sh` (génération automatique)
- **Protection**: Ajouté au `.gitignore`
- **Encodage**: Base64 (standard Kubernetes)

#### ⚠️ IMPORTANT
```bash
# NE JAMAIS commiter :
00-secrets.yaml
*-secrets.yaml

# Toujours commiter :
*-secrets.yaml.example
```

### 2. Pod Security

#### Security Context (tous les pods)
```yaml
securityContext:
  runAsNonRoot: true          # ✅ Pas de root
  runAsUser: 1000             # ✅ User spécifique
  fsGroup: 1000               # ✅ Groupe système
  readOnlyRootFilesystem: true # ✅ Filesystem en lecture seule
  allowPrivilegeEscalation: false # ✅ Pas d'escalade de privilèges
  capabilities:
    drop: [ALL]               # ✅ Suppression de toutes les capabilities
  seccompProfile:
    type: RuntimeDefault      # ✅ Profile seccomp
```

### 3. Network Security

#### NetworkPolicies actives
- ✅ Isolation par défaut (deny all)
- ✅ Règles Ingress strictes (whitelist)
- ✅ Règles Egress contrôlées
- ✅ Communication inter-services limitée

#### Exemple
```yaml
# Service Patient → PostgreSQL uniquement
egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### 4. Secrets Management Production

#### Recommandations
1. **Sealed Secrets** (Bitnami)
   - Chiffrement des secrets dans Git
   - Déchiffrement automatique dans le cluster

2. **External Secrets Operator**
   - Intégration AWS Secrets Manager
   - Intégration Azure Key Vault
   - Intégration GCP Secret Manager
   - Rotation automatique

3. **HashiCorp Vault**
   - Gestion centralisée
   - Rotation automatique
   - Audit trails
   - Dynamic secrets

### 5. TLS/HTTPS

#### Certificats
- ✅ Secret TLS configuré
- ✅ Ingress avec HTTPS
- 🔄 TODO: Intégrer cert-manager (Let's Encrypt)

```bash
# Production: Installer cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### 6. RBAC (Role-Based Access Control)

#### Principes
- Least Privilege (moindre privilège)
- ServiceAccounts dédiés par service
- Roles et ClusterRoles définis
- RoleBindings strictes

### 7. Monitoring & Audit

#### Logs
- ✅ Prometheus configuré
- ✅ Grafana avec dashboards
- 🔄 TODO: ELK Stack ou Loki pour logs centralisés

#### Audit
- Activer Kubernetes Audit Logs
- Monitoring des accès secrets
- Alertes sur comportements anormaux

### 8. Resource Management

#### Protection contre DoS
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

#### High Availability
- ✅ 3 replicas minimum par service
- ✅ PodDisruptionBudget configuré
- ✅ HPA (Horizontal Pod Autoscaler)
- ✅ Pod Anti-Affinity

### 9. Données médicales (RGPD/HDS)

#### Conformité
- ✅ Chiffrement au repos (secrets)
- ✅ Chiffrement en transit (TLS)
- 🔄 TODO: Chiffrement application (AES-256)
- 🔄 TODO: Audit logs RGPD
- 🔄 TODO: Anonymisation données de test

#### Backups
```yaml
# CronJob backup chiffré
- Frequency: Quotidien
- Retention: 30 jours
- Encryption: AES-256
- Location: Offsite sécurisé
```

### 10. Image Security

#### Best Practices
```dockerfile
# ✅ Image minimale (alpine)
FROM python:3.9-alpine

# ✅ Scan de vulnérabilités
RUN apk add --no-cache --security-updates

# ✅ User non-root
USER 1000:1000

# ✅ Read-only
VOLUME ["/tmp"]
```

## 🚀 Déploiement Sécurisé

### 1. Génération des secrets
```bash
cd infrastructure/kubernetes
./generate-secrets.sh
```

### 2. Vérification
```bash
# Vérifier que les secrets ne sont pas dans git
git status | grep secret

# Vérifier le .gitignore
cat .gitignore | grep secret
```

### 3. Application
```bash
# Appliquer les secrets
kubectl apply -f 00-secrets.yaml

# Vérifier
kubectl get secrets -n medisecure
```

### 4. Déploiement
```bash
# Ordre recommandé
kubectl apply -f 00-secrets.yaml
kubectl apply -f *-statefulset.yaml
kubectl apply -f service-*-deployment.yaml
kubectl apply -f networkpolicy.yaml
kubectl apply -f ingress.yaml
```

## 🔍 Audit de Sécurité

### Checklist avant production

- [ ] Secrets générés avec mots de passe forts (32+ chars)
- [ ] Secrets **jamais** committés dans git
- [ ] TLS/HTTPS activé partout
- [ ] NetworkPolicies appliquées
- [ ] RBAC configuré
- [ ] Resource limits définis
- [ ] SecurityContext strict sur tous les pods
- [ ] Images scannées (Trivy, Clair)
- [ ] Backups automatiques configurés
- [ ] Monitoring et alertes actifs
- [ ] Audit logs activés
- [ ] Plan de réponse aux incidents
- [ ] Conformité RGPD/HDS validée

### Outils recommandés
```bash
# Scanner de vulnérabilités
trivy image medisecure/service-patient:latest

# Audit de configuration
kubeaudit all -n medisecure

# Policy enforcement
kube-bench run

# Scan réseau
kube-hunter --remote
```

## 📞 En cas d'incident

### 1. Rotation immédiate des secrets
```bash
./generate-secrets.sh
kubectl delete secret --all -n medisecure
kubectl apply -f 00-secrets.yaml
kubectl rollout restart deployment -n medisecure
```

### 2. Vérification des accès
```bash
kubectl get events -n medisecure
kubectl logs -l tier=microservice -n medisecure --since=1h
```

### 3. Isolation
```bash
# Bloquer tout trafic
kubectl apply -f networkpolicy-deny-all.yaml
```

## 📚 Références

- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [OWASP Kubernetes Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html)
- [RGPD](https://www.cnil.fr/)
- [HDS](https://esante.gouv.fr/labels-certifications/hds)
