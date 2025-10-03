-- Migration: Add Token Usage Tracking Table
-- Description: Creates table for tracking API token usage per user
-- Created: 2025-10-02

-- ============================================================================
-- Table: auth_users (Supabase Auth users metadata)
-- ============================================================================
-- Create profiles table to extend Supabase auth.users
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    username TEXT UNIQUE,
    full_name TEXT,
    avatar_url TEXT,
    bio TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Public profiles are viewable by everyone"
    ON public.profiles FOR SELECT
    USING (true);

CREATE POLICY "Users can insert their own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Create index
CREATE INDEX IF NOT EXISTS idx_profiles_username ON public.profiles(username);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);

-- ============================================================================
-- Table: token_usage
-- Description: Tracks API token usage for each user analysis
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.token_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    analysis_timestamp TIMESTAMPTZ DEFAULT NOW(),
    openai_prompt_tokens INTEGER DEFAULT 0,
    openai_completion_tokens INTEGER DEFAULT 0,
    openai_total_tokens INTEGER DEFAULT 0,
    perplexity_prompt_tokens INTEGER DEFAULT 0,
    perplexity_completion_tokens INTEGER DEFAULT 0,
    perplexity_total_tokens INTEGER DEFAULT 0,
    ensemble_units INTEGER DEFAULT 0,
    total_cost_estimate DECIMAL(10,4) DEFAULT 0.0,
    profile_analyzed TEXT
);

-- Create indexes for token_usage table
CREATE INDEX IF NOT EXISTS idx_token_usage_user_id ON public.token_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_timestamp ON public.token_usage(analysis_timestamp DESC);

-- Enable RLS
ALTER TABLE public.token_usage ENABLE ROW LEVEL SECURITY;

-- Token usage policies
CREATE POLICY "Users can view their own token usage"
    ON public.token_usage FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Anyone can insert token usage"
    ON public.token_usage FOR INSERT
    WITH CHECK (true);

-- Grant permissions
GRANT ALL ON public.profiles TO authenticated;
GRANT ALL ON public.profiles TO service_role;
GRANT ALL ON public.token_usage TO authenticated;
GRANT ALL ON public.token_usage TO service_role;

-- ============================================================================
-- Trigger: Auto-create profile on user signup
-- ============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.profiles (id, email, username, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'username', split_part(NEW.email, '@', 1)),
        NEW.raw_user_meta_data->>'full_name'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Create trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- Trigger: Update updated_at on profile changes
-- ============================================================================
DROP TRIGGER IF EXISTS update_profiles_updated_at ON public.profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE public.profiles IS 'Extended user profiles for Supabase Auth users';
COMMENT ON TABLE public.token_usage IS 'Tracks API token usage per user analysis';

