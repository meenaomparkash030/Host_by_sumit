#!/bin/bash
# ─── SHAPPNO VPS ─── Backup Script ─────────────────────────────────────

BACKUP_DIR="/app/backups"
DATA_DIR="/app/data"
SERVERS_DIR="/app/servers"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

echo "[SHAPPNO] Starting backup at $TIMESTAMP"

# Create backup
tar -czf "$BACKUP_FILE" -C /app data servers 2>/dev/null

if [ $? -eq 0 ]; then
    echo "[SHAPPNO] ✅ Backup created: $BACKUP_FILE"
    # Keep only last 10 backups
    cd "$BACKUP_DIR" && ls -t backup_*.tar.gz | tail -n +11 | xargs -r rm
    echo "[SHAPPNO] ✅ Old backups cleaned"
else
    echo "[SHAPPNO] ❌ Backup failed"
    exit 1
fi

echo "[SHAPPNO] ✅ Backup completed"
