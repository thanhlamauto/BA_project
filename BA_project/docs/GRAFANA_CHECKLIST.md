# Grafana Cloud Setup Checklist

Print this and check off each step as you go! ✓

---

## 📋 Pre-Setup

- [ ] Internet connection available
- [ ] Email account ready (Google/GitHub recommended)
- [ ] Text editor open for copy-pasting credentials

---

## 🔐 Step 1: Create Grafana Cloud Account (2 min)

- [ ] Visit: https://grafana.com/auth/sign-up/create-user
- [ ] Sign up with Google/GitHub/Email
- [ ] Choose **Free** plan
- [ ] Confirm email (check spam folder)
- [ ] Login successful

**✓ Checkpoint:** You should see "Welcome to Grafana Cloud" page

---

## 🔑 Step 2: Get Credentials (2 min)

- [ ] Click **"My Account"** (top-right)
- [ ] Go to **"Grafana Cloud Portal"**
- [ ] Find **"Prometheus"** section
- [ ] Click **"Send Metrics"** or **"Remote Write"**
- [ ] Copy **Remote Write Endpoint** (URL)
- [ ] Copy **Username/Instance ID** (number)
- [ ] Copy **Password/API Key** (starts with `glc_`)

**✓ Checkpoint:** You have 3 values saved in notepad

```
URL:     https://prometheus-prod-XX-XXX.grafana.net/api/prom/push
User:    123456
API Key: glc_ey...xxxxxx
```

---

## 💻 Step 3: Configure Application (1 min)

**Option A: Using .env file (Recommended for local)**

- [ ] Open terminal in project folder
- [ ] Create `.env` file:
```bash
cat > BA_project/.env << 'EOF'
GRAFANA_CLOUD_URL=https://prometheus-prod-XX-XXX.grafana.net/api/prom/push
GRAFANA_CLOUD_USER=123456
GRAFANA_CLOUD_API_KEY=glc_ey...xxxxxx
EOF
```
- [ ] Replace with your actual values
- [ ] Save file

**Option B: Environment variables (Production)**

- [ ] In Render/hosting dashboard, add 3 environment variables
- [ ] Save and restart service

**✓ Checkpoint:** Environment variables are set

---

## 🧪 Step 4: Test Connection (1 min)

- [ ] Open terminal in `BA_project` folder
- [ ] Run test script:
```bash
cd BA_project
python scripts/test_grafana.py
```

**Expected output:**
```
✓ GRAFANA_CLOUD_URL: https://prometheus-prod...
✓ GRAFANA_CLOUD_USER: 123456
✓ Successfully pushed test metrics!
✓ All tests passed (4/4)
```

- [ ] All 4 tests passed

**✓ Checkpoint:** Test script shows "All tests passed"

**If tests fail:**
- ❌ 401 error → Check API key and user ID
- ❌ 404 error → Verify URL ends with `/api/prom/push`
- ❌ Timeout → Check internet connection

---

## 📊 Step 5: Import Dashboard (2 min)

- [ ] Go back to Grafana Cloud web interface
- [ ] Click **Dashboards** (left sidebar, looks like 📊)
- [ ] Click **New** → **Import**
- [ ] Click **Upload JSON file**
- [ ] Select: `BA_project/grafana-dashboards/ab-test-dashboard.json`
- [ ] In "Prometheus" dropdown, select your datasource
- [ ] Click **Import**

**✓ Checkpoint:** You see "A/B Test - Movie Recommender" dashboard

---

## 🚀 Step 6: Start Application (1 min)

- [ ] Open terminal in `BA_project` folder
- [ ] Start Flask app:
```bash
python app.py
```

**Look for these messages:**
```
[Grafana] Starting metrics push loop (interval: 60s)
[Grafana] Metrics pushed successfully
```

- [ ] Grafana messages appear in logs
- [ ] No errors shown

**✓ Checkpoint:** App running, metrics pushing

---

## 🎉 Step 7: Verify Dashboard (2 min)

- [ ] Wait 1-2 minutes for first metrics
- [ ] Refresh Grafana dashboard (F5)
- [ ] Dashboard shows data (numbers, not "No data")
- [ ] Time range is "Last 6 hours" (top-right)

**What you should see:**
- [ ] Control Impressions: number > 0
- [ ] Treatment Impressions: number > 0
- [ ] CTR values displayed
- [ ] Charts showing data points

**✓ Checkpoint:** Dashboard displays metrics successfully

---

## 📱 Step 8: Generate Test Data (Optional)

- [ ] Visit: http://localhost:5000
- [ ] Click on some movie recommendations
- [ ] Refresh page a few times
- [ ] Return to Grafana dashboard
- [ ] Wait 60 seconds for metrics update
- [ ] Verify numbers increased

**✓ Checkpoint:** Metrics update as you interact with app

---

## ✅ Final Verification

- [ ] Dashboard auto-refreshes every 30 seconds
- [ ] Control and Treatment metrics both show data
- [ ] CTR/CVR percentages are reasonable (0-100%)
- [ ] Time series charts show trends
- [ ] No "No data" warnings

---

## 🎊 Success Criteria

**You're done when:**
1. ✅ Grafana dashboard visible
2. ✅ Metrics updating every 60 seconds
3. ✅ Charts showing data for both variants
4. ✅ App logs show "Metrics pushed successfully"

---

## 🆘 Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| "Not configured" in logs | Check `.env` file exists and has correct values |
| 401 Unauthorized | Regenerate API key in Grafana Cloud |
| Dashboard shows "No data" | Wait 2 minutes, check time range (top-right) |
| Metrics stop updating | Restart Flask app |
| Can't find Prometheus | Click "Administration" → "Data sources" |

---

## 📚 Need More Help?

- **Detailed guide:** `docs/GRAFANA_SETUP.md`
- **Quick start:** `GRAFANA_QUICKSTART.md`
- **Full deployment:** `DEPLOYMENT.md`

---

## 📝 Notes Section

Use this space to write down your credentials (delete after setup):

```
My Grafana Cloud URL:
_____________________________________________________________

My Instance ID:
_____________________________________________________________

My API Key (first 10 chars):
_____________________________________________________________
```

---

**⏱️ Total setup time: ~10 minutes**
**💰 Cost: $0 (completely free tier)**
**🔄 Updates: Automatic every 60 seconds**

---

🎉 **Congratulations!** You now have professional MLOps monitoring! 🚀
