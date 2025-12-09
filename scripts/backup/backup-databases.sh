#!/bin/bash

# Script de sauvegarde automatisé pour MediSecure
# Usage: ./backup-databases.sh [daily|weekly|manual]

set -e

# Configuration
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
COMPOSE_FILE="compose.yml"
RETENTION_DAYS=30

# Créer le répertoire de sauvegarde s'il n'existe pas
mkdir -p $BACKUP_DIR/{postgresql,mongodb,mariadb,minio,redis}

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que Docker Compose est lancé
check_services() {
    log_info "Vérification des services Docker..."
    
    if ! docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        log_error "Aucun service Docker Compose n'est en cours d'exécution"
        exit 1
    fi
    
    log_info "Services Docker détectés"
}

# Sauvegarde PostgreSQL (Patients + Keycloak)
backup_postgresql() {
    log_info "Sauvegarde PostgreSQL - Base patients..."
    
    # Base patients
    docker-compose -f $COMPOSE_FILE exec -T medisecure-db pg_dump \
        -U medisecure_user \
        -d medisecure_patients \
        --no-password \
        --verbose \
        --clean \
        --if-exists > $BACKUP_DIR/postgresql/patients_$DATE.sql
    
    if [ $? -eq 0 ]; then
        log_info "✓ Sauvegarde patients terminée: patients_$DATE.sql"
    else
        log_error "✗ Échec sauvegarde patients"
        return 1
    fi
    
    # Base Keycloak
    log_info "Sauvegarde PostgreSQL - Base Keycloak..."
    docker-compose -f $COMPOSE_FILE exec -T medisecure-keycloak-db pg_dump \
        -U keycloak_user \
        -d keycloak \
        --no-password \
        --verbose \
        --clean \
        --if-exists > $BACKUP_DIR/postgresql/keycloak_$DATE.sql
    
    if [ $? -eq 0 ]; then
        log_info "✓ Sauvegarde Keycloak terminée: keycloak_$DATE.sql"
    else
        log_error "✗ Échec sauvegarde Keycloak"
        return 1
    fi
    
    # Compression
    gzip $BACKUP_DIR/postgresql/patients_$DATE.sql
    gzip $BACKUP_DIR/postgresql/keycloak_$DATE.sql
    log_info "✓ Fichiers PostgreSQL compressés"
}

# Sauvegarde MongoDB (RDV)
backup_mongodb() {
    log_info "Sauvegarde MongoDB - Base appointments..."
    
    docker-compose -f $COMPOSE_FILE exec -T medisecure-mongodb mongodump \
        --username mongo_admin \
        --password mongo_password \
        --db medisecure_appointments \
        --authenticationDatabase admin \
        --gzip \
        --archive > $BACKUP_DIR/mongodb/appointments_$DATE.archive
    
    if [ $? -eq 0 ]; then
        log_info "✓ Sauvegarde MongoDB terminée: appointments_$DATE.archive"
    else
        log_error "✗ Échec sauvegarde MongoDB"
        return 1
    fi
}

# Sauvegarde MariaDB (Facturation)
backup_mariadb() {
    log_info "Sauvegarde MariaDB - Base billing..."
    
    docker-compose -f $COMPOSE_FILE exec -T medisecure-mariadb mysqldump \
        --user=mariadb_user \
        --password=mariadb_password \
        --single-transaction \
        --routines \
        --triggers \
        --all-databases > $BACKUP_DIR/mariadb/billing_$DATE.sql
    
    if [ $? -eq 0 ]; then
        log_info "✓ Sauvegarde MariaDB terminée: billing_$DATE.sql"
        gzip $BACKUP_DIR/mariadb/billing_$DATE.sql
        log_info "✓ Fichier MariaDB compressé"
    else
        log_error "✗ Échec sauvegarde MariaDB"
        return 1
    fi
}

# Sauvegarde MinIO (Documents)
backup_minio() {
    log_info "Sauvegarde MinIO - Documents médicaux..."
    
    # Utiliser mc (MinIO Client) pour synchroniser
    docker-compose -f $COMPOSE_FILE exec -T medisecure-minio sh -c "
        mc config host add local http://localhost:9000 minio_admin minio_password
        mc mirror --overwrite local/medisecure-documents /backup/minio/documents_$DATE/
    " > /dev/null 2>&1
    
    # Alternative: copie directe du volume si mc n'est pas disponible
    if [ $? -ne 0 ]; then
        log_warn "mc non disponible, copie directe du volume..."
        docker run --rm \
            -v medisecure_minio_data:/source:ro \
            -v $(pwd)/$BACKUP_DIR/minio:/backup \
            alpine:latest \
            sh -c "cp -r /source/* /backup/documents_$DATE/ 2>/dev/null || true"
    fi
    
    if [ -d "$BACKUP_DIR/minio/documents_$DATE" ] && [ "$(ls -A $BACKUP_DIR/minio/documents_$DATE)" ]; then
        log_info "✓ Sauvegarde MinIO terminée: documents_$DATE/"
        
        # Compression du dossier
        tar -czf $BACKUP_DIR/minio/documents_$DATE.tar.gz -C $BACKUP_DIR/minio documents_$DATE/
        rm -rf $BACKUP_DIR/minio/documents_$DATE/
        log_info "✓ Documents compressés"
    else
        log_warn "Aucun document trouvé ou répertoire vide"
    fi
}

# Sauvegarde Redis (Cache - optionnel)
backup_redis() {
    log_info "Sauvegarde Redis - Cache et sessions..."
    
    # Forcer la sauvegarde Redis
    docker-compose -f $COMPOSE_FILE exec -T medisecure-redis redis-cli \
        --no-auth-warning \
        -a redis_password \
        BGSAVE > /dev/null
    
    # Attendre la fin de la sauvegarde
    sleep 2
    
    # Copier le fichier RDB
    docker-compose -f $COMPOSE_FILE exec -T medisecure-redis cat /data/dump.rdb > $BACKUP_DIR/redis/redis_$DATE.rdb
    
    if [ -f "$BACKUP_DIR/redis/redis_$DATE.rdb" ] && [ -s "$BACKUP_DIR/redis/redis_$DATE.rdb" ]; then
        log_info "✓ Sauvegarde Redis terminée: redis_$DATE.rdb"
        gzip $BACKUP_DIR/redis/redis_$DATE.rdb
    else
        log_warn "Fichier Redis vide ou inexistant"
    fi
}

# Nettoyage des anciennes sauvegardes
cleanup_old_backups() {
    log_info "Nettoyage des sauvegardes anciennes (> $RETENTION_DAYS jours)..."
    
    find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find $BACKUP_DIR -name "*.archive" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find $BACKUP_DIR -name "*.rdb.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    log_info "✓ Nettoyage terminé"
}

# Génération du rapport de sauvegarde
generate_report() {
    local backup_type=$1
    local report_file="$BACKUP_DIR/backup_report_$DATE.txt"
    
    cat > $report_file << EOF
=== RAPPORT DE SAUVEGARDE MEDISECURE ===
Date: $(date)
Type: $backup_type
Durée: $SECONDS secondes

=== FICHIERS CRÉÉS ===
EOF

    # Lister les fichiers créés
    find $BACKUP_DIR -name "*$DATE*" -type f >> $report_file
    
    echo "" >> $report_file
    echo "=== TAILLES ====" >> $report_file
    du -sh $BACKUP_DIR/*/ >> $report_file
    
    echo "" >> $report_file
    echo "=== ESPACE DISQUE ====" >> $report_file
    df -h $BACKUP_DIR >> $report_file
    
    log_info "✓ Rapport généré: $report_file"
}

# Fonction principale
main() {
    local backup_type=${1:-manual}
    
    log_info "=== DÉBUT SAUVEGARDE MEDISECURE ($backup_type) ==="
    log_info "Date: $(date)"
    
    # Vérifications préliminaires
    check_services
    
    # Exécution des sauvegardes selon le type
    case $backup_type in
        "daily")
            log_info "Sauvegarde quotidienne - Données critiques"
            backup_postgresql
            backup_mariadb
            ;;
        "weekly")
            log_info "Sauvegarde hebdomadaire - Complète"
            backup_postgresql
            backup_mongodb
            backup_mariadb
            backup_minio
            backup_redis
            ;;
        "manual"|*)
            log_info "Sauvegarde manuelle - Complète"
            backup_postgresql
            backup_mongodb
            backup_mariadb
            backup_minio
            backup_redis
            ;;
    esac
    
    # Nettoyage et rapport
    cleanup_old_backups
    generate_report $backup_type
    
    log_info "=== SAUVEGARDE TERMINÉE ==="
    log_info "Durée totale: $SECONDS secondes"
    log_info "Fichiers sauvegardés dans: $BACKUP_DIR"
}

# Gestion des erreurs
trap 'log_error "Erreur lors de la sauvegarde à la ligne $LINENO"' ERR

# Exécution
main "$@"