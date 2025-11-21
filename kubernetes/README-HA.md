# MediSecure - Déploiement Kubernetes High Availability

## 🎯 Architecture Haute Disponibilité (99.9% uptime)

Cette configuration assure:
- **Zero downtime deployments** avec RollingUpdate
- **Auto-scaling** (HPA) basé sur CPU/Memory  
- **Multiple replicas** pour chaque service
- **StatefulSets** pour les bases de données avec réplication
- **Pod Disruption Budgets** pour maintenir la disponibilité
- **Network Policies** pour la sécurité
- **Monitoring** avec Prometheus + Grafana
- **Backups automatiques** quotidiens

## 📋 Prérequis

### 1. Kubernetes cluster avec au moins 3 worker nodes

### 2. Nginx Ingress Controller
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

### 3. Metrics Server pour HPA
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### 4. Cert-Manager pour TLS (optionnel)
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

## 🚀 Ordre de déploiement COMPLET

### 1. Créer TOUS les Secrets (OBLIGATOIRE EN PREMIER)
```bash
# Copier et modifier les secrets
cp secrets.yaml.example secrets.yaml
cp secrets-databases.yaml.example secrets-databases.yaml

# Générer un JWT secret fort
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Éditer les fichiers secrets avec vos valeurs
nano secrets.yaml
nano secrets-databases.yaml

# Appliquer les secrets
kubectl apply -f secrets.yaml
kubectl apply -f secrets-databases.yaml
```

⚠️ **IMPORTANT** : Ne JAMAIS commiter les fichiers secrets sans .example !

### 2. Créer les PersistentVolumes et ConfigMaps
```bash
kubectl apply -f postgres-pv-pvc.yaml
kubectl apply -f pgadmin-pv-pvc.yaml
kubectl apply -f medisecure-init-sql-configmap.yaml
```

### 3. Déployer PostgreSQL (Service Patient)
```bash
kubectl apply -f db-deployment.yml
kubectl apply -f db-service.yaml
```

### 4. Déployer MongoDB (Service RDV) - StatefulSet
```bash
kubectl apply -f mongodb-statefulset.yaml
kubectl apply -f mongodb-service.yaml
```

### 5. Déployer MinIO (Stockage Documents) - StatefulSet
```bash
kubectl apply -f minio-statefulset.yaml
kubectl apply -f minio-service.yaml
```

### 6. Déployer MariaDB (Service Facturation) - StatefulSet
```bash
kubectl apply -f mariadb-statefulset.yaml
kubectl apply -f mariadb-service.yaml
```

### 7. Déployer le Backend
```bash
kubectl apply -f backend-deployment.yml
kubectl apply -f backend-service.yaml
```

### 8. Déployer le Frontend
```bash
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
```

### 9. Configurer l'Auto-scaling (HPA)
```bash
kubectl apply -f hpa-backend.yaml
kubectl apply -f hpa-frontend.yaml
```

### 10. Configurer les Pod Disruption Budgets
```bash
kubectl apply -f poddisruptionbudget.yaml
```

### 11. Configurer les Network Policies (Sécurité)
```bash
kubectl apply -f networkpolicy.yaml
```

### 12. Configurer l'Ingress
```bash
# Modifier ingress.yaml avec votre nom de domaine
nano ingress.yaml

kubectl apply -f ingress.yaml
```

### 13. Déployer le Monitoring (Optionnel mais recommandé)
```bash
kubectl apply -f monitoring-prometheus.yaml
kubectl apply -f monitoring-grafana.yaml
```

### 14. Configurer les Backups automatiques
```bash
kubectl apply -f backup-cronjob.yaml
```

### 15. (Optionnel) Déployer pgAdmin
```bash
kubectl apply -f pgadmin-deployment.yml
kubectl apply -f pgadmin-service.yaml
```

## 🎬 Déploiement complet en une commande

```bash
kubectl apply -f secrets.yaml && \
kubectl apply -f secrets-databases.yaml && \
kubectl apply -f postgres-pv-pvc.yaml && \
kubectl apply -f pgadmin-pv-pvc.yaml && \
kubectl apply -f medisecure-init-sql-configmap.yaml && \
kubectl apply -f db-deployment.yml && \
kubectl apply -f db-service.yaml && \
kubectl apply -f mongodb-statefulset.yaml && \
kubectl apply -f mongodb-service.yaml && \
kubectl apply -f minio-statefulset.yaml && \
kubectl apply -f minio-service.yaml && \
kubectl apply -f mariadb-statefulset.yaml && \
kubectl apply -f mariadb-service.yaml && \
kubectl apply -f backend-deployment.yml && \
kubectl apply -f backend-service.yaml && \
kubectl apply -f frontend-deployment.yaml && \
kubectl apply -f frontend-service.yaml && \
kubectl apply -f hpa-backend.yaml && \
kubectl apply -f hpa-frontend.yaml && \
kubectl apply -f poddisruptionbudget.yaml && \
kubectl apply -f networkpolicy.yaml && \
kubectl apply -f ingress.yaml && \
kubectl apply -f monitoring-prometheus.yaml && \
kubectl apply -f monitoring-grafana.yaml && \
kubectl apply -f backup-cronjob.yaml
```

## 🔍 Vérification du déploiement

### Vérifier que tous les pods sont en cours d'exécution
```bash
kubectl get pods -o wide
```

Vous devriez voir:
- 3x backend pods (ou plus avec HPA)
- 3x frontend pods (ou plus avec HPA)
- 1x PostgreSQL pod
- 3x MongoDB pods (StatefulSet)
- 4x MinIO pods (StatefulSet)
- 3x MariaDB pods (StatefulSet)

### Vérifier les services
```bash
kubectl get services
```

### Vérifier l'auto-scaling
```bash
kubectl get hpa
```

### Vérifier les Pod Disruption Budgets
```bash
kubectl get pdb
```

### Consulter les logs
```bash
# Backend
kubectl logs -l app=backend --tail=50

# Frontend
kubectl logs -l app=frontend --tail=50

# PostgreSQL
kubectl logs -l app=medisecure-db --tail=50

# MongoDB
kubectl logs -l app=mongodb --tail=50

# MinIO
kubectl logs -l app=minio --tail=50
```

### Surveiller en temps réel
```bash
watch kubectl get pods,hpa,pdb
```

## 🌐 Accès aux services

### Avec Ingress (Production)
- Frontend: https://medisecure.example.com
- Backend API: https://api.medisecure.example.com
- Grafana: https://medisecure.example.com/grafana (configurer dans ingress)
- Prometheus: Port-forward uniquement pour sécurité

### Avec Minikube (Développement)
```bash
# Frontend
minikube service frontend-service

# Backend
minikube service backend-service

# pgAdmin
minikube service pgadmin-service

# Grafana
minikube service grafana-service

# Prometheus
minikube service prometheus-service
```

### Port-forward pour accès direct
```bash
# Backend
kubectl port-forward svc/backend-service 8000:8000

# Frontend
kubectl port-forward svc/frontend-service 3000:80

# Prometheus
kubectl port-forward svc/prometheus-service 9090:9090

# Grafana
kubectl port-forward svc/grafana-service 3001:3000

# MinIO Console
kubectl port-forward svc/minio-loadbalancer 9001:9001
```

## 📊 Monitoring

### Accéder à Prometheus
```bash
kubectl port-forward svc/prometheus-service 9090:9090
# Ouvrir: http://localhost:9090
```

### Accéder à Grafana
```bash
kubectl port-forward svc/grafana-service 3000:3000
# Ouvrir: http://localhost:3000
# Identifiants: admin / (voir secret grafana-secret)
```

### Configurer Grafana
1. Ajouter Prometheus comme Data Source: http://prometheus-service:9090
2. Importer des dashboards:
   - **315**: Kubernetes cluster monitoring
   - **6417**: Kubernetes pod metrics
   - **1860**: Node Exporter

## 💾 Backups

### Backups automatiques
Les CronJobs effectuent automatiquement:
- **PostgreSQL**: Tous les jours à 2h00
- **MongoDB**: Tous les jours à 3h00
- Rétention: 7 jours

### Backup manuel PostgreSQL
```bash
kubectl exec -it db-deployment-xxx -- pg_dump -U medisecure_user medisecure_patients > backup.sql
```

### Restaurer PostgreSQL
```bash
kubectl exec -i db-deployment-xxx -- psql -U medisecure_user medisecure_patients < backup.sql
```

### Backup manuel MongoDB
```bash
kubectl exec -it mongodb-0 -- mongodump --username=mongo_admin --password=PASSWORD --authenticationDatabase=admin --out=/tmp/backup
```

### Vérifier les backups
```bash
kubectl get cronjobs
kubectl get jobs
```

## 🔐 Sécurité

### Secrets - Configuration de production

⚠️ **AVANT DE DÉPLOYER EN PRODUCTION** :

1. Générez de nouveaux secrets forts:
```bash
# JWT Secret
python -c "import secrets; print(secrets.token_urlsafe(64))"

# PostgreSQL Password
python -c "import secrets; print(secrets.token_urlsafe(32))"

# MongoDB Password
python -c "import secrets; print(secrets.token_urlsafe(32))"

# MinIO Passwords
python -c "import secrets; print(secrets.token_urlsafe(32))"

# MariaDB Password
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. Modifiez tous les fichiers secrets avec vos valeurs
3. Ne commitez JAMAIS les fichiers secrets réels sur Git
4. Utilisez un gestionnaire de secrets (Vault, AWS Secrets Manager, etc.) en production

### Network Policies actives
- Backend peut communiquer avec toutes les DB
- Frontend peut communiquer uniquement avec Backend
- Les DB sont isolées et accessibles uniquement par Backend
- Tout le trafic DNS est autorisé

## 🧹 Nettoyage

### Supprimer tout le déploiement
```bash
kubectl delete -f .
```

### Supprimer uniquement l'application (garder les volumes)
```bash
kubectl delete deployment,statefulset,service,hpa,pdb,ingress,cronjob --all
```

### Supprimer les volumes (⚠️ Perte de données)
```bash
kubectl delete pvc --all
kubectl delete pv --all
```

## 📈 Scalabilité

### Scaling manuel
```bash
# Backend
kubectl scale deployment backend-deployment --replicas=5

# Frontend
kubectl scale deployment frontend-deployment --replicas=5

# MongoDB
kubectl scale statefulset mongodb --replicas=5

# MinIO
kubectl scale statefulset minio --replicas=6  # Doit être pair pour MinIO
```

### Auto-scaling (déjà configuré)
- **Backend**: 3-10 pods (70% CPU, 80% Memory)
- **Frontend**: 3-10 pods (70% CPU, 80% Memory)

## 🎯 Tests de haute disponibilité

### Test 1: Simuler la panne d'un pod
```bash
# Supprimer un pod backend
kubectl delete pod -l app=backend --force --grace-period=0

# Observer la récréation automatique
watch kubectl get pods
```

### Test 2: Test de charge
```bash
# Installer hey (load testing tool)
# https://github.com/rakyll/hey

hey -z 60s -c 50 https://api.medisecure.example.com/health
```

### Test 3: Drain d'un node
```bash
# Drain un worker node
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Observer la redistribution des pods
watch kubectl get pods -o wide

# Reactivate le node
kubectl uncordon <node-name>
```

## 🏥 Health Checks

### Endpoints de santé
- Backend: `GET /health`
- Frontend: `GET /`

### Vérifier la santé
```bash
# Via kubectl
kubectl get pods | grep -v Running

# Via curl (si exposé)
curl https://api.medisecure.example.com/health
```

## 📋 Ressources par service

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit | Replicas |
|---------|-------------|-----------|----------------|--------------|----------|
| Frontend | 100m | 200m | 128Mi | 256Mi | 3-10 (HPA) |
| Backend | 250m | 500m | 256Mi | 512Mi | 3-10 (HPA) |
| PostgreSQL | 250m | 500m | 256Mi | 512Mi | 1 |
| MongoDB | 500m | 1000m | 512Mi | 1Gi | 3 |
| MinIO | 500m | 1000m | 512Mi | 2Gi | 4 |
| MariaDB | 500m | 1000m | 512Mi | 1Gi | 3 |
| Prometheus | 500m | 1000m | 512Mi | 1Gi | 1 |
| Grafana | 250m | 500m | 256Mi | 512Mi | 1 |

**Total minimum requis**: ~6 CPU cores, ~12Gi RAM

## 🔄 Mises à jour Rolling

### Mettre à jour le backend
```bash
# Build et push nouvelle image
docker build -t coussecousse/medisecure-backend:v2.0 .
docker push coussecousse/medisecure-backend:v2.0

# Mettre à jour le deployment
kubectl set image deployment/backend-deployment medisecure-backend=coussecousse/medisecure-backend:v2.0

# Observer le rolling update
kubectl rollout status deployment/backend-deployment
```

### Rollback en cas de problème
```bash
kubectl rollout undo deployment/backend-deployment
```

## 📞 Support & Dépannage

### Problèmes communs

**Pods en CrashLoopBackOff**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name> --previous
```

**HPA ne scale pas**
```bash
# Vérifier metrics-server
kubectl get apiservice v1beta1.metrics.k8s.io

# Vérifier les métriques
kubectl top nodes
kubectl top pods
```

**Ingress ne fonctionne pas**
```bash
# Vérifier ingress-controller
kubectl get pods -n ingress-nginx

# Vérifier ingress
kubectl describe ingress medisecure-ingress
```

## 🎓 Compte admin par défaut
- Email: `admin@medisecure.com`
- Password: `Admin123!`

⚠️ **Changez ce mot de passe après la première connexion !**

## 📚 Documentation supplémentaire
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Prometheus Monitoring](https://prometheus.io/docs/introduction/overview/)
- [MinIO Distributed Mode](https://min.io/docs/minio/kubernetes/upstream/)
- [MongoDB on Kubernetes](https://www.mongodb.com/docs/kubernetes-operator/)

---

**Version**: 2.0 (High Availability)  
**Date**: 2025-11-21  
**SLA cible**: 99.9% uptime
