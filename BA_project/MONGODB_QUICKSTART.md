# MongoDB Migration - Quick Start

**⏱️ Setup time: 10 minutes**

---

## 🎯 What You Get

- ✅ **21,000+ real movies** with posters (vs 20 sample movies)
- ✅ **Fast database queries** (indexed, <10ms)
- ✅ **Production-ready** (concurrent writes, cloud-hosted)
- ✅ **User profiles** (auto-generated from logs)
- ✅ **Free tier** (MongoDB Atlas M0)

---

## 🚀 3-Step Setup

### 1️⃣ Create MongoDB Atlas (2 min)

```bash
# 1. Sign up: https://www.mongodb.com/cloud/atlas
# 2. Create FREE M0 cluster
# 3. Create database user (username + password)
# 4. Add IP: 0.0.0.0/0 (Network Access)
# 5. Load Sample Dataset (for 21,000+ movies!)
```

### 2️⃣ Get Connection String (1 min)

```bash
# In Atlas, click "Connect" → "Connect your application"
# Copy the connection string:

export MONGODB_URI="mongodb+srv://user:password@cluster.mongodb.net/ba_project"

# Or add to .env file:
echo 'MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ba_project' >> .env
```

### 3️⃣ Run Migration (2 min)

```bash
# Test connection first
python scripts/test_mongodb.py

# Migrate all data
python scripts/migrate_to_mongodb.py

# Clear and re-migrate (if needed)
python scripts/migrate_to_mongodb.py --clear
```

**Expected output:**
```
📤 Uploading CSV Logs
  📄 Reading impressions.csv..... ✅ 567 docs
  📄 Reading clicks.csv... ✅ 123 docs
  📄 Reading subscriptions.csv. ✅ 24 docs

👥 Extracting user profiles...
  ✅ Created 120 user profiles

🎬 Checking sample_mflix database...
  ✅ sample_mflix.movies: 21,349 movies
     • With posters: 8,147

✅ Migration completed successfully!
```

---

## ⚙️ Enable MongoDB in App

```bash
# Use MongoDB for logs
export USE_MONGODB_LOGGING=true

# Use MongoDB for movies (21,000+ with posters!)
export USE_MONGODB_MOVIES=true

# Start app
python app.py
```

**Look for these messages:**
```
[MongoDB] Connected: 21,349 movies available
[MongoDB] Loaded 500 movies
[MongoDB Logger] Ready (async writes)
```

---

## 🔍 Verify It Works

### Check Dashboard

```bash
# Visit: http://localhost:5000/dashboard
# You should see metrics from MongoDB
```

### Check Movies

```bash
# Visit: http://localhost:5000
# You should see REAL movie posters (not just 20 samples)
# Scroll down - there are 21,000+ movies available!
```

### Query MongoDB

```bash
# Install MongoDB Compass: https://www.mongodb.com/products/compass
# Or use Atlas web interface → Browse Collections
```

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| Connection failed | Check IP whitelist in Atlas (add 0.0.0.0/0) |
| No movies in sample_mflix | Load Sample Dataset in Atlas (takes 5-10 min) |
| App still uses CSV | Set `USE_MONGODB_LOGGING=true` and restart |
| Duplicate data | Run with `--clear` flag |

---

## 📊 What Gets Migrated?

```
CSV Files                    →  MongoDB Collections
─────────────────────────────────────────────────────
data/logs/impressions.csv   →  impressions (567 docs)
data/logs/clicks.csv        →  clicks (123 docs)
data/logs/subscriptions.csv →  subscriptions (24 docs)
data/logs/engagements.csv   →  engagements (...)
data/logs/performances.csv  →  performances (...)

Auto-generated:
  → users (120 profiles with metrics)

MongoDB Atlas Sample Dataset:
  → sample_mflix.movies (21,349 movies)
     • 8,147 with high-quality posters
     • IMDB ratings, genres, plots
     • Real data from Netflix/IMDb
```

---

## 💡 Pro Tips

### Backup First

```bash
cp -r data/logs data/logs_backup_$(date +%Y%m%d)
```

### Full .env File

```bash
# MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ba_project
USE_MONGODB_LOGGING=true
USE_MONGODB_MOVIES=true

# App
ENVIRONMENT=development
SECRET_KEY=your-secret-key

# Optional: Grafana Cloud
GRAFANA_CLOUD_URL=https://prometheus-*.grafana.net/api/prom/push
GRAFANA_CLOUD_USER=123456
GRAFANA_CLOUD_API_KEY=glc_xxxxx
```

### Check Data

```bash
# Count users
python -c "from utils.logger_service import get_db; print('Users:', get_db()['users'].count_documents({}))"

# Count impressions
python -c "from utils.logger_service import get_db; print('Impressions:', get_db()['impressions'].count_documents({}))"
```

### MongoDB Compass (Recommended)

Best way to explore your data visually:

```
1. Download: https://www.mongodb.com/products/compass
2. Connect: mongodb+srv://user:pass@cluster.mongodb.net/ba_project
3. Browse collections, run queries, export data
```

---

## 📚 Full Documentation

For detailed guide, see: **[docs/MONGODB_MIGRATION.md](docs/MONGODB_MIGRATION.md)**

---

## ✅ Success Checklist

- [ ] MongoDB Atlas cluster created (M0 FREE)
- [ ] Sample Dataset loaded (21,000+ movies)
- [ ] Connection string copied
- [ ] `test_mongodb.py` passes all tests
- [ ] Migration script completed successfully
- [ ] Environment variables set (`USE_MONGODB_*=true`)
- [ ] App starts with "[MongoDB]" messages
- [ ] Dashboard shows metrics
- [ ] Movies page shows real posters

---

## 🎉 Done!

You now have:
- ✅ Production-ready database
- ✅ 21,000+ real movies
- ✅ Fast queries (<10ms)
- ✅ User profiles with metrics
- ✅ Cloud-hosted (MongoDB Atlas)
- ✅ $0 cost (free tier)

**Next:** Deploy to production! See `DEPLOYMENT.md`

---

**Need help?** Run: `python scripts/test_mongodb.py`

*Last updated: 2026-01-19*
