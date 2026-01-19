# MongoDB Migration Guide

Complete guide to migrate your CSV logs to MongoDB for better performance and scalability.

---

## 🎯 Why Migrate to MongoDB?

### Current Setup (CSV)
- ❌ Slow queries as data grows
- ❌ No concurrent writes (file locking)
- ❌ Limited to 20 sample movies
- ❌ Manual data analysis

### After Migration (MongoDB)
- ✅ Fast indexed queries
- ✅ Concurrent writes (production-ready)
- ✅ **21,000+ real movies with posters** (sample_mflix)
- ✅ Powerful aggregation queries
- ✅ User profiles with metrics
- ✅ Cloud-ready (MongoDB Atlas)

---

## 📋 Prerequisites

### 1. MongoDB Atlas Account (Free)

```bash
# Sign up at: https://www.mongodb.com/cloud/atlas
# Choose: M0 FREE tier (512MB, perfect for this project)
# Region: Choose closest to you
```

### 2. Get Connection String

```
In MongoDB Atlas:
1. Click "Connect" on your cluster
2. Choose "Connect your application"
3. Copy connection string:
   mongodb+srv://username:password@cluster.mongodb.net/ba_project
```

### 3. Install Sample Dataset (Important!)

This gives you **21,000+ real movies with posters**:

```
1. In Atlas, click "..." on your cluster
2. Select "Load Sample Dataset"
3. Wait 5-10 minutes for completion
4. Verify: You should see "sample_mflix" database with 21,000+ movies
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Set MongoDB URI

```bash
# Option A: Export environment variable
export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/ba_project"

# Option B: Add to .env file (recommended)
echo 'MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ba_project' >> .env
```

**⚠️ Replace:**
- `username` → your MongoDB user
- `password` → your password (URL-encoded if contains special chars)
- `cluster` → your cluster name

### Step 2: Test Connection

```bash
python scripts/test_mongodb.py
```

**Expected output:**
```
✅ Connected to MongoDB
✅ Can read from database
✅ Can write to database
✅ All tests passed
```

### Step 3: Run Migration

```bash
# First time migration
python scripts/migrate_to_mongodb.py

# Or clear existing data first
python scripts/migrate_to_mongodb.py --clear
```

**Expected output:**
```
========================================
MongoDB Migration Script
========================================

📤 Uploading CSV Logs
  📄 Reading impressions.csv..... ✅ 567 docs
  📄 Reading clicks.csv... ✅ 123 docs
  📄 Reading subscriptions.csv. ✅ 24 docs
  ...

👥 Extracting user profiles...
  ✅ Created 120 user profiles

📊 Creating indexes for performance...
  ✅ impressions: 3 indexes
  ✅ clicks: 3 indexes
  ...

🎬 Checking sample_mflix database...
  ✅ sample_mflix.movies: 21,349 movies
     • With posters: 8,147

  📽️  Sample movies:
     • The Shawshank Redemption (1994)
       Rating: 9.3/10 | Genres: Drama
       Poster: ✓

✅ Migration completed successfully!
```

---

## 📊 What Gets Migrated?

### 1. **Logs** (from CSV files)

| CSV File | MongoDB Collection | Description |
|----------|-------------------|-------------|
| `impressions.csv` | `impressions` | Recommendations shown to users |
| `clicks.csv` | `clicks` | User clicks on movies |
| `subscriptions.csv` | `subscriptions` | Subscription conversions |
| `conversions.csv` | `conversions` | General conversions |
| `engagements.csv` | `engagements` | User engagement events |
| `performances.csv` | `performances` | API performance metrics |

### 2. **User Profiles** (auto-generated)

The script analyzes your logs and creates user profiles:

```javascript
{
  user_id: "control_user_42",
  variant: "control",
  first_seen: ISODate("2026-01-15T10:30:00Z"),
  total_impressions: 150,
  total_clicks: 45,
  total_subscriptions: 1,
  ctr: 30.0,  // Click-through rate
  converted: true,
  created_at: ISODate("2026-01-19T...")
}
```

### 3. **Movies** (from sample_mflix - already in MongoDB)

You get access to 21,000+ real movies:

```javascript
{
  _id: ObjectId("..."),
  title: "Inception",
  year: 2010,
  genres: ["Action", "Mystery", "Sci-Fi"],
  poster: "https://...",  // Real movie poster URL
  plot: "A thief who steals...",
  imdb: {
    rating: 8.8,
    votes: 1234567
  },
  runtime: 148
}
```

---

## 🔧 Configuration

### Enable MongoDB in Your App

```bash
# Use MongoDB for logging instead of CSV
export USE_MONGODB_LOGGING=true

# Use MongoDB movies instead of sample data (21,000+ movies!)
export USE_MONGODB_MOVIES=true
```

### Full .env Example

```bash
# Application
ENVIRONMENT=development
SECRET_KEY=your-secret-key

# MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ba_project
USE_MONGODB_LOGGING=true
USE_MONGODB_MOVIES=true

# BentoCloud (optional)
BENTOML_ENDPOINT=http://localhost:3000

# Grafana Cloud (optional)
GRAFANA_CLOUD_URL=https://prometheus-prod-*.grafana.net/api/prom/push
GRAFANA_CLOUD_USER=123456
GRAFANA_CLOUD_API_KEY=glc_xxxxx
```

---

## 📈 Verify Migration

### 1. Check Collections in Atlas

```
1. Go to MongoDB Atlas
2. Click "Browse Collections"
3. Select your database (ba_project)
4. You should see:
   - impressions (567 documents)
   - clicks (123 documents)
   - subscriptions (24 documents)
   - users (120 documents)
   - etc.
```

### 2. Query Data

Using MongoDB Compass or Atlas:

```javascript
// Find all control users who converted
db.users.find({
  variant: "control",
  converted: true
})

// Get impressions for a specific user
db.impressions.find({
  user_id: "control_user_1"
}).sort({ timestamp: -1 })

// Find movies with rating > 8.0
db.movies.find({
  "imdb.rating": { $gt: 8.0 },
  "poster": { $exists: true }
}).limit(10)
```

### 3. Test App with MongoDB

```bash
# Start app with MongoDB enabled
export USE_MONGODB_LOGGING=true
export USE_MONGODB_MOVIES=true
python app.py
```

Visit http://localhost:5000 - you should see:
- **21,000+ movies** (if USE_MONGODB_MOVIES=true)
- Real movie posters from TMDB
- Fast page loads
- Dashboard shows correct metrics

---

## 🐛 Troubleshooting

### Connection Failed

**Error:** `ServerSelectionTimeoutError`

**Fix:**
1. Check MongoDB URI is correct
2. Verify network access in Atlas:
   - Security → Network Access
   - Add IP: `0.0.0.0/0` (or your IP)
3. Check username/password are correct

### No Data After Migration

**Problem:** Collections are empty

**Fix:**
```bash
# Check if CSV files exist
ls -lh data/logs/

# Run migration with verbose output
python scripts/migrate_to_mongodb.py --clear

# Verify in Atlas web interface
```

### Sample Dataset Not Loading

**Problem:** sample_mflix has 0 movies

**Fix:**
1. In Atlas, click "..." → "Load Sample Dataset"
2. Wait 5-10 minutes (it's ~400MB of data)
3. Verify:
   ```bash
   python scripts/test_mongodb.py
   ```

### Duplicate Data

**Problem:** Running migration multiple times creates duplicates

**Fix:**
```bash
# Clear and re-migrate
python scripts/migrate_to_mongodb.py --clear
```

### App Still Using CSV

**Problem:** App not using MongoDB after migration

**Fix:**
```bash
# Make sure environment variables are set
export USE_MONGODB_LOGGING=true
export USE_MONGODB_MOVIES=true

# Restart app
python app.py

# Check logs for "[MongoDB]" messages
```

---

## 💡 Pro Tips

### 1. Use MongoDB Compass

Download free GUI tool: https://www.mongodb.com/products/compass

```bash
# Connect with your URI
mongodb+srv://username:password@cluster.mongodb.net/ba_project
```

**Benefits:**
- Visual query builder
- Schema analysis
- Index management
- Data export/import

### 2. Index Optimization

The migration script creates indexes automatically, but you can add more:

```javascript
// Create compound index for faster queries
db.impressions.createIndex({ variant: 1, timestamp: -1, user_id: 1 })

// Check index usage
db.impressions.explain().find({ variant: "control" })
```

### 3. Backup Before Migration

```bash
# Backup CSV files
cp -r data/logs data/logs_backup_$(date +%Y%m%d)

# Or use mongodump after migration
mongodump --uri="mongodb+srv://..." --db=ba_project --out=backup/
```

### 4. Incremental Migration

If you have a lot of data:

```bash
# Migrate only specific collections
# Edit scripts/migrate_to_mongodb.py and comment out unwanted collections
```

### 5. Monitor Performance

```bash
# Check query performance in Atlas
# Performance → Query Performance tab

# Enable profiling for slow queries
db.setProfilingLevel(1, { slowms: 100 })
db.system.profile.find().sort({ ts: -1 }).limit(5)
```

---

## 📚 Next Steps

After successful migration:

1. **Test thoroughly**
   ```bash
   # Generate some traffic
   # Open http://localhost:5000
   # Click around, subscribe
   
   # Check dashboard
   # http://localhost:5000/dashboard
   ```

2. **Set up Grafana** (optional)
   ```bash
   python scripts/test_grafana.py
   # See: docs/GRAFANA_SETUP.md
   ```

3. **Deploy to production**
   ```bash
   # See: DEPLOYMENT.md
   # Render.com with MongoDB Atlas
   ```

4. **Explore MongoDB features**
   - Aggregation pipelines
   - Change streams (real-time updates)
   - Atlas Search (full-text search)
   - Charts (built-in dashboards)

---

## 🆘 Need Help?

### Resources

- **MongoDB Docs**: https://docs.mongodb.com
- **Atlas Tutorial**: https://docs.atlas.mongodb.com/tutorial/
- **Compass Guide**: https://docs.mongodb.com/compass/

### Quick Commands

```bash
# Test connection
python scripts/test_mongodb.py

# Re-migrate (clear first)
python scripts/migrate_to_mongodb.py --clear

# Check environment
env | grep MONGODB

# Verify data
python -c "from utils.logger_service import get_db; print('Users:', get_db()['users'].count_documents({}))"
```

---

## 🎓 Architecture Comparison

### Before (CSV)

```
Flask App
   │
   ├─→ Write to impressions.csv (locked during write)
   ├─→ Write to clicks.csv (locked during write)
   ├─→ Read 20 sample movies from memory
   └─→ Calculate metrics by parsing CSVs (slow)
```

### After (MongoDB)

```
Flask App
   │
   ├─→ Write to MongoDB (concurrent, fast)
   │      • impressions collection
   │      • clicks collection
   │      • subscriptions collection
   │
   ├─→ Read from sample_mflix (21,000+ movies)
   │      • Indexed queries (<10ms)
   │      • Real posters from TMDB
   │
   └─→ Calculate metrics with aggregation (instant)
        • Pre-computed user profiles
        • Indexed by variant, timestamp
```

**Result:** 10x faster, production-ready, scalable! 🚀

---

**Ready to migrate?** Run: `python scripts/migrate_to_mongodb.py`

*Last updated: 2026-01-19*
