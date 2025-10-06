# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**TrendXL 2.0** is a full-stack TikTok trend analysis platform that helps users discover trending content by analyzing TikTok profiles. It uses AI to extract relevant hashtags and find trending videos.

**Stack:**

- Frontend: React + TypeScript + Vite + Chakra UI + Tailwind CSS
- Backend: FastAPI (Python) + Supabase (PostgreSQL) + Stripe
- Deployment: Vercel (frontend + serverless backend)

## Development Commands

### Frontend Development

```bash
npm run dev              # Start dev server on port 3000
npm run build           # Build for production (outputs to dist/)
npm run preview         # Preview production build
npm run lint            # Run ESLint
npm run lint:fix        # Fix ESLint issues
```

### Backend Development

```bash
# From backend/ directory
python run_server.py    # Start FastAPI server on port 8000

# Or from root:
npm run backend         # Start backend server
npm run dev:full        # Run both frontend and backend concurrently
```

### Testing

```bash
npx playwright test                    # Run all Playwright tests
npx playwright test --ui              # Run tests in UI mode
npx playwright test --debug           # Run tests in debug mode
npx playwright show-report            # View test report

# Backend tests
cd backend && python test_free_trial.py <user-uuid>
```

## Architecture

### Frontend-Backend Communication

**Development:** Frontend (localhost:3000) → Backend (localhost:8000)

**Production (Vercel):**

- Frontend and backend both deployed on same domain
- Frontend uses relative paths (no explicit backend URL)
- API routes handled via `vercel.json` rewrites to `/api/` serverless functions
- Backend code adapted for Vercel serverless in `backend/vercel_adapter.py`

### Key Services (Backend)

**Trend Analysis Pipeline:**

1. `ensemble_service.py` - Fetches TikTok profile/posts via Ensemble Data API
2. `openai_service.py` - Extracts hashtags using GPT-4o
3. `perplexity_service.py` - Discovers Creative Center hashtags via Perplexity
4. `content_relevance_service.py` - Validates relevance of trending videos
5. `trend_analysis_service.py` - Orchestrates the entire pipeline

**Other Services:**

- `cache_service.py` - Redis caching for API responses
- `advanced_creative_center_service.py` - TikTok Creative Center hashtag discovery
- `auth_service_supabase.py` - User authentication via Supabase
- `stripe_service.py` - Subscription management via Stripe
- `supabase_client.py` - Database operations and free trial tracking

### Authentication Flow

1. User registers/logs in → `AuthContext.tsx` handles state
2. Auth tokens stored in localStorage and Supabase session
3. Backend validates JWT tokens via `get_current_user_from_token()`
4. Token passed via `Authorization: Bearer <token>` header
5. Supabase Auth integration provides fallback for token retrieval

### Subscription & Free Trial System

**Free Trial:**

- New users get 1 free analysis per day
- Tracked in `daily_free_analyses` table (Supabase)
- Resets daily at 00:00 UTC
- Check via `/api/v1/free-trial/info` endpoint
- **Auto-refresh system**: Frontend components auto-update every 60 seconds
- **Pre-check validation**: Status checked BEFORE backend request for better UX
- **Real-time countdown**: Shows exact time until reset with auto-update

**Subscription (Stripe):**

- Checkout flow: Create session → User pays → Webhook updates Supabase
- Check subscription: `/api/v1/subscription/check`
- Admin users bypass all limits
- Subscription info stored in `users` table (`stripe_customer_id`, `subscription_status`)

### Database Schema (Supabase)

**profiles table (auth.users):**

- `id` (UUID) - Primary key
- `email`, `username`, `password_hash`
- `stripe_customer_id`, `subscription_status`, `subscription_end_date`
- `is_admin` - Bypass all limits
- `full_name`, `avatar_url`, `bio`

**scan_history table:**

- Stores complete analysis results for "My Trends" feature
- `id` (UUID), `user_id` (references auth.users)
- `username` (TikTok username analyzed)
- `profile_data` (JSONB) - Complete analysis: profile, trends, hashtags, posts, tokenUsage
- `scan_type` ('free' or 'paid')
- `created_at`, `updated_at`
- RLS enabled - users can only view/edit their own scans

**daily_free_analyses table:**

- Tracks free trial usage per user per day
- Unique constraint: one user per day
- Auto-cleanup after 90 days

**token_usage table:**

- Tracks API token consumption (OpenAI, Perplexity, Ensemble)
- Used for analytics and cost tracking

## Environment Variables

### Frontend (.env or Vercel)

```bash
VITE_BACKEND_API_URL=        # Empty for Vercel, http://localhost:8000 for dev
```

### Backend (.env or Vercel)

```bash
# Required
SUPABASE_URL=                # Supabase project URL
SUPABASE_KEY=                # Supabase anon key
SUPABASE_SERVICE_KEY=        # Supabase service role key
JWT_SECRET=                  # For JWT token signing
STRIPE_API_KEY=              # Stripe secret key
STRIPE_PRICE_ID=             # Stripe subscription price ID
ENSEMBLE_API_TOKEN=          # Ensemble Data API key
OPENAI_API_KEY=              # OpenAI API key
PERPLEXITY_API_KEY=          # Perplexity API key

# Optional
REDIS_URL=                   # Redis cache (optional)
STRIPE_WEBHOOK_SECRET=       # For Stripe webhook verification
```

## Code Style & Conventions

### TypeScript/React (from .cursor/rules)

- Use functional components with TypeScript interfaces (not types)
- Prefer named exports for components
- Use descriptive variable names with auxiliary verbs (isLoading, hasError)
- Minimize 'use client', 'useEffect', 'setState' where possible
- Use Chakra UI and Tailwind for styling
- Mobile-first responsive design

### Python/FastAPI

- Async/await for all I/O operations
- Pydantic models for request/response validation
- Type hints everywhere
- Comprehensive error handling via `error_responses.py`
- Logging via Python's logging module (logger.info, logger.error)

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user info
- `PUT /api/v1/auth/profile` - Update user profile

### Trend Analysis

- `POST /api/v1/analyze` - Main analysis endpoint (requires auth)
  - Checks subscription/free trial before processing
  - Records token usage
  - Returns profile, posts, hashtags, trending videos

### Subscription

- `GET /api/v1/subscription/info` - Get subscription details
- `GET /api/v1/subscription/check` - Check active subscription
- `POST /api/v1/subscription/checkout` - Create Stripe checkout session
- `POST /api/v1/subscription/create-payment-link` - Public payment link
- `POST /api/v1/subscription/cancel` - Cancel subscription
- `POST /api/v1/subscription/reactivate` - Reactivate subscription

### Free Trial

- `GET /api/v1/free-trial/info` - Get free trial status

### Health

- `GET /health` - Health check endpoint

## Common Development Tasks

### Adding a new API endpoint

1. Define Pydantic model in `backend/models.py`
2. Add route handler in `backend/main.py`
3. Add corresponding service function in `backend/services/`
4. Create frontend service function in `src/services/`
5. Update TypeScript types in `src/types/`

### Modifying the analysis pipeline

- Main orchestration: `backend/services/trend_analysis_service.py`
- Individual services in `backend/services/`
- Token usage tracking built into each service
- Caching via `cache_service.py`

### Database migrations

- SQL files in `backend/` directory
- Run via Supabase Dashboard → SQL Editor
- Test locally before production

**Migration files (run in order):**

1. `supabase_migration.sql` - Base tables (users, trend_feed, etc.)
2. `supabase_token_usage_migration.sql` - Token usage tracking
3. `supabase_stripe_migration.sql` - Stripe subscription fields
4. `supabase_free_trial_migration.sql` - Daily free trial system
5. `supabase_admin_migration.sql` - Admin user support
6. `supabase_scan_history_migration.sql` - **NEW:** My Trends history storage

**Important:** The `scan_history` table is required for the "My Trends" feature to work. Without it, analysis results won't be saved.

### Deployment

**Vercel (recommended):**

```bash
git push origin main  # Auto-deploys via Vercel integration
```

**Manual deploy:**

```bash
vercel --prod
```

## Important Notes

- API rate limiting: 60 requests/minute (configured in backend)
- Free trial limit: 1 analysis/day for non-subscribers
- Admin users (is_admin=true) bypass all limits
- All external API usage tracked in token_usage table
- Vercel serverless functions have 300s timeout (5 min - configured in vercel.json)
- Cache TTL: Profile data cached for 1 hour
- The README.md is actually a TikTok API guide (legacy documentation)
- Analysis optimized to fetch 20 posts per user (down from 50) for better performance

## Troubleshooting

### 504 Gateway Timeout Errors

**Symptom:** `/api/v1/analyze` endpoint returns 504 error in production

**Causes:**

- Vercel serverless function timeout (default 60s, now set to 300s)
- Too many posts being fetched and analyzed
- Multiple sequential API calls (Ensemble → OpenAI → Perplexity → Ensemble)

**Solutions:**

1. ✅ Increased Vercel timeout to 300s in `vercel.json`
2. ✅ Reduced `max_posts_per_user` from 50 to 20 in `backend/config.py`
3. Enable Redis caching to speed up repeated requests
4. Consider implementing async/streaming responses for long-running analyses

### Missing Avatar/Cover Images (Warnings in Logs)

**Symptom:** Logs show `⚠️ No avatar found` or `⚠️ No cover image found`

**Not Actually an Error:**

- These are informational warnings, not failures
- System has fallback mechanisms:
  - Avatars: Returns empty string when not found
  - Cover images: Uses first image from `additional_images` array
- Profile analysis completes successfully despite warnings

**Root Cause:**

- Ensemble Data API response structure varies by profile
- Some profiles don't expose avatar URLs in expected fields
- TikTok API may return different image structures

### Creative Center 404 Errors

**Symptom:** `/api/v1/analyze-creative-center` returns 404

**Solution:**

- This endpoint may not be implemented on Vercel
- Frontend falls back to traditional analysis automatically
- Check `backend/main.py` for Creative Center endpoint implementation
