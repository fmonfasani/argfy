#!/bin/bash
# health_check.sh - Verify all services are healthy after deploy
# Usage: ./health_check.sh https://your-domain.com https://api.your-domain.com

set -e

FRONTEND_URL="${1:-http://localhost:3000}"
BACKEND_URL="${2:-http://localhost:8000}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================="
echo " Argfy Health Check"
echo "========================================="
echo ""

PASS=0
FAIL=0
TOTAL=0

check() {
  local name="$1"
  local url="$2"
  local expected="$3"
  TOTAL=$((TOTAL + 1))

  echo -n "Checking $name... "
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")

  if [ "$status" = "$expected" ]; then
    echo -e "${GREEN}OK${NC} ($status)"
    PASS=$((PASS + 1))
  else
    echo -e "${RED}FAIL${NC} (expected $expected, got $status)"
    FAIL=$((FAIL + 1))
  fi
}

# Backend health checks
echo "--- Backend ($BACKEND_URL) ---"
check "Root endpoint" "$BACKEND_URL/" "200"
check "Health check" "$BACKEND_URL/health" "200"
check "Indicators current" "$BACKEND_URL/api/v1/indicators/current" "200"
check "Fundamentals screener" "$BACKEND_URL/api/v1/fundamentals/screener" "200"
check "Docs (Swagger)" "$BACKEND_URL/docs" "200"
echo ""

# Frontend health checks
echo "--- Frontend ($FRONTEND_URL) ---"
check "Home page" "$FRONTEND_URL" "200"
check "Screener page" "$FRONTEND_URL/cedears" "200"
check "Pricing page" "$FRONTEND_URL/pricing" "200"
check "API docs page" "$FRONTEND_URL/api" "200"
check "Login page" "$FRONTEND_URL/auth/login" "200"
echo ""

# Response time checks
echo "--- Response Times ---"
for url in "$BACKEND_URL/health" "$FRONTEND_URL"; do
  time_ms=$(curl -s -o /dev/null -w "%{time_total}" --max-time 10 "$url" 2>/dev/null || echo "0")
  time_ms_scaled=$(echo "$time_ms * 1000" | bc 2>/dev/null || echo "0")
  echo -n "  $url: "
  if [ "$(echo "$time_ms_scaled" | cut -d'.' -f1)" -gt 2000 ] 2>/dev/null; then
    echo -e "${RED}${time_ms_scaled}ms (slow)${NC}"
  else
    echo -e "${GREEN}${time_ms_scaled}ms${NC}"
  fi
done
echo ""

# Summary
echo "========================================="
if [ $FAIL -eq 0 ]; then
  echo -e " ${GREEN}ALL CHECKS PASSED${NC} ($PASS/$TOTAL)"
  exit 0
else
  echo -e " ${RED}$FAIL CHECKS FAILED${NC} ($PASS/$TOTAL passed)"
  exit 1
fi
