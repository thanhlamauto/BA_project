# Deployment Guide - MLOps Demo

## Quick Start Checklist

- [ ] **Step 1**: MongoDB Atlas - Create free cluster
- [ ] **Step 2**: BentoCloud - Deploy model service
- [ ] **Step 3**: Render.com - Deploy Flask app
- [ ] **Step 4**: Grafana Cloud - Setup monitoring (optional)

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Render.com    │────▶│   BentoCloud    │     │  Grafana Cloud  │
│   Flask App     │     │  Model Serving  │     │   Monitoring    │
└────────┬────────┘     └─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│  MongoDB Atlas  │
│    Database     │
└─────────────────┘
```

---

## Step 1: MongoDB Atlas

### 1.1 Create Account & Cluster
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up (free)
3. Create **M0 FREE** cluster
4. Choose region: Singapore or nearest

### 1.2 Create Database User
```
Username: ba_demo_user
Password: <generate strong password>
Role: Read and write to any database
```

### 1.3 Network Access
- Add IP: `0.0.0.0/0` (Allow from anywhere)

### 1.4 Get Connection String
```
mongodb+srv://ba_demo_user:<password>@cluster0.xxxxx.mongodb.net/ba_project
```

### 1.5 Test Connection
```bash
export MONGODB_URI="your-connection-string"
python scripts/test_mongodb.py
```

---

## Step 2: BentoCloud

### 2.1 Setup
```bash
pip install bentoml
bentoml cloud login
```

### 2.2 Deploy
```bash
cd BA_project/bentoml_service
bentoml build
bentoml push movie-recommender:latest
bentoml deployment create movie-recommender:latest --name movie-recommender
```

### 2.3 Get Endpoint
- Dashboard: https://cloud.bentoml.com
- Copy URL: `https://movie-recommender-xxx.mt1.bentoml.ai`

---

## Step 3: Render.com

### 3.1 Push to GitHub
```bash
git add -A
git commit -m "Add MLOps infrastructure"
git push origin feature/mlops
```

### 3.2 Create Web Service
1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - Root Directory: `BA_project`
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app`

### 3.3 Environment Variables
| Variable | Value |
|----------|-------|
| `ENVIRONMENT` | `production` |
| `SECRET_KEY` | (auto-generate) |
| `MONGODB_URI` | `mongodb+srv://...` |
| `USE_MONGODB_LOGGING` | `true` |
| `BENTOML_ENDPOINT` | `https://movie-recommender-xxx.bentoml.ai` |

### 3.4 Verify
```bash
curl https://ba-movie-recommender.onrender.com/health
```

---

## Step 4: Grafana Cloud (Optional)

### 4.1 Setup
1. Go to https://grafana.com
2. Sign up free
3. Get API Key from Administration → API Keys

### 4.2 Import Dashboard
- Dashboards → New → Import
- Upload: `grafana-dashboards/ab-test-dashboard.json`

### 4.3 Connect Metrics
- Your app exposes metrics at `/metrics`
- Configure Prometheus scraping in Grafana Cloud

---

## Local Development

### With Docker
```bash
cd BA_project
docker-compose up
```
- App: http://localhost:5000
- MongoDB: localhost:27017

### Without Docker
```bash
cd BA_project
pip install -r requirements.txt
python app.py
```

---

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | `development` or `production` | `development` |
| `SECRET_KEY` | Flask secret key | auto-generated |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/ba_project` |
| `USE_MONGODB_LOGGING` | Use MongoDB for logging | `false` |
| `BENTOML_ENDPOINT` | BentoCloud API URL | `http://localhost:3000` |
| `GRAFANA_CLOUD_API_KEY` | Grafana Cloud API key | (empty) |

---

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Home page |
| `/dashboard` | A/B Test dashboard |
| `/health` | Health check (200 if running) |
| `/ready` | Readiness check (dependencies) |
| `/metrics` | Prometheus metrics |

---

## Costs (All Free Tier)

| Service | Free Tier |
|---------|-----------|
| MongoDB Atlas | M0 - 512MB storage |
| BentoCloud | Limited requests/month |
| Render.com | 750 hours/month, sleeps after 15min |
| Grafana Cloud | 10k series, 14 days retention |

**Total: $0/month** for demo purposes

---

## Troubleshooting

### MongoDB Connection Failed
- Check IP whitelist (0.0.0.0/0)
- Verify username/password
- Check connection string format

### BentoCloud Deploy Failed
- Ensure logged in: `bentoml cloud login`
- Check bentofile.yaml syntax
- Verify all files exist

### Render Build Failed
- Check requirements.txt
- Verify root directory is `BA_project`
- Check build logs in Render dashboard

### App Sleeps on Render
- Free tier sleeps after 15min inactivity
- First request after sleep takes ~30s to wake
- Consider upgrading for always-on
