# Grafana Cloud - Quick Start

**⏱️ Setup time: 5 minutes**

## 🚀 Quick Setup (3 Steps)

### 1. Get Grafana Cloud Credentials

```bash
# Visit: https://grafana.com/auth/sign-up/create-user
# Sign up (free, no credit card)
# Go to: Prometheus → Send Metrics
# Copy the 3 values below:
```

### 2. Set Environment Variables

```bash
# Create .env file
cat > .env << 'EOF'
GRAFANA_CLOUD_URL=https://prometheus-prod-xx-xxx.grafana.net/api/prom/push
GRAFANA_CLOUD_USER=123456
GRAFANA_CLOUD_API_KEY=glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EOF

# Or export directly
export GRAFANA_CLOUD_URL="https://prometheus-prod-xx-xxx.grafana.net/api/prom/push"
export GRAFANA_CLOUD_USER="123456"
export GRAFANA_CLOUD_API_KEY="glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 3. Test Connection

```bash
# Install dependencies (if needed)
pip install requests python-dotenv

# Run test
python scripts/test_grafana.py
```

**Expected output:**
```
✓ GRAFANA_CLOUD_URL: https://prometheus-prod...
✓ GRAFANA_CLOUD_USER: 123456
✓ GRAFANA_CLOUD_API_KEY: glc_ey...xxxxx
✓ Successfully pushed test metrics!
✓ All tests passed (4/4)

🎉 Success! Your Grafana Cloud setup is working perfectly.
```

---

## 📊 Import Dashboard

```bash
# 1. In Grafana Cloud: Dashboards → New → Import
# 2. Upload: grafana-dashboards/ab-test-dashboard.json
# 3. Click Import
```

---

## 🏃 Run Your App

```bash
python app.py
```

Look for this message:
```
[Grafana] Starting metrics push loop (interval: 60s)
[Grafana] Metrics pushed successfully
```

---

## 🔍 View Metrics

**In Grafana Cloud:**
1. Go to **Explore** (compass icon)
2. Select **Prometheus** datasource
3. Query: `ba_ab_ctr`
4. Click **Run Query**

**Or view the dashboard:**
1. Go to **Dashboards**
2. Open **"A/B Test - Movie Recommender"**
3. Watch metrics update every 60 seconds

---

## ⚠️ Troubleshooting

| Error | Fix |
|-------|-----|
| "Not configured" | Set environment variables |
| "401 Unauthorized" | Check API key and user ID |
| "404 Not Found" | Verify URL ends with `/api/prom/push` |
| "No data" in dashboard | Wait 1-2 minutes, check app logs |

---

## 📚 Full Documentation

For detailed instructions, see: **[docs/GRAFANA_SETUP.md](docs/GRAFANA_SETUP.md)**

---

## 🆓 Free Tier Limits

- **10,000 series** - plenty for this project
- **14 days retention** - good for A/B tests
- **No credit card required**

**Perfect for demos and personal projects!** 🎉
