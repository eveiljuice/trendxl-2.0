-- Migration: Create TrendXL 2.0 Database Schema
-- Description: Creates tables for Users, TrendFeed, InteractionLog, and NicheAdapters
-- Created: 2025-10-02

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table: Users
-- Description: Stores TikTok user profile information
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    link TEXT NOT NULL UNIQUE,
    parsed_niche TEXT,
    location TEXT,
    followers INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0.00,
    top_posts JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for Users table
CREATE INDEX IF NOT EXISTS idx_users_link ON public.users(link);
CREATE INDEX IF NOT EXISTS idx_users_parsed_niche ON public.users(parsed_niche);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON public.users(created_at DESC);

-- ============================================================================
-- Table: TrendFeed
-- Description: Stores trending content and analysis results
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.trend_feed (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    trend_title TEXT NOT NULL,
    platform TEXT DEFAULT 'tiktok',
    video_url TEXT,
    stat_metrics JSONB DEFAULT '{}'::jsonb,
    relevance_score DECIMAL(5,2) DEFAULT 0.00,
    date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for TrendFeed table
CREATE INDEX IF NOT EXISTS idx_trend_feed_user_id ON public.trend_feed(user_id);
CREATE INDEX IF NOT EXISTS idx_trend_feed_platform ON public.trend_feed(platform);
CREATE INDEX IF NOT EXISTS idx_trend_feed_relevance_score ON public.trend_feed(relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_trend_feed_date ON public.trend_feed(date DESC);
CREATE INDEX IF NOT EXISTS idx_trend_feed_created_at ON public.trend_feed(created_at DESC);

-- ============================================================================
-- Table: InteractionLog
-- Description: Tracks user interactions with trends
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.interaction_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    trend_id UUID REFERENCES public.trend_feed(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL CHECK (action_type IN ('watched', 'clicked', 'ignored')),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for InteractionLog table
CREATE INDEX IF NOT EXISTS idx_interaction_log_user_id ON public.interaction_log(user_id);
CREATE INDEX IF NOT EXISTS idx_interaction_log_trend_id ON public.interaction_log(trend_id);
CREATE INDEX IF NOT EXISTS idx_interaction_log_action_type ON public.interaction_log(action_type);
CREATE INDEX IF NOT EXISTS idx_interaction_log_timestamp ON public.interaction_log(timestamp DESC);

-- ============================================================================
-- Table: NicheAdapters
-- Description: Stores niche-specific content analysis and topic tags
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.niche_adapters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain TEXT NOT NULL,
    parsed_by_gpt_summary TEXT,
    topic_tags JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for NicheAdapters table
CREATE INDEX IF NOT EXISTS idx_niche_adapters_domain ON public.niche_adapters(domain);
CREATE INDEX IF NOT EXISTS idx_niche_adapters_created_at ON public.niche_adapters(created_at DESC);

-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trend_feed ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.interaction_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.niche_adapters ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users are viewable by everyone"
    ON public.users FOR SELECT
    USING (true);

CREATE POLICY "Users can insert their own data"
    ON public.users FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Users can update their own data"
    ON public.users FOR UPDATE
    USING (true);

-- TrendFeed policies
CREATE POLICY "Trends are viewable by everyone"
    ON public.trend_feed FOR SELECT
    USING (true);

CREATE POLICY "Anyone can insert trends"
    ON public.trend_feed FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Anyone can update trends"
    ON public.trend_feed FOR UPDATE
    USING (true);

-- InteractionLog policies
CREATE POLICY "Interactions are viewable by everyone"
    ON public.interaction_log FOR SELECT
    USING (true);

CREATE POLICY "Anyone can insert interactions"
    ON public.interaction_log FOR INSERT
    WITH CHECK (true);

-- NicheAdapters policies
CREATE POLICY "Niche adapters are viewable by everyone"
    ON public.niche_adapters FOR SELECT
    USING (true);

CREATE POLICY "Anyone can insert niche adapters"
    ON public.niche_adapters FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Anyone can update niche adapters"
    ON public.niche_adapters FOR UPDATE
    USING (true);

-- ============================================================================
-- Functions and Triggers
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for Users table
DROP TRIGGER IF EXISTS update_users_updated_at ON public.users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for NicheAdapters table
DROP TRIGGER IF EXISTS update_niche_adapters_updated_at ON public.niche_adapters;
CREATE TRIGGER update_niche_adapters_updated_at
    BEFORE UPDATE ON public.niche_adapters
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Comments for documentation
-- ============================================================================

COMMENT ON TABLE public.users IS 'Stores TikTok user profile information';
COMMENT ON TABLE public.trend_feed IS 'Stores trending content and analysis results';
COMMENT ON TABLE public.interaction_log IS 'Tracks user interactions with trends';
COMMENT ON TABLE public.niche_adapters IS 'Stores niche-specific content analysis and topic tags';

-- ============================================================================
-- Grants
-- ============================================================================

-- Grant permissions to authenticated users
GRANT ALL ON public.users TO authenticated;
GRANT ALL ON public.trend_feed TO authenticated;
GRANT ALL ON public.interaction_log TO authenticated;
GRANT ALL ON public.niche_adapters TO authenticated;

-- Grant permissions to service role
GRANT ALL ON public.users TO service_role;
GRANT ALL ON public.trend_feed TO service_role;
GRANT ALL ON public.interaction_log TO service_role;
GRANT ALL ON public.niche_adapters TO service_role;

