# Scripts de Sauvegarde Automatisés - MediSecure

## Vue d'ensemble

Ce répertoire contient les scripts de sauvegarde automatisés pour l'infrastructure Docker Compose de MediSecure. Les sauvegardes couvrent toutes les bases de données critiques et les documents médicaux.

## Structure des fichiers

```
scripts/backup/
├── backup-databases.sh     # Script principal de sauvegarde
├── restore-databases.sh    # Script de restauration
├── setup-backup.sh         # Installation automatisée
├── crontab-backup          # Configuration cron
└── README.md              # Cette documentation
```

## Installation rapide

### 1. Permissions et installation
```bash
# Rendre les scripts exécutables
chmod +x scripts/backup/*.sh

# Installation automatisée (nécessite sudo)
sudo ./scripts/backup/setup-backup.sh
```

### 2. Configuration manuelle (alternative)
```bash
# Créer les répertoires
sudo mkdir -p /backups/{postgresql,mongodb,mariadb,minio,redis}

# Installer la crontab
crontab scripts/backup/crontab-backup
```

## Utilisation

### Sauvegardes manuelles
```bash
# Sauvegarde complète
./scripts/backup/backup-databases.sh manual

# Sauvegarde quotidienne (données critiques)
./scripts/backup/backup-databases.sh daily

# Sauvegarde hebdomadaire (complète)
./scripts/backup/backup-databases.sh weekly
```

### Restauration
```bash
# Restaurer toutes les bases
./scripts/backup/restore-databases.sh 20231122_143045 all

# Restaurer une base spécifique
./scripts/backup/restore-databases.sh 20231122_143045 postgresql
```

## Planification automatique

### Tâches cron configurées
- **Quotidien (2h00)** : PostgreSQL + MariaDB (données critiques)
- **Hebdomadaire (Dimanche 3h00)** : Sauvegarde complète
- **Monitoring (12h00)** : Vérification espace disque

### Services sauvegardés

| Service | Base de données | Méthode | Fréquence |
|---------|----------------|---------|-----------|
| **Patients** | PostgreSQL | pg_dump | Quotidien |
| **Keycloak** | PostgreSQL | pg_dump | Quotidien |
| **RDV** | MongoDB | mongodump | Hebdomadaire |
| **Facturation** | MariaDB | mysqldump | Quotidien |
| **Documents** | MinIO | mc mirror | Hebdomadaire |
| **Cache** | Redis | RDB export | Hebdomadaire |

## Fichiers de sauvegarde

### Nomenclature
```
/backups/
├── postgresql/
│   ├── patients_20231122_143045.sql.gz
│   └── keycloak_20231122_143045.sql.gz
├── mongodb/
│   └── appointments_20231122_143045.archive
├── mariadb/
│   └── billing_20231122_143045.sql.gz
├── minio/
│   └── documents_20231122_143045.tar.gz
└── redis/
    └── redis_20231122_143045.rdb.gz
```

### Rétention
- **Fichiers** : Suppression automatique après 30 jours
- **Logs** : Conservation 90 jours
- **Compression** : Gzip pour tous les formats

## Monitoring et logs

### Fichiers de logs
```bash
# Logs quotidiens
tail -f /var/log/backup-daily.log

# Logs hebdomadaires
tail -f /var/log/backup-weekly.log

# Surveillance espace disque
tail -f /var/log/syslog | grep backup-monitor
```

### Vérification des sauvegardes
```bash
# Lister les sauvegardes disponibles
ls -la /backups/*/

# Vérifier l'intégrité d'un backup PostgreSQL
zcat /backups/postgresql/patients_20231122_143045.sql.gz | head -20

# Taille des sauvegardes
du -sh /backups/*/
```

## Sécurité et conformité

### Chiffrement
- **Transport** : Connexions Docker internes sécurisées
- **Repos** : Possibilité d'ajouter GPG pour chiffrer les backups
- **Accès** : Permissions restrictives (750) sur /backups

### Conformité HDS/RGPD
- **Audit trail** : Tous les backups sont loggés
- **Rétention** : Suppression automatique selon la politique
- **Intégrité** : Vérification des hash MD5 possible

### Configuration GPG (optionnel)
```bash
# Générer une clé de chiffrement
gpg --gen-key

# Chiffrer une sauvegarde
gpg --encrypt --recipient medisecure-backup patients_20231122_143045.sql.gz
```

## Troubleshooting

### Problèmes courants

#### Services non démarrés
```bash
# Vérifier les services Docker
docker-compose ps

# Redémarrer si nécessaire
docker-compose up -d
```

#### Espace disque insuffisant
```bash
# Vérifier l'espace
df -h /backups

# Nettoyage manuel
find /backups -name "*.gz" -mtime +7 -delete
```

#### Erreurs de permissions
```bash
# Corriger les permissions
sudo chown -R $(whoami):$(whoami) /backups
sudo chmod -R 750 /backups
```

### Commandes de diagnostic
```bash
# Test des connexions DB
docker-compose exec medisecure-db pg_isready -U medisecure_user
docker-compose exec medisecure-mongodb mongo --eval "db.runCommand('ping')"

# Vérifier les tâches cron
crontab -l | grep backup

# Status du service cron
sudo systemctl status cron
```

## Restauration d'urgence

### Procédure complète
1. **Arrêter les services**
   ```bash
   docker-compose down
   ```

2. **Nettoyer les volumes (ATTENTION)**
   ```bash
   docker volume rm medisecure_postgres_data
   docker volume rm medisecure_mongodb_data
   ```

3. **Redémarrer les bases**
   ```bash
   docker-compose up -d medisecure-db medisecure-mongodb
   ```

4. **Restaurer les données**
   ```bash
   ./scripts/backup/restore-databases.sh 20231122_143045 all
   ```

5. **Redémarrer tous les services**
   ```bash
   docker-compose up -d
   ```

### Contact support
En cas de problème critique, documenter :
- Heure de l'incident
- Messages d'erreur dans les logs
- Dernière sauvegarde connue fonctionnelle
- État des services Docker

---

**⚠️ Important** : Toujours tester les procédures de restauration en environnement de développement avant une utilisation en production.