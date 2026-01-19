#!/bin/bash

# MongoDB Production Setup Script
# Tests MongoDB connection and generates demo data

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "MongoDB Production Setup"
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo ""
    echo "Creating .env template..."
    cat > .env << 'EOF'
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/ba_project
USE_MONGODB_LOGGING=true
USE_MONGODB_MOVIES=true

# Admin Secret (change in production!)
ADMIN_SECRET=demo_secret_2024

# Optional: Grafana Cloud
GRAFANA_CLOUD_URL=
GRAFANA_CLOUD_USER=
GRAFANA_CLOUD_API_KEY=
EOF
    echo -e "${GREEN}✓ Created .env template${NC}"
    echo ""
    echo -e "${YELLOW}Please edit .env file and add your MongoDB connection string!${NC}"
    echo "Then run this script again."
    exit 1
fi

# Load environment variables
source .env

# Check MongoDB URI
if [ -z "$MONGODB_URI" ] || [[ "$MONGODB_URI" == *"xxxxx"* ]]; then
    echo -e "${RED}✗ MongoDB URI not configured in .env${NC}"
    echo ""
    echo "Please set MONGODB_URI in .env file:"
    echo "  MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ba_project"
    exit 1
fi

echo -e "\n${BLUE}Step 1: Testing MongoDB Connection${NC}"
python scripts/test_mongodb.py

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ MongoDB connection failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check MongoDB Atlas → Network Access → Add 0.0.0.0/0"
    echo "  2. Verify connection string is correct"
    echo "  3. Check username/password don't have special chars"
    exit 1
fi

echo -e "\n${BLUE}Step 2: Generating Demo Data (100 users)${NC}"
python scripts/generate_demo_data.py --users 100

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to generate demo data${NC}"
    exit 1
fi

echo -e "\n${BLUE}Step 3: Migrating to MongoDB${NC}"
python scripts/migrate_to_mongodb.py

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Migration failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ MongoDB Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${BLUE}What's Next:${NC}"
echo "  1. Test locally: python app.py"
echo "  2. Visit: http://localhost:5000/dashboard"
echo "  3. Verify dashboard shows 100 users (50/50 split)"
echo ""
echo "  4. Deploy to Render:"
echo "     - Set environment variables in Render"
echo "     - Push code: git push origin main"
echo "     - Generate data via API (see MONGODB_PRODUCTION_GUIDE.md)"

echo -e "\n${BLUE}MongoDB Collections Created:${NC}"
echo "  ✅ impressions (300+ events)"
echo "  ✅ clicks (150+ events)"
echo "  ✅ subscriptions (20+ events)"
echo "  ✅ engagements (150+ events)"
echo "  ✅ users (100 profiles)"

echo -e "\n${BLUE}Real Movies Available:${NC}"
if [ "$USE_MONGODB_MOVIES" = "true" ]; then
    echo "  ✅ Using sample_mflix: 21,349 movies"
else
    echo "  ⚠️  Using local sample: 120 movies"
    echo "     To use 21K+ real movies, set: USE_MONGODB_MOVIES=true"
fi

echo -e "\n${YELLOW}Remember:${NC} Data is now persistent in MongoDB Atlas!"
echo "It will NOT be deleted on app restart 🎉"
