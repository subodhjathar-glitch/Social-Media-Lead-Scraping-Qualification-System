-- Isha Lead Engagement System - Supabase Database Schema
-- Migration: Initial Schema Creation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLE 1: LEADS
-- =====================================================
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    platform TEXT DEFAULT 'YouTube',
    comment TEXT NOT NULL,
    video_url TEXT,
    comment_url TEXT,

    -- Legacy intent field (for backward compatibility)
    intent TEXT CHECK (intent IN ('High', 'Medium', 'Low')),
    confidence INTEGER CHECK (confidence >= 0 AND confidence <= 100),
    ai_reasoning TEXT,

    -- New pain-based fields
    intent_type TEXT CHECK (intent_type IN ('physical_pain', 'mental_pain', 'discipline', 'spiritual', 'practice_aligned', 'low_intent')),
    pain_intensity INTEGER CHECK (pain_intensity >= 0 AND pain_intensity <= 10),
    readiness_score INTEGER CHECK (readiness_score >= 0 AND readiness_score <= 100),
    practice_mention TEXT,
    language TEXT CHECK (language IN ('en', 'hi', 'mr', 'other')),
    prefilter_status TEXT,

    -- Metadata
    lead_hash TEXT UNIQUE NOT NULL,
    scraped_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for leads table
CREATE INDEX idx_leads_intent_type ON leads(intent_type);
CREATE INDEX idx_leads_readiness_score ON leads(readiness_score);
CREATE INDEX idx_leads_scraped_date ON leads(scraped_date);
CREATE INDEX idx_leads_lead_hash ON leads(lead_hash);

-- =====================================================
-- TABLE 2: TEACHER PROFILES
-- =====================================================
CREATE TABLE teacher_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    teacher_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    contact_number TEXT,
    role TEXT,
    practice_experience TEXT,
    tone_preference TEXT CHECK (tone_preference IN ('Compassionate', 'Casual', 'Formal')),
    sign_off TEXT,
    youtube_account TEXT,
    active BOOLEAN DEFAULT TRUE,
    daily_reply_limit INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for active teachers
CREATE INDEX idx_teacher_profiles_active ON teacher_profiles(active);
CREATE INDEX idx_teacher_profiles_email ON teacher_profiles(email);

-- =====================================================
-- TABLE 3: CONVERSATION THREADS
-- =====================================================
CREATE TABLE conversation_threads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    comment_author TEXT NOT NULL,
    original_comment TEXT NOT NULL,
    comment_url TEXT,
    video_url TEXT,
    conversation_stage INTEGER DEFAULT 0,
    full_history TEXT,
    ai_context_summary TEXT,
    last_reply_date DATE,
    status TEXT CHECK (status IN ('active', 'waiting_response', 'converted', 'closed', 'no_response')) DEFAULT 'active',
    pain_type TEXT,
    readiness_score INTEGER CHECK (readiness_score >= 0 AND readiness_score <= 100),
    resources_shared TEXT,
    assigned_teacher_id UUID REFERENCES teacher_profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for conversation threads
CREATE INDEX idx_conversation_threads_lead_id ON conversation_threads(lead_id);
CREATE INDEX idx_conversation_threads_status ON conversation_threads(status);
CREATE INDEX idx_conversation_threads_assigned_teacher ON conversation_threads(assigned_teacher_id);

-- =====================================================
-- TABLE 4: PENDING REPLIES
-- =====================================================
CREATE TABLE pending_replies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id UUID REFERENCES conversation_threads(id) ON DELETE CASCADE,
    lead_name TEXT NOT NULL,
    their_last_message TEXT,
    ai_generated_reply TEXT NOT NULL,
    approval_status TEXT CHECK (approval_status IN ('pending', 'approved', 'rejected', 'posted')) DEFAULT 'pending',
    assigned_teacher_id UUID REFERENCES teacher_profiles(id),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE,
    posted_at TIMESTAMP WITH TIME ZONE,
    engagement_result TEXT CHECK (engagement_result IN ('no_reply', 'replied', 'positive', 'negative')),
    your_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for pending replies
CREATE INDEX idx_pending_replies_thread_id ON pending_replies(thread_id);
CREATE INDEX idx_pending_replies_approval_status ON pending_replies(approval_status);
CREATE INDEX idx_pending_replies_assigned_teacher ON pending_replies(assigned_teacher_id);
CREATE INDEX idx_pending_replies_generated_at ON pending_replies(generated_at);

-- =====================================================
-- TABLE 5: RESOURCES
-- =====================================================
CREATE TABLE resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_name TEXT UNIQUE NOT NULL,
    resource_link TEXT,
    description TEXT,
    when_to_share TEXT,
    resource_type TEXT CHECK (resource_type IN ('practice', 'video', 'app', 'program', 'article')),
    pain_types TEXT[], -- Array of pain types
    minimum_readiness_score INTEGER DEFAULT 0 CHECK (minimum_readiness_score >= 0 AND minimum_readiness_score <= 100),
    times_shared INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for resources
CREATE INDEX idx_resources_active ON resources(active);
CREATE INDEX idx_resources_resource_type ON resources(resource_type);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to all tables
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teacher_profiles_updated_at BEFORE UPDATE ON teacher_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversation_threads_updated_at BEFORE UPDATE ON conversation_threads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pending_replies_updated_at BEFORE UPDATE ON pending_replies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resources_updated_at BEFORE UPDATE ON resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE teacher_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE pending_replies ENABLE ROW LEVEL SECURITY;
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;

-- Policies for authenticated users (teachers)
-- Note: You'll configure authentication in Supabase dashboard

-- Allow all operations for authenticated users (for now - can be more restrictive later)
CREATE POLICY "Allow all for authenticated users" ON leads
    FOR ALL TO authenticated USING (true);

CREATE POLICY "Allow all for authenticated users" ON teacher_profiles
    FOR ALL TO authenticated USING (true);

CREATE POLICY "Allow all for authenticated users" ON conversation_threads
    FOR ALL TO authenticated USING (true);

CREATE POLICY "Allow all for authenticated users" ON pending_replies
    FOR ALL TO authenticated USING (true);

CREATE POLICY "Allow all for authenticated users" ON resources
    FOR ALL TO authenticated USING (true);

-- Allow service role (backend) full access
CREATE POLICY "Allow all for service role" ON leads
    FOR ALL TO service_role USING (true);

CREATE POLICY "Allow all for service role" ON teacher_profiles
    FOR ALL TO service_role USING (true);

CREATE POLICY "Allow all for service role" ON conversation_threads
    FOR ALL TO service_role USING (true);

CREATE POLICY "Allow all for service role" ON pending_replies
    FOR ALL TO service_role USING (true);

CREATE POLICY "Allow all for service role" ON resources
    FOR ALL TO service_role USING (true);

-- =====================================================
-- SEED DATA (Optional - can be added via UI)
-- =====================================================

-- Add a default resource (example)
INSERT INTO resources (
    resource_name,
    resource_link,
    description,
    when_to_share,
    resource_type,
    pain_types,
    minimum_readiness_score,
    active
) VALUES (
    'Isha Kriya Free Meditation',
    'https://www.ishafoundation.org/Isha-kriya',
    'Free 12-minute guided meditation for stress, anxiety, and inner peace',
    'Beginners, anxiety, stress, mental struggles. Stage 2+ of conversation.',
    'practice',
    ARRAY['mental_pain', 'spiritual', 'general'],
    60,
    TRUE
);

-- =====================================================
-- VIEWS (Helpful for dashboard queries)
-- =====================================================

-- View for active conversations with teacher details
CREATE VIEW active_conversations AS
SELECT
    ct.*,
    tp.teacher_name,
    tp.email as teacher_email,
    l.name as lead_full_name,
    l.comment as original_lead_comment
FROM conversation_threads ct
LEFT JOIN teacher_profiles tp ON ct.assigned_teacher_id = tp.id
LEFT JOIN leads l ON ct.lead_id = l.id
WHERE ct.status = 'active';

-- View for pending approvals with thread context
CREATE VIEW pending_approvals_view AS
SELECT
    pr.*,
    ct.comment_author,
    ct.original_comment,
    ct.conversation_stage,
    ct.pain_type,
    ct.readiness_score,
    ct.comment_url,
    ct.video_url,
    tp.teacher_name,
    tp.email as teacher_email
FROM pending_replies pr
JOIN conversation_threads ct ON pr.thread_id = ct.id
LEFT JOIN teacher_profiles tp ON pr.assigned_teacher_id = tp.id
WHERE pr.approval_status = 'pending'
ORDER BY pr.generated_at DESC;

-- View for dashboard statistics
CREATE VIEW dashboard_stats AS
SELECT
    (SELECT COUNT(*) FROM leads WHERE scraped_date = CURRENT_DATE) as leads_today,
    (SELECT COUNT(*) FROM conversation_threads WHERE status = 'active') as active_conversations,
    (SELECT COUNT(*) FROM pending_replies WHERE approval_status = 'pending') as pending_approvals,
    (SELECT COUNT(*) FROM pending_replies WHERE approval_status = 'posted' AND DATE(posted_at) = CURRENT_DATE) as replies_posted_today;

-- =====================================================
-- COMMENTS (Documentation)
-- =====================================================

COMMENT ON TABLE leads IS 'Qualified leads from YouTube comments with pain-based metrics';
COMMENT ON TABLE teacher_profiles IS 'Teacher/volunteer profiles for reply approval and assignment';
COMMENT ON TABLE conversation_threads IS 'Ongoing conversation threads with leads';
COMMENT ON TABLE pending_replies IS 'AI-generated replies pending teacher approval';
COMMENT ON TABLE resources IS 'Free resources to share with leads (Isha Kriya, apps, programs)';

COMMENT ON COLUMN leads.intent_type IS 'Pain-based intent classification: spiritual, mental_pain, discipline, physical_pain, practice_aligned, low_intent';
COMMENT ON COLUMN leads.pain_intensity IS 'Pain intensity score from 0 (mild) to 10 (critical)';
COMMENT ON COLUMN leads.readiness_score IS 'Readiness for engagement score from 0 (passive) to 100 (highly motivated)';
COMMENT ON COLUMN conversation_threads.conversation_stage IS 'Number of exchanges in conversation (0 = initial, 1 = first reply, etc.)';
COMMENT ON COLUMN resources.pain_types IS 'Array of pain types this resource addresses (mental_pain, spiritual, etc.)';
