#!/bin/bash
# Script de health check rápido

echo "��� Argfy Health Check"
echo "===================="

# Check backend
echo -n "Backend API: "
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✅ UP"
else
    echo "❌ DOWN"
fi

# Check frontend
echo -n "Frontend: "
if curl -f -s http://localhost:3000 > /dev/null; then
    echo "✅ UP"
else
    echo "❌ DOWN"
fi

# Check database
echo -n "Database: "
if [ -f "backend/data/argentina.db" ]; then
    echo "✅ EXISTS"
else
    echo "❌ MISSING"
fi

# Check API endpoints
echo -n "API Endpoints: "
if curl -f -s http://localhost:8000/api/v1/indicators/current > /dev/null; then
    echo "✅ WORKING"
else
    echo "❌ FAILING"
fi
