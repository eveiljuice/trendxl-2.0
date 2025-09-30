# Railway Deployment Guide - TrendXL 2.0

## Separate Backend & Frontend Services Configuration

This guide explains how to deploy TrendXL 2.0 as separate backend and frontend services on Railway.

---

## 📋 Overview

TrendXL 2.0 uses a **monorepo structure** with:

- **Backend**: Python FastAPI service (Dockerfile.backend)
- **Frontend**: React + Vite served by Nginx (Dockerfile.frontend)

Each service is deployed independently with its own configuration file.

---

## 🚀 Quick Start: Railway CLI Deployment

### Prerequisites

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login
```

### Step 1: Create Railway Project

```bash
# Initialize a new Railway project
railway init

# Or link to existing project
railway link
```

### Step 2: Deploy Backend Service

```bash
# Create backend service
railway add --service backend

# Set the configuration file for backend
# In Railway UI: Settings > Config as Code > Set to "railway.backend.toml"

# Set required environment variables
railway variables set ENSEMBLE_API_TOKEN="your_ensemble_token" --service backend
railway variables set OPENAI_API_KEY="your_openai_key" --service backend
railway variables set PERPLEXITY_API_KEY="your_perplexity_key" --service backend

# Optional: Add Redis
railway add --database redis
railway variables set REDIS_URL='${{Redis.REDIS_URL}}' --service backend

# Deploy backend
railway up --service backend
```

### Step 3: Deploy Frontend Service

```bash
# Create frontend service
railway add --service frontend

# Set the configuration file for frontend
# In Railway UI: Settings > Config as Code > Set to "railway.frontend.toml"

# Get backend URL (after backend is deployed)
BACKEND_URL=$(railway variables get RAILWAY_PUBLIC_DOMAIN --service backend)

# Set backend URL for frontend
railway variables set VITE_BACKEND_API_URL="https://${BACKEND_URL}" --service frontend

# Deploy frontend
railway up --service frontend
```

---

## 🎯 Railway Web UI Deployment

### Method 1: Deploy from GitHub (Recommended)

1. **Connect Repository**

   - Go to [Railway Dashboard](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Create Backend Service**
   - Railway will detect your Dockerfile
   - Click "Add Service" or it may auto-create
   - Name it: `backend` or `trendxl-backend`
3. **Configure Backend Service**
   - Go to service settings
   - **Root Directory**: Leave blank (defaults to `/`)
   - **Config as Code**: Set to `railway.backend.toml`
   - **Watch Paths**: `/backend/**` (automatically set by config)
4. **Set Backend Environment Variables**
   ```env
   ENSEMBLE_API_TOKEN=your_ensemble_api_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   PERPLEXITY_API_KEY=your_perplexity_api_key_here
   ```
5. **Deploy Backend**

   - Railway will automatically deploy
   - Wait for deployment to complete
   - Note the public URL (e.g., `https://trendxl-backend-production.up.railway.app`)

6. **Create Frontend Service**

   - Click "+ New Service"
   - Select "GitHub Repo" (same repo)
   - Name it: `frontend` or `trendxl-frontend`

7. **Configure Frontend Service**
   - Go to service settings
   - **Root Directory**: Leave blank
   - **Config as Code**: Set to `railway.frontend.toml`
   - **Watch Paths**: Automatically set by config
8. **Set Frontend Environment Variables**

   ```env
   VITE_BACKEND_API_URL=https://trendxl-backend-production.up.railway.app
   ```

   **OR** use service reference:

   ```env
   VITE_BACKEND_API_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}
   ```

9. **Deploy Frontend**
   - Railway will automatically deploy
   - Frontend will be built with the backend URL baked in

---

## 📁 Configuration Files Explained

### Backend Configuration (`railway.backend.toml`)

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile.backend"
watchPatterns = ["/backend/**"]  # Only rebuild when backend files change

[deploy]
startCommand = "python run_server.py"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
numReplicas = 1
overlapSeconds = 30      # Zero-downtime deployment
drainingSeconds = 60     # Graceful shutdown

[env]
PYTHONPATH = "/app/backend"
HOST = "0.0.0.0"
ENVIRONMENT = "production"
# API keys set in Railway UI
```

### Frontend Configuration (`railway.frontend.toml`)

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile.frontend"
watchPatterns = ["/src/**", "/public/**", ...]  # Frontend files only

[deploy]
startCommand = "nginx -g 'daemon off;'"
healthcheckPath = "/health"
healthcheckTimeout = 60
numReplicas = 1
overlapSeconds = 10
drainingSeconds = 30

# VITE_ variables must be set at BUILD time
```

---

## 🔧 Service Configuration Details

### Backend Service Settings

| Setting           | Value                  | Description                          |
| ----------------- | ---------------------- | ------------------------------------ |
| **Builder**       | Dockerfile             | Uses Dockerfile.backend              |
| **Start Command** | `python run_server.py` | Starts FastAPI server                |
| **Health Check**  | `/health`              | Health endpoint                      |
| **Port**          | Auto (PORT env var)    | Railway sets automatically           |
| **Watch Paths**   | `/backend/**`          | Only backend changes trigger rebuild |

### Frontend Service Settings

| Setting           | Value                         | Description                           |
| ----------------- | ----------------------------- | ------------------------------------- |
| **Builder**       | Dockerfile                    | Uses Dockerfile.frontend              |
| **Start Command** | `nginx -g 'daemon off;'`      | Starts Nginx                          |
| **Health Check**  | `/health`                     | Nginx health endpoint                 |
| **Port**          | Auto (PORT env var)           | Railway sets automatically            |
| **Watch Paths**   | `/src/**`, `/public/**`, etc. | Only frontend changes trigger rebuild |

---

## 🔐 Environment Variables

### Backend Service (Required)

```env
# API Keys (Required)
ENSEMBLE_API_TOKEN=your_token_here
OPENAI_API_KEY=sk-your_key_here
PERPLEXITY_API_KEY=pplx-your_key_here  # Optional but recommended

# Database (Optional - if using Railway Postgres)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (Optional - if using Railway Redis)
REDIS_URL=${{Redis.REDIS_URL}}

# These are auto-set by Railway
PYTHONPATH=/app/backend
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
HOST=0.0.0.0
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Frontend Service (Required)

```env
# Backend API URL - MUST be set at BUILD time!
VITE_BACKEND_API_URL=https://your-backend-service.up.railway.app

# Or use service reference (Railway will resolve this)
VITE_BACKEND_API_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}
```

⚠️ **Important**: `VITE_` prefixed variables are **build-time** variables. They are baked into the JavaScript bundle during `npm run build`. If you change them, you must redeploy the frontend.

---

## 🔗 Service Communication

### Option 1: Public Domain (Recommended for Frontend → Backend)

Frontend uses backend's public domain:

```env
VITE_BACKEND_API_URL=https://trendxl-backend-production.up.railway.app
```

### Option 2: Service References

Use Railway's service reference syntax:

```env
# In frontend service
VITE_BACKEND_API_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}
```

### Option 3: Private Networking (Optional)

If both services are in the same project, you can use private networking:

```env
# Backend to Backend service communication
BACKEND_PRIVATE_URL=${{backend.RAILWAY_PRIVATE_DOMAIN}}
```

---

## 📊 Monitoring & Logs

### View Logs

```bash
# Backend logs
railway logs --service backend

# Frontend logs
railway logs --service frontend

# Follow logs in real-time
railway logs --service backend --follow
```

### Health Checks

- **Backend**: `https://your-backend.up.railway.app/health`
- **Frontend**: `https://your-frontend.up.railway.app/health`

### Deployment Status

Check in Railway UI:

- Services tab
- Deployments for each service
- Metrics & logs

---

## 🐛 Troubleshooting

### Backend Not Starting

1. **Check API Keys**

   ```bash
   railway variables --service backend
   ```

   Ensure `ENSEMBLE_API_TOKEN` and `OPENAI_API_KEY` are set

2. **Check Logs**

   ```bash
   railway logs --service backend
   ```

3. **Check Health Endpoint**
   ```bash
   curl https://your-backend.up.railway.app/health
   ```

### Frontend Not Connecting to Backend

1. **Verify Backend URL**

   ```bash
   railway variables --service frontend
   ```

   Ensure `VITE_BACKEND_API_URL` is correct

2. **Rebuild Frontend**
   If you changed `VITE_BACKEND_API_URL`, redeploy:

   ```bash
   railway up --service frontend
   ```

3. **Check CORS Settings**
   Backend should allow frontend domain in CORS

### Build Failures

1. **Check Dockerfile Paths**

   - Backend: `Dockerfile.backend` exists
   - Frontend: `Dockerfile.frontend` exists

2. **Check Config Files**

   - `railway.backend.toml` in root
   - `railway.frontend.toml` in root

3. **Watch Patterns**
   Ensure watch patterns match your file changes

---

## 🔄 Updating Services

### Update Backend

```bash
# Make changes to backend code
git add backend/
git commit -m "Update backend"
git push

# Railway auto-deploys if GitHub integration is set up
# Or manually:
railway up --service backend
```

### Update Frontend

```bash
# Make changes to frontend code
git add src/
git commit -m "Update frontend"
git push

# Railway auto-deploys
# Or manually:
railway up --service frontend
```

### Update Environment Variables

```bash
# Update backend variable
railway variables set OPENAI_API_KEY="new_key" --service backend

# Update frontend variable (requires rebuild!)
railway variables set VITE_BACKEND_API_URL="new_url" --service frontend
railway up --service frontend  # Rebuild required
```

---

## 📚 Additional Resources

- [Railway Docs - Monorepo Deployments](https://docs.railway.app/guides/monorepo)
- [Railway Docs - Config as Code](https://docs.railway.app/reference/config-as-code)
- [Railway Docs - Environment Variables](https://docs.railway.app/develop/variables)
- [Railway CLI Reference](https://docs.railway.app/reference/cli-api)

---

## ✅ Checklist

Before deploying, ensure:

- [ ] Both `Dockerfile.backend` and `Dockerfile.frontend` exist
- [ ] Both `railway.backend.toml` and `railway.frontend.toml` are configured
- [ ] Backend environment variables are set (API keys)
- [ ] Frontend `VITE_BACKEND_API_URL` points to backend
- [ ] Both services have correct watch patterns
- [ ] Health check endpoints work (`/health`)
- [ ] CORS is configured for frontend domain

---

## 🎉 Success!

Once deployed:

- Backend API: `https://your-backend.up.railway.app`
- Frontend App: `https://your-frontend.up.railway.app`
- Test: Open frontend URL → should connect to backend → fetch trends

**Congratulations! Your TrendXL 2.0 is live on Railway! 🚀**
