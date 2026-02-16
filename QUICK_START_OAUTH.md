# ⚡ Quick Start: YouTube OAuth (5 Steps)

## 🎯 Goal: Enable One-Click Auto-Posting

---

## Step 1: Google Cloud Console (5 min)

```
1. Go to: https://console.cloud.google.com/
2. Create project: "Yogavani Lead System"
3. Enable "YouTube Data API v3"
4. Create OAuth consent screen (External)
5. Add yourself as test user
```

---

## Step 2: Create OAuth Credentials (2 min)

```
1. Create OAuth Client ID
2. Type: "Desktop app"
3. Name: "Yogavani Desktop Client"
4. Download JSON
5. Save as: client_secret.json (in project folder)
```

---

## Step 3: Run Setup Script (2 min)

```bash
cd /home/subodh/Social-Media-Lead-Scraping-Qualification-System
source .venv/bin/activate
python setup_youtube_oauth.py
```

**Follow the prompts:**
- Browser opens
- Sign in with YouTube account
- Click "Continue" (ignore warning)
- Grant permissions
- Done!

---

## Step 4: Restart Dashboard

```bash
streamlit run streamlit_app.py
```

---

## Step 5: Test It! (1 min)

```
1. Go to "✅ Pending Approvals"
2. See: "✅ YouTube OAuth configured"
3. Click "✅ Approve & Post" on any reply
4. Watch it post automatically! 🚀
```

---

## ✅ Success Indicators

You'll know it worked when:
- ✅ Green banner: "YouTube OAuth configured"
- ✅ Button says: "Approve & Post" (not just "Approve")
- ✅ Clicking button shows: "🚀 Posting to YouTube..."
- ✅ Success message: "Reply posted to YouTube successfully!"
- ✅ Balloons animation 🎈
- ✅ Reply appears on actual YouTube video

---

## 🆘 Quick Troubleshoot

**Problem:** "client_secret.json not found"
- **Fix:** Download it from Google Cloud Console and save in project root

**Problem:** Browser won't open
- **Fix:** Copy the URL from terminal and paste in browser manually

**Problem:** "OAuth not configured" in dashboard
- **Fix:** Delete `youtube_token.pickle` and run setup script again

**Problem:** Post fails
- **Fix:** Check YouTube API quota in Google Cloud Console

---

## 📁 Files You'll Have After Setup

```
client_secret.json      (OAuth credentials - keep private!)
youtube_token.pickle    (Access token - auto-refreshes)
```

Both are in `.gitignore` - won't be committed to git.

---

## 🎯 What Happens After Setup

### Before OAuth:
```
Approve → Moves to "Approved Replies" → Manual copy-paste to YouTube
```

### After OAuth:
```
Approve & Post → 🚀 Automatically posts to YouTube → Status: "Posted" ✅
```

**That's it! No more manual posting.** 🎉

---

## 📖 Full Documentation

For detailed step-by-step guide with screenshots:
- See `YOUTUBE_OAUTH_SETUP.md`

For troubleshooting and advanced options:
- See `YOUTUBE_OAUTH_SETUP.md` → Troubleshooting section

---

**Ready to set it up? Start with Step 1!** 🚀

**Namaskaram! 🙏**
