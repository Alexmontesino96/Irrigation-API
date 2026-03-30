#!/bin/bash

# ============================================
# Backup automatico - Irrigation System DB
# ============================================

BACKUP_DIR="/Users/alexmontesino/Irrigation_System/backups"
DB_URL="postgresql://postgres:vifqy7-fontiH-qidzyp@db.fzxhlzfwpbnrkltsjiqj.supabase.co:5432/postgres"
KEEP_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.dump"
LOG_FILE="${BACKUP_DIR}/backup.log"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Iniciando backup..." >> "$LOG_FILE"

/opt/homebrew/opt/postgresql@17/bin/pg_dump "$DB_URL" \
  --format=custom \
  --no-owner \
  --no-acl \
  --file="$BACKUP_FILE" 2>> "$LOG_FILE"

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[$(date)] Backup exitoso: $BACKUP_FILE ($SIZE)" >> "$LOG_FILE"
else
    echo "[$(date)] ERROR: Backup fallido" >> "$LOG_FILE"
    exit 1
fi

# Eliminar backups mas viejos que KEEP_DAYS dias
find "$BACKUP_DIR" -name "backup_*.dump" -mtime +$KEEP_DAYS -delete
DELETED=$?
if [ $DELETED -eq 0 ]; then
    echo "[$(date)] Limpieza: backups > ${KEEP_DAYS} dias eliminados" >> "$LOG_FILE"
fi

echo "[$(date)] Backup completado" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
