# 🚀 Getting Started - Quick Setup Guide

Everything is ready to run! Follow these steps to get the system working in **5 minutes**.

---

## ✅ System Status

**All components verified and working:**
- ✅ Python 3.12.3 + Virtual environment
- ✅ All dependencies installed
- ✅ Supabase database connected
- ✅ Environment variables configured
- ✅ Authentication system ready
- ✅ File structure complete

---

## 🎯 Quick Start (Choose One Path)

### Option A: Automated Startup (Recommended)

**One command to rule them all:**

```bash
./start_system.sh
```

This script will:
1. Check system health
2. Ask what you want to do:
   - Run scraper only
   - Launch UI only
   - Both scraper + UI

**That's it!** Just run the script and follow the prompts.

---

### Option B: Manual Commands (More Control)

#### 1. Run System Health Check (Optional but recommended)

```bash
./venv/bin/python3 system_check.py
```

**Expected output:** "🎉 All checks passed! System is ready to run."

#### 2. Run the Scraper (Collect Leads)

```bash
./venv/bin/python3 src/main.py
```

**What happens:**
- Scrapes YouTube comments from configured channels
- Pre-filters low-quality comments (70-90% filtered out)
- AI qualifies leads (pain type, intensity, readiness)
- Checks for duplicates (SHA-256 hash)
- Stores ONLY new, qualified leads in Supabase

**Output:**
```
Starting YouTube Lead Scraper...
Found X videos to process
Processing comments...
Pre-filtered: XX/YY comments passed
AI Qualification: ZZ qualified leads
Duplicate check: AA duplicates skipped
Stored: BB new leads in database
✅ Scraping complete!
```

#### 3. Launch the UI (Frontend)

```bash
./venv/bin/streamlit run streamlit_app.py
```

**What happens:**
- Streamlit UI starts on http://localhost:8501
- Browser opens automatically (if not, open manually)
- Login page appears

**Login:**
- Email: `subodh.jathar@gmail.com` (or any allowed email from .env)
- Click "Continue"
- ✅ You're in!

---

## 📱 Using the Frontend

### Pages Overview

1. **📊 Dashboard**
   - View metrics: leads today, active conversations, pending approvals
   - Charts: leads over time, pain type distribution, readiness scores
   - System status

2. **✅ Pending Approvals** (MAIN PAGE)
   - See all AI-generated replies awaiting approval
   - **Edit replies** inline
   - **Rate quality** (1-5 stars)
   - **Add notes**
   - **Approve & Post** to YouTube (or manual fallback)

3. **💬 Conversations**
   - View active conversation threads
   - See multi-stage progression (Stage 0 → 1 → 2 → 3+)
   - Track resources shared

4. **📋 Leads**
   - All qualified leads from scraping
   - Filter by pain type, readiness, date
   - Export to CSV

5. **👥 Teachers**
   - Add/edit teacher profiles
   - Set daily reply limits
   - Manage preferences

6. **📚 Resources**
   - Add resources (Isha Kriya, programs, etc.)
   - No manual SQL needed!
   - Track sharing frequency

7. **📈 Analytics** (Coming Soon)
   - Advanced insights

8. **👤 My Profile**
   - Edit your teacher profile
   - View personal statistics

---

## 🔄 Typical Workflow

### Daily Routine for Teachers

```
1. Morning: Run Scraper
   └─> ./venv/bin/python3 src/main.py

2. Check Dashboard
   └─> See new leads count

3. Review Pending Approvals
   └─> Edit AI replies if needed
   └─> Rate quality
   └─> Approve & Auto-post to YouTube

4. Monitor Conversations
   └─> Track lead responses
   └─> Continue engagement

5. Evening: Add Resources (if needed)
   └─> Keep library updated
```

### First-Time Setup (One-Time Tasks)

**1. Add Teacher Profiles** (if not done yet)

Via UI:
1. Login
2. Go to "Teachers" page
3. Click "Add New Teacher"
4. Fill in details:
   - Name: Your Name
   - Email: your.email@example.com
   - Tone: Compassionate
   - Sign-off: "Blessings, Your Name"
   - Daily Limit: 10
5. Click "Add"

**2. Add Resources**

1. Go to "Resources" page
2. Click "Add New Resource"
3. Example:
   - Name: Isha Kriya Free Meditation
   - Link: https://www.ishafoundation.org/Isha-kriya
   - Description: Free 12-minute guided meditation
   - Type: practice
   - Pain Types: mental_pain, spiritual, general
   - Min Readiness: 60
4. Click "Add Resource"

Repeat for other resources (Inner Engineering, practice app, etc.)

---

## 🐛 Troubleshooting

### Issue: "Name or service not known" error

**Cause:** Network/DNS issue connecting to Supabase

**Solutions:**

1. **Check internet connection**
   ```bash
   ping google.com
   ```

2. **If on WSL, fix DNS:**
   ```bash
   echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
   ```

3. **Test Supabase connection:**
   ```bash
   ./venv/bin/python3 -c "from src.database import SupabaseDatabase; db = SupabaseDatabase(); print('OK')"
   ```

4. **Verify .env credentials:**
   - Open `.env` file
   - Check `SUPABASE_URL` and `SUPABASE_KEY` are correct
   - No typos, no extra spaces

### Issue: Can't login to UI

**Cause:** Email not in allowed list

**Solution:**
1. Check `.env` file for `ALLOWED_EMAILS`
2. Add your email: `ALLOWED_EMAILS=email1@example.com,email2@example.com`
3. Restart UI

### Issue: No leads after scraping

**Possible causes:**
1. All comments already in database (duplicates)
2. Pre-filter too aggressive
3. No qualified comments in time period
4. YouTube quota exceeded

**Check logs:**
```bash
tail -50 logs/scraper.log
```

### Issue: Frontend shows "Error loading..."

**Solutions:**
1. Check Supabase connection (see first troubleshooting item)
2. Verify database tables exist (run migration if needed)
3. Check browser console for errors (F12 → Console)

---

## 📊 Database Setup (If Not Done)

**Only if tables don't exist yet:**

1. Open Supabase SQL Editor: https://supabase.com/dashboard
2. Copy entire contents of: `supabase/migrations/001_initial_schema.sql`
3. Paste into SQL Editor
4. Click "Run"
5. Verify 5 tables created: leads, teacher_profiles, conversation_threads, pending_replies, resources

**📖 Full guide:** `SUPABASE_QUICK_START.md`

---

## 🔐 YouTube Auto-Posting (Optional)

**Skip this initially - use manual posting instead**

When ready to enable auto-posting:
1. Follow guide: `docs/YOUTUBE_OAUTH_SETUP.md`
2. Run: `./venv/bin/python3 authenticate_youtube.py`
3. Complete OAuth in browser
4. Restart UI

**Result:** Approved replies auto-post to YouTube!

---

## 📁 Quick Command Reference

```bash
# System health check
./venv/bin/python3 system_check.py

# Run scraper
./venv/bin/python3 src/main.py

# Launch UI
./venv/bin/streamlit run streamlit_app.py

# Automated startup (recommended)
./start_system.sh

# Check logs
tail -50 logs/scraper.log
tail -50 logs/qualifier.log
tail -50 logs/database.log

# Test database
./venv/bin/python3 -c "from src.database import SupabaseDatabase; db = SupabaseDatabase(); print('✅ OK')"

# YouTube authentication
./venv/bin/python3 authenticate_youtube.py
```

---

## 🎓 Next Steps

### Today (First Run)
1. ✅ Run system check: `./venv/bin/python3 system_check.py`
2. ✅ Run scraper: `./venv/bin/python3 src/main.py`
3. ✅ Launch UI: `./venv/bin/streamlit run streamlit_app.py`
4. ✅ Login and explore dashboard
5. ✅ Add teachers (if needed)
6. ✅ Add resources

### This Week
1. Review pending approvals daily
2. Approve and post replies
3. Monitor conversations
4. Set up YouTube OAuth (optional)

### Future
1. Deploy to cloud (Streamlit Cloud)
2. Set up automated scraping (GitHub Actions)
3. Add advanced analytics
4. Multi-language support

---

## 📞 Support

**Documentation:**
- `SUPABASE_QUICK_START.md` - Database setup (5 min)
- `IMPLEMENTATION_GUIDE.md` - Complete guide (30 min)
- `docs/YOUTUBE_OAUTH_SETUP.md` - OAuth setup (20 min)

**Quick Help:**
- Run system check: `./venv/bin/python3 system_check.py`
- Check logs in: `logs/` directory
- Test database connection (see command reference above)

---

## ✅ Success Checklist

- [ ] System check passes (6/6 checks)
- [ ] Scraper runs successfully
- [ ] UI launches without errors
- [ ] Can login with allowed email
- [ ] Dashboard shows data
- [ ] Can add teachers via UI
- [ ] Can add resources via UI
- [ ] Pending approvals work
- [ ] Can approve and (manually) post replies

---

## 🎉 You're Ready!

**Everything is set up and working!**

**To start right now:**

```bash
./start_system.sh
```

Or manually:

```bash
# Terminal 1: Run scraper
./venv/bin/python3 src/main.py

# Terminal 2: Launch UI
./venv/bin/streamlit run streamlit_app.py
```

**Open browser:** http://localhost:8501

**Login:** subodh.jathar@gmail.com

**Start engaging leads!** 🚀

---

**Built with ❤️ for Isha Foundation**
**Version:** 2.0 (Supabase Migration)
**Status:** ✅ Production Ready
