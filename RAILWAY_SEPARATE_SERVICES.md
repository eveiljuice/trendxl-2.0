# Railway Deployment - Separate Services Configuration

This guide explains how to deploy TrendXL 2.0 with separate frontend and backend services on Railway.

## 🚀 Services Overview

### Backend Service

- **Domain**: `trendxl-20-backend-production.up.railway.app`
- **Port**: 8000
- **Technology**: Python 3.10 + FastAPI + Uvicorn

### Frontend Service

- **Domain**: `trendxl-20-frontend-production.up.railway.app`
- **Port**: 80
- **Technology**: React + Vite + Nginx

## 📋 Configuration Files Updated

### 1. Frontend Configuration (`.env.production`)

```env
VITE_BACKEND_API_URL=https://trendxl-20-backend-production.up.railway.app
```

### 2. Backend CORS Configuration (`backend/config.py`)

```python
cors_origins = [
    "https://trendxl-20-frontend-production.up.railway.app",
    # ... other origins
]
```

### 3. Frontend API Service (`src/services/backendApi.ts`)

- Uses `VITE_BACKEND_API_URL` environment variable
- Automatically connects to Railway backend in production

## 🛠️ Railway Setup Instructions

### Backend Service Setup

1. **Create Backend Service**

   - Repository: Connect your GitHub repo
   - Root Directory: `/backend` (or keep root and use Dockerfile.backend)
   - Build Command: Automatic (uses Dockerfile)
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables (Backend)**

   ```
   ENSEMBLE_API_TOKEN=your_ensemble_token
   OPENAI_API_KEY=your_openai_key
   PERPLEXITY_API_KEY=your_perplexity_key
   PORT=8000
   REDIS_URL=redis://localhost:6379
   CORS_ORIGINS=https://trendxl-20-frontend-production.up.railway.app
   ```

3. **Custom Domain** (Optional)
   - Add your backend domain if needed
   - Update `.env.production` with the custom domain

### Frontend Service Setup

1. **Create Frontend Service**

   - Repository: Connect your GitHub repo
   - Root Directory: `/` (project root)
   - Build Command: `npm ci && npm run build`
   - Start Command: Use Nginx to serve static files

2. **Environment Variables (Frontend)**

   ```
   VITE_BACKEND_API_URL=https://trendxl-20-backend-production.up.railway.app
   NODE_ENV=production
   ```

3. **Dockerfile for Frontend**
   - Builds React app with Vite
   - Serves static files with Nginx
   - Port: 80

## 🔄 Deployment Workflow

### Initial Deployment

1. **Deploy Backend First**

   ```bash
   git add .
   git commit -m "Configure backend for Railway"
   git push origin main
   ```

   - Railway will automatically deploy backend
   - Note the backend URL

2. **Deploy Frontend**
   - Update `.env.production` with backend URL
   - Commit and push changes
   - Railway will automatically deploy frontend

### Updating Configuration

If you need to change the Railway domains:

1. Update `.env.production`:

   ```env
   VITE_BACKEND_API_URL=https://your-new-backend.up.railway.app
   ```

2. Update `backend/config.py`:

   ```python
   cors_origins = [
       "https://your-new-frontend.up.railway.app",
   ]
   ```

3. Commit and push:
   ```bash
   git add .env.production backend/config.py
   git commit -m "Update Railway service URLs"
   git push origin main
   ```

## 🧪 Testing

### Test Backend Health

```bash
curl https://trendxl-20-backend-production.up.railway.app/health
```

Expected response:

```json
{
  "status": "healthy",
  "services": {
    "backend": true,
    "cache": true,
    "ensemble_api": true,
    "openai_api": true
  }
}
```

### Test Frontend

1. Open browser: `https://trendxl-20-frontend-production.up.railway.app`
2. Check browser console for API connection logs
3. Try analyzing a TikTok profile

## 🔍 Troubleshooting

### CORS Errors

**Problem**: Frontend can't connect to backend
**Solution**:

- Check `backend/config.py` CORS origins include frontend URL
- Verify environment variables are set in Railway
- Check backend logs for CORS errors

### API Connection Timeout

**Problem**: Requests to backend timeout
**Solution**:

- Check backend service is running in Railway dashboard
- Verify backend URL in `.env.production`
- Check backend logs for errors

### Build Failures

**Problem**: Railway build fails
**Solution**:

- Check `package-lock.json` is committed
- Verify all dependencies are in `package.json`
- Check Railway build logs for specific errors

## 📊 Monitoring

### Backend Monitoring

- Railway Dashboard → Backend Service → Metrics
- Check CPU, Memory, and Network usage
- Monitor response times

### Frontend Monitoring

- Railway Dashboard → Frontend Service → Metrics
- Check build times and deployment status
- Monitor static file serving

## 🔐 Security Notes

1. **API Keys**: Never commit API keys to Git
2. **CORS**: Restrict CORS origins in production (remove `"*"`)
3. **HTTPS**: Always use HTTPS in production
4. **Rate Limiting**: Backend has rate limiting enabled

## 🚀 Production Checklist

- [ ] Backend deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] Environment variables configured
- [ ] CORS properly configured
- [ ] API keys set in Railway
- [ ] Custom domains configured (if needed)
- [ ] HTTPS enabled
- [ ] Monitoring setup
- [ ] Error tracking configured

## 📝 Notes

- Both services auto-deploy on Git push
- Railway provides automatic HTTPS
- Services can scale independently
- Check Railway dashboard for logs and metrics

## 🆘 Support

If you encounter issues:

1. Check Railway logs for both services
2. Verify environment variables
3. Test backend health endpoint
4. Check browser console for errors
5. Review CORS configuration

---

**Last Updated**: September 30, 2025
**Version**: 2.0
**Deployment Type**: Separate Services (Frontend + Backend)
