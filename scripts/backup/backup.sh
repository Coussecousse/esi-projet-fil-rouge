#!/bin/bash
# Backup script for MediSecure HDS-compliant data protection
# Usage: ./backup.sh <environment>
# Environments: dev, staging, production

set -e

ENVIRONMENT="${1:-dev}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/backups/medisecure"
BACKUP_NAME="medisecure_${ENVIRONMENT}_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== MediSecure Backup - ${ENVIRONMENT} ===${NC}"
echo "Timestamp: ${TIMESTAMP}"
echo "Backup location: ${BACKUP_PATH}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"
mkdir -p "${BACKUP_PATH}"

# Function to backup PostgreSQL
backup_postgres() {
    echo -e "${YELLOW}Backing up PostgreSQL...${NC}"
    
    if docker compose ps | grep -q "postgres.*Up"; then
        # Backup via docker exec
        docker compose exec -T postgres pg_dumpall -U medisecure | gzip > "${BACKUP_PATH}/postgres_full.sql.gz"
        
        # Verify backup file exists and is not empty
        if [ -s "${BACKUP_PATH}/postgres_full.sql.gz" ]; then
            echo -e "${GREEN}✓ PostgreSQL backup completed${NC}"
            return 0
        else
            echo -e "${RED}✗ PostgreSQL backup file is empty${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ PostgreSQL container not running, skipping${NC}"
        return 0
    fi
}

# Function to backup MongoDB
backup_mongodb() {
    echo -e "${YELLOW}Backing up MongoDB...${NC}"
    
    if docker compose ps | grep -q "mongodb.*Up"; then
        # Create MongoDB dump directory
        mkdir -p "${BACKUP_PATH}/mongodb"
        
        # Backup via docker exec
        docker compose exec -T mongodb mongodump --archive --gzip | cat > "${BACKUP_PATH}/mongodb/dump.archive.gz"
        
        # Verify backup file exists and is not empty
        if [ -s "${BACKUP_PATH}/mongodb/dump.archive.gz" ]; then
            echo -e "${GREEN}✓ MongoDB backup completed${NC}"
            return 0
        else
            echo -e "${RED}✗ MongoDB backup file is empty${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ MongoDB container not running, skipping${NC}"
        return 0
    fi
}

# Function to backup MariaDB (if exists)
backup_mariadb() {
    echo -e "${YELLOW}Backing up MariaDB...${NC}"
    
    if docker compose ps | grep -q "mariadb.*Up"; then
        docker compose exec -T mariadb mysqldump -u root --all-databases | gzip > "${BACKUP_PATH}/mariadb_full.sql.gz"
        
        if [ -s "${BACKUP_PATH}/mariadb_full.sql.gz" ]; then
            echo -e "${GREEN}✓ MariaDB backup completed${NC}"
            return 0
        else
            echo -e "${RED}✗ MariaDB backup file is empty${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ MariaDB container not running, skipping${NC}"
        return 0
    fi
}

# Function to backup Redis (if needed - save RDB snapshot)
backup_redis() {
    echo -e "${YELLOW}Backing up Redis...${NC}"
    
    if docker compose ps | grep -q "redis.*Up"; then
        # Trigger Redis BGSAVE
        docker compose exec -T redis redis-cli BGSAVE
        sleep 2
        
        # Copy dump.rdb if it exists
        docker compose exec -T redis cat /data/dump.rdb > "${BACKUP_PATH}/redis_dump.rdb" 2>/dev/null || true
        
        if [ -f "${BACKUP_PATH}/redis_dump.rdb" ]; then
            echo -e "${GREEN}✓ Redis backup completed${NC}"
        else
            echo -e "${YELLOW}⚠ Redis backup not available (cache only)${NC}"
        fi
        return 0
    else
        echo -e "${YELLOW}⚠ Redis container not running, skipping${NC}"
        return 0
    fi
}

# Function to backup application data/volumes
backup_volumes() {
    echo -e "${YELLOW}Backing up Docker volumes...${NC}"
    
    # Backup MinIO data (documents storage)
    if docker compose ps | grep -q "minio.*Up"; then
        mkdir -p "${BACKUP_PATH}/minio"
        docker compose exec -T minio tar czf - /data 2>/dev/null > "${BACKUP_PATH}/minio/data.tar.gz" || true
        echo -e "${GREEN}✓ MinIO data backup completed${NC}"
    fi
}

# Create backup metadata
create_metadata() {
    echo -e "${YELLOW}Creating backup metadata...${NC}"
    
    cat > "${BACKUP_PATH}/metadata.json" <<EOF
{
  "environment": "${ENVIRONMENT}",
  "timestamp": "${TIMESTAMP}",
  "date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "hostname": "$(hostname)",
  "docker_compose_version": "$(docker compose version --short)",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "git_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
}
EOF
    
    echo -e "${GREEN}✓ Metadata created${NC}"
}

# Main backup process
main() {
    echo ""
    echo -e "${GREEN}Starting backup process...${NC}"
    echo ""
    
    # Execute backups
    backup_postgres
    backup_mongodb
    backup_mariadb
    backup_redis
    backup_volumes
    create_metadata
    
    # Create compressed archive
    echo ""
    echo -e "${YELLOW}Creating compressed archive...${NC}"
    cd "${BACKUP_DIR}"
    tar czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}/"
    
    # Calculate checksum
    sha256sum "${BACKUP_NAME}.tar.gz" > "${BACKUP_NAME}.tar.gz.sha256"
    
    # Get backup size
    BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
    
    echo -e "${GREEN}✓ Compressed archive created: ${BACKUP_SIZE}${NC}"
    
    # Clean up uncompressed directory
    rm -rf "${BACKUP_NAME}"
    
    echo ""
    echo -e "${GREEN}=== Backup completed successfully ===${NC}"
    echo "Backup file: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
    echo "Checksum: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz.sha256"
    echo "Size: ${BACKUP_SIZE}"
    
    # Retention policy: keep last 7 backups for dev/staging, 30 for production
    if [ "${ENVIRONMENT}" = "production" ]; then
        KEEP_DAYS=30
    else
        KEEP_DAYS=7
    fi
    
    echo ""
    echo -e "${YELLOW}Applying retention policy (${KEEP_DAYS} days)...${NC}"
    find "${BACKUP_DIR}" -name "medisecure_${ENVIRONMENT}_*.tar.gz" -mtime +${KEEP_DAYS} -delete
    find "${BACKUP_DIR}" -name "medisecure_${ENVIRONMENT}_*.sha256" -mtime +${KEEP_DAYS} -delete
    
    echo -e "${GREEN}✓ Old backups cleaned${NC}"
    
    # Log to audit file
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Backup completed - Environment: ${ENVIRONMENT} - File: ${BACKUP_NAME}.tar.gz - Size: ${BACKUP_SIZE}" >> /var/log/medisecure/deployments.log 2>/dev/null || true
}

# Validate environment
if [[ ! "${ENVIRONMENT}" =~ ^(dev|staging|production)$ ]]; then
    echo -e "${RED}Error: Invalid environment '${ENVIRONMENT}'${NC}"
    echo "Usage: $0 <environment>"
    echo "Valid environments: dev, staging, production"
    exit 1
fi

# Run main backup
main

exit 0
