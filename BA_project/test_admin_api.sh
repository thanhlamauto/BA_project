#!/bin/bash

# Test Admin API endpoints
# Usage: bash test_admin_api.sh

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=================================="
echo "Testing Admin API Endpoints"
echo "=================================="

# Base URL (change for production)
BASE_URL="${1:-http://localhost:5000}"
SECRET="demo_secret_2024"

echo -e "\n${BLUE}Base URL:${NC} $BASE_URL"
echo -e "${BLUE}Secret:${NC} $SECRET"

# Test 1: Generate demo data
echo -e "\n${BLUE}Test 1: Generate Demo Data (50 users)${NC}"
response=$(curl -s -X POST "$BASE_URL/admin/generate-demo-data" \
  -H "Content-Type: application/json" \
  -d "{\"num_users\": 50, \"secret\": \"$SECRET\"}")

echo "$response" | python -m json.tool

if echo "$response" | grep -q '"success": true'; then
    echo -e "${GREEN}✓ Demo data generated successfully${NC}"
else
    echo -e "${RED}✗ Failed to generate demo data${NC}"
fi

# Test 2: Check stats
echo -e "\n${BLUE}Test 2: Check Stats${NC}"
response=$(curl -s "$BASE_URL/admin/stats?secret=$SECRET")
echo "$response" | python -m json.tool

if echo "$response" | grep -q '"success": true'; then
    echo -e "${GREEN}✓ Stats retrieved successfully${NC}"
else
    echo -e "${RED}✗ Failed to retrieve stats${NC}"
fi

# Test 3: Test authentication (should fail with wrong secret)
echo -e "\n${BLUE}Test 3: Test Authentication (wrong secret)${NC}"
response=$(curl -s -X POST "$BASE_URL/admin/generate-demo-data" \
  -H "Content-Type: application/json" \
  -d '{"num_users": 10, "secret": "wrong_secret"}')

if echo "$response" | grep -q '"error": "Invalid secret key"'; then
    echo -e "${GREEN}✓ Authentication working correctly${NC}"
else
    echo -e "${RED}✗ Authentication failed${NC}"
fi

echo -e "\n${BLUE}Test 4: View Dashboard${NC}"
echo "Open: $BASE_URL/dashboard"

echo -e "\n=================================="
echo -e "${GREEN}All tests completed!${NC}"
echo "=================================="
