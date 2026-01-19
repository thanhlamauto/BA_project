# Deployment Checklist - Render.com

**Fix Sample Ratio Mismatch & Setup Production Data**

---

## 🎯 Issue: Dashboard Empty on Production

After deploying to Render, dashboard shows:
- ❌ 0 users or very few users
- ❌ Sample Ratio Mismatch (100/0 or imbalanced split)
- ❌ No metrics

**Root Cause:** CSV files in `.gitignore` → not deployed to production

---

## ✅ Solution Overview

**3 Steps:**
1. Deploy code with admin API endpoints
2. Generate demo data via API call
3. Verify dashboard shows balanced metrics

---

## 📋 Step-by-Step Guide

### Step 1: Deploy Latest Code

```bash
# Commit all changes
git add .
git commit -m "Add admin API for demo data generation"
git push origin main
```

**Render auto-deploys** (wait 3-5 minutes)

### Step 2: Generate Demo Data

**Option A: Using curl (Fastest)**

```bash
# Replace YOUR-APP with your Render URL
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 100, "secret": "demo_secret_2024"}'
```

**Option B: Using Browser/Postman**

- **URL:** `https://YOUR-APP.onrender.com/admin/generate-demo-data`
- **Method:** POST
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "num_users": 100,
  "secret": "demo_secret_2024"
}
```

### Step 3: Verify Dashboard

Visit: `https://YOUR-APP.onrender.com/dashboard`

**Expected:**
- ✅ Control: ~50 users (49-51%)
- ✅ Treatment: ~50 users (49-51%)
- ✅ CTR and CVR metrics displayed
- ✅ No "Sample Ratio Mismatch" warning

---

## 🔐 Security: Change Admin Secret (Recommended)

### For Production:

1. **Generate secure secret:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Example output: a7f3c9e2b4d8...
```

2. **Set in Render:**
   - Go to Render Dashboard → Your Service
   - Environment tab
   - Add variable:
     ```
     ADMIN_SECRET=a7f3c9e2b4d8...
     ```
   - Save Changes

3. **Use new secret in API calls:**
```bash
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 100, "secret": "a7f3c9e2b4d8..."}'
```

---

## 📊 Expected API Response

```json
{
  "success": true,
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
  },
  "files_written": {
    "impressions": 333,
    "clicks": 152,
    "subscriptions": 20,
    "engagements": 152
  }
}
```

---

## 🔄 Important: Data Persistence

### ⚠️ Render Free Tier = Ephemeral Storage

**Data is deleted when:**
- App restarts
- You redeploy
- Server goes to sleep (15min inactivity)

### Solutions:

**Option 1: Regenerate After Each Deploy**

Add to `render-build.sh`:
```bash
#!/bin/bash
pip install -r requirements.txt

# Auto-generate demo data
python scripts/generate_demo_data.py --users 100
```

Update `render.yaml`:
```yaml
buildCommand: "bash render-build.sh"
```

**Option 2: Use MongoDB Atlas (Recommended)**

```bash
# In Render environment
USE_MONGODB_LOGGING=true
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ba_project

# Then run migration (one time)
python scripts/migrate_to_mongodb.py
```

**Option 3: Manual Regeneration**

After each restart/redeploy, run:
```bash
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 100, "secret": "demo_secret_2024"}'
```

---

## 🛠️ Additional Admin Commands

### Check Current Stats

```bash
curl "https://YOUR-APP.onrender.com/admin/stats?secret=demo_secret_2024"
```

### Clear All Data

```bash
curl -X POST https://YOUR-APP.onrender.com/admin/clear-demo-data \
  -H "Content-Type: application/json" \
  -d '{"secret": "demo_secret_2024"}'
```

### Regenerate with Different Size

```bash
# 200 users
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 200, "secret": "demo_secret_2024"}'
```

---

## 🐛 Troubleshooting

### Problem: 403 Forbidden Error

```json
{"error": "Invalid secret key"}
```

**Fix:** Check `ADMIN_SECRET` environment variable in Render matches your API call

### Problem: Still Shows 0 Users After Generation

**Debug steps:**

1. **Check Render logs:**
   - Dashboard → Logs tab
   - Look for errors after API call

2. **Verify data directory:**
```bash
# In Render Shell
ls -la data/logs/
```

3. **Try smaller number:**
```bash
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 10, "secret": "demo_secret_2024"}'
```

### Problem: App Sleeps and Data Lost

**This is normal for Render Free Tier.**

**Solutions:**
1. Use MongoDB (permanent storage)
2. Regenerate data when app wakes up
3. Upgrade to Render Starter ($7/month)

---

## ✅ Deployment Checklist

- [ ] **Step 1: Deploy Code**
  - [ ] Pushed to GitHub
  - [ ] Render deployment successful
  - [ ] No build errors in logs

- [ ] **Step 2: Security (Optional)**
  - [ ] Generated secure ADMIN_SECRET
  - [ ] Set in Render environment
  - [ ] Tested with new secret

- [ ] **Step 3: Generate Data**
  - [ ] Called generate-demo-data API
  - [ ] Got success response
  - [ ] Files_written counts look correct

- [ ] **Step 4: Verify Dashboard**
  - [ ] Dashboard shows metrics
  - [ ] Control: 45-55% users
  - [ ] Treatment: 45-55% users
  - [ ] No Sample Ratio Mismatch warning

- [ ] **Step 5: Test Functionality**
  - [ ] Can login with random user
  - [ ] Gets assigned to variant
  - [ ] Recommendations show
  - [ ] Can rate movies
  - [ ] Can subscribe

- [ ] **Step 6: Share**
  - [ ] Shared URL with team
  - [ ] Added to portfolio
  - [ ] Screenshots taken

---

## 🎯 Quick Command Template

```bash
# Save your URL
export APP_URL="https://YOUR-APP.onrender.com"
export SECRET="demo_secret_2024"

# Generate data
curl -X POST $APP_URL/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d "{\"num_users\": 100, \"secret\": \"$SECRET\"}"

# Check stats
curl "$APP_URL/admin/stats?secret=$SECRET"

# View dashboard
open $APP_URL/dashboard
```

---

## 📞 Need Help?

### Check These Files:

- `PRODUCTION_SETUP.md` - Detailed production guide
- `AB_TESTING_GUIDE.md` - A/B testing explained
- `RENDER_DEPLOYMENT.md` - Full Render deployment
- `MONGODB_QUICKSTART.md` - MongoDB setup

### Test Locally First:

```bash
# Start app
python app.py

# Test admin API
bash test_admin_api.sh

# Should see ✓ marks for all tests
```

---

## 🎉 Success Criteria

Your production app is ready when:

✅ Dashboard shows balanced metrics (49-51% split)  
✅ 100+ users with realistic data  
✅ CTR around 30-50%  
✅ CVR around 10-20%  
✅ No Sample Ratio Mismatch warning  
✅ Users can login and rate movies  
✅ Recommendations personalize after rating  

**Live Demo URL:** `https://YOUR-APP.onrender.com`

---

*Last updated: 2026-01-19*  
*Render.com | Admin API | Demo Data Ready*
