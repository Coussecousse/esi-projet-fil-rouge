# MediSecure - Déploiement Kubernetes

## Ordre de déploiement

### 1. Créer les Secrets (OBLIGATOIRE EN PREMIER)
```bash
kubectl apply -f secrets.yaml
```

⚠️ **IMPORTANT** : En production, modifiez les valeurs dans `secrets.yaml` avant de déployer !

### 2. Créer les PersistentVolumes et PersistentVolumeClaims
```bash
kubectl apply -f postgres-pv-pvc.yaml
kubectl apply -f pgadmin-pv-pvc.yaml
```

### 3. Créer la ConfigMap pour l'initialisation de la base de données
```bash
kubectl apply -f medisecure-init-sql-configmap.yaml
```

### 4. Déployer la base de données PostgreSQL
```bash
kubectl apply -f db-deployment.yml
kubectl apply -f db-service.yaml
```

### 5. Déployer le backend
```bash
kubectl apply -f backend-deployment.yml
kubectl apply -f backend-service.yaml
```

### 6. Déployer le frontend
```bash
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
```

### 7. (Optionnel) Déployer pgAdmin
```bash
kubectl apply -f pgadmin-deployment.yml
kubectl apply -f pgadmin-service.yaml
```

## Déploiement complet en une commande
```bash
kubectl apply -f secrets.yaml && \
kubectl apply -f postgres-pv-pvc.yaml && \
kubectl apply -f pgadmin-pv-pvc.yaml && \
kubectl apply -f medisecure-init-sql-configmap.yaml && \
kubectl apply -f db-deployment.yml && \
kubectl apply -f db-service.yaml && \
kubectl apply -f backend-deployment.yml && \
kubectl apply -f backend-service.yaml && \
kubectl apply -f frontend-deployment.yaml && \
kubectl apply -f frontend-service.yaml && \
kubectl apply -f pgadmin-deployment.yml && \
kubectl apply -f pgadmin-service.yaml
```

## Vérification du déploiement
```bash
# Vérifier que tous les pods sont en cours d'exécution
kubectl get pods

# Vérifier les services
kubectl get services

# Consulter les logs du backend
kubectl logs -l app=backend --tail=50

# Consulter les logs de la base de données
kubectl logs -l app=medisecure-db --tail=50
```

## Accès aux services

### Avec Minikube
```bash
# Frontend
minikube service frontend-service

# Backend
minikube service backend-service

# pgAdmin
minikube service pgadmin-service
```

## Secrets - Configuration de production

⚠️ **AVANT DE DÉPLOYER EN PRODUCTION** :

1. Générez un nouveau JWT secret :
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. Modifiez `secrets.yaml` avec vos valeurs :
   - `POSTGRES_PASSWORD` : mot de passe PostgreSQL
   - `JWT_SECRET_KEY` : clé secrète JWT générée
   - `PGADMIN_DEFAULT_PASSWORD` : mot de passe pgAdmin

3. Ne commitez JAMAIS `secrets.yaml` avec les vraies valeurs !

## Nettoyage
```bash
# Supprimer tous les déploiements
kubectl delete -f .

# Supprimer uniquement l'application (garder les volumes)
kubectl delete deployment --all
kubectl delete service --all
```

## Resources

- Frontend : 128Mi-256Mi RAM, 100m-200m CPU
- Backend : 256Mi-512Mi RAM, 250m-500m CPU
- Database : 256Mi-512Mi RAM, 250m-500m CPU
- pgAdmin : 128Mi-256Mi RAM, 100m-200m CPU

## Compte admin par défaut
- Email: `admin@medisecure.com`
- Password: `Admin123!`

⚠️ Changez ce mot de passe après la première connexion !
