#!/bin/bash
# Restore backup for MediSecure - HDS compliant recovery
# Usage: ./restore-backup.sh <environment> [backup-file]

set -e

ENVIRONMENT="$1"
BACKUP_FILE="$2"
BACKUP_DIR="/var/backups/medisecure"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}=== MediSecure Backup Restoration ===${NC}"
echo -e "${RED}⚠️  WARNING: This will overwrite current data!${NC}"
echo ""

# Validate environment
if [[ ! "${ENVIRONMENT}" =~ ^(dev|staging|production)$ ]]; then
    echo -e "${RED}Error: Invalid environment '${ENVIRONMENT}'${NC}"
    echo "Usage: $0 <environment> [backup-file]"
    echo "Valid environments: dev, staging, production"
    exit 1
fi

# Find backup file
if [ -z "${BACKUP_FILE}" ]; then
    # Find most recent backup for this environment
    BACKUP_FILE=$(ls -t ${BACKUP_DIR}/medisecure_${ENVIRONMENT}_*.tar.gz 2>/dev/null | head -n1)
    
    if [ -z "${BACKUP_FILE}" ]; then
        # Try 'latest' keyword
        if [ "$2" = "latest" ]; then
            BACKUP_FILE=$(ls -t ${BACKUP_DIR}/medisecure_${ENVIRONMENT}_*.tar.gz 2>/dev/null | head -n1)
        fi
    fi
fi

# Check if backup exists
if [ -z "${BACKUP_FILE}" ] || [ ! -f "${BACKUP_FILE}" ]; then
    echo -e "${RED}✗ No backup file found${NC}"
    echo "Available backups for ${ENVIRONMENT}:"
    ls -lh ${BACKUP_DIR}/medisecure_${ENVIRONMENT}_*.tar.gz 2>/dev/null || echo "  (none)"
    exit 1
fi

echo "Environment: ${ENVIRONMENT}"
echo "Backup file: ${BACKUP_FILE}"
echo "Backup size: $(du -h ${BACKUP_FILE} | cut -f1)"
echo "Backup date: $(stat -c %y ${BACKUP_FILE} | cut -d'.' -f1)"
echo ""

# Require manual confirmation for production
if [ "${ENVIRONMENT}" = "production" ]; then
    echo -e "${RED}🚨 PRODUCTION RESTORE - CRITICAL OPERATION${NC}"
    echo -e "${RED}This will restore production data from backup!${NC}"
    echo ""
    read -p "Type 'RESTORE PRODUCTION' to continue: " CONFIRM
    if [ "${CONFIRM}" != "RESTORE PRODUCTION" ]; then
        echo "Restoration cancelled"
        exit 1
    fi
else
    echo -e "${YELLOW}Restore will begin in 5 seconds... (Ctrl+C to cancel)${NC}"
    sleep 5
fi

# Verify backup first
echo ""
echo -e "${YELLOW}Verifying backup integrity...${NC}"
if ! ./scripts/verify-backup.sh "${BACKUP_FILE}"; then
    echo -e "${RED}✗ Backup verification failed. Aborting restore.${NC}"
    exit 1
fi

# Extract backup
echo ""
echo -e "${YELLOW}Extracting backup...${NC}"
TEMP_DIR=$(mktemp -d)
tar xzf "${BACKUP_FILE}" -C "${TEMP_DIR}"
BACKUP_CONTENTS=$(ls "${TEMP_DIR}")
RESTORE_PATH="${TEMP_DIR}/${BACKUP_CONTENTS}"

echo -e "${GREEN}✓ Backup extracted to ${TEMP_DIR}${NC}"

# Stop services (optional, safer for restore)
echo ""
read -p "Stop services before restore? (recommended) [Y/n]: " STOP_SERVICES
if [[ "${STOP_SERVICES}" != "n" ]]; then
    echo -e "${YELLOW}Stopping services...${NC}"
    docker compose stop
fi

# Restore PostgreSQL
restore_postgres() {
    echo ""
    echo -e "${YELLOW}Restoring PostgreSQL...${NC}"
    
    if [ -f "${RESTORE_PATH}/postgres_full.sql.gz" ]; then
        # Ensure container is running
        docker compose up -d postgres
        sleep 5
        
        # Drop existing connections and restore
        gunzip -c "${RESTORE_PATH}/postgres_full.sql.gz" | docker compose exec -T postgres psql -U medisecure
        
        echo -e "${GREEN}✓ PostgreSQL restored${NC}"
    else
        echo -e "${YELLOW}⚠ PostgreSQL backup not found, skipping${NC}"
    fi
}

# Restore MongoDB
restore_mongodb() {
    echo ""
    echo -e "${YELLOW}Restoring MongoDB...${NC}"
    
    if [ -f "${RESTORE_PATH}/mongodb/dump.archive.gz" ]; then
        # Ensure container is running
        docker compose up -d mongodb
        sleep 5
        
        # Restore MongoDB
        gunzip -c "${RESTORE_PATH}/mongodb/dump.archive.gz" | docker compose exec -T mongodb mongorestore --archive --drop
        
        echo -e "${GREEN}✓ MongoDB restored${NC}"
    else
        echo -e "${YELLOW}⚠ MongoDB backup not found, skipping${NC}"
    fi
}

# Restore MariaDB
restore_mariadb() {
    echo ""
    echo -e "${YELLOW}Restoring MariaDB...${NC}"
    
    if [ -f "${RESTORE_PATH}/mariadb_full.sql.gz" ]; then
        # Ensure container is running
        docker compose up -d mariadb
        sleep 5
        
        # Restore MariaDB
        gunzip -c "${RESTORE_PATH}/mariadb_full.sql.gz" | docker compose exec -T mariadb mysql -u root
        
        echo -e "${GREEN}✓ MariaDB restored${NC}"
    else
        echo -e "${YELLOW}⚠ MariaDB backup not found, skipping${NC}"
    fi
}

# Restore Redis
restore_redis() {
    echo ""
    echo -e "${YELLOW}Restoring Redis...${NC}"
    
    if [ -f "${RESTORE_PATH}/redis_dump.rdb" ]; then
        # Stop Redis
        docker compose stop redis
        
        # Copy dump file
        docker compose cp "${RESTORE_PATH}/redis_dump.rdb" redis:/data/dump.rdb
        
        # Start Redis
        docker compose up -d redis
        
        echo -e "${GREEN}✓ Redis restored${NC}"
    else
        echo -e "${YELLOW}⚠ Redis backup not found, skipping (cache will rebuild)${NC}"
    fi
}

# Main restore process
echo ""
echo -e "${BLUE}Starting restore process...${NC}"

restore_postgres
restore_mongodb
restore_mariadb
restore_redis

# Restart all services
echo ""
echo -e "${YELLOW}Restarting all services...${NC}"
docker compose up -d

# Wait for services
echo "Waiting for services to be ready..."
sleep 30

# Verify services
echo ""
echo -e "${YELLOW}Verifying services...${NC}"
docker compose ps

# Cleanup
echo ""
echo -e "${YELLOW}Cleaning up temporary files...${NC}"
rm -rf "${TEMP_DIR}"

echo ""
echo -e "${GREEN}=== Restore completed successfully ===${NC}"
echo "Environment: ${ENVIRONMENT}"
echo "Restored from: $(basename ${BACKUP_FILE})"
echo ""
echo -e "${BLUE}Recommended next steps:${NC}"
echo "1. Verify application health: curl http://localhost:8000/health"
echo "2. Check logs: docker compose logs"
echo "3. Test critical endpoints"
echo "4. Validate data integrity"

# Log restore
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Backup restored - Environment: ${ENVIRONMENT} - Source: $(basename ${BACKUP_FILE})" >> /var/log/medisecure/deployments.log 2>/dev/null || true

exit 0
