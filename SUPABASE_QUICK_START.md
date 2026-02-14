# Supabase Quick Start Guide

## Step 1: Execute Database Migration (5 minutes)

### 1.1 Open Supabase SQL Editor

1. Go to your Supabase project: https://supabase.com/dashboard
2. Click on your project
3. Navigate to **SQL Editor** in the left sidebar
4. Click **New Query**

### 1.2 Execute Migration Script

1. Open the file: `supabase/migrations/001_initial_schema.sql`
2. Copy **ALL** contents (lines 1-302)
3. Paste into Supabase SQL Editor
4. Click **Run** (or press Ctrl+Enter)
5. Wait for "Success. No rows returned" message

### 1.3 Verify Tables Created

1. Go to **Table Editor** in the left sidebar
2. You should see 5 tables:
   - ✅ `leads`
   - ✅ `teacher_profiles`
   - ✅ `conversation_threads`
   - ✅ `pending_replies`
   - ✅ `resources`

## Step 2: Seed Teacher Profiles (2 minutes)

### 2.1 Add Teacher Profiles

In the same SQL Editor, run this query to add your teacher profiles:

```sql
-- Add Teacher 1 (replace with actual info)
INSERT INTO teacher_profiles (
    teacher_name,
    email,
    contact_number,
    role,
    practice_experience,
    tone_preference,
    sign_off,
    daily_reply_limit,
    active
) VALUES (
    'Teacher Name 1',
    'teacher1@example.com',
    '+1234567890',
    'Isha Volunteer',
    '5+ years of Inner Engineering practice',
    'Compassionate',
    'Blessings,
Teacher Name 1',
    10,
    TRUE
);

-- Add Teacher 2 (replace with actual info)
INSERT INTO teacher_profiles (
    teacher_name,
    email,
    contact_number,
    role,
    practice_experience,
    tone_preference,
    sign_off,
    daily_reply_limit,
    active
) VALUES (
    'Teacher Name 2',
    'teacher2@example.com',
    '+0987654321',
    'Isha Practitioner',
    '3+ years of Isha Kriya practice',
    'Casual',
    'Warm regards,
Teacher Name 2',
    15,
    TRUE
);
```

**IMPORTANT:** Edit the teacher details before running!

### 2.2 Delete Pre-Seeded Resource (Per Plan)

The migration includes one pre-seeded resource. Let's remove it so you can add your own:

```sql
-- Remove pre-seeded resource
DELETE FROM resources WHERE resource_name = 'Isha Kriya Free Meditation';
```

## Step 3: Get Your Supabase Credentials

### 3.1 Find Your Project URL and API Key

1. Go to **Settings** → **API** in your Supabase dashboard
2. Copy the following:
   - **Project URL** (looks like: `https://abcdefg.supabase.co`)
   - **anon/public key** (long string starting with `eyJ...`)

### 3.2 Update Your .env File

Create or update `.env` file in the project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your_key_here

# Other API keys (if you already have them)
OPENAI_API_KEY=your_openai_key
YOUTUBE_API_KEY=your_youtube_key
```

## Step 4: Test Database Connection (1 minute)

Run this command to verify connectivity:

```bash
python -c "from src.database import SupabaseDatabase; db = SupabaseDatabase(); print('✅ Connected to Supabase!'); teachers = db.get_active_teachers(); print(f'Found {len(teachers)} active teachers')"
```

**Expected Output:**
```
✅ Connected to Supabase!
Found 2 active teachers
```

## Step 5: Run Small Scrape Test (Optional - 5 minutes)

Test the duplicate detection and scraping:

```bash
# This will scrape only NEW comments (no duplicates)
python src/main.py
```

The system will:
1. ✅ Scrape comments from YouTube
2. ✅ Pre-filter low-quality comments (70-90% filtered out)
3. ✅ Qualify leads using AI
4. ✅ Check for duplicates using lead_hash
5. ✅ Store only NEW, qualified leads

## Next Steps

Once database is set up and tested:

1. ✅ **Sprint 2**: Add authentication system
2. ✅ **Sprint 3**: Build Airtable-style approval sheet
3. ✅ **Sprint 4**: Integrate YouTube posting
4. ✅ **Sprint 5**: Add analytics & automation visibility

## Troubleshooting

### Error: "Invalid API key"
- Make sure you copied the **anon/public** key, not the service_role key
- Check for extra spaces in .env file

### Error: "Could not connect"
- Verify SUPABASE_URL ends with `.supabase.co`
- Check your internet connection
- Ensure project is not paused in Supabase dashboard

### Tables not created
- Run the migration script again (it's idempotent)
- Check for error messages in SQL Editor

## Support

- Supabase Docs: https://supabase.com/docs
- SQL Editor: https://supabase.com/dashboard/project/_/sql
