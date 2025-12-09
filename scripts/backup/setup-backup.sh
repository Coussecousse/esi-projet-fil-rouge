#!/bin/bash

# Script d'installation et configuration des sauvegardes automatisées
# Usage: sudo ./setup-backup.sh

set -e

# Configuration
BACKUP_DIR="/backups"
SCRIPT_DIR="/app/scripts/backup"
LOG_DIR="/var/log"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Vérifier les privilèges root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Ce script doit être exécuté avec les privilèges root (sudo)"
        exit 1
    fi
}

# Créer les répertoires nécessaires
create_directories() {
    log_info "Création des répertoires de sauvegarde..."
    
    mkdir -p $BACKUP_DIR/{postgresql,mongodb,mariadb,minio,redis}
    mkdir -p $LOG_DIR
    
    # Permissions appropriées
    chmod 750 $BACKUP_DIR
    chown -R 1000:1000 $BACKUP_DIR 2>/dev/null || true
    
    log_info "✓ Répertoires créés: $BACKUP_DIR"
}

# Installer les dépendances
install_dependencies() {
    log_info "Installation des dépendances..."
    
    # Détecter la distribution
    if command -v apt-get > /dev/null; then
        # Debian/Ubuntu
        apt-get update > /dev/null
        apt-get install -y cron gzip tar findutils > /dev/null
    elif command -v yum > /dev/null; then
        # RHEL/CentOS
        yum install -y cronie gzip tar findutils > /dev/null
    elif command -v apk > /dev/null; then
        # Alpine (Docker)
        apk add --no-cache dcron gzip tar findutils > /dev/null
    fi
    
    log_info "✓ Dépendances installées"
}

# Configurer les permissions des scripts
setup_permissions() {
    log_info "Configuration des permissions..."
    
    # Scripts exécutables
    chmod +x $SCRIPT_DIR/backup-databases.sh
    chmod +x $SCRIPT_DIR/restore-databases.sh
    chmod +x $SCRIPT_DIR/setup-backup.sh
    
    # Crontab lisible
    chmod 644 $SCRIPT_DIR/crontab-backup
    
    log_info "✓ Permissions configurées"
}

# Installer la crontab
install_crontab() {
    log_info "Installation de la crontab..."
    
    # Sauvegarder la crontab existante
    crontab -l > /tmp/crontab-backup.txt 2>/dev/null || echo "# Nouvelle crontab" > /tmp/crontab-backup.txt
    
    # Ajouter les tâches de sauvegarde si elles n'existent pas déjà
    if ! crontab -l 2>/dev/null | grep -q "backup-databases.sh"; then
        cat /tmp/crontab-backup.txt $SCRIPT_DIR/crontab-backup | crontab -
        log_info "✓ Tâches cron installées"
    else
        log_warn "Tâches cron déjà présentes"
    fi
    
    # Démarrer le service cron
    if command -v systemctl > /dev/null; then
        systemctl enable cron 2>/dev/null || true
        systemctl start cron 2>/dev/null || true
    elif command -v service > /dev/null; then
        service cron start 2>/dev/null || true
    fi
}

# Test de la configuration
test_backup() {
    log_info "Test de la configuration..."
    
    # Vérifier que Docker Compose fonctionne
    if command -v docker-compose > /dev/null; then
        if docker-compose -f compose.yml ps > /dev/null 2>&1; then
            log_info "✓ Docker Compose accessible"
        else
            log_warn "Docker Compose non accessible depuis ce répertoire"
        fi
    else
        log_warn "Docker Compose non installé"
    fi
    
    # Test d'écriture dans le répertoire de backup
    if touch $BACKUP_DIR/test-write && rm $BACKUP_DIR/test-write; then
        log_info "✓ Répertoire de sauvegarde accessible en écriture"
    else
        log_error "Impossible d'écrire dans $BACKUP_DIR"
        exit 1
    fi
    
    # Afficher l'espace disque disponible
    local available_space=$(df -h $BACKUP_DIR | awk 'NR==2{print $4}')
    log_info "Espace disponible pour les sauvegardes: $available_space"
}

# Afficher les informations de configuration
show_info() {
    log_info "=== CONFIGURATION TERMINÉE ==="
    echo ""
    echo "📁 Répertoire de sauvegarde: $BACKUP_DIR"
    echo "📜 Scripts: $SCRIPT_DIR"
    echo "📋 Logs: $LOG_DIR/backup-*.log"
    echo ""
    echo "🕒 Planification automatique:"
    echo "   • Sauvegarde quotidienne: 2h00 (données critiques)"
    echo "   • Sauvegarde hebdomadaire: Dimanche 3h00 (complète)"
    echo ""
    echo "🔧 Commandes utiles:"
    echo "   • Sauvegarde manuelle: ./backup-databases.sh manual"
    echo "   • Restauration: ./restore-databases.sh <date> [service]"
    echo "   • Voir les tâches cron: crontab -l"
    echo "   • Logs: tail -f $LOG_DIR/backup-daily.log"
    echo ""
    echo "📊 Surveillance:"
    crontab -l | grep backup || echo "   Aucune tâche cron trouvée"
    echo ""
}

# Fonction principale
main() {
    log_info "=== INSTALLATION DES SAUVEGARDES MEDISECURE ==="
    
    check_root
    create_directories
    install_dependencies
    setup_permissions
    install_crontab
    test_backup
    show_info
    
    log_info "✅ Installation terminée avec succès !"
}

main "$@"