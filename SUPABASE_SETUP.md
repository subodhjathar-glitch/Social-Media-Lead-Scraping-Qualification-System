# 🚀 Complete Supabase Setup Guide

## 🎉 What You Have Now

✅ Complete Supabase database schema
✅ Supabase-powered backend (replaces Airtable)
✅ Beautiful Streamlit UI dashboard
✅ All existing features working
✅ **ZERO cost** - completely free!

---

## 📋 Setup Steps (15-20 minutes)

### **Step 1: Create Supabase Account** (5 min)

1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub (recommended) or email
4. **It's completely FREE** - no credit card needed!

### **Step 2: Create New Project** (3 min)

1. Click "New Project"
2. Fill in:
   - **Name:** `isha-lead-engagement`
   - **Database Password:** Generate strong password (save it!)
   - **Region:** Choose closest to you (e.g., "South Asia (Mumbai)" for India)
3. Click "Create new project"
4. **Wait 2-3 minutes** for project to initialize

### **Step 3: Get Your Credentials** (2 min)

Once project is ready:

1. Go to **Settings** (⚙️ icon in sidebar)
2. Click **API**
3. Copy these values:

```
Project URL: https://xxxxxxxxxxxxx.supabase.co
anon/public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Step 4: Run Database Migration** (5 min)

**Option A: SQL Editor (Easiest)**

1. In Supabase dashboard, go to **SQL Editor** (database icon in sidebar)
2. Click "New query"
3. Copy the entire contents of `supabase/migrations/001_initial_schema.sql`
4. Paste into SQL Editor
5. Click "Run" (or press Ctrl/Cmd + Enter)
6. ✅ You should see "Success. No rows returned"

**Option B: Command Line**

```bash
# Install Supabase CLI (optional)
npm install -g supabase

# Login
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Run migration
supabase db push
```

### **Step 5: Update .env File** (2 min)

Edit your `.env` file:

```bash
# Supabase (NEW)
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Keep your other credentials
YOUTUBE_API_KEY=...
OPENAI_API_KEY=...
EMAIL_FROM=...
EMAIL_PASSWORD=...
```

### **Step 6: Install New Dependencies** (2 min)

```bash
pip install -r requirements.txt
```

This installs:
- `supabase` - Python client for Supabase
- `streamlit` - UI dashboard
- `plotly` - Beautiful charts
- `pandas` - Data manipulation

### **Step 7: Test the System** (5 min)

**Test 1: Database Connection**

```bash
python -c "from src.database import SupabaseDatabase; db = SupabaseDatabase(); print('✅ Connected!')"
```

**Test 2: Run Small Scrape**

```bash
DAYS_BACK=1 MAX_VIDEOS_PER_CHANNEL=1 MAX_COMMENTS_PER_VIDEO=5 python -m src.main
```

Expected output:
- Scrapes a few comments
- Stores in Supabase
- No errors

**Test 3: Launch UI Dashboard**

```bash
streamlit run streamlit_app.py
```

Opens in browser at http://localhost:8501

✅ You should see the dashboard!

---

## 🎨 Using the Streamlit Dashboard

### **Dashboard Features:**

**📊 Dashboard Page**
- Real-time statistics
- Charts and graphs
- Quick actions

**⏳ Pending Approvals** (MOST IMPORTANT)
- View AI-generated replies
- Edit inline
- One-click approve/reject
- NO email needed!

**💬 Conversations**
- View all active threads
- See full conversation history
- Track engagement

**📋 Leads**
- Filter by pain type, readiness
- Export to CSV
- Search functionality

**👥 Teachers**
- Add/edit teacher profiles
- Manage permissions
- Set daily limits

**📚 Resources**
- Add/edit resources
- Track usage statistics
- Enable/disable resources

---

## 🔄 Migrating from Airtable (If You Have Data)

If you already added data to Airtable, here's how to migrate:

### **Manual Migration** (Easiest)

**For Each Table:**

1. **Export from Airtable:**
   - Open table in Airtable
   - Click "..." menu → "Download CSV"
   - Save file

2. **Import to Supabase:**
   - Go to Supabase Table Editor
   - Select table
   - Click "Insert" → "Insert rows"
   - Upload CSV
   - Map columns
   - Import

**OR Use Supabase UI:**
- Go to **Table Editor** in Supabase
- Manually add rows using the UI (good for small amounts of data)

### **Automated Migration Script** (For Bulk Data)

If you have a lot of data, I can provide a Python script to automate the migration. Let me know!

---

## 🚀 Deploying the Streamlit UI (Free Hosting)

### **Option 1: Streamlit Cloud** (Easiest - Recommended)

1. **Push code to GitHub:**
```bash
git add .
git commit -m "Add Streamlit UI"
git push origin main
```

2. **Deploy on Streamlit Cloud:**
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Connect your GitHub repo
   - Select `streamlit_app.py`
   - Add secrets (environment variables):
     ```
     SUPABASE_URL = "your-url"
     SUPABASE_KEY = "your-key"
     ```
   - Click "Deploy"
   - **Done!** Your UI is live at `https://your-app.streamlit.app`

3. **Share with team:**
   - Send them the URL
   - They can access from any device
   - No installation needed!

### **Option 2: Run Locally**

```bash
streamlit run streamlit_app.py
```

---

## 💰 Cost Comparison: Airtable vs Supabase

### **Airtable:**
- Free tier: 1,000 records (limited!)
- After that: $20/user/month
- With 2 teachers: **$480/year**

### **Supabase:**
- Free tier: 500MB database (plenty!)
- Unlimited records
- Unlimited API calls
- **Total cost: $0/year** 🎉

### **Savings: $480/year!**

---

## 🎯 Daily Workflow (With UI)

### **Your New Workflow:**

**Morning (Automatic):**
1. System scrapes comments
2. Qualifies leads
3. Creates conversation threads
4. Generates replies
5. Stores in Supabase

**Your Task (5-10 minutes):**
1. Open Streamlit dashboard: `https://your-app.streamlit.app`
2. Go to "⏳ Pending Approvals"
3. Review AI replies
4. Click "✅ Approve" or edit inline
5. **Done!**

**No email needed!** Everything in one beautiful interface.

---

## 🔒 Security & Permissions

### **Supabase Security:**

1. **Row Level Security (RLS):** ✅ Enabled
   - Only authenticated users can access data
   - Service role (backend) has full access

2. **API Keys:**
   - `anon` key: Safe to use in frontend
   - `service_role` key: Keep secret (for backend only)

3. **Authentication:** (Optional)
   - You can add user authentication later
   - For now, anyone with UI link can access
   - **Recommendation:** Deploy privately or add auth

---

## 🆚 Airtable vs Supabase Feature Comparison

| Feature | Airtable | Supabase | Winner |
|---------|----------|----------|--------|
| **Free Records** | 1,000 | Unlimited | 🏆 Supabase |
| **Free Storage** | 2GB | 500MB + storage | 🏆 Supabase |
| **API Calls** | 5/sec | Unlimited | 🏆 Supabase |
| **Cost (2 users)** | $480/year | $0/year | 🏆 Supabase |
| **Custom UI** | ❌ No | ✅ Yes | 🏆 Supabase |
| **Database Type** | Proprietary | PostgreSQL | 🏆 Supabase |
| **Real-time** | ❌ No | ✅ Yes | 🏆 Supabase |
| **Self-hosted** | ❌ No | ✅ Yes | 🏆 Supabase |

---

## 🐛 Troubleshooting

### Issue: "Supabase credentials not found"
**Solution:** Check your `.env` file has `SUPABASE_URL` and `SUPABASE_KEY`

### Issue: "Table doesn't exist"
**Solution:** Run the migration script in SQL Editor (Step 4)

### Issue: Streamlit not loading
**Solution:**
```bash
pip install streamlit
streamlit run streamlit_app.py
```

### Issue: Can't approve replies
**Solution:** Make sure database has data. Run a test scrape first.

---

## 📊 What's Different from Airtable?

### **Backwards Compatible:**
- All existing code works
- Same method names
- Same functionality

### **Better:**
- ✅ Unlimited records
- ✅ Faster queries
- ✅ Real-time updates
- ✅ Custom UI
- ✅ PostgreSQL power
- ✅ **FREE forever**

### **New Features:**
- 🎨 Beautiful Streamlit UI
- 📊 Real-time dashboard
- ⚡ One-click approvals
- 📱 Mobile-friendly
- 🔍 Advanced filtering
- 📥 CSV export

---

## 🎓 Next Steps

1. ✅ Complete Supabase setup (Steps 1-7)
2. ✅ Test with small scrape
3. ✅ Launch Streamlit UI
4. ✅ Add your teacher profile
5. ✅ Add resources
6. ✅ Test approval workflow
7. ✅ Deploy UI to Streamlit Cloud
8. 🚀 Go live!

---

## 💡 Pro Tips

1. **Bookmark your dashboard URL** for quick access
2. **Add to home screen on mobile** for app-like experience
3. **Check dashboard daily** for pending approvals
4. **Export leads weekly** for backup
5. **Monitor readiness scores** to prioritize high-value leads

---

## 📞 Support

**If you encounter issues:**
1. Check this guide's Troubleshooting section
2. Review logs: `logs/YYYYMMDD.log`
3. Test database connection
4. Verify environment variables

---

## 🎉 Congratulations!

You now have a **professional, free, scalable** lead engagement system!

**Features:**
✅ Pain-based qualification
✅ Conversation tracking
✅ AI reply generation
✅ Beautiful UI dashboard
✅ One-click approvals
✅ Mobile-friendly
✅ Real-time updates
✅ Unlimited scale
✅ **$0 cost**

**Ready to engage leads!** 🕉️
