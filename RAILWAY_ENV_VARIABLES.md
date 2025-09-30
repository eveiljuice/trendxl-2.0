# Railway Environment Variables Setup

## 🔑 Required Environment Variables for Backend Service

Before deploying to Railway, you **MUST** set these environment variables in the Railway dashboard for your backend service.

---

## Backend Service Variables

### Required API Keys

Go to **Railway Dashboard → Your Project → Backend Service → Variables** and add:

#### 1. Ensemble Data API Token

```env
ENSEMBLE_API_TOKEN=your_ensemble_token_here
```

- **Get it from**: https://dashboard.ensembledata.com/
- **Required**: Yes ✅
- **Format**: Alphanumeric string with dashes/underscores
- **Example**: `ed-1234567890abcdef`

#### 2. OpenAI API Key

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxx
```

- **Get it from**: https://platform.openai.com/api-keys
- **Required**: Yes ✅
- **Format**: Must start with `sk-` or `sk-proj-`
- **Example**: `sk-proj-abc123...`

#### 3. Perplexity API Key

```env
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxx
```

- **Get it from**: https://www.perplexity.ai/settings/api
- **Required**: Recommended ⭐
- **Format**: Should start with `pplx-`
- **Example**: `pplx-abc123...`

---

## Optional Variables

### Redis (if using Railway Redis service)

```env
REDIS_URL=${{Redis.REDIS_URL}}
```

This will automatically connect to your Railway Redis service if you've added it.

### Custom Configuration

```env
# Server settings (Railway will override PORT automatically)
HOST=0.0.0.0
DEBUG=false
ENVIRONMENT=production

# Redis cache TTL (in seconds)
CACHE_PROFILE_TTL=1800
CACHE_POSTS_TTL=900
CACHE_TRENDS_TTL=300

# Rate limiting
MAX_REQUESTS_PER_MINUTE=60
```

---

## Frontend Service Variables

### Required for Frontend

```env
VITE_BACKEND_API_URL=https://your-backend-service.up.railway.app
```

**OR** use service reference (recommended):

```env
VITE_BACKEND_API_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}
```

⚠️ **Important**: Frontend MUST be rebuilt after changing `VITE_*` variables!

---

## How to Set Variables in Railway

### Method 1: Railway Web UI

1. Open your project on Railway
2. Click on the **Backend** service
3. Go to **Variables** tab
4. Click **+ New Variable**
5. Add each variable:
   - **Variable Name**: `ENSEMBLE_API_TOKEN`
   - **Value**: Your actual token
6. Click **Add**
7. Repeat for all variables
8. Railway will automatically redeploy

### Method 2: Railway CLI

```bash
# Set backend variables
railway variables set ENSEMBLE_API_TOKEN="your_token" --service backend
railway variables set OPENAI_API_KEY="your_key" --service backend
railway variables set PERPLEXITY_API_KEY="your_key" --service backend

# Set frontend variable
railway variables set VITE_BACKEND_API_URL="https://your-backend.up.railway.app" --service frontend
```

### Method 3: Railway Service Reference (Frontend → Backend)

For frontend to automatically use backend's URL:

```bash
railway variables set VITE_BACKEND_API_URL='https://${{backend.RAILWAY_PUBLIC_DOMAIN}}' --service frontend
```

---

## Verification

### Check if variables are set:

```bash
# View backend variables
railway variables --service backend

# View frontend variables
railway variables --service frontend
```

### Check logs after deployment:

```bash
# Backend logs
railway logs --service backend

# Look for these lines:
# ✅ Ensemble Data API token validated
# ✅ OpenAI API key validated
# ✅ Perplexity API key validated
```

---

## Troubleshooting

### ❌ Service fails health check

**Cause**: Missing API keys prevent server from starting

**Solution**: 
1. Check Railway logs: `railway logs --service backend`
2. Look for warnings about missing API keys
3. Set the missing variables in Railway dashboard
4. Service will automatically redeploy

### ❌ Frontend can't connect to backend

**Cause**: `VITE_BACKEND_API_URL` not set or incorrect

**Solution**:
1. Get backend URL from Railway dashboard
2. Set `VITE_BACKEND_API_URL` in frontend service variables
3. **Redeploy frontend** (VITE vars are build-time!)

### ⚠️ API keys showing warnings in logs

Even with warnings, the server will start and health checks will pass. But API calls will fail.

**Solution**: Replace placeholder/invalid keys with real ones.

---

## Security Best Practices

1. ✅ **Never commit** API keys to Git
2. ✅ **Always use** Railway environment variables
3. ✅ **Rotate keys** periodically
4. ✅ **Use different keys** for development vs production
5. ✅ **Monitor usage** on API provider dashboards

---

## Quick Setup Checklist

Before deploying:

- [ ] Get Ensemble Data API token from https://dashboard.ensembledata.com/
- [ ] Get OpenAI API key from https://platform.openai.com/api-keys
- [ ] Get Perplexity API key from https://www.perplexity.ai/settings/api
- [ ] Set `ENSEMBLE_API_TOKEN` in Railway backend service
- [ ] Set `OPENAI_API_KEY` in Railway backend service
- [ ] Set `PERPLEXITY_API_KEY` in Railway backend service
- [ ] Deploy backend service
- [ ] Get backend public URL
- [ ] Set `VITE_BACKEND_API_URL` in Railway frontend service
- [ ] Deploy frontend service
- [ ] Test both health checks

---

**Ready to deploy!** 🚀

For full deployment guide, see [RAILWAY_QUICK_START.md](./RAILWAY_QUICK_START.md)

