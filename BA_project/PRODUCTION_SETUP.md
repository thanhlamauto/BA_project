# Production Setup - Render.com

**Fix Sample Ratio Mismatch on Production**

---

## 🎯 Problem

After deploying to Render.com:
- ❌ Dashboard shows 0 users or imbalanced split
- ❌ Sample Ratio Mismatch detected
- ❌ No demo data on production

**Why?** CSV files are in `.gitignore`, so they don't get deployed!

---

## ✅ Solution: Generate Demo Data via API

### Method 1: Using curl (Recommended)

```bash
# Generate 100 demo users on production
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{
    "num_users": 100,
    "secret": "demo_secret_2024"
  }'
```

### Method 2: Using Postman/Insomnia

**Endpoint:** `POST https://YOUR-APP.onrender.com/admin/generate-demo-data`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "num_users": 100,
  "secret": "demo_secret_2024"
}
```

### Method 3: Using Python

```python
import requests

url = "https://YOUR-APP.onrender.com/admin/generate-demo-data"
response = requests.post(url, json={
    "num_users": 100,
    "secret": "demo_secret_2024"
})

print(response.json())
```

---

## 🔐 Security: Change Admin Secret

### For Local Development

```bash
# In .env file
ADMIN_SECRET=your_secure_random_key_here
```

### For Render.com Production

1. Go to **Render Dashboard**
2. Select your service
3. Go to **Environment** tab
4. Add environment variable:
   ```
   Key: ADMIN_SECRET
   Value: your_secure_random_key_here
   ```
4. Click **Save Changes**

**Generate secure key:**
```bash
# On Mac/Linux
openssl rand -hex 32

# Or Python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📊 Expected Response

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

## 🔄 Step-by-Step Deployment

### 1. Update Code

```bash
cd BA_project

# Make sure latest code is committed
git add .
git commit -m "Add admin endpoints for demo data generation"
git push origin main
```

### 2. Wait for Render Deploy

- Render auto-deploys when you push to GitHub
- Wait 3-5 minutes for build to complete
- Check **Logs** tab in Render Dashboard

### 3. Generate Demo Data

```bash
# Replace YOUR-APP with your actual Render URL
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 100, "secret": "demo_secret_2024"}'
```

### 4. Verify Dashboard

Visit: `https://YOUR-APP.onrender.com/dashboard`

**You should see:**
- ✅ Control: ~50 users
- ✅ Treatment: ~50 users
- ✅ Balanced distribution (49-51%)
- ✅ CTR and CVR metrics

---

## 🛠️ Additional Admin Commands

### Check Current Stats

```bash
curl "https://YOUR-APP.onrender.com/admin/stats?secret=demo_secret_2024"
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "impressions": 333,
    "clicks": 152,
    "subscriptions": 20,
    "engagements": 152
  }
}
```

### Clear All Data

```bash
curl -X POST https://YOUR-APP.onrender.com/admin/clear-demo-data \
  -H "Content-Type: application/json" \
  -d '{"secret": "demo_secret_2024"}'
```

### Regenerate Fresh Data

```bash
# Clear old data
curl -X POST https://YOUR-APP.onrender.com/admin/clear-demo-data \
  -H "Content-Type: application/json" \
  -d '{"secret": "demo_secret_2024"}'

# Generate new data
curl -X POST https://YOUR-APP.onrender.com/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d '{"num_users": 150, "secret": "demo_secret_2024"}'
```

---

## 🔍 Troubleshooting

### Problem: 403 Forbidden

**Error:**
```json
{
  "error": "Invalid secret key"
}
```

**Fix:**
- Check your `ADMIN_SECRET` environment variable in Render
- Make sure you're using the correct secret in API calls

### Problem: Still Shows 0 Users

**Possible causes:**
1. **Data not generated yet**
   - Run the generate command above

2. **Render shell method (alternative):**
   ```bash
   # In Render Dashboard → Shell tab
   cd /opt/render/project/src/BA_project
   python scripts/generate_demo_data.py --users 100
   ```

3. **Check logs:**
   ```bash
   # In Render Dashboard → Logs tab
   # Look for errors after running generate command
   ```

### Problem: Data Disappears After Restart

**This is normal on Render Free Tier!**

Render Free tier uses **ephemeral storage** - files are deleted on restart.

**Solutions:**

**Option A: Use MongoDB (Recommended)**
```bash
# In Render environment variables
USE_MONGODB_LOGGING=true
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ba_project

# Then run migration
python scripts/migrate_to_mongodb.py
```

**Option B: Regenerate on Each Deploy**

Create `render-build.sh`:
```bash
#!/bin/bash
pip install -r requirements.txt
python scripts/generate_demo_data.py --users 100
```

Update `render.yaml`:
```yaml
buildCommand: "bash render-build.sh"
```

**Option C: Upgrade to Paid Tier**
- Render Starter ($7/month) has persistent storage

---

## 📱 User Testing on Production

After generating demo data:

1. **Share URL with testers:**
   ```
   https://YOUR-APP.onrender.com
   ```

2. **Instructions for testers:**
   - Click "Login" button
   - User ID is auto-generated (or click "🎲 Random")
   - They'll be assigned to Control or Treatment
   - Rate movies to see personalization
   - Check dashboard to see their data

3. **Monitor metrics:**
   - Watch dashboard for real user interactions
   - Mix of demo data + real user data = realistic metrics

---

## 🎯 Quick Command Reference

```bash
# Your production URL
export RENDER_URL="https://YOUR-APP.onrender.com"
export SECRET="demo_secret_2024"

# Generate 100 users
curl -X POST $RENDER_URL/admin/generate-demo-data \
  -H "Content-Type: application/json" \
  -d "{\"num_users\": 100, \"secret\": \"$SECRET\"}"

# Check stats
curl "$RENDER_URL/admin/stats?secret=$SECRET"

# Clear data
curl -X POST $RENDER_URL/admin/clear-demo-data \
  -H "Content-Type: application/json" \
  -d "{\"secret\": \"$SECRET\"}"

# View dashboard
open $RENDER_URL/dashboard
```

---

## 🔒 Security Best Practices

### 1. Use Strong Secret in Production

```bash
# Generate strong secret
python -c "import secrets; print(secrets.token_hex(32))"

# Set in Render environment
ADMIN_SECRET=<your-generated-secret>
```

### 2. Disable Admin Endpoints in Production (Optional)

If you don't need admin endpoints after initial setup:

```python
# In app.py
if os.getenv('ENVIRONMENT') == 'development':
    from routes import admin
    app.register_blueprint(admin.bp)
```

### 3. Rate Limiting (Optional)

Consider adding rate limiting for admin endpoints using Flask-Limiter.

---

## ✅ Checklist

After following this guide:

- [ ] Pushed latest code to GitHub
- [ ] Render deployed successfully
- [ ] Set `ADMIN_SECRET` in Render (optional but recommended)
- [ ] Generated demo data via API
- [ ] Dashboard shows balanced metrics (~50/50 split)
- [ ] Tested login with random user
- [ ] Verified A/B testing works
- [ ] Shared URL with team/portfolio

---

## 🎉 Success!

Your production app now has:
- ✅ 100 demo users with realistic data
- ✅ Balanced A/B split (50/50)
- ✅ Dashboard showing metrics
- ✅ Ready for demos and interviews

**Live URL:** `https://YOUR-APP.onrender.com`

---

*Last updated: 2026-01-19*  
*Render Free Tier | Ephemeral Storage | Admin API Ready*
