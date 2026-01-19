#!/bin/bash
# Deploy BentoML service to BentoCloud
# Run: chmod +x scripts/deploy_bento.sh && ./scripts/deploy_bento.sh

set -e

echo "🚀 Deploying BentoML Service to BentoCloud..."

# Navigate to bentoml_service directory
cd "$(dirname "$0")/../bentoml_service"

# Check if logged in
echo "📋 Checking BentoCloud login..."
bentoml cloud current-context || {
    echo "❌ Not logged in. Please run: bentoml cloud login"
    exit 1
}

# Build the Bento
echo "📦 Building Bento..."
bentoml build

# Get the latest bento tag
BENTO_TAG=$(bentoml list -o json | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['tag'] if data else '')")

if [ -z "$BENTO_TAG" ]; then
    echo "❌ No Bento found. Build may have failed."
    exit 1
fi

echo "✅ Built: $BENTO_TAG"

# Push to BentoCloud
echo "☁️ Pushing to BentoCloud..."
bentoml push "$BENTO_TAG"

# Deploy
echo "🚀 Deploying..."
bentoml deployment create "$BENTO_TAG" --name movie-recommender || {
    echo "ℹ️ Deployment may already exist. Updating..."
    bentoml deployment update movie-recommender --bento "$BENTO_TAG"
}

echo ""
echo "🎉 Deployment complete!"
echo "📍 Check your deployment at: https://cloud.bentoml.com"
echo ""
echo "After deployment, get your endpoint URL and set it in Render:"
echo "  BENTOML_ENDPOINT=https://movie-recommender-xxxxx.mt1.bentoml.ai"
