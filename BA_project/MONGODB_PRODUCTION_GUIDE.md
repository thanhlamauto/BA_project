# MongoDB Production Setup - Complete Guide

**Best Solution for Render.com + Persistent Data**

---

## 🎯 Why MongoDB?

### CSV Files (Current):
- ❌ Deleted on every Render restart
- ❌ Must regenerate data via API
- ❌ Lost after 15min sleep
- ❌ Not scalable

### MongoDB Atlas (Recommended):
- ✅ **Persistent** - Data never lost
- ✅ **Free tier** - M0 cluster (512MB)
- ✅ **Cloud-hosted** - Accessible anywhere
- ✅ **Scalable** - Ready for production
- ✅ **21,000+ real movies** available

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Create MongoDB Atlas (5 min)

1. **Sign up:** https://www.mongodb.com/cloud/atlas
2. **Create FREE M0 cluster**
   - Choose region closest to you
   - Wait 3-5 minutes for creation
3. **Create database user:**
   - Username: `ba_demo_user`
   - Password: Generate strong password
   - Role: Read and write to any database
4. **Network Access:**
   - IP Access List → Add IP
   - Add: `0.0.0.0/0` (allow from anywhere)
5. **Load Sample Dataset (Important!):**
   - Click `...` on cluster → Load Sample Dataset
   - Wait 5-10 minutes
   - This gives you **21,000+ real movies** with posters!

### Step 2: Get Connection String

1. Click **"Connect"** on your cluster
2. Choose **"Connect your application"**
3. Copy connection string:
```
mongodb+srv://ba_demo_user:<password>@cluster0.xxxxx.mongodb.net/ba_project
```

4. **Replace** `<password>` with your actual password

### Step 3: Configure & Deploy

#### A. Set Environment Variables in Render

Go to Render Dashboard → Your Service → Environment:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb+srv://ba_demo_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/ba_project
USE_MONGODB_LOGGING=true
USE_MONGODB_MOVIES=true
```

Click **"Save Changes"** → Render will auto-restart

#### B. Generate Initial Data

**Option 1: Via Admin API (Easier)**
```bash
# After Render restarts with MongoDB config
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 100, "secret": "demo_secret_2024"}'
```

**Option 2: Via Migration Script (More Control)**
```bash
# In Render Shell (Dashboard → Shell tab)
cd /opt/render/project/src/BA_project
python scripts/migrate_to_mongodb.py
```

---

## 📊 What You Get

### With MongoDB Enabled:

```
MongoDB Atlas (Free Tier)
├── ba_project (your database)
│   ├── impressions (100+ docs)
│   ├── clicks (50+ docs)
│   ├── subscriptions (20+ docs)
│   ├── engagements (50+ docs)
│   ├── users (100+ profiles with metrics)
│   └── performances (API metrics)
│
└── sample_mflix (auto-loaded)
    └── movies (21,349 real movies!)
        ├── With IMDB ratings
        ├── With real posters
        ├── With genres, plot, runtime
        └── Ready to use
```

### Benefits:

1. **Persistent Data**
   - ✅ Never lost on restart
   - ✅ Survives deployments
   - ✅ Works after sleep/wake

2. **Better Movies**
   - ✅ 21,000+ real movies (vs 120 samples)
   - ✅ Real TMDB posters
   - ✅ Actual IMDB ratings
   - ✅ Better recommendations

3. **Production Ready**
   - ✅ Concurrent writes
   - ✅ Fast indexed queries
   - ✅ Cloud backup
   - ✅ $0 cost (free tier)

---

## 🔧 Local Testing First

Before deploying to production, test locally:

### 1. Create .env File

```bash
cd BA_project
cat > .env << 'EOF'
# MongoDB Atlas
MONGODB_URI=mongodb+srv://ba_demo_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/ba_project
USE_MONGODB_LOGGING=true
USE_MONGODB_MOVIES=true

# Optional: Admin secret
ADMIN_SECRET=demo_secret_2024
EOF
```

### 2. Test MongoDB Connection

```bash
python scripts/test_mongodb.py
```

**Expected output:**
```
✅ Connected to MongoDB Atlas
✅ Database read/write working
✅ sample_mflix available: 21,349 movies
✅ All tests passed (5/5)
```

### 3. Generate Local Demo Data

```bash
python scripts/generate_demo_data.py --users 100
```

### 4. Migrate to MongoDB

```bash
python scripts/migrate_to_mongodb.py
```

**Expected output:**
```
📤 Uploading CSV Logs
  ✅ impressions: 333 documents
  ✅ clicks: 152 documents
  ✅ subscriptions: 20 documents

👥 Extracting user profiles...
  ✅ Created 100 user profiles

🎬 Checking sample_mflix database...
  ✅ sample_mflix.movies: 21,349 movies

✅ Migration completed successfully!
```

### 5. Start App with MongoDB

```bash
python app.py
```

**Look for these messages:**
```
[MongoDB] Connected: 21,349 movies available
[MongoDB] Loaded 500 movies
[MongoDB Logger] Ready (async writes)
```

### 6. Test Dashboard

Visit: http://localhost:5000/dashboard

**Should show:**
- ✅ Control: ~50 users
- ✅ Treatment: ~50 users
- ✅ All metrics from MongoDB

---

## 🌐 Production Deployment

### Step 1: Update Render Environment

1. Go to **Render Dashboard** → Your Service
2. Click **"Environment"** tab
3. Add these variables:

```bash
MONGODB_URI=mongodb+srv://ba_demo_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/ba_project
USE_MONGODB_LOGGING=true
USE_MONGODB_MOVIES=true
```

4. Click **"Save Changes"**
5. Wait for auto-restart (2-3 minutes)

### Step 2: Verify MongoDB Connection

Check Render logs for:
```
[MongoDB] Connected: 21,349 movies available
[MongoDB Logger] Service started (MongoDB backend)
```

### Step 3: Migrate Data to Production MongoDB

**Method A: Admin API (Recommended)**

```bash
# Generate users directly to MongoDB
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 100, "secret": "demo_secret_2024"}'
```

**Method B: Render Shell**

```bash
# In Render Dashboard → Shell tab
cd /opt/render/project/src/BA_project
python scripts/generate_demo_data.py --users 100
python scripts/migrate_to_mongodb.py
```

### Step 4: Verify in MongoDB Atlas

1. Go to **MongoDB Atlas** → Browse Collections
2. Select your cluster → `ba_project` database
3. You should see:
   - `impressions` (300+ documents)
   - `clicks` (150+ documents)
   - `subscriptions` (20+ documents)
   - `users` (100+ documents)

### Step 5: Check Production Dashboard

Visit: `https://YOUR-APP.onrender.com/dashboard`

**Should show:**
- ✅ Control: ~50 users (49-51%)
- ✅ Treatment: ~50 users (49-51%)
- ✅ Realistic metrics
- ✅ No Sample Ratio Mismatch

---

## 🎬 Using Real Movies (21,000+)

With `USE_MONGODB_MOVIES=true`, your app now uses real Netflix/IMDb movies!

### Features:

1. **21,000+ Movies** (vs 120 samples)
2. **Real Data:**
   - IMDB ratings (1-10)
   - Genres (Action, Drama, Sci-Fi, etc.)
   - Release years (1900-2024)
   - Movie plots
   - Runtime

3. **Real Posters:**
   - High-quality images
   - From TMDB/IMDb
   - Professional quality

### Example Movie Data:

```javascript
{
  "_id": ObjectId("573a1390f29313caabcd4135"),
  "title": "Inception",
  "year": 2010,
  "genres": ["Action", "Mystery", "Sci-Fi", "Thriller"],
  "poster": "https://m.media-amazon.com/images/M/...",
  "plot": "A thief who steals corporate secrets...",
  "imdb": {
    "rating": 8.8,
    "votes": 1892352
  },
  "runtime": 148,
  "directors": ["Christopher Nolan"],
  "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", ...]
}
```

### User Experience:

- **Before:** 120 sample movies, repetitive
- **After:** 21,000+ unique movies, diverse genres
- **Recommendations:** Much better with real ratings
- **Demo Quality:** Professional, production-ready

---

## 🔄 Admin API Still Works with MongoDB

All admin endpoints work seamlessly with MongoDB:

```bash
# Generate data (writes to MongoDB)
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 50, "secret": "demo_secret_2024"}'

# Check stats (reads from MongoDB)
curl "https://YOUR-APP.onrender.com/admin/stats?secret=demo_secret_2024"

# Clear data (MongoDB collections)
curl -X POST https://YOUR-APP.onrender.com/admin/clear-demo-data \
  -H "Content-Type: application/json" \
  -d '{"secret": "demo_secret_2024"}'
```

---

## 📈 Performance Comparison

### CSV Files:
- Query time: 500ms (read entire file)
- Concurrent writes: ❌ (file locking)
- Scalability: Poor (>10k rows slow)

### MongoDB:
- Query time: <10ms (indexed)
- Concurrent writes: ✅ (unlimited)
- Scalability: Excellent (millions of docs)

---

## 💰 Cost Breakdown

### Free Tier (Perfect for Portfolio):

| Service | Free Tier | What You Get |
|---------|-----------|--------------|
| **MongoDB Atlas M0** | FREE | 512MB storage, 100 connections |
| **Render Web Service** | FREE | 750 hours/month |
| **Total** | **$0/month** | Full production stack! |

### Data You Can Store (M0 - 512MB):

- ✅ 21,000+ movies (sample_mflix)
- ✅ 10,000+ users with profiles
- ✅ 50,000+ impressions
- ✅ 25,000+ clicks
- ✅ 5,000+ subscriptions
- ✅ More than enough for demo!

---

## 🐛 Troubleshooting

### Problem: Connection Failed

**Error:** `ServerSelectionTimeoutError`

**Fix:**
1. Check MongoDB Atlas → Network Access
2. Ensure `0.0.0.0/0` is added (allow all IPs)
3. Verify connection string is correct
4. Check password doesn't have special chars (URL encode if needed)

### Problem: sample_mflix Not Available

**Error:** `sample_mflix has 0 movies`

**Fix:**
1. In Atlas, click `...` on cluster
2. Select "Load Sample Dataset"
3. Wait 5-10 minutes for completion
4. Verify: should see 8 databases including `sample_mflix`

### Problem: Data Still Disappears

**Check:**
```bash
# Verify MongoDB is enabled in Render
env | grep MONGODB_URI
env | grep USE_MONGODB_LOGGING

# Should show:
# USE_MONGODB_LOGGING=true
# MONGODB_URI=mongodb+srv://...
```

### Problem: App Logs Show "CSV backend"

**Fix:** MongoDB not enabled properly

```bash
# In Render environment, set:
USE_MONGODB_LOGGING=true

# Restart app
```

---

## ✅ Verification Checklist

After MongoDB setup:

- [ ] MongoDB Atlas cluster created (M0 FREE)
- [ ] Sample dataset loaded (21,349 movies)
- [ ] Connection string obtained
- [ ] Environment variables set in Render
- [ ] App logs show "[MongoDB] Connected"
- [ ] Admin API generated demo data
- [ ] Dashboard shows 100 users (50/50 split)
- [ ] MongoDB Atlas shows data in collections
- [ ] App uses real movies (21,000+)
- [ ] Data persists after restart
- [ ] No Sample Ratio Mismatch

---

## 🎯 Quick Commands

```bash
# Set variables
export RENDER_URL="https://YOUR-APP.onrender.com"
export SECRET="demo_secret_2024"

# Test MongoDB connection (local)
python scripts/test_mongodb.py

# Generate and migrate data (local)
python scripts/generate_demo_data.py --users 100
python scripts/migrate_to_mongodb.py

# Generate data on production
curl -X POST $RENDER_URL/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d "{\"num_users\": 100, \"secret\": \"$SECRET\"}"

# Check production dashboard
open $RENDER_URL/dashboard
```

---

## 🎉 Success!

**Your production app now has:**

✅ **Persistent MongoDB storage** (data never lost)  
✅ **21,000+ real movies** with posters  
✅ **100 demo users** with realistic metrics  
✅ **50/50 A/B split** (perfect distribution)  
✅ **Professional quality** (production-ready)  
✅ **$0 cost** (all free tier)  

**Live URL:** `https://YOUR-APP.onrender.com`

Perfect for:
- 🎯 Portfolio demonstrations
- 🎯 Technical interviews
- 🎯 System design showcases
- 🎯 Production deployment examples

---

## 📚 Related Documentation

- `MONGODB_QUICKSTART.md` - Quick setup guide
- `scripts/test_mongodb.py` - Test connection
- `scripts/migrate_to_mongodb.py` - Migration tool
- `PRODUCTION_SETUP.md` - Alternative methods

---

*Last updated: 2026-01-19*  
*MongoDB Atlas M0 | 21,349 Movies | Persistent Storage | Production Ready*
