# Grafana Cloud Setup Guide

Complete guide for setting up Grafana Cloud monitoring with Prometheus metrics.

## 🎯 Overview

This setup enables real-time A/B test monitoring with:
- ✅ **Automatic metrics push** every 60 seconds
- ✅ **Beautiful dashboard** with CTR/CVR tracking
- ✅ **Free tier** - 10K series, 14 days retention
- ✅ **No infrastructure** - fully managed cloud service

---

## 📋 Step-by-Step Setup

### Step 1: Sign Up for Grafana Cloud

1. Visit: https://grafana.com/auth/sign-up/create-user
2. Sign up using:
   - **Google** account (recommended)
   - **GitHub** account
   - Email address
3. Choose **Free** plan (no credit card required)

### Step 2: Access Your Grafana Stack

After sign up, Grafana automatically creates a "stack" for you:
- **Grafana** (dashboards & visualizations)
- **Prometheus** (metrics storage)
- **Loki** (logs - optional)

To access:
1. Go to **My Account** → **Grafana Cloud Portal**
2. Click on your stack name (e.g., `yourname-stack`)

### Step 3: Get Prometheus Remote Write Credentials

This is the **most important step** - these credentials allow your app to push metrics.

1. In your Grafana Cloud Portal, find **Prometheus**
2. Click **"Send Metrics"** or **"Remote Write"**
3. You'll see three values:

```
Remote Write Endpoint: https://prometheus-prod-xx-prod-xx-prod.grafana.net/api/prom/push
Username/Instance ID: 123456
Password/API Key: glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Keep these credentials safe!** You'll need them in the next step.

### Step 4: Configure Your Application

#### Option A: Using `.env` file (Local Development)

Create or edit `BA_project/.env`:

```bash
# Grafana Cloud Prometheus Remote Write
GRAFANA_CLOUD_URL=https://prometheus-prod-xx-prod-xx-prod.grafana.net/api/prom/push
GRAFANA_CLOUD_USER=123456
GRAFANA_CLOUD_API_KEY=glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### Option B: Environment Variables (Production)

For Render.com or other hosting:

```bash
export GRAFANA_CLOUD_URL="https://prometheus-prod-xx-prod-xx-prod.grafana.net/api/prom/push"
export GRAFANA_CLOUD_USER="123456"
export GRAFANA_CLOUD_API_KEY="glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Step 5: Test the Connection

Run the test script to verify your credentials:

```bash
cd BA_project
python scripts/test_grafana.py
```

**Expected output:**
```
[✓] Grafana Cloud configured
[✓] Credentials valid
[✓] Successfully pushed test metrics
[✓] Metrics visible in Grafana Cloud

Success! Your Grafana Cloud is working.
```

If you see errors, check:
- ✓ Credentials copied correctly (no extra spaces)
- ✓ URL includes `/api/prom/push` at the end
- ✓ API key starts with `glc_`

### Step 6: Import Dashboard

Now let's create the beautiful A/B test dashboard:

1. In Grafana Cloud, click **Dashboards** (left sidebar)
2. Click **New** → **Import**
3. Click **Upload JSON file**
4. Select: `BA_project/grafana-dashboards/ab-test-dashboard.json`
5. Click **Import**

**🎉 Done!** Your dashboard is ready.

### Step 7: Start Your Application

```bash
cd BA_project
python app.py
```

You should see:
```
[Grafana] Starting metrics push loop (interval: 60s)
[Grafana] Metrics pushed successfully
```

### Step 8: View Your Dashboard

1. Go to **Dashboards** in Grafana Cloud
2. Open **"A/B Test - Movie Recommender"**
3. Wait 1-2 minutes for first metrics to appear

---

## 📊 Dashboard Overview

Your dashboard shows:

### Top Row - Key Metrics
- **Control Impressions** - Total views for Matrix Factorization
- **Treatment Impressions** - Total views for LightGCN
- **Control CTR** - Click-through rate (%)
- **Treatment CTR** - Click-through rate (%)

### Middle Row - Time Series
- **CTR Over Time** - Line chart comparing both variants
- **CVR Over Time** - Conversion rate trends

### Bottom Row - Analysis
- **User Distribution** - Pie chart showing split
- **CTR Lift (%)** - Gauge showing improvement
- **CVR Lift (%)** - Conversion improvement

---

## 🔧 Configuration Reference

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GRAFANA_CLOUD_URL` | Prometheus remote write endpoint | `https://prometheus-prod-*.grafana.net/api/prom/push` |
| `GRAFANA_CLOUD_USER` | Instance ID (username) | `123456` |
| `GRAFANA_CLOUD_API_KEY` | Generated API token | `glc_ey...` |

### Metrics Pushed

The app automatically pushes these metrics every 60 seconds:

| Metric | Type | Description |
|--------|------|-------------|
| `ba_ab_impressions_total` | Counter | Total recommendations shown |
| `ba_ab_clicks_total` | Counter | Total clicks on recommendations |
| `ba_ab_subscriptions_total` | Counter | Total conversions |
| `ba_ab_users_total` | Counter | Total users in each variant |
| `ba_ab_ctr` | Gauge | Click-through rate (%) |
| `ba_ab_cvr` | Gauge | Conversion rate (%) |

All metrics have a `variant` label: `control` or `treatment`

---

## 🐛 Troubleshooting

### "Not configured" message
- **Cause**: Environment variables not set
- **Fix**: Check `.env` file exists and has correct values

### "Push failed: 401"
- **Cause**: Invalid credentials
- **Fix**: Verify API key and username from Grafana Cloud Portal

### "Push failed: 404"
- **Cause**: Wrong URL
- **Fix**: Ensure URL ends with `/api/prom/push`

### "Push failed: 429"
- **Cause**: Rate limit exceeded
- **Fix**: Check you're not pushing too frequently (default: 60s is good)

### Dashboard shows "No data"
- **Cause**: Metrics not yet received
- **Fix**: 
  1. Wait 1-2 minutes after app start
  2. Check app logs for "Metrics pushed successfully"
  3. Verify time range in dashboard (top-right)

### Connection timeout
- **Cause**: Network/firewall issue
- **Fix**: 
  1. Test with: `curl -I https://prometheus-prod-*.grafana.net`
  2. Check firewall allows HTTPS outbound

---

## 💡 Tips & Best Practices

### For Local Development
```bash
# Create .env file
cat > .env << EOF
GRAFANA_CLOUD_URL=your-url-here
GRAFANA_CLOUD_USER=your-user-here
GRAFANA_CLOUD_API_KEY=your-key-here
EOF

# Test it
python scripts/test_grafana.py
```

### For Production (Render.com)
1. Go to **Environment** tab in Render dashboard
2. Add the three environment variables
3. Click **Save Changes**
4. Render will auto-restart with new config

### Monitoring Multiple Environments

Add environment label to distinguish dev/staging/prod:

```python
# In grafana_metrics.py, update format_prometheus_metrics():
environment = os.getenv('ENVIRONMENT', 'development')
lines.append(f'ba_app_info{{version="1.0.0",environment="{environment}"}} 1')
```

Then filter in Grafana: `ba_ab_ctr{environment="production"}`

### Custom Time Ranges

Dashboard defaults to last 6 hours. To change:
1. Click time picker (top-right)
2. Select: Last 24 hours, Last 7 days, etc.
3. Click **Save** to make it default

---

## 🚀 Next Steps

1. **Generate Traffic**: Visit http://localhost:5000 and interact with the app
2. **Watch Metrics**: Refresh Grafana dashboard every minute
3. **Analyze Results**: Look for CTR/CVR differences between variants
4. **Share Dashboard**: Click **Share** → Get link for your team

---

## 📚 Resources

- [Grafana Cloud Docs](https://grafana.com/docs/grafana-cloud/)
- [Prometheus Remote Write](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#remote_write)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)

---

## 🎓 Understanding the Stack

```
┌─────────────────────────────────────────────────────┐
│                Your Flask App                       │
│  - Calculates metrics (CTR, CVR)                    │
│  - Pushes to Grafana Cloud every 60s                │
└─────────────────────┬───────────────────────────────┘
                      │ HTTPS POST
                      │ (Prometheus format)
                      ▼
┌─────────────────────────────────────────────────────┐
│         Grafana Cloud - Prometheus                  │
│  - Receives & stores metrics                        │
│  - Time-series database                             │
│  - 10K series, 14 days retention (free)             │
└─────────────────────┬───────────────────────────────┘
                      │ PromQL Queries
                      ▼
┌─────────────────────────────────────────────────────┐
│         Grafana Cloud - Dashboard                   │
│  - Visualizes metrics                               │
│  - Real-time charts & graphs                        │
│  - Alerts (optional)                                │
└─────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ No server to maintain
- ✅ Auto-scaling
- ✅ High availability
- ✅ Industry-standard tools
- ✅ Free for personal projects

---

**Need help?** Check the troubleshooting section or open an issue on GitHub.
