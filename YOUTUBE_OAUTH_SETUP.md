# 🚀 YouTube OAuth Setup Guide

## Complete Auto-Posting Setup (15 minutes)

This guide will enable **one-click automatic posting** from your dashboard to YouTube.

---

## 📋 Prerequisites

- Google account with YouTube channel access
- Access to Google Cloud Console
- This lead engagement system

---

## 🎯 Step-by-Step Instructions

### **Step 1: Google Cloud Console Setup**

#### 1.1 Create a Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** at the top
3. Click **"NEW PROJECT"**
4. Enter:
   - **Project name:** `Yogavani Lead System`
   - **Organization:** (leave default)
5. Click **"CREATE"**
6. Wait for project creation (30 seconds)

#### 1.2 Enable YouTube Data API v3

1. Go to [API Library](https://console.cloud.google.com/apis/library)
2. Search for: `YouTube Data API v3`
3. Click on **"YouTube Data API v3"**
4. Click **"ENABLE"**
5. Wait for activation

---

### **Step 2: OAuth Consent Screen**

#### 2.1 Configure Consent Screen

1. Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
2. Select **"External"** user type
3. Click **"CREATE"**

#### 2.2 Fill App Information

**App information:**
- **App name:** `Yogavani Lead System`
- **User support email:** Your Gmail address
- **App logo:** (optional)

**Developer contact information:**
- **Email addresses:** Your Gmail address

Click **"SAVE AND CONTINUE"**

#### 2.3 Scopes (Step 2)

- Click **"SAVE AND CONTINUE"** (no changes needed)

#### 2.4 Test Users (Step 3)

- Click **"+ ADD USERS"**
- Enter your Gmail address (the one that has YouTube channel access)
- Click **"ADD"**
- Click **"SAVE AND CONTINUE"**

#### 2.5 Summary (Step 4)

- Review and click **"BACK TO DASHBOARD"**

---

### **Step 3: Create OAuth Credentials**

#### 3.1 Create OAuth Client ID

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **"+ CREATE CREDENTIALS"**
3. Select **"OAuth client ID"**

#### 3.2 Configure Client

- **Application type:** `Desktop app`
- **Name:** `Yogavani Desktop Client`
- Click **"CREATE"**

#### 3.3 Download Credentials

1. You'll see a popup with "OAuth client created"
2. Click **"DOWNLOAD JSON"** or the download icon (⬇️)
3. Save the file as `client_secret.json` in your project directory:
   ```
   /home/subodh/Social-Media-Lead-Scraping-Qualification-System/client_secret.json
   ```

---

### **Step 4: Run OAuth Setup Script**

Open terminal and run:

```bash
# Navigate to project directory
cd /home/subodh/Social-Media-Lead-Scraping-Qualification-System

# Activate virtual environment
source .venv/bin/activate

# Run OAuth setup
python setup_youtube_oauth.py
```

#### What Happens:

1. Script checks for `client_secret.json`
2. Opens your browser for authentication
3. You'll see a Google sign-in page

#### In the Browser:

1. **Sign in** with your YouTube account
2. You'll see: **"Google hasn't verified this app"**
   - Click **"Continue"** (it's your own app!)
3. **Grant permissions:**
   - Check all boxes
   - Click **"Continue"**
4. You'll see: **"Authentication successful! You can close this window."**

#### Back in Terminal:

```
✅ SUCCESS! YouTube OAuth is now configured!
🚀 You can now post comments automatically from the dashboard!
```

---

### **Step 5: Test Auto-Posting**

```bash
# Restart dashboard
streamlit run streamlit_app.py
```

**In the Dashboard:**

1. Go to **"✅ Pending Approvals"**
2. You'll see: ✅ **YouTube OAuth configured - Replies will post automatically!**
3. Select a reply
4. Edit if needed
5. Click **"✅ Approve & Post"**
6. **Watch it post automatically!** 🚀

**You'll see:**
- 🚀 **"Posting to YouTube..."** spinner
- ✅ **"Reply posted to YouTube successfully!"**
- 🎈 Balloons animation
- Reply moves to **"Posted"** status

---

## 🎯 Expected Flow (After Setup)

### **Teacher Workflow:**

```
1. Open Dashboard
   ↓
2. "✅ Pending Approvals" page
   ↓
3. Review AI reply
   ↓
4. Edit if needed
   ↓
5. Click "✅ Approve & Post"
   ↓
6. 🚀 Automatic posting to YouTube
   ↓
7. ✅ Status: "Posted"
   ↓
8. Move to next approval
```

### **What Happens Automatically:**

- ✅ Reply posted to YouTube as a comment
- ✅ Database updated with "posted" status
- ✅ Conversation stage incremented
- ✅ Timestamp recorded
- ✅ Dashboard metrics updated
- ✅ Reply visible in "Already Posted" tab

---

## 🔧 Troubleshooting

### **"client_secret.json not found"**

- Make sure you downloaded it from Google Cloud Console
- Save it in the project root directory
- File name must be exactly: `client_secret.json`

### **"OAuth not configured" warning in dashboard**

```bash
# Check if token file exists
ls youtube_token.pickle

# If not, run setup again
python setup_youtube_oauth.py
```

### **"Failed to post" error**

**Possible causes:**
1. **YouTube API quota exceeded** (10,000 units/day)
   - Wait 24 hours for reset
   - Or request quota increase in Google Cloud Console

2. **Comments disabled on video**
   - Can't be fixed - skip this lead

3. **Token expired**
   - Delete `youtube_token.pickle`
   - Run `python setup_youtube_oauth.py` again

### **"Google hasn't verified this app" warning won't go away**

- This is normal for personal apps
- Click **"Continue"** - it's safe (it's your own app!)
- To remove warning: publish app in Google Cloud Console (not necessary)

---

## 🔐 Security Notes

### **Files Created:**

- `client_secret.json` - OAuth credentials (keep private!)
- `youtube_token.pickle` - Access token (keep private!)

### **Important:**

- ✅ Both files are in `.gitignore` (won't be committed)
- ✅ Never share these files
- ✅ Keep them secure on your server

### **Token Refresh:**

- Access tokens expire after 1 hour
- Refresh tokens last indefinitely
- System automatically refreshes tokens as needed
- No manual intervention required

---

## 📊 YouTube API Quota

### **Quota Limits:**

- **Daily quota:** 10,000 units
- **Comment post:** 50 units each
- **Maximum posts/day:** ~200 comments

### **Monitor Usage:**

1. Go to [Google Cloud Console - Quotas](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas)
2. View current usage
3. Request increase if needed (up to 1 million units/day)

---

## ✅ Verification Checklist

After setup, verify:

- [ ] `client_secret.json` exists in project directory
- [ ] `youtube_token.pickle` created after OAuth flow
- [ ] Dashboard shows "✅ YouTube OAuth configured"
- [ ] Test post works successfully
- [ ] Reply appears on YouTube
- [ ] Status updates to "Posted" in dashboard

---

## 🎉 You're Done!

Your system now has **fully automated YouTube posting**!

**Next steps:**
1. Approve a few test replies
2. Verify they post correctly
3. Train your teachers on the workflow
4. Start engaging with leads automatically!

**Namaskaram! 🙏**
