# Railway Environment Setup

## Backend Service Environment Variables

Set these variables in your Railway backend service:

### Required API Keys

```bash
ENSEMBLE_API_TOKEN=your_real_ensemble_api_token_here
OPENAI_API_KEY=your_real_openai_api_key_here
```

### CORS Configuration

```bash
# Allow Railway frontend domains
CORS_ORIGIN_REGEX=https?://.*\.railway\.app$|https?://.*\.up\.railway\.app$

# Or specific origins (alternative)
# CORS_ORIGINS=["https://your-frontend.up.railway.app"]
```

### Optional Settings

```bash
DEBUG=false
HOST=0.0.0.0
PORT=8000
REDIS_URL=redis://localhost:6379
```

## Frontend Service

Frontend automatically uses `.env.production` during build which contains:

```bash
VITE_BACKEND_API_URL=https://trendxl-20-backend-production.up.railway.app
```

**Important**: Update the backend URL in `.env.production` to match your actual Railway backend service domain.

## Quick Setup Steps

1. **Backend Service**:

   - Add environment variables above
   - Deploy from `backend/` directory
   - Note the generated Railway domain

2. **Frontend Service**:

   - Update `.env.production` with real backend URL
   - Deploy from root directory (uses `Dockerfile`)
   - Should automatically connect to backend

3. **Testing**:
   - Open frontend URL
   - Check browser console for no CORS errors
   - Verify API calls go to Railway backend, not localhost

## Troubleshooting

- **CORS errors**: Check `CORS_ORIGIN_REGEX` on backend
- **localhost:8000**: Frontend using wrong backend URL - update `.env.production`
- **500 errors**: Check backend logs for API key issues
