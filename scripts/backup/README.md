# MediSecure Backup Scripts - HDS Compliant

Scripts de backup, vérification et restauration conformes aux exigences HDS pour la protection des données de santé.

## 📁 Scripts disponibles

### 1. `backup.sh` - Sauvegarde automatique

Crée une sauvegarde complète de toutes les bases de données et volumes.

**Usage:**
```bash
./scripts/backup.sh <environment>
```

**Environnements supportés:**
- `dev` - Développement (retention: 7 jours)
- `staging` - Pré-production (retention: 7 jours)
- `production` - Production (retention: 30 jours)

**Ce qui est sauvegardé:**
- ✅ PostgreSQL (dump complet)
- ✅ MongoDB (dump avec mongodump)
- ✅ MariaDB (dump complet si présent)
- ✅ Redis (snapshot RDB)
- ✅ MinIO (volumes de données)
- ✅ Métadonnées (git commit, timestamp, etc.)

**Exemples:**
```bash
# Backup dev
./scripts/backup.sh dev

# Backup production
./scripts/backup.sh production
```

**Sortie:**
- Archive: `/var/backups/medisecure/medisecure_<env>_<timestamp>.tar.gz`
- Checksum: `/var/backups/medisecure/medisecure_<env>_<timestamp>.tar.gz.sha256`
- Log: `/var/log/medisecure/deployments.log`

---

### 2. `verify-backup.sh` - Vérification d'intégrité

Vérifie l'intégrité d'une sauvegarde (checksum, archive, dumps).

**Usage:**
```bash
# Vérifier le backup le plus récent
./scripts/verify-backup.sh

# Vérifier un backup spécifique
./scripts/verify-backup.sh /var/backups/medisecure/medisecure_production_20251205_103045.tar.gz
```

**Vérifications effectuées:**
- ✅ Checksum SHA256
- ✅ Intégrité de l'archive tar.gz
- ✅ Présence des dumps de bases de données
- ✅ Intégrité des dumps compressés
- ✅ Métadonnées du backup
- ✅ Âge du backup

**Code retour:**
- `0` - Backup valide
- `1` - Backup corrompu ou invalide

---

### 3. `restore-backup.sh` - Restauration

Restaure une sauvegarde complète (⚠️ **DANGEREUX** - écrase les données actuelles).

**Usage:**
```bash
# Restaurer le backup le plus récent
./scripts/restore-backup.sh <environment>

# Restaurer un backup spécifique
./scripts/restore-backup.sh <environment> /path/to/backup.tar.gz

# Restaurer le dernier backup (alias)
./scripts/restore-backup.sh production latest
```

**Exemples:**
```bash
# Restaurer dev avec le backup le plus récent
./scripts/restore-backup.sh dev

# Restaurer production avec backup spécifique
./scripts/restore-backup.sh production /var/backups/medisecure/medisecure_production_20251205_103045.tar.gz
```

**⚠️ Sécurité:**
- **Dev/Staging**: Délai de 5 secondes avant exécution
- **Production**: Requiert confirmation manuelle `RESTORE PRODUCTION`
- Vérification automatique du backup avant restauration
- Option d'arrêt des services (recommandé)

**Processus:**
1. Vérification de l'intégrité du backup
2. Extraction de l'archive
3. Arrêt optionnel des services
4. Restauration PostgreSQL
5. Restauration MongoDB
6. Restauration MariaDB
7. Restauration Redis
8. Redémarrage des services
9. Vérification de santé

---

## 🔧 Configuration requise

### Prérequis système

```bash
# Créer les répertoires nécessaires
sudo mkdir -p /var/backups/medisecure
sudo mkdir -p /var/log/medisecure
sudo chown -R medisecure-deploy:medisecure-deploy /var/backups/medisecure
sudo chown -R medisecure-deploy:medisecure-deploy /var/log/medisecure
```

### Permissions

Les scripts doivent être exécutables:
```bash
chmod +x scripts/backup.sh
chmod +x scripts/verify-backup.sh
chmod +x scripts/restore-backup.sh
```

### Dépendances

- Docker & Docker Compose
- `tar`, `gzip`, `sha256sum`
- `python3` (pour formattage JSON)
- Accès au répertoire `/var/backups/medisecure`

---

## 📋 Utilisation dans le CI/CD

### GitHub Actions Integration

Les scripts sont appelés automatiquement par le pipeline CI/CD:

**Staging (deploy-staging):**
```yaml
- name: Pre-deployment backup
  run: |
    cd /opt/medisecure
    ./scripts/backup.sh staging
```

**Production (deploy-production):**
```yaml
- name: Backup databases (CRITICAL)
  run: |
    ./scripts/backup.sh production
    ./scripts/verify-backup.sh || exit 1
```

**Rollback automatique:**
```yaml
- name: Rollback on failure
  if: failure()
  run: |
    ./scripts/restore-backup.sh production latest
```

---

## 🧪 Tests recommandés

### Test 1: Backup dev complet
```bash
# 1. Créer backup
./scripts/backup.sh dev

# 2. Vérifier
./scripts/verify-backup.sh

# 3. Lister les backups
ls -lh /var/backups/medisecure/
```

### Test 2: Cycle backup-restore
```bash
# 1. Backup initial
./scripts/backup.sh dev

# 2. Modifier des données de test
docker compose exec -T postgres psql -U medisecure -c "INSERT INTO test_table VALUES (999);"

# 3. Restaurer
./scripts/restore-backup.sh dev

# 4. Vérifier que les données sont revenues
```

### Test 3: Vérification intégrité
```bash
# Vérifier tous les backups récents
for backup in /var/backups/medisecure/medisecure_dev_*.tar.gz; do
    echo "Checking: $backup"
    ./scripts/verify-backup.sh "$backup"
done
```

---

## 🛡️ Conformité HDS

Ces scripts respectent les exigences HDS:

### Traçabilité
- ✅ Logs d'audit horodatés (UTC)
- ✅ Métadonnées de backup (git commit, hostname, etc.)
- ✅ Historique dans `/var/log/medisecure/deployments.log`

### Intégrité
- ✅ Checksum SHA256 pour chaque backup
- ✅ Vérification automatique avant restauration
- ✅ Test d'intégrité des archives

### Disponibilité
- ✅ Restauration rapide (<5 minutes)
- ✅ Rollback automatique en cas d'échec
- ✅ Backup avant chaque déploiement critique

### Retention
- ✅ Dev/Staging: 7 jours
- ✅ Production: 30 jours
- ✅ Nettoyage automatique des backups obsolètes

---

## 📊 Structure des backups

```
medisecure_production_20251205_103045.tar.gz
└── medisecure_production_20251205_103045/
    ├── metadata.json              # Métadonnées (env, git, timestamp)
    ├── postgres_full.sql.gz       # Dump PostgreSQL complet
    ├── mariadb_full.sql.gz        # Dump MariaDB complet
    ├── redis_dump.rdb             # Snapshot Redis
    ├── mongodb/
    │   └── dump.archive.gz        # Archive MongoDB
    └── minio/
        └── data.tar.gz            # Données MinIO (documents)
```

---

## ⚠️ Avertissements

### ❌ À NE PAS FAIRE

- ❌ Restaurer en production sans confirmation
- ❌ Supprimer manuellement des backups
- ❌ Modifier les permissions de `/var/backups/medisecure`
- ❌ Interrompre une restauration en cours

### ✅ Bonnes pratiques

- ✅ Tester régulièrement les restaurations en dev
- ✅ Vérifier l'intégrité après chaque backup
- ✅ Surveiller l'espace disque de `/var/backups`
- ✅ Conserver au moins 3 backups de production
- ✅ Documenter les restaurations dans les logs

---

## 🚨 Procédure d'urgence

### Restauration d'urgence production

```bash
# 1. SSH sur le serveur production
ssh medisecure-deploy@medisecure.health

# 2. Lister les backups disponibles
ls -lh /var/backups/medisecure/medisecure_production_*

# 3. Vérifier le dernier backup
./scripts/verify-backup.sh

# 4. CONFIRMER avec l'équipe

# 5. Restaurer
./scripts/restore-backup.sh production latest

# 6. Vérifier les services
docker compose ps
curl https://medisecure.health/health

# 7. Logger l'incident
echo "Emergency restore at $(date) - Reason: [DESCRIPTION]" >> /var/log/medisecure/incidents.log
```

---

## 📞 Support

En cas de problème:

1. **Vérifier les logs**: `/var/log/medisecure/deployments.log`
2. **Vérifier l'espace disque**: `df -h /var/backups`
3. **Lister les backups**: `ls -lh /var/backups/medisecure/`
4. **Tester la vérification**: `./scripts/verify-backup.sh`

Pour les erreurs de restauration, consulter:
- `docker compose logs`
- `/var/log/medisecure/deployments.log`
- État des containers: `docker compose ps`

---

## 📚 Ressources

- **Documentation HDS**: https://esante.gouv.fr/labels-certifications/hds
- **Docker Compose**: https://docs.docker.com/compose/
- **PostgreSQL Backup**: https://www.postgresql.org/docs/current/backup.html
- **MongoDB Backup**: https://www.mongodb.com/docs/manual/core/backups/
