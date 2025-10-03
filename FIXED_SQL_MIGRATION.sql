-- ============================================================================
-- FIXED: Create scan_history table (handles existing policies)
-- ============================================================================

-- Step 1: Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own scan history" ON public.scan_history;
DROP POLICY IF EXISTS "Users can insert own scans" ON public.scan_history;
DROP POLICY IF EXISTS "Users can delete own scans" ON public.scan_history;

-- Step 2: Create table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.scan_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  username text NOT NULL,
  profile_data jsonb NOT NULL,
  scan_type text NOT NULL DEFAULT 'free' CHECK (scan_type IN ('free', 'paid')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Step 3: Drop existing indexes if they exist and recreate
DROP INDEX IF EXISTS public.idx_scan_history_user_id;
DROP INDEX IF EXISTS public.idx_scan_history_created_at;
DROP INDEX IF EXISTS public.idx_scan_history_username;

-- Create indexes for faster lookups
CREATE INDEX idx_scan_history_user_id ON public.scan_history(user_id);
CREATE INDEX idx_scan_history_created_at ON public.scan_history(created_at DESC);
CREATE INDEX idx_scan_history_username ON public.scan_history(username);

-- Step 4: Enable Row Level Security
ALTER TABLE public.scan_history ENABLE ROW LEVEL SECURITY;

-- Step 5: Create RLS Policies (now they won't exist)
CREATE POLICY "Users can view own scan history" ON public.scan_history
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own scans" ON public.scan_history
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own scans" ON public.scan_history
  FOR DELETE
  USING (auth.uid() = user_id);

-- Step 6: Grant permissions to authenticated users
GRANT SELECT, INSERT, DELETE ON public.scan_history TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;

-- Step 7: Add helpful comments
COMMENT ON TABLE public.scan_history IS 'Stores history of TikTok profile scans performed by users';
COMMENT ON COLUMN public.scan_history.user_id IS 'Reference to the user who performed the scan';
COMMENT ON COLUMN public.scan_history.username IS 'TikTok username that was scanned';
COMMENT ON COLUMN public.scan_history.profile_data IS 'Complete profile data from the scan stored as JSON';
COMMENT ON COLUMN public.scan_history.scan_type IS 'Type of scan: free (trial) or paid (subscription)';

-- Verification: Show what was created
SELECT 
  'scan_history table created successfully!' as status,
  COUNT(*) as policy_count
FROM pg_policies 
WHERE tablename = 'scan_history';

