# scripts/data-refresh.sh
#!/bin/bash
# Script para refrescar datos de demo

echo "🔄 Refreshing Argfy data..."

cd backend
source venv/bin/activate

# Refresh via API
curl -X POST http://localhost:8000/api/v1/indicators/refresh

# También regenerar datos históricos
python scripts/init_database.py --extend

echo "✅ Data refresh completed"

