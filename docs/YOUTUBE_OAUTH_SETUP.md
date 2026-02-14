# YouTube OAuth Setup Guide

This guide will help you set up OAuth authentication for posting YouTube comments automatically.

## Why OAuth is Needed

YouTube API requires OAuth (not just an API key) to:
- Post comments
- Reply to comments
- Modify channel content

**Without OAuth:** You can only READ data (view comments, videos, etc.)
**With OAuth:** You can WRITE data (post replies automatically)

---

## Prerequisites

- Google Cloud account
- YouTube channel (for posting)
- 15-20 minutes

---

## Step 1: Create Google Cloud Project (5 minutes)

### 1.1 Go to Google Cloud Console

1. Visit: https://console.cloud.google.com/
2. Sign in with your Google account
3. Click **Select a Project** → **New Project**

### 1.2 Create Project

1. **Project Name:** `Isha Lead Engagement`
2. **Organization:** Leave as default
3. Click **Create**
4. Wait for project creation (10-20 seconds)

### 1.3 Select Your Project

1. Click **Select a Project** dropdown (top bar)
2. Select **Isha Lead Engagement**

---

## Step 2: Enable YouTube Data API (2 minutes)

### 2.1 Enable API

1. Go to: https://console.cloud.google.com/apis/library
2. Search for: **YouTube Data API v3**
3. Click **YouTube Data API v3**
4. Click **Enable**
5. Wait for activation

---

## Step 3: Create OAuth Credentials (5 minutes)

### 3.1 Configure OAuth Consent Screen

1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Select **User Type: External**
3. Click **Create**

**Fill in details:**
- **App name:** `Isha Lead Engagement System`
- **User support email:** Your email
- **Developer contact:** Your email
- Leave other fields blank
4. Click **Save and Continue**

**Scopes:**
5. Click **Add or Remove Scopes**
6. Search for: `youtube.force-ssl`
7. Check: **YouTube Data API v3 - View and manage your YouTube account**
8. Click **Update** → **Save and Continue**

**Test Users:**
9. Click **Add Users**
10. Add the email of your YouTube account (the one that will post comments)
11. Click **Save and Continue** → **Back to Dashboard**

### 3.2 Create OAuth Client ID

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **Create Credentials** → **OAuth client ID**

**Configure:**
- **Application type:** Desktop app
- **Name:** `Isha Lead Poster`
- Click **Create**

### 3.3 Download Credentials

1. In the credentials list, find **Isha Lead Poster**
2. Click the **Download** icon (↓)
3. Save file as: `client_secret.json`
4. Move file to project root: `/home/subodh/Social-Media-Lead-Scraping-Qualification-System/`

**⚠️ IMPORTANT:** Keep this file secret! Add to `.gitignore`

---

## Step 4: Authenticate Your YouTube Account (5 minutes)

### 4.1 Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 4.2 Run Authentication Script

Create a file `authenticate_youtube.py`:

```python
"""
YouTube OAuth Authentication Script

Run this ONCE to authenticate your YouTube account.
It will save credentials to 'youtube_token.pickle' for future use.
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes required for posting comments
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def authenticate():
    """Authenticate and save credentials."""
    creds = None

    # Check if token already exists
    if os.path.exists('youtube_token.pickle'):
        print("🔍 Found existing token...")
        with open('youtube_token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If credentials are invalid or don't exist, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open('youtube_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            print("✅ Credentials saved to youtube_token.pickle")

    print("\n✅ Authentication successful!")
    print("You can now post YouTube comments via the API.")
    return creds

if __name__ == '__main__':
    authenticate()
```

### 4.3 Run the Script

```bash
python authenticate_youtube.py
```

**What happens:**
1. Browser opens automatically
2. Sign in with your YouTube account
3. Review permissions (click **Allow**)
4. See "Authentication successful!" message
5. A file `youtube_token.pickle` is created

**⚠️ Keep `youtube_token.pickle` secret!** Add to `.gitignore`

---

## Step 5: Update Streamlit App (2 minutes)

### 5.1 Load Credentials in App

Add to `streamlit_app_v2.py` (near the top):

```python
import pickle
from google.auth.transport.requests import Request

# Load YouTube credentials
@st.cache_resource
def load_youtube_credentials():
    """Load YouTube OAuth credentials."""
    if os.path.exists('youtube_token.pickle'):
        with open('youtube_token.pickle', 'rb') as token:
            creds = pickle.load(token)

            # Refresh if expired
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            return creds
    return None

youtube_creds = load_youtube_credentials()
```

### 5.2 Initialize YouTube Poster

```python
from src.youtube_poster_supabase import YouTubePoster

# Initialize poster
youtube_poster = YouTubePoster(supabase)
youtube_poster.initialize_youtube_client(youtube_creds)
```

### 5.3 Use in Approval Handler

When teacher clicks "Approve & Post":

```python
if st.button("✅ Approve & Post"):
    # Update status
    supabase.table('pending_replies').update({
        'approval_status': 'approved',
        'approved_at': datetime.now().isoformat()
    }).eq('id', reply['id']).execute()

    # Post to YouTube
    result = youtube_poster.post_approved_reply_from_ui(reply['id'], edited_reply)

    if result['status'] == 'success':
        st.success("✅ Reply approved and posted to YouTube!")
        st.balloons()
    elif result['status'] == 'no_oauth':
        st.warning("⚠️ OAuth not configured. Reply approved but not posted.")
        st.info("Run: python authenticate_youtube.py")
    else:
        st.error(f"❌ Posting failed: {result.get('error')}")
        st.info("Reply is approved - you can retry posting later")

    st.rerun()
```

---

## Step 6: Test the Integration (3 minutes)

### 6.1 Small Test

1. Open Streamlit app: `streamlit run streamlit_app_v2.py`
2. Login as teacher
3. Go to **Pending Approvals**
4. Click **Approve & Post** on a test reply
5. Check YouTube to verify comment appeared

### 6.2 Expected Behavior

**Success:**
- ✅ Reply approved and posted to YouTube!
- Status changes to "Posted"
- Comment appears on YouTube within seconds

**OAuth Not Configured:**
- ⚠️ Reply approved but not posted
- Reminder to run `authenticate_youtube.py`

**Posting Failed:**
- ❌ Error message shown
- Reply stays in "Approved" status
- Can retry later

---

## Troubleshooting

### Error: "Client secret not found"

**Solution:**
- Download `client_secret.json` again from Google Cloud Console
- Place in project root

### Error: "Insufficient permissions"

**Solution:**
- Re-run `python authenticate_youtube.py`
- Make sure you grant all permissions

### Error: "Quota exceeded"

**Solution:**
- YouTube API has daily quota limits
- Wait 24 hours for quota reset
- Or request quota increase in Google Cloud Console

### Error: "Comments disabled"

**Solution:**
- This video has comments disabled
- Skip this lead or notify manually

---

## Security Best Practices

### 1. Keep Credentials Secret

Add to `.gitignore`:
```
client_secret.json
youtube_token.pickle
*.pickle
```

### 2. Rotate Credentials Periodically

- Every 3-6 months, delete `youtube_token.pickle`
- Re-run `authenticate_youtube.py`

### 3. Use Service Account (Advanced)

For production:
- Create a service account
- Share YouTube channel access with service account
- Use service account credentials

---

## Manual Fallback (If OAuth Not Working)

If OAuth setup fails, use manual posting:

1. Teacher approves reply in UI
2. System shows:
   - ✅ Reply approved
   - 📋 Copy reply text (button)
   - 🔗 Open YouTube comment (button)
3. Teacher:
   - Copies text
   - Opens YouTube
   - Pastes manually
   - Clicks "Mark as Posted Manually" in UI

---

## Support

- **Google Cloud Console:** https://console.cloud.google.com/
- **YouTube API Docs:** https://developers.google.com/youtube/v3
- **OAuth Setup Help:** https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps

---

## Summary Checklist

- [ ] Created Google Cloud project
- [ ] Enabled YouTube Data API v3
- [ ] Configured OAuth consent screen
- [ ] Created OAuth client ID
- [ ] Downloaded `client_secret.json`
- [ ] Ran `authenticate_youtube.py`
- [ ] Generated `youtube_token.pickle`
- [ ] Updated Streamlit app
- [ ] Tested posting a reply
- [ ] Added credentials to `.gitignore`

**Estimated time:** 15-20 minutes

**Result:** Fully automated YouTube reply posting! 🚀
