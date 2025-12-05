#!/bin/bash
# Verify backup integrity for MediSecure HDS compliance
# Usage: ./verify-backup.sh [backup-file.tar.gz]

set -e

BACKUP_DIR="/var/backups/medisecure"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== MediSecure Backup Verification ===${NC}"

# Get backup file
if [ -n "$1" ]; then
    BACKUP_FILE="$1"
else
    # Find most recent backup
    BACKUP_FILE=$(ls -t ${BACKUP_DIR}/medisecure_*.tar.gz 2>/dev/null | head -n1)
fi

# Check if backup exists
if [ -z "${BACKUP_FILE}" ] || [ ! -f "${BACKUP_FILE}" ]; then
    echo -e "${RED}✗ No backup file found${NC}"
    exit 1
fi

echo "Verifying: ${BACKUP_FILE}"
echo ""

# Verify checksum exists
CHECKSUM_FILE="${BACKUP_FILE}.sha256"
if [ ! -f "${CHECKSUM_FILE}" ]; then
    echo -e "${RED}✗ Checksum file not found: ${CHECKSUM_FILE}${NC}"
    exit 1
fi

# Verify checksum
echo -e "${YELLOW}Verifying checksum...${NC}"
cd "$(dirname "${BACKUP_FILE}")"
if sha256sum -c "$(basename "${CHECKSUM_FILE}")" 2>/dev/null; then
    echo -e "${GREEN}✓ Checksum verified${NC}"
else
    echo -e "${RED}✗ Checksum verification failed${NC}"
    exit 1
fi

# Verify archive integrity
echo ""
echo -e "${YELLOW}Verifying archive integrity...${NC}"
if tar tzf "${BACKUP_FILE}" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Archive integrity verified${NC}"
else
    echo -e "${RED}✗ Archive is corrupted${NC}"
    exit 1
fi

# List contents
echo ""
echo -e "${YELLOW}Archive contents:${NC}"
tar tzf "${BACKUP_FILE}" | head -n 20
FILE_COUNT=$(tar tzf "${BACKUP_FILE}" | wc -l)
echo "... (${FILE_COUNT} total files)"

# Verify metadata
echo ""
echo -e "${YELLOW}Extracting and verifying metadata...${NC}"
TEMP_DIR=$(mktemp -d)
tar xzf "${BACKUP_FILE}" -C "${TEMP_DIR}" --wildcards "*/metadata.json" 2>/dev/null || true

METADATA_FILE=$(find "${TEMP_DIR}" -name "metadata.json" 2>/dev/null | head -n1)
if [ -f "${METADATA_FILE}" ]; then
    echo -e "${GREEN}✓ Metadata found${NC}"
    echo ""
    cat "${METADATA_FILE}" | python3 -m json.tool 2>/dev/null || cat "${METADATA_FILE}"
else
    echo -e "${YELLOW}⚠ Metadata not found (older backup format)${NC}"
fi

# Cleanup
rm -rf "${TEMP_DIR}"

# Verify database dumps
echo ""
echo -e "${YELLOW}Verifying database dumps...${NC}"

TEMP_EXTRACT=$(mktemp -d)
tar xzf "${BACKUP_FILE}" -C "${TEMP_EXTRACT}" 2>/dev/null

# Check PostgreSQL
if [ -f "${TEMP_EXTRACT}"/*/postgres_full.sql.gz ]; then
    PG_SIZE=$(du -h "${TEMP_EXTRACT}"/*/postgres_full.sql.gz | cut -f1)
    if gunzip -t "${TEMP_EXTRACT}"/*/postgres_full.sql.gz 2>/dev/null; then
        echo -e "${GREEN}✓ PostgreSQL dump verified (${PG_SIZE})${NC}"
    else
        echo -e "${RED}✗ PostgreSQL dump corrupted${NC}"
        rm -rf "${TEMP_EXTRACT}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ PostgreSQL dump not found${NC}"
fi

# Check MongoDB
if [ -f "${TEMP_EXTRACT}"/*/mongodb/dump.archive.gz ]; then
    MONGO_SIZE=$(du -h "${TEMP_EXTRACT}"/*/mongodb/dump.archive.gz | cut -f1)
    if gunzip -t "${TEMP_EXTRACT}"/*/mongodb/dump.archive.gz 2>/dev/null; then
        echo -e "${GREEN}✓ MongoDB dump verified (${MONGO_SIZE})${NC}"
    else
        echo -e "${RED}✗ MongoDB dump corrupted${NC}"
        rm -rf "${TEMP_EXTRACT}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ MongoDB dump not found${NC}"
fi

# Check MariaDB
if [ -f "${TEMP_EXTRACT}"/*/mariadb_full.sql.gz ]; then
    MARIA_SIZE=$(du -h "${TEMP_EXTRACT}"/*/mariadb_full.sql.gz | cut -f1)
    if gunzip -t "${TEMP_EXTRACT}"/*/mariadb_full.sql.gz 2>/dev/null; then
        echo -e "${GREEN}✓ MariaDB dump verified (${MARIA_SIZE})${NC}"
    else
        echo -e "${RED}✗ MariaDB dump corrupted${NC}"
        rm -rf "${TEMP_EXTRACT}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ MariaDB dump not found${NC}"
fi

# Cleanup
rm -rf "${TEMP_EXTRACT}"

# Get backup age
BACKUP_AGE=$(( ($(date +%s) - $(stat -c %Y "${BACKUP_FILE}")) / 3600 ))
BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)

echo ""
echo -e "${GREEN}=== Verification completed successfully ===${NC}"
echo "Backup file: ${BACKUP_FILE}"
echo "Size: ${BACKUP_SIZE}"
echo "Age: ${BACKUP_AGE} hours"
echo ""

# Warning if backup is old
if [ "${BACKUP_AGE}" -gt 48 ]; then
    echo -e "${YELLOW}⚠ Warning: Backup is older than 48 hours${NC}"
fi

# Log verification
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Backup verified - File: $(basename ${BACKUP_FILE})" >> /var/log/medisecure/deployments.log 2>/dev/null || true

exit 0
