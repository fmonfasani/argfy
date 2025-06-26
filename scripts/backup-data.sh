#!/bin/bash
# Script para hacer backup de los datos

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "í³¦ Creando backup en $BACKUP_DIR..."

# Backup de base de datos
if [ -f "backend/data/argentina.db" ]; then
    cp backend/data/argentina.db "$BACKUP_DIR/"
    echo "âœ… Base de datos respaldada"
fi

# Backup de logs
if [ -d "backend/logs" ]; then
    cp -r backend/logs "$BACKUP_DIR/"
    echo "âœ… Logs respaldados"
fi

# Backup de configuraciÃ³n
cp backend/.env "$BACKUP_DIR/" 2>/dev/null || true
cp frontend/.env.local "$BACKUP_DIR/" 2>/dev/null || true

echo "âœ… Backup completado en $BACKUP_DIR"
