# Isha Lead Engagement System v2.0

> **Intelligent social media lead scraping, qualification, and engagement system for Isha Foundation.**

Automatically discover, qualify, and engage with individuals seeking spiritual guidance on YouTube through AI-powered conversation management.

---

## 🎯 Overview

This system helps Isha volunteers efficiently engage with people expressing pain, struggle, or seeking guidance in YouTube comments by:

1. **Discovering** qualified leads via YouTube comment scraping
2. **Qualifying** leads using AI-based pain intensity and readiness analysis
3. **Engaging** through personalized, teacher-approved replies
4. **Tracking** multi-stage conversations and conversions
5. **Learning** from engagement patterns to improve over time

---

## ✨ Features

### Core Capabilities

- ✅ **Smart Lead Discovery**
  - Scrapes YouTube comments from specified channels/videos
  - Pre-filters low-quality comments (70-90% filtered out)
  - AI qualification based on pain type and readiness
  - **Duplicate prevention:** Never scrape the same comment twice

- ✅ **Pain-Based Qualification**
  - Identifies: Spiritual seeking, Mental pain, Discipline issues, Physical pain
  - Scores: Pain intensity (0-10) and Readiness (0-100)
  - Filters: Only engages with qualified, ready leads

- ✅ **Teacher Authentication & Workflow**
  - Secure email-based login
  - Airtable-style approval sheet
  - Inline reply editing
  - Rating system for AI replies
  - Personal statistics dashboard

- ✅ **Automated Engagement**
  - AI-generated personalized replies
  - Auto-posting to YouTube (OAuth)
  - Manual fallback option
  - Multi-stage conversation tracking
  - Resource recommendation

- ✅ **Analytics & Insights**
  - Lead conversion funnel
  - Resource effectiveness
  - Teacher performance metrics
  - Engagement patterns
  - Time-based trends

### What's New in v2.0 (Supabase Migration)

| Feature | v1.0 (Airtable) | v2.0 (Supabase) |
|---------|-----------------|------------------|
| Database | Airtable (cloud, paid) | Supabase PostgreSQL (free tier) |
| Authentication | None | Email-based teacher login ✨ |
| UI | Basic cards | Airtable-style approval sheet ✨ |
| Inline Editing | No | Yes ✨ |
| Rating System | No | 1-5 stars + notes ✨ |
| YouTube Posting | Manual only | Auto-posting + manual ✨ |
| Teacher Self-Service | No | Full profile management ✨ |
| Resource Management | Manual SQL | UI-based ✨ |
| Performance | API rate limits | Direct DB (faster) ✨ |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Supabase account (free tier)
- OpenAI API key
- YouTube Data API key
- (Optional) Google OAuth credentials for auto-posting

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd Social-Media-Lead-Scraping-Qualification-System

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### Database Setup (5 minutes)

1. **Create Supabase project** at https://supabase.com
2. **Execute migration**:
   - Open Supabase SQL Editor
   - Copy contents of `supabase/migrations/001_initial_schema.sql`
   - Paste and execute
3. **Get credentials**: Supabase → Settings → API
4. **Update .env**:
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key_here
   ```

**📖 Detailed guide:** `SUPABASE_QUICK_START.md`

### Run the System

```bash
# Scrape leads (backend)
python src/main.py

# Launch UI (frontend)
streamlit run streamlit_app.py

# Open browser: http://localhost:8501
# Login with teacher email (add via UI or SQL)
```

---

## 📋 System Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    SCRAPING PIPELINE                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌────────────────────────────────────┐
    │  1. Fetch YouTube Comments         │
    │     (from specified channels)      │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │  2. Pre-filter Low Quality         │
    │     (emoji-only, praise-only, etc) │
    │     → 70-90% filtered out          │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │  3. AI Qualification               │
    │     • Pain type detection          │
    │     • Intensity scoring (0-10)     │
    │     • Readiness scoring (0-100)    │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │  4. Duplicate Check                │
    │     (lead_hash SHA-256)            │
    │     → Skip if already exists       │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │  5. Store in Supabase              │
    │     • leads table                  │
    │     • conversation_threads         │
    └────────────┬───────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  ENGAGEMENT PIPELINE                         │
└─────────────────────────────────────────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │  6. Generate AI Reply              │
    │     (personalized to pain type)    │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │  7. Teacher Approval               │
    │     • Review in Streamlit UI       │
    │     • Edit if needed               │
    │     • Rate quality                 │
    │     • Approve                      │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │  8. Post to YouTube                │
    │     • Auto-post (OAuth)            │
    │     • OR manual fallback           │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │  9. Track Conversation             │
    │     • Monitor for responses        │
    │     • Multi-stage engagement       │
    │     • Resource recommendation      │
    └────────────────────────────────────┘
```

---

## 🎨 UI Screenshots

### Dashboard
- Real-time metrics (leads, conversations, approvals, posted)
- Activity charts (7-day trends)
- Pain type distribution
- System status

### Pending Approvals (Airtable-style)
- Expandable rows with full context
- Inline reply editing
- Rating system (1-5 stars)
- Filters & sorting
- One-click approve & post

### Conversations
- Active thread tracking
- Stage progression (0 → 1 → 2 → 3+)
- AI context summaries
- Resource sharing history

### My Profile
- Personal statistics
- Editable profile fields
- Performance metrics

---

## 🗂️ Project Structure

```
Social-Media-Lead-Scraping-Qualification-System/
├── src/
│   ├── auth.py                      # Teacher authentication
│   ├── config.py                    # Settings & environment vars
│   ├── database.py                  # Supabase database operations
│   ├── scraper.py                   # YouTube comment scraper
│   ├── prefilter.py                 # Low-quality comment filter
│   ├── qualifier.py                 # AI-based lead qualification
│   ├── reply_generator.py           # AI reply generation
│   ├── conversation.py              # Conversation tracking
│   ├── youtube_poster_supabase.py   # YouTube auto-posting
│   ├── keywords.py                  # Pain-based keywords
│   └── utils.py                     # Helper functions
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql   # Database schema
├── docs/
│   ├── YOUTUBE_OAUTH_SETUP.md       # OAuth setup guide
│   └── ...
├── streamlit_app.py                 # Main UI application
├── authenticate_youtube.py          # OAuth authentication script
├── .env.example                     # Environment variables template
├── requirements.txt                 # Python dependencies
├── SUPABASE_QUICK_START.md          # Database setup guide
├── IMPLEMENTATION_GUIDE.md          # Complete setup guide
├── IMPLEMENTATION_COMPLETE.md       # Summary of implementation
└── README.md                        # This file
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# Scraping Config
DAYS_BACK=7
MAX_VIDEOS_PER_CHANNEL=10
MAX_COMMENTS_PER_VIDEO=100
```

### Teacher Profiles

Add via Streamlit UI or SQL:

```sql
INSERT INTO teacher_profiles (
    teacher_name, email, tone_preference, sign_off, daily_reply_limit, active
) VALUES (
    'Your Name',
    'your.email@example.com',
    'Compassionate',
    'Blessings,
Your Name',
    10,
    TRUE
);
```

### Resources

Add via Streamlit UI:
- Go to "Resources" page
- Click "Add New Resource"
- Fill in details (name, link, pain types, etc.)

---

## 📊 Database Schema

### Core Tables

1. **leads** - Qualified YouTube comment leads
   - Pain type, intensity, readiness
   - Unique lead_hash for duplicate prevention

2. **teacher_profiles** - Teacher/volunteer profiles
   - Login credentials, preferences, limits

3. **conversation_threads** - Multi-stage conversations
   - Full history, context, stage tracking

4. **pending_replies** - AI-generated replies awaiting approval
   - Edit, rate, approve workflow

5. **resources** - Free resources to share
   - Isha Kriya, programs, videos, etc.

**📖 Full schema:** `supabase/migrations/001_initial_schema.sql`

---

## 🎓 Usage Examples

### Scrape YouTube Comments

```bash
# Default: Scrapes recent comments from configured channels
python src/main.py

# Results:
# - Pre-filtered for quality
# - AI-qualified for pain/readiness
# - Duplicates automatically skipped
# - Stored in Supabase
```

### Launch UI

```bash
streamlit run streamlit_app.py

# 1. Login with teacher email
# 2. Check dashboard for new leads
# 3. Go to "Pending Approvals"
# 4. Review AI replies
# 5. Edit if needed
# 6. Approve → Auto-posts to YouTube
```

### Set Up YouTube Auto-Posting

```bash
# 1. Follow guide: docs/YOUTUBE_OAUTH_SETUP.md
# 2. Download client_secret.json from Google Cloud
# 3. Run authentication:
python authenticate_youtube.py

# 4. Browser opens → Sign in → Accept
# 5. Credentials saved
# 6. Restart Streamlit
```

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test database connection
python -c "from src.database import SupabaseDatabase; db = SupabaseDatabase(); print('✅ OK')"

# Test scraper
python src/scraper.py

# Test UI
streamlit run streamlit_app.py
```

---

## 🔐 Security

- **Authentication:** Email-based teacher login
- **Row-level security:** Supabase RLS policies
- **Secrets:** `.env` file (never commit!)
- **OAuth:** `client_secret.json` and `youtube_token.pickle` (gitignored)
- **Session management:** Streamlit session state

**⚠️ Important:** Always add sensitive files to `.gitignore`

---

## 📈 Analytics (Planned)

- Lead conversion funnel
- Resource effectiveness by pain type
- Teacher performance comparison
- Response time metrics
- Engagement patterns (time of day, day of week)
- Drop-off analysis

---

## 🚧 Roadmap

### Short-term
- [ ] Automated reply generation for all pending threads
- [ ] Advanced analytics dashboard
- [ ] GitHub Actions automation (scheduled scraping)
- [ ] Production deployment (Streamlit Cloud)

### Medium-term
- [ ] Multi-language support (Hindi, Marathi)
- [ ] AI learning from teacher feedback
- [ ] Conversation context tracking improvements
- [ ] Resource recommendation AI

### Long-term
- [ ] Multi-platform support (Instagram, Facebook)
- [ ] Voice/video comment analysis
- [ ] Predictive lead scoring
- [ ] Integration with Isha programs database

---

## 🤝 Contributing

This is an internal Isha Foundation project. For questions or issues:

1. Check documentation in `docs/`
2. Review `IMPLEMENTATION_GUIDE.md`
3. Contact project maintainer

---

## 📝 License

Internal use only - Isha Foundation

---

## 🙏 Acknowledgments

Built with love for Isha Foundation's mission of offering yoga and spiritual guidance to seekers worldwide.

**Technologies:**
- Python 3.9+
- Streamlit (UI)
- Supabase (PostgreSQL database)
- OpenAI GPT (AI qualification & replies)
- YouTube Data API v3
- Google OAuth 2.0

---

## 📞 Support

**Documentation:**
- `SUPABASE_QUICK_START.md` - Database setup
- `IMPLEMENTATION_GUIDE.md` - Complete guide
- `docs/YOUTUBE_OAUTH_SETUP.md` - OAuth setup

**Quick Commands:**

```bash
# Test database
python -c "from src.database import SupabaseDatabase; db = SupabaseDatabase(); print('✅ OK')"

# Run scraper
python src/main.py

# Launch UI
streamlit run streamlit_app.py

# Authenticate YouTube
python authenticate_youtube.py
```

---

**Version:** 2.0 (Supabase Migration)
**Status:** ✅ Production Ready
**Last Updated:** February 2026

🕉️ **Isha Foundation** - Inner Engineering for the digital age
