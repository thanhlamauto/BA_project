# Final Deployment Guide - Render.com + MongoDB

**All-In-One Guide for Production Deployment**

---

## 🎯 Overview

Your app is now **production-ready** with two deployment options:

1. **CSV Backend** - Simple but data lost on restart
2. **MongoDB Backend** - Professional, persistent data ✅ **RECOMMENDED**

---

## 🚀 Recommended: MongoDB Production Setup

### Why MongoDB for Render.com?

| Feature | CSV | MongoDB |
|---------|-----|---------|
| Data persistence | ❌ Lost on restart | ✅ Permanent |
| Movies available | 120 | 21,349 |
| Dashboard data | Must regenerate | Always available |
| Production ready | No | Yes |
| Cost | Free | Free |

---

## 📋 Complete Setup (15 minutes)

### Step 1: Create MongoDB Atlas (5 min)

1. **Sign up:** https://www.mongodb.com/cloud/atlas
   - Use GitHub/Google login for faster signup

2. **Create FREE M0 Cluster:**
   - Click "Build a Database"
   - Choose "M0 FREE" tier
   - Select region (closest to Render server)
   - Cluster name: `ba-project-cluster`
   - Click "Create"

3. **Create Database User:**
   - Security → Database Access → Add New User
   - Username: `ba_demo_user`
   - Password: Click "Autogenerate Secure Password" (copy it!)
   - Role: "Atlas admin" or "Read and write to any database"
   - Click "Add User"

4. **Network Access:**
   - Security → Network Access → Add IP Address
   - Click "Allow Access from Anywhere"
   - This adds `0.0.0.0/0` (required for Render)
   - Click "Confirm"

5. **Load Sample Dataset (IMPORTANT!):**
   - Database → Clusters → Click `...` on your cluster
   - Select "Load Sample Dataset"
   - Wait 5-10 minutes (21,349 movies being loaded)
   - ✅ Verify: Should see 8 databases including `sample_mflix`

6. **Get Connection String:**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Driver: Python, Version: 3.12 or later
   - Copy connection string:
   ```
   mongodb+srv://ba_demo_user:<password>@ba-project-cluster.xxxxx.mongodb.net/
   ```
   - Replace `<password>` with the password you copied in step 3

---

### Step 2: Configure Render.com (3 min)

1. **Go to Render Dashboard:**
   - Find your service (ba-movie-recommender)
   - Click on service name

2. **Set Environment Variables:**
   - Click "Environment" tab (left sidebar)
   - Click "Add Environment Variable"

**Add these 3 variables:**

```bash
# Variable 1
Key: MONGODB_URI
Value: mongodb+srv://ba_demo_user:YOUR_PASSWORD@ba-project-cluster.xxxxx.mongodb.net/ba_project

# Variable 2
Key: USE_MONGODB_LOGGING
Value: true

# Variable 3
Key: USE_MONGODB_MOVIES
Value: true
```

3. **Save Changes:**
   - Click "Save Changes" button
   - Render will automatically restart your app (2-3 min)

---

### Step 3: Deploy Latest Code (2 min)

```bash
# Commit all changes
git add .
git commit -m "Add MongoDB support with admin API"
git push origin main
```

Render will auto-deploy (wait 3-5 minutes)

---

### Step 4: Verify MongoDB Connection (1 min)

1. **Check Render Logs:**
   - Render Dashboard → Your Service → Logs tab
   - Look for these messages:
   ```
   [MongoDB] Connected successfully
   [MongoDB] sample_mflix: 21,349 movies available
   [MongoDB Logger] Service started (MongoDB backend)
   ```

2. **If you see errors:**
   - Double-check MONGODB_URI (no typos)
   - Verify Network Access allows `0.0.0.0/0`
   - Check password doesn't have special chars like `@`, `#`, `$`

---

### Step 5: Generate Demo Data (2 min)

**Method A: Using curl (Fastest)**

```bash
# Replace YOUR-APP with your Render URL
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 100, "secret": "demo_secret_2024"}'
```

**Expected Response:**
```json
{
  "success": true,
  "backend": "MongoDB",
  "message": "Generated demo data for 100 users",
  "stats": {
    "control": {
      "users": 49,
      "impressions": 162,
      "clicks": 80,
      "subscriptions": 8,
      "ctr": 49.38,
      "cvr": 10.0
    },
    "treatment": {
      "users": 51,
      "impressions": 171,
      "clicks": 72,
      "subscriptions": 12,
      "ctr": 42.11,
      "cvr": 16.67
    }
  }
}
```

**Method B: Using Postman/Browser Extension**

- URL: `https://YOUR-APP.onrender.com/admin/generate-demo-data`
- Method: POST
- Headers: `Content-Type: application/json`
- Body:
```json
{
  "num_users": 100,
  "secret": "demo_secret_2024"
}
```

---

### Step 6: Verify Dashboard (1 min)

1. **Visit Dashboard:**
   ```
   https://YOUR-APP.onrender.com/dashboard
   ```

2. **Expected Results:**
   - ✅ Control: 49 users (49%)
   - ✅ Treatment: 51 users (51%)
   - ✅ Total Impressions: 300+
   - ✅ Total Clicks: 150+
   - ✅ Total Subscriptions: 20+
   - ✅ CTR: 40-50%
   - ✅ CVR: 10-20%
   - ✅ **No "Sample Ratio Mismatch" warning!**

---

### Step 7: Verify in MongoDB Atlas (1 min)

1. **Go to MongoDB Atlas → Browse Collections**
2. Select your cluster → `ba_project` database
3. **You should see:**
   - `impressions` - 300+ documents
   - `clicks` - 150+ documents
   - `subscriptions` - 20+ documents
   - `engagements` - 150+ documents
   - `users` - 100+ documents

4. **Check sample_mflix:**
   - Switch to `sample_mflix` database
   - Open `movies` collection
   - Should have 21,349 documents ✅

---

## ✅ Verification Checklist

- [ ] MongoDB Atlas cluster created (M0 FREE)
- [ ] Sample dataset loaded (21,349 movies)
- [ ] Connection string obtained
- [ ] Environment variables set in Render
- [ ] Code pushed to GitHub
- [ ] Render deployed successfully
- [ ] Logs show "[MongoDB] Connected"
- [ ] Admin API generated 100 users
- [ ] Dashboard shows 50/50 split
- [ ] No Sample Ratio Mismatch warning
- [ ] MongoDB Atlas shows data in collections

---

## 🎉 Success Criteria

Your app is production-ready when:

✅ **Dashboard shows:**
- Control: 45-55% of users
- Treatment: 45-55% of users
- Realistic CTR/CVR metrics
- No warnings

✅ **User experience:**
- Can login with random user
- Gets assigned to variant
- Sees 24 recommendations (real movies!)
- Can rate movies
- Recommendations update with personalization
- Can subscribe

✅ **Data persistence:**
- Dashboard still shows data after app restart
- No need to regenerate data
- Survives sleep/wake cycles

---

## 🔐 Security: Change Admin Secret (Optional but Recommended)

### Generate Secure Secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Example output: `a7f3c9e2b4d8f1a3c6e9...`

### Set in Render:

1. Render Dashboard → Environment
2. Add variable:
   ```
   Key: ADMIN_SECRET
   Value: a7f3c9e2b4d8f1a3c6e9...
   ```
3. Save Changes

### Use in API calls:

```bash
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 100, "secret": "a7f3c9e2b4d8f1a3c6e9..."}'
```

---

## 🐛 Troubleshooting

### Dashboard Still Shows 0 Users

**Check:**
1. MongoDB connection logs (should see "Connected")
2. Run generate-demo-data API again
3. Check MongoDB Atlas → browse collections (data there?)

### "Sample Ratio Mismatch" Still Appears

**Fix:**
1. Clear data:
```bash
curl -X POST https://YOUR-APP.onrender.com/admin/clear-demo-data \
  -H "Content-Type: application/json" \
  -d '{"secret": "demo_secret_2024"}'
```

2. Regenerate with more users:
```bash
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 200, "secret": "demo_secret_2024"}'
```

### MongoDB Connection Failed

**Error:** `ServerSelectionTimeoutError`

**Fix:**
1. MongoDB Atlas → Network Access
2. Ensure `0.0.0.0/0` is listed
3. Check connection string (no typos)
4. Verify password is correct

### No Movies After Rating

**Check:**
1. `USE_MONGODB_MOVIES=true` in Render environment
2. sample_mflix loaded (21,349 movies)
3. Restart app after setting variable

---

## 🎯 Admin API Commands

```bash
# Set your URL
export APP_URL="https://YOUR-APP.onrender.com"
export SECRET="demo_secret_2024"

# Generate 100 users
curl -X POST $APP_URL/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d "{\"num_users\": 100, \"secret\": \"$SECRET\"}"

# Check stats
curl "$APP_URL/admin/stats?secret=$SECRET"

# Clear all data
curl -X POST $APP_URL/admin/clear-demo-data \
  -H "Content-Type: application/json" \
  -d "{\"secret\": \"$SECRET\"}"
```

---

## 📊 What You've Built

### Technical Stack:
- **Frontend:** HTML/CSS/JavaScript (Netflix-inspired UI)
- **Backend:** Flask (Python)
- **Database:** MongoDB Atlas (21K+ movies)
- **Deployment:** Render.com (auto-deploy from GitHub)
- **A/B Testing:** Consistent hashing (50/50 split)
- **Algorithms:** Matrix Factorization vs LightGCN
- **Monitoring:** Dashboard with real-time metrics

### Features:
- ✅ User authentication with auto-generated IDs
- ✅ A/B testing with 50/50 split
- ✅ 21,000+ real movies with posters
- ✅ Personalized recommendations
- ✅ Movie rating system
- ✅ Premium subscription
- ✅ Analytics dashboard
- ✅ Sample Ratio Mismatch detection
- ✅ Admin API for data management

---

## 🎓 Portfolio Value

**Perfect for showcasing:**

1. **Full-Stack Development**
   - Frontend: Netflix-inspired UI
   - Backend: RESTful API
   - Database: MongoDB (NoSQL)

2. **Machine Learning**
   - Recommender systems (Matrix Factorization, LightGCN)
   - Personalization algorithms
   - A/B testing methodology

3. **Production Engineering**
   - Cloud deployment (Render + MongoDB Atlas)
   - Environment configuration
   - Persistent storage
   - API design

4. **Data Science**
   - A/B test design
   - Statistical analysis (CTR, CVR, SRM)
   - Metrics dashboard
   - Consistent hashing

---

## 📱 Share Your Work

**Your Live URLs:**
- **App:** `https://YOUR-APP.onrender.com`
- **Dashboard:** `https://YOUR-APP.onrender.com/dashboard`

**Add to:**
- LinkedIn portfolio
- GitHub README
- Resume projects section
- Interview discussions

**Screenshots to take:**
- Homepage with 21K+ movies
- Dashboard showing A/B metrics
- Personalized recommendations after rating
- MongoDB Atlas collections

---

## 📚 Complete Documentation

| File | Purpose |
|------|---------|
| `MONGODB_PRODUCTION_GUIDE.md` | MongoDB setup (detailed) |
| `BACKEND_COMPARISON.md` | CSV vs MongoDB comparison |
| `AB_TESTING_GUIDE.md` | A/B testing explained |
| `DEPLOY_CHECKLIST.md` | Deployment steps |
| `PRODUCTION_SETUP.md` | Admin API guide |
| `setup_mongodb_production.sh` | Automated local setup |

---

## 🎉 Congratulations!

You now have a **production-grade** movie recommendation system with:

✅ Persistent MongoDB storage  
✅ 21,000+ real movies  
✅ Professional A/B testing  
✅ Balanced metrics (50/50 split)  
✅ Live deployment on Render  
✅ Portfolio-ready quality  

**Total Cost: $0/month** 💰

---

*Last updated: 2026-01-19*  
*Render.com + MongoDB Atlas | Production Ready | Portfolio Quality*
