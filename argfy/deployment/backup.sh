#!/usr/bin/env bash
set -euo pipefail

TS=$(date -u +%Y%m%d_%H%M%S)
OUT=/backups/postgres/argfy_${TS}.sql.gz

CONTAINER=$(docker ps --format '{{.Names}}' | grep -E 'argfy.*postgres' | head -1)
if [[ -z "$CONTAINER" ]]; then
    echo "No postgres container found"
    exit 1
fi

docker exec "$CONTAINER" pg_dump -U argfy -d argfy | gzip > "$OUT"
find /backups/postgres -name "argfy_*.sql.gz" -mtime +7 -delete

echo "[$(date -u +%FT%TZ)] Backup OK: $OUT ($(du -h "$OUT" | cut -f1))"
