#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE konga;
    GRANT ALL PRIVILEGES ON DATABASE konga TO $POSTGRES_USER;
EOSQL

echo "Konga database created successfully"
