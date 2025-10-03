# 🏗️ TrendXL 2.0 - Architecture Overview

## 📐 System Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                     Railway Cloud Platform                    │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Users (Browser)                        │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                     │
│                         │ HTTPS                               │
│                         ▼                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Frontend Service (Nginx + React)              │  │
│  │  • Domain: *.up.railway.app                          │  │
│  │  • Docker: Dockerfile.frontend                       │  │
│  │  • Port: Dynamic (Railway assigns)                   │  │
│  │  • Static files served by Nginx                      │  │
│  │  • Entrypoint: docker-entrypoint.sh                  │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                      │
│                       │ HTTP/JSON                            │
│                       │ (Internal Railway Network)           │
│                       ▼                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Backend Service (FastAPI + Uvicorn)           │  │
│  │  • Domain: *.up.railway.app                          │  │
│  │  • Docker: Dockerfile.backend                        │  │
│  │  • Port: 8000 (or Railway assigned)                  │  │
│  │  • API: REST JSON                                    │  │
│  └────────┬──────────────────┬─────────────────────────┘  │
│           │                  │                             │
│           │                  │                             │
│           ▼                  ▼                             │
│  ┌────────────────┐  ┌────────────────┐                   │
│  │  Redis Cache   │  │  SQLite DB     │                   │
│  │  (Optional)    │  │  (Persistent)  │                   │
│  └────────────────┘  └────────────────┘                   │
│                                                             │
└──────────────────────┬─────────────────┬────────────────────┘
                       │                 │
                       │ External APIs   │
                       ▼                 ▼
    ┌──────────────────────────────────────────────┐
    │          External Services                   │
    ├──────────────────────────────────────────────┤
    │  • Ensemble Data (TikTok API)               │
    │  • OpenAI GPT-4o (Content Analysis)         │
    │  • Perplexity (Creative Center Search)      │
    └──────────────────────────────────────────────┘
```

---

## 🔄 Request Flow

### 1. User Profile Analysis Request

```
User Browser
    │
    │ 1. Enter @username
    │
    ▼
Frontend (React)
    │
    │ 2. POST /api/v1/analyze
    │    { profile_url: "@username" }
    │
    ▼
Backend (FastAPI)
    │
    ├─→ 3a. Check Redis Cache
    │      └─→ If cached: return immediately
    │
    ├─→ 3b. Call Ensemble Data API
    │      └─→ Get profile + posts
    │
    ├─→ 3c. Call OpenAI GPT-4o
    │      └─→ Extract hashtags from content
    │
    ├─→ 3d. Call Perplexity API
    │      └─→ Discover Creative Center hashtags
    │
    └─→ 3e. Call Ensemble Data API (again)
           └─→ Search trending videos by hashtags
    │
    │ 4. Store in Redis Cache
    │ 5. Return results
    │
    ▼
Frontend (React)
    │
    │ 6. Display results:
    │    • Profile stats
    │    • Video grid
    │    • Hashtag analysis
    │    • Trending videos
    │
    ▼
User Browser
```

---

## 🐳 Docker Architecture

### Frontend Container

```
┌─────────────────────────────────────────┐
│   Dockerfile.frontend                   │
├─────────────────────────────────────────┤
│                                         │
│  Stage 1: Builder (node:18-alpine)     │
│  ┌────────────────────────────────┐    │
│  │ • npm ci (install deps)        │    │
│  │ • COPY source code             │    │
│  │ • npm run build (Vite)         │    │
│  │ • Output: /app/dist            │    │
│  └────────────────────────────────┘    │
│              │                          │
│              │ Copy dist files          │
│              ▼                          │
│  Stage 2: Production (nginx:alpine)    │
│  ┌────────────────────────────────┐    │
│  │ • COPY dist → /usr/share/...   │    │
│  │ • COPY nginx.conf              │    │
│  │ • COPY docker-entrypoint.sh    │    │
│  │ • ENTRYPOINT: entrypoint.sh    │    │
│  └────────────────────────────────┘    │
│              │                          │
│              │ Runtime                  │
│              ▼                          │
│  ┌────────────────────────────────┐    │
│  │ docker-entrypoint.sh:          │    │
│  │ • Read $PORT from Railway      │    │
│  │ • sed replace PLACEHOLDER      │    │
│  │ • nginx -g "daemon off;"       │    │
│  └────────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

**Result:**

- Image size: ~30 MB
- Build time: 3-5 minutes
- Runtime: Nginx serving static files

---

### Backend Container

```
┌─────────────────────────────────────────┐
│   Dockerfile.backend                    │
├─────────────────────────────────────────┤
│                                         │
│  Single Stage (python:3.10-slim)       │
│  ┌────────────────────────────────┐    │
│  │ • Install system deps          │    │
│  │   (gcc, g++, curl)             │    │
│  │ • COPY requirements.txt        │    │
│  │ • pip install -r requirements  │    │
│  │ • Verify imports               │    │
│  │ • COPY backend code            │    │
│  │ • Create non-root user         │    │
│  │ • Switch to user               │    │
│  └────────────────────────────────┘    │
│              │                          │
│              │ Runtime                  │
│              ▼                          │
│  ┌────────────────────────────────┐    │
│  │ CMD: python run_server.py      │    │
│  │ • Read PORT from Railway       │    │
│  │ • Start Uvicorn server         │    │
│  │ • Load FastAPI app             │    │
│  └────────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

**Result:**

- Image size: ~400 MB
- Build time: 3-5 minutes
- Runtime: Uvicorn ASGI server

---

## 📡 API Communication

### Frontend → Backend

```javascript
// src/services/backendApi.ts

const BACKEND_URL = import.meta.env.VITE_BACKEND_API_URL;
// Railway: https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}

axios.post(`${BACKEND_URL}/api/v1/analyze`, {
  profile_url: "@username",
});
```

### Backend → External APIs

```python
# backend/services/ensemble_service.py
ensemble_api.get_user_profile(username)

# backend/services/openai_service.py
openai.chat.completions.create(
    model="gpt-4o",
    messages=[...]
)

# backend/services/perplexity_service.py
requests.post(
    "https://api.perplexity.ai/chat/completions",
    json={...}
)
```

---

## 🔐 Security Architecture

### 1. Network Security

```
Internet (HTTPS)
    │
    │ TLS/SSL (Railway provides)
    ▼
Railway Load Balancer
    │
    ├─→ Frontend Service
    │   • Static files only
    │   • No server-side logic
    │   • Security headers (CSP, X-Frame-Options)
    │
    └─→ Backend Service
        • Internal network communication
        • CORS validation
        • Rate limiting
        • API key validation
```

### 2. Secrets Management

```
Railway Environment Variables
    │
    ├─→ Backend Service
    │   • ENSEMBLE_API_TOKEN (encrypted)
    │   • OPENAI_API_KEY (encrypted)
    │   • PERPLEXITY_API_KEY (encrypted)
    │   • Redis credentials (encrypted)
    │
    └─→ Frontend Service
        • VITE_BACKEND_API_URL (public)
        • NODE_ENV (public)
```

**Important:**

- ⚠️ **Never** commit .env files
- ✅ Use Railway Variables for all secrets
- ✅ VITE\_\* vars are public (embedded in client bundle)
- ✅ Backend API keys stay on server

### 3. Authentication Flow (Future)

```
User → Frontend → Backend
                    │
                    ├─→ JWT Token Generation
                    │   • Sign with secret key
                    │   • Include user_id, exp
                    │
                    └─→ Token Validation
                        • Verify signature
                        • Check expiration
                        • Load user context
```

---

## 📊 Data Flow

### Caching Strategy

```
Request
    │
    ▼
Backend
    │
    ├─→ Check Redis Cache
    │   │
    │   ├─→ If HIT: Return cached data ⚡
    │   │
    │   └─→ If MISS:
    │       │
    │       └─→ Call External APIs
    │           │
    │           ├─→ Process data
    │           ├─→ Store in Redis
    │           │   • profile: TTL 30 min
    │           │   • posts: TTL 15 min
    │           │   • trends: TTL 5 min
    │           │
    │           └─→ Return fresh data
    │
    └─→ Response
```

### Database Schema

```sql
-- SQLite (backend/trendxl_users.db)

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE,
    hashed_password TEXT,
    created_at TIMESTAMP
);

CREATE TABLE profiles (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    tiktok_username TEXT,
    last_analyzed TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE analysis_history (
    id INTEGER PRIMARY KEY,
    profile_id INTEGER,
    analysis_data JSON,
    created_at TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id)
);
```

---

## 🚀 Deployment Architecture

### Railway Project Structure

```
TrendXL 2.0 Project
│
├─ Backend Service
│  ├─ GitHub: main branch
│  ├─ Build: Dockerfile.backend
│  ├─ Port: ${{RAILWAY_PORT}}
│  ├─ Domain: auto-generated
│  └─ Variables:
│     ├─ ENSEMBLE_API_TOKEN
│     ├─ OPENAI_API_KEY
│     ├─ PERPLEXITY_API_KEY
│     ├─ REDIS_URL (if using addon)
│     └─ CORS_ORIGINS
│
├─ Frontend Service
│  ├─ GitHub: main branch
│  ├─ Build: Dockerfile.frontend
│  ├─ Port: ${{RAILWAY_PORT}}
│  ├─ Domain: auto-generated
│  └─ Variables:
│     ├─ NODE_ENV=production
│     ├─ VITE_APP_TITLE
│     └─ VITE_BACKEND_API_URL
│
└─ Redis Service (Optional)
   ├─ Type: Railway Addon
   ├─ Memory: 256 MB (free tier)
   └─ Persistence: Yes
```

### Build & Deploy Process

```
Git Push → GitHub
    │
    │ Webhook
    ▼
Railway Detects Change
    │
    ├─→ Backend Service
    │   │
    │   ├─ 1. Pull code
    │   ├─ 2. Build Docker image
    │   │     • docker build -f Dockerfile.backend
    │   ├─ 3. Run health check
    │   ├─ 4. Deploy new version
    │   └─ 5. Route traffic
    │
    └─→ Frontend Service
        │
        ├─ 1. Pull code
        ├─ 2. Build Docker image
        │     • Stage 1: npm run build
        │     • Stage 2: nginx setup
        ├─ 3. Run health check
        ├─ 4. Deploy new version
        └─ 5. Route traffic
```

---

## 🔍 Monitoring & Observability

### Health Checks

```
Railway → Every 30 seconds
    │
    ├─→ Backend: GET /health
    │   Response: {
    │     "status": "healthy",
    │     "services": {
    │       "ensemble_api": true,
    │       "openai_api": true,
    │       "redis": true
    │     }
    │   }
    │
    └─→ Frontend: GET /health
        Response: "healthy"
```

### Logging

```
Backend Logs:
    • Uvicorn access logs
    • FastAPI app logs
    • API call logs
    • Error stack traces

Frontend Logs:
    • Nginx access logs
    • Browser console logs
    • API request/response logs
    • Performance metrics
```

### Metrics (Railway Dashboard)

```
Service Metrics:
    • CPU usage
    • Memory usage
    • Network I/O
    • Request count
    • Response time
    • Error rate
```

---

## 📦 Dependencies

### Backend (Python)

```
Core:
├─ fastapi>=0.104.1         # Web framework
├─ uvicorn[standard]>=0.24  # ASGI server
├─ pydantic>=2.5.0          # Data validation
└─ pydantic-settings>=2.0   # Settings management

APIs:
├─ openai>=1.3.0            # GPT-4o integration
├─ ensembledata>=0.2.6      # TikTok API SDK
└─ httpx>=0.25.2            # HTTP client

Storage:
├─ redis>=5.0.0             # Caching
└─ aiofiles>=23.2.1         # Async file I/O

Auth:
├─ python-jose[crypto]>=3.3 # JWT tokens
└─ passlib[bcrypt]>=1.7.4   # Password hashing

Testing:
├─ pytest>=7.4.3
└─ pytest-asyncio>=0.21.1
```

### Frontend (JavaScript/TypeScript)

```
Core:
├─ react@18.2.0             # UI library
├─ react-dom@18.2.0         # React DOM
├─ vite@4.5.0               # Build tool
└─ typescript@5.2.2         # Type safety

UI:
├─ @chakra-ui/react@3.26.0  # Component library
├─ lucide-react@0.294.0     # Icons
├─ tailwindcss@3.3.5        # CSS framework
└─ @emotion/react@11.14.0   # CSS-in-JS

HTTP:
└─ axios@1.6.0              # HTTP client

Build:
├─ @vitejs/plugin-react     # Vite React plugin
├─ autoprefixer             # CSS vendor prefixes
└─ postcss                  # CSS processing
```

---

## 🎯 Performance Optimizations

### Frontend

```
Build Optimizations:
├─ Multi-stage Docker build → 30 MB image
├─ Code splitting (vendor, ui chunks)
├─ Tree shaking (unused code removal)
└─ Minification (JS, CSS)

Runtime Optimizations:
├─ Nginx gzip compression
├─ Aggressive static asset caching (1 year)
├─ CDN-friendly headers
└─ HTTP/2 support
```

### Backend

```
Application:
├─ Redis caching (30 min → 5 min TTLs)
├─ Async I/O (asyncio, httpx)
├─ Connection pooling
└─ Lazy loading

Database:
├─ SQLite with WAL mode
├─ Indexed queries
└─ Connection reuse

API Calls:
├─ Rate limiting
├─ Retry logic
└─ Request deduplication
```

---

## 🔮 Future Enhancements

### Short Term

- [ ] Add authentication (JWT)
- [ ] User dashboard
- [ ] Analysis history
- [ ] Export to CSV/PDF

### Medium Term

- [ ] Real-time WebSocket updates
- [ ] Multi-language support
- [ ] Advanced filtering
- [ ] Scheduled analysis

### Long Term

- [ ] Machine learning predictions
- [ ] Competitor analysis
- [ ] Trend forecasting
- [ ] Mobile app

---

**Version:** TrendXL 2.0  
**Last Updated:** October 1, 2025  
**Status:** Production Ready ✅
