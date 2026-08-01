#!/usr/bin/env bash
set -euo pipefail
DB_NAME="${DB_NAME:-scanner_db}"
DB_USER="${DB_USER:-scanner_user}"
DB_PASSWORD="${DB_PASSWORD:-changeme_dev_password}"
log() { echo -e "\n\033[1;32m[DB SETUP]\033[0m $1"; }

log "Ensuring PostgreSQL is running..."
sudo systemctl start postgresql

ROLE_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'")
if [ "$ROLE_EXISTS" = "1" ]; then
    log "Role '${DB_USER}' already exists, skipping."
else
    log "Creating role '${DB_USER}'..."
    sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';"
fi

DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'")
if [ "$DB_EXISTS" = "1" ]; then
    log "Database '${DB_NAME}' already exists, skipping."
else
    log "Creating database '${DB_NAME}'..."
    sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"
fi

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"
log "Database ready: ${DB_NAME} / ${DB_USER} / ${DB_PASSWORD}"
