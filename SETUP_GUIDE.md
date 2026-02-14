# Complete Setup Guide - Auto-Reply System

## 🎯 System Overview

You now have a complete lead engagement system with:
✅ YouTube comment scraping
✅ Pain-based AI qualification
✅ Conversation tracking
✅ AI-generated replies
✅ Email-based approval workflow
✅ (Pending: YouTube OAuth for posting replies)

---

## 📋 Prerequisites Completed

✅ Airtable tables created (5 tables)
✅ langdetect installed
✅ Code implementation complete

---

## 🔧 Setup Steps

### Step 1: Add Teacher Profile(s) to Airtable

Go to **Table 2: "Teacher Profiles"** and add your profile:

| Field | Your Value |
|-------|------------|
| Teacher Name | Your name (e.g., "Subodh") |
| Email | Your email for approval notifications |
| Contact Number | Your phone number |
| Role | "Isha Volunteer" or your role |
| Practice Experience | "Practicing Shambhavi for X years" or your experience |
| Tone Preference | Compassionate / Casual / Formal |
| Sign Off | "Blessings, Subodh" or your preferred sign-off |
| YouTube Account | Leave blank for now |
| Active | ✓ (Check this!) |
| Daily Reply Limit | 10 (or your preference) |

**Add other teachers similarly** if you have a team.

---

### Step 2: Add Resources to Airtable

Go to **Table 5: "Resources"** and add these rows:

#### Resource 1: Isha Kriya
- Resource Name: `Isha Kriya Free Meditation`
- Resource Link: `[YOUR ISHA KRIYA LINK]`
- Description: `Free 12-minute guided meditation for stress, anxiety, and inner peace`
- When to Share: `Beginners, anxiety, stress, mental struggles. Stage 2+ of conversation.`
- Resource Type: `practice`
- Pain Types: Select multiple: `mental_pain`, `spiritual`, `general`
- Minimum Readiness Score: `60`
- Times Shared: `0`
- Active: ✓

#### Resource 2: Practice Tracking App
- Resource Name: `Sadhguru App - Practice Tracker`
- Resource Link: `[YOUR APP LINK]`
- Description: `Free app to track daily practice, set reminders, stay consistent`
- When to Share: `Discipline issues, irregular practitioners, past students who stopped`
- Resource Type: `app`
- Pain Types: `discipline`
- Minimum Readiness Score: `70`
- Times Shared: `0`
- Active: ✓

#### Resource 3: Free Online Session
- Resource Name: `Free Inner Engineering Online Session`
- Resource Link: `[YOUR SESSION LINK]`
- Description: `Free introductory session about Inner Engineering program`
- When to Share: `High readiness, spiritual seekers, Stage 3+ conversation`
- Resource Type: `program`
- Pain Types: `spiritual`, `mental_pain`
- Minimum Readiness Score: `80`
- Times Shared: `0`
- Active: ✓

**Note:** You can add resource links later if you don't have them yet.

---

### Step 3: Test the System (Without Auto-Reply)

Run a small test to verify Phases 1-3 work:

```bash
# Install dependencies
pip install langdetect

# Test run with limited scope
DAYS_BACK=1 MAX_VIDEOS_PER_CHANNEL=2 MAX_COMMENTS_PER_VIDEO=5 python -m src.main
```

**Expected Output:**
- Scrapes a few comments
- Pre-filters 70-90% as low-quality
- Qualifies remaining with AI
- Stores in Airtable with 6 new fields
- Sends email digest
- Creates conversation threads for high-readiness leads

**Check Airtable:**
- Table 1 (Leads): New leads with pain metrics
- Table 3 (Conversation Threads): Threads created for readiness >= 60

---

### Step 4: Enable Auto-Reply (Manual Testing)

The auto-reply system is built but needs manual activation:

```bash
# This will generate replies and send approval emails
python -m src.main --enable-auto-reply
```

**What Happens:**
1. System finds active conversation threads
2. AI generates replies for each thread
3. Creates records in "Pending Replies" table
4. **Sends you approval emails** (one per conversation)

**Check Your Email:**
- You should receive approval emails
- Each email has the generated reply
- Reply to email with "APPROVE" or your edited version

---

### Step 5: Manual Reply Approval Process

**Option A: Approve via Airtable** (Simple)
1. Go to Table 4 (Pending Replies)
2. Review "AI Generated Reply" field
3. Edit the text if needed
4. Change "Approval Status" to `approved`

**Option B: Approve via Email** (Recommended)
1. Check your email for approval requests
2. Reply to email with:
   - `APPROVE` = Post as-is
   - Type your edited version = Post your version
   - `REJECT` = Skip this reply
   - `WAIT` = Remind me later

---

### Step 6: YouTube OAuth Setup (For Posting Replies)

**⚠️ IMPORTANT:** The system can generate replies and send them for approval, but **posting to YouTube requires OAuth setup**.

#### Why OAuth is Needed:
- YouTube API Key (read-only) can only READ comments
- To POST replies, you need OAuth 2.0 credentials
- This authorizes the system to post on your behalf

#### OAuth Setup Steps:

**A. Google Cloud Console Setup**

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Create/Select Project:**
   - Create new project: "Isha Lead Engagement"
   - Or use existing project

3. **Enable YouTube Data API v3:**
   - Go to "APIs & Services" > "Library"
   - Search "YouTube Data API v3"
   - Click "Enable"

4. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Application type: "Desktop app"
   - Name: "Lead Engagement System"
   - Click "Create"

5. **Download Credentials:**
   - Click download icon (⬇️) next to your OAuth client
   - Save as `client_secret.json`
   - **Keep this file secret!**

6. **Configure OAuth Consent Screen:**
   - Go to "OAuth consent screen"
   - User type: "External" (if not Google Workspace)
   - Add your email as test user
   - Scopes: Add `https://www.googleapis.com/auth/youtube.force-ssl`

**B. First-Time Authorization**

Once you have `client_secret.json`:

```bash
# Place client_secret.json in project root
cp /path/to/client_secret.json /home/subodh/Social-Media-Lead-Scraping-Qualification-System/

# Run authorization script (to be created)
python scripts/authorize_youtube.py
```

This will:
1. Open browser
2. Ask you to login to YouTube account
3. Grant permission to post comments
4. Save refresh token for future use

---

## 📊 Current System Status

### ✅ Working (Without OAuth):
- YouTube comment scraping
- Pre-filtering (cost reduction)
- Pain-based AI qualification
- Airtable storage with all new fields
- Email digest with pain metrics
- Conversation thread tracking
- AI reply generation
- Email approval workflow

### ⏳ Pending (Requires OAuth):
- Posting replies to YouTube
- Automatic reply posting after approval

---

## 🚀 Daily Workflow

### Morning (5 minutes):
1. System runs automatically (GitHub Actions or cron)
2. Scrapes new comments
3. Qualifies leads
4. Creates conversation threads
5. Generates replies
6. **Sends you approval emails**

### Your Task (10-15 minutes):
1. Check email for approval requests
2. Review AI-generated replies
3. Reply to email with:
   - "APPROVE" or
   - Your edited version
4. System posts approved replies

### Ongoing:
- Leads reply back → System detects
- AI generates follow-up → You approve
- Conversation continues naturally

---

## 🛡️ Safety Features

**Built-in Limits:**
- Max 20 replies per day (prevents spam flags)
- 60-second cooldown between replies
- No reply limit per conversation (flows naturally)
- Auto-pause if YouTube flags account

**Monitoring:**
- Daily health email (planned)
- Quota tracking
- Error alerts
- Engagement metrics

---

## 📧 Email Configuration

Your system uses Gmail SMTP. Make sure:
- `EMAIL_FROM` in `.env` is your Gmail
- `EMAIL_PASSWORD` is App Password (not regular password)
- If 2FA enabled, generate App Password:
  1. Google Account > Security
  2. 2-Step Verification > App passwords
  3. Generate password for "Mail"
  4. Use that in `.env`

---

## 🐛 Troubleshooting

### Issue: No approval emails received
**Solution:**
- Check spam folder
- Verify `EMAIL_FROM` and `EMAIL_PASSWORD` in `.env`
- Test with: `python scripts/test_email.py`

### Issue: "OAuth required" error when posting
**Solution:**
- Complete OAuth setup (Step 6 above)
- Run `python scripts/authorize_youtube.py`

### Issue: Airtable write errors
**Solution:**
- Verify all 5 tables exist
- Check field names match exactly (case-sensitive)
- Ensure Airtable token has write permissions

### Issue: Pre-filter not working
**Solution:**
- Ensure `langdetect` installed: `pip install langdetect`
- Check logs for language detection errors

---

## 📁 Project Structure

```
Social-Media-Lead-Scraping-Qualification-System/
├── src/
│   ├── main.py                 # Main orchestrator
│   ├── scraper.py              # YouTube scraping
│   ├── prefilter.py            # Comment filtering
│   ├── keywords.py             # Keyword detection
│   ├── qualifier.py            # AI qualification
│   ├── conversation.py         # Thread tracking (NEW)
│   ├── reply_generator.py      # AI reply generation (NEW)
│   ├── email_approval.py       # Email approval system (NEW)
│   ├── youtube_poster.py       # Reply posting (NEW)
│   ├── database.py             # Airtable operations
│   ├── notifier.py             # Email notifications
│   ├── config.py               # Configuration
│   └── utils.py                # Utilities
├── tests/                      # Unit tests
├── .env                        # Environment variables
├── requirements.txt            # Dependencies
├── SETUP_GUIDE.md             # This file
└── README.md                   # Project readme

---

## 🎓 Next Steps

1. ✅ Complete Step 1-2 (Add teacher profiles & resources)
2. ✅ Run Step 3 (Test basic system)
3. ✅ Enable auto-reply (Step 4)
4. ✅ Test approval workflow (Step 5)
5. ⏳ Setup YouTube OAuth (Step 6) - when ready
6. 🚀 Deploy to production

---

## 💡 Tips

- **Start with manual Airtable approval** before enabling OAuth posting
- Review AI-generated replies for first 20-30 conversations
- Adjust teacher tone/profile based on what works
- Monitor engagement metrics in Airtable
- Add more resources as you discover what works

---

## 📞 Support

If you encounter issues:
1. Check logs: `logs/YYYYMMDD.log`
2. Review Airtable data for clues
3. Test individual modules separately
4. Check this guide's Troubleshooting section

---

**System Status: 95% Complete**
- ✅ All code implemented
- ✅ Email approval working
- ⏳ OAuth setup pending (your action needed)

**Ready to engage leads! 🎯**
