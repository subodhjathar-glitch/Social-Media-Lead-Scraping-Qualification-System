-- Teacher Learning System Migration
-- Enables AI to learn from teacher edits and adapt responses

-- Create table to store teacher edits for learning
CREATE TABLE IF NOT EXISTS teacher_edits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    teacher_id UUID REFERENCES teacher_profiles(id) ON DELETE CASCADE,
    pending_reply_id UUID REFERENCES pending_replies(id) ON DELETE CASCADE,
    original_ai_text TEXT NOT NULL,
    edited_text TEXT NOT NULL,
    edit_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Analysis fields
    changes_made TEXT[],
    sentiment_shift JSONB,
    key_phrases_added TEXT[],
    key_phrases_removed TEXT[],

    -- Context metadata
    lead_context JSONB,

    CONSTRAINT different_texts CHECK (original_ai_text != edited_text)
);

CREATE INDEX idx_teacher_edits_teacher ON teacher_edits(teacher_id);
CREATE INDEX idx_teacher_edits_timestamp ON teacher_edits(edit_timestamp DESC);

-- Add teacher style profile fields
ALTER TABLE teacher_profiles
ADD COLUMN IF NOT EXISTS learned_style JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS common_phrases TEXT[] DEFAULT ARRAY[]::TEXT[],
ADD COLUMN IF NOT EXISTS editing_patterns JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS last_learning_update TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN teacher_profiles.learned_style IS 'AI-learned style preferences from edits';
COMMENT ON COLUMN teacher_profiles.common_phrases IS 'Commonly used phrases by this teacher';
COMMENT ON COLUMN teacher_profiles.editing_patterns IS 'Detected patterns in how teacher edits responses';
