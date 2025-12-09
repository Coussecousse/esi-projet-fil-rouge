#!/bin/bash

# Script de restauration pour MediSecure
# Usage: ./restore-databases.sh <backup_date> [service]
# Exemple: ./restore-databases.sh 20231122_143045 postgresql

set -e

# Configuration
BACKUP_DIR="/backups"
COMPOSE_FILE="compose.yml"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier les paramètres
if [ $# -lt 1 ]; then
    echo "Usage: $0 <backup_date> [service]"
    echo "Services disponibles: postgresql, mongodb, mariadb, minio, redis, all"
    echo "Exemple: $0 20231122_143045 postgresql"
    exit 1
fi

BACKUP_DATE=$1
SERVICE=${2:-all}

# Vérifier que les fichiers de sauvegarde existent
check_backup_files() {
    log_info "Vérification des fichiers de sauvegarde pour la date: $BACKUP_DATE"
    
    local files_found=false
    
    if [ -f "$BACKUP_DIR/postgresql/patients_$BACKUP_DATE.sql.gz" ]; then
        log_info "✓ Sauvegarde PostgreSQL patients trouvée"
        files_found=true
    fi
    
    if [ -f "$BACKUP_DIR/mongodb/appointments_$BACKUP_DATE.archive" ]; then
        log_info "✓ Sauvegarde MongoDB trouvée"
        files_found=true
    fi
    
    if [ -f "$BACKUP_DIR/mariadb/billing_$BACKUP_DATE.sql.gz" ]; then
        log_info "✓ Sauvegarde MariaDB trouvée"
        files_found=true
    fi
    
    if [ ! "$files_found" = true ]; then
        log_error "Aucun fichier de sauvegarde trouvé pour la date $BACKUP_DATE"
        exit 1
    fi
}

# Restauration PostgreSQL
restore_postgresql() {
    log_info "Restauration PostgreSQL..."
    
    # Patients
    if [ -f "$BACKUP_DIR/postgresql/patients_$BACKUP_DATE.sql.gz" ]; then
        log_info "Restauration base patients..."
        
        zcat $BACKUP_DIR/postgresql/patients_$BACKUP_DATE.sql.gz | \
        docker-compose -f $COMPOSE_FILE exec -T medisecure-db psql \
            -U medisecure_user \
            -d medisecure_patients
        
        log_info "✓ Base patients restaurée"
    fi
    
    # Keycloak
    if [ -f "$BACKUP_DIR/postgresql/keycloak_$BACKUP_DATE.sql.gz" ]; then
        log_info "Restauration base Keycloak..."
        
        zcat $BACKUP_DIR/postgresql/keycloak_$BACKUP_DATE.sql.gz | \
        docker-compose -f $COMPOSE_FILE exec -T medisecure-keycloak-db psql \
            -U keycloak_user \
            -d keycloak
        
        log_info "✓ Base Keycloak restaurée"
    fi
}

# Restauration MongoDB
restore_mongodb() {
    log_info "Restauration MongoDB..."
    
    if [ -f "$BACKUP_DIR/mongodb/appointments_$BACKUP_DATE.archive" ]; then
        docker-compose -f $COMPOSE_FILE exec -T medisecure-mongodb mongorestore \
            --username mongo_admin \
            --password mongo_password \
            --db medisecure_appointments \
            --authenticationDatabase admin \
            --gzip \
            --archive < $BACKUP_DIR/mongodb/appointments_$BACKUP_DATE.archive
        
        log_info "✓ MongoDB restaurée"
    fi
}

# Restauration MariaDB
restore_mariadb() {
    log_info "Restauration MariaDB..."
    
    if [ -f "$BACKUP_DIR/mariadb/billing_$BACKUP_DATE.sql.gz" ]; then
        zcat $BACKUP_DIR/mariadb/billing_$BACKUP_DATE.sql.gz | \
        docker-compose -f $COMPOSE_FILE exec -T medisecure-mariadb mysql \
            --user=root \
            --password=mariadb_root_password
        
        log_info "✓ MariaDB restaurée"
    fi
}

# Fonction principale
main() {
    log_info "=== DÉBUT RESTAURATION MEDISECURE ==="
    log_info "Date de sauvegarde: $BACKUP_DATE"
    log_info "Service(s): $SERVICE"
    
    # Vérifications
    check_backup_files
    
    # Confirmation
    echo -n "Êtes-vous sûr de vouloir restaurer ? Cette action est irréversible ! [y/N]: "
    read -r confirmation
    
    if [ "$confirmation" != "y" ] && [ "$confirmation" != "Y" ]; then
        log_warn "Restauration annulée par l'utilisateur"
        exit 0
    fi
    
    # Restauration selon le service demandé
    case $SERVICE in
        "postgresql")
            restore_postgresql
            ;;
        "mongodb")
            restore_mongodb
            ;;
        "mariadb")
            restore_mariadb
            ;;
        "all")
            restore_postgresql
            restore_mongodb
            restore_mariadb
            ;;
        *)
            log_error "Service non reconnu: $SERVICE"
            exit 1
            ;;
    esac
    
    log_info "=== RESTAURATION TERMINÉE ==="
}

main