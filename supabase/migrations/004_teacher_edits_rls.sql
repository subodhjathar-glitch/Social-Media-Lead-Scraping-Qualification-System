-- Migration 004: Create teacher_edits table with RLS
-- Run this in the Supabase SQL Editor to fix:
--   "Could not find the table 'public.teacher_edits' in the schema cache"

-- Create table (safe: does nothing if it already exists)
CREATE TABLE IF NOT EXISTS teacher_edits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    teacher_id UUID REFERENCES teacher_profiles(id) ON DELETE CASCADE,
    pending_reply_id UUID REFERENCES pending_replies(id) ON DELETE CASCADE,
    original_ai_text TEXT NOT NULL,
    edited_text TEXT NOT NULL,
    edit_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changes_made TEXT[],
    sentiment_shift JSONB,
    key_phrases_added TEXT[],
    key_phrases_removed TEXT[],
    lead_context JSONB,
    CONSTRAINT different_texts CHECK (original_ai_text != edited_text)
);

CREATE INDEX IF NOT EXISTS idx_teacher_edits_teacher ON teacher_edits(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_edits_timestamp ON teacher_edits(edit_timestamp DESC);

-- Add learned_style columns to teacher_profiles if missing
ALTER TABLE teacher_profiles
    ADD COLUMN IF NOT EXISTS learned_style JSONB DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS common_phrases TEXT[] DEFAULT ARRAY[]::TEXT[],
    ADD COLUMN IF NOT EXISTS editing_patterns JSONB DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS last_learning_update TIMESTAMP WITH TIME ZONE;

-- Enable RLS
ALTER TABLE teacher_edits ENABLE ROW LEVEL SECURITY;

-- Allow service role (backend scraper) full access
CREATE POLICY "Allow all for service role" ON teacher_edits
    FOR ALL TO service_role USING (true);

-- Allow authenticated users (teachers via Streamlit) full access
CREATE POLICY "Allow all for authenticated users" ON teacher_edits
    FOR ALL TO authenticated USING (true);
