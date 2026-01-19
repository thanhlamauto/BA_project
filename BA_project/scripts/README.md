# Scripts Directory

Utility scripts for testing and deployment.

---

## 📁 Available Scripts

### 🔍 Testing Scripts

#### `test_mongodb.py`
Test MongoDB Atlas connection and verify database operations.

```bash
# Setup
export MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/ba_project"

# Run test
python scripts/test_mongodb.py
```

**Tests:**
- ✓ Connection to MongoDB
- ✓ Database read/write operations
- ✓ Collections accessible
- ✓ Metrics calculation from logs

---

#### `test_grafana.py`
Test Grafana Cloud connection and metrics push.

```bash
# Setup
export GRAFANA_CLOUD_URL="https://prometheus-prod-*.grafana.net/api/prom/push"
export GRAFANA_CLOUD_USER="123456"
export GRAFANA_CLOUD_API_KEY="glc_xxxxx..."

# Run test
python scripts/test_grafana.py
```

**Tests:**
- ✓ Environment variables configured
- ✓ Connection to Grafana Cloud
- ✓ Metrics module working
- ✓ Full metrics push successful

**Expected output:**
```
Testing Grafana Cloud Configuration
✓ GRAFANA_CLOUD_URL: https://prometheus-prod...
✓ GRAFANA_CLOUD_USER: 123456
✓ GRAFANA_CLOUD_API_KEY: glc_ey...xxxxx

Testing Connection
✓ Successfully pushed test metrics!

Testing Metrics Module
✓ Successfully imported metrics modules
✓ Grafana Cloud is configured
✓ Found metrics for 2 variants
✓ Formatted 24 lines of metrics

Testing Full Metrics Push
✓ Successfully pushed metrics!

Test Summary
✓ PASS  Configuration
✓ PASS  Connection
✓ PASS  Metrics Module
✓ PASS  Full Metrics Push

✓ All tests passed (4/4)
🎉 Success! Your Grafana Cloud setup is working perfectly.
```

---

### 🚀 Deployment Scripts

#### `deploy_bento.sh`
Deploy recommender model to BentoCloud.

```bash
bash scripts/deploy_bento.sh
```

**Steps:**
1. Builds BentoML service
2. Pushes to BentoCloud
3. Creates/updates deployment
4. Returns endpoint URL

---

#### `migrate_to_mongodb.py`
Migrate existing CSV logs to MongoDB.

```bash
# Setup MongoDB first
export MONGODB_URI="mongodb+srv://..."
export USE_MONGODB_LOGGING=true

# Run migration
python scripts/migrate_to_mongodb.py
```

**What it does:**
- Reads CSV files from `data/logs/`
- Converts to MongoDB documents
- Uploads to appropriate collections
- Verifies data integrity

---

## 🔧 Prerequisites

### For all scripts:
```bash
pip install -r requirements.txt
```

### For MongoDB tests:
- MongoDB Atlas account
- Connection string with read/write permissions

### For Grafana tests:
- Grafana Cloud account (free)
- Prometheus Remote Write credentials

### For BentoML deployment:
- BentoCloud account
- Logged in: `bentoml cloud login`

---

## 📚 Related Documentation

| Script | Documentation |
|--------|---------------|
| `test_mongodb.py` | `DEPLOYMENT.md` - Step 1 |
| `test_grafana.py` | `docs/GRAFANA_SETUP.md` |
| `deploy_bento.sh` | `DEPLOYMENT.md` - Step 2 |
| `migrate_to_mongodb.py` | `UPGRADE_SUMMARY.md` |

---

## 🐛 Troubleshooting

### Script not executable
```bash
chmod +x scripts/*.py
chmod +x scripts/*.sh
```

### Module import errors
```bash
# Make sure you're in the BA_project directory
cd BA_project
python scripts/test_grafana.py
```

### MongoDB connection fails
```bash
# Test with MongoDB shell first
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/ba_project"

# Check IP whitelist in MongoDB Atlas
# Add 0.0.0.0/0 for allow all
```

### Grafana connection fails
```bash
# Verify credentials
echo $GRAFANA_CLOUD_URL
echo $GRAFANA_CLOUD_USER
echo $GRAFANA_CLOUD_API_KEY

# Test with curl
curl -i -X POST "$GRAFANA_CLOUD_URL" \
  -u "$GRAFANA_CLOUD_USER:$GRAFANA_CLOUD_API_KEY" \
  -H "Content-Type: text/plain" \
  -d "test_metric 1"
```

---

## 💡 Pro Tips

### Run all tests at once
```bash
#!/bin/bash
echo "Testing MongoDB..."
python scripts/test_mongodb.py

echo -e "\nTesting Grafana..."
python scripts/test_grafana.py

echo -e "\nAll tests complete!"
```

### Use .env file for credentials
```bash
# Create .env file
cat > .env << 'EOF'
MONGODB_URI=mongodb+srv://...
GRAFANA_CLOUD_URL=https://...
GRAFANA_CLOUD_USER=123456
GRAFANA_CLOUD_API_KEY=glc_...
EOF

# Scripts will automatically load from .env
python scripts/test_grafana.py
```

### Automate testing in CI/CD
```yaml
# .github/workflows/test.yml
- name: Test MongoDB
  run: python scripts/test_mongodb.py
  env:
    MONGODB_URI: ${{ secrets.MONGODB_URI }}

- name: Test Grafana
  run: python scripts/test_grafana.py
  env:
    GRAFANA_CLOUD_URL: ${{ secrets.GRAFANA_CLOUD_URL }}
    GRAFANA_CLOUD_USER: ${{ secrets.GRAFANA_CLOUD_USER }}
    GRAFANA_CLOUD_API_KEY: ${{ secrets.GRAFANA_CLOUD_API_KEY }}
```

---

## 🎯 Quick Reference

| Want to... | Run this |
|------------|----------|
| Test MongoDB works | `python scripts/test_mongodb.py` |
| Test Grafana works | `python scripts/test_grafana.py` |
| Deploy model | `bash scripts/deploy_bento.sh` |
| Migrate to MongoDB | `python scripts/migrate_to_mongodb.py` |
| Check all services | Run all test scripts |

---

**Need help?** Check the main documentation files in the repository root.
