# Quick Start Guide

Get your lead scraping system running in under 1 hour.

## Prerequisites Checklist

Before you begin, obtain these API keys (links provided):

- [ ] YouTube Data API key - [Get it here](https://console.cloud.google.com/apis/library/youtube.googleapis.com)
- [ ] OpenAI API key - [Get it here](https://platform.openai.com/api-keys)
- [ ] Airtable Personal Access Token - [Get it here](https://airtable.com/create/tokens)
- [ ] Airtable Base ID - Create base at [airtable.com](https://airtable.com)
- [ ] Gmail App Password - [Get it here](https://myaccount.google.com/apppasswords)

## Step-by-Step Setup

### 1. Run Setup Script (2 minutes)

```bash
bash setup.sh
```

Answer 'y' to create virtual environment (recommended).

### 2. Configure API Keys (3 minutes)

Edit the `.env` file:

```bash
nano .env
```

Fill in these required values:

```env
YOUTUBE_API_KEY=your_actual_key_here
OPENAI_API_KEY=sk-your_actual_key_here
AIRTABLE_TOKEN=pat.your_actual_token_here
AIRTABLE_BASE_ID=app_your_actual_base_id_here
EMAIL_PASSWORD=your_16_char_app_password_here
```

Save and exit (Ctrl+X, then Y, then Enter).

### 3. Set Up Airtable Base (5 minutes)

1. Go to [airtable.com](https://airtable.com) and create new base
2. Rename table to "Leads"
3. Add these fields (in order):

| Field Name | Field Type | Options |
|------------|-----------|---------|
| Name | Single line text | - |
| Platform | Single select | Options: YouTube |
| Comment | Long text | - |
| Video URL | URL | - |
| Comment URL | URL | - |
| Intent | Single select | Options: High, Medium, Low |
| Confidence | Number | Integer, 0-100 |
| AI Reasoning | Long text | - |
| Lead Hash | Single line text | - |
| Scraped Date | Date | Use US format |
| Created Time | Created time | Auto |

4. Copy Base ID from URL: `https://airtable.com/BASE_ID_HERE/...`

### 4. Test Your Setup (2 minutes)

```bash
python test_setup.py
```

**Expected output**: All tests should show ✓ PASS

If any test fails, check the error message and fix the corresponding API key.

### 5. Run First Scrape (5 minutes)

```bash
python -m src.main
```

Watch the console for progress:

```
PHASE 1: Scraping YouTube Comments
PHASE 2: Filtering Duplicates
PHASE 3: AI Lead Qualification
PHASE 4: Storing Leads in Airtable
PHASE 5: Sending Email Digest
```

### 6. Verify Results (2 minutes)

**Check Airtable**:
- Open your base
- Verify leads appear in table
- Check all fields are populated

**Check Email**:
- Look for "Lead Digest" email
- Click direct comment links to verify they work

**Check Logs**:
```bash
cat logs/$(date +%Y%m%d).log
```

### 7. Set Up GitHub Actions (10 minutes)

**Push to GitHub**:

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit: Lead scraping system"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

**Add Secrets**:

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each of these:

| Secret Name | Value |
|-------------|-------|
| YOUTUBE_API_KEY | Your YouTube API key |
| OPENAI_API_KEY | Your OpenAI API key |
| AIRTABLE_TOKEN | Your Airtable token |
| AIRTABLE_BASE_ID | Your Airtable base ID |
| EMAIL_PASSWORD | Your Gmail app password |

**Enable Workflow**:

1. Go to **Actions** tab
2. Click "I understand my workflows, go ahead and enable them"
3. Click on "Scrape and Qualify Leads" workflow
4. Click "Run workflow" → "Run workflow" for manual test

### 8. Monitor First Automated Run (5 minutes)

**Check workflow execution**:

1. Go to **Actions** tab
2. Click on running workflow
3. Watch real-time logs
4. Wait for ✓ completion

**Verify results**:
- Check Airtable for new leads
- Check email for digest
- Download log artifacts if needed

## Troubleshooting

### Test fails: "Invalid YOUTUBE_API_KEY"
- Verify you enabled YouTube Data API v3 in Google Cloud Console
- Check API key restrictions (if any)
- Generate new key if needed

### Test fails: "Invalid OPENAI_API_KEY"
- Verify key starts with `sk-`
- Check you have credits in your OpenAI account
- Keys are case-sensitive

### Test fails: "Invalid AIRTABLE_TOKEN"
- Token should start with `pat`
- Verify scopes: `data.records:read` and `data.records:write`
- Verify token has access to your base

### Test fails: "AIRTABLE_BASE_ID not found"
- Base ID should start with `app`
- Get it from Airtable URL when viewing your base
- Verify table name is exactly "Leads"

### Email not received
- Check spam/junk folder
- Verify EMAIL_PASSWORD is 16-character app password (no spaces)
- Ensure 2FA is enabled on Gmail account
- Try generating new app password

### GitHub Actions fails
- Verify all 5 secrets are added correctly
- Check secrets don't have extra spaces
- Review workflow logs for specific error
- Test locally first to isolate issue

## Configuration Tips

### For Testing (Conservative)

Edit `.env` for first few runs:

```env
MAX_VIDEOS_PER_CHANNEL=2
MAX_COMMENTS_PER_VIDEO=20
YOUTUBE_QUOTA_LIMIT=500
```

### For Production (Standard)

Edit `.env` after testing:

```env
MAX_VIDEOS_PER_CHANNEL=10
MAX_COMMENTS_PER_VIDEO=100
YOUTUBE_QUOTA_LIMIT=3330
```

### For Aggressive Scraping

```env
MAX_VIDEOS_PER_CHANNEL=20
MAX_COMMENTS_PER_VIDEO=200
YOUTUBE_QUOTA_LIMIT=4500
DAYS_BACK=14
```

## Success Indicators

After successful setup, you should have:

- [x] All tests pass in `test_setup.py`
- [x] First scrape completes without errors
- [x] Leads visible in Airtable with all fields populated
- [x] Email digest received with formatted HTML
- [x] Direct comment links work (take you to specific comment)
- [x] GitHub Actions workflow runs successfully
- [x] Logs created in `logs/` directory

## What Happens Next?

**Automatic Schedule**:
- System runs at 6 AM UTC (convert to your timezone)
- System runs at 6 PM UTC
- ~3-7 minutes per run
- No intervention needed

**Your Daily Routine**:
1. Check email digest (2-3 min)
2. Review high-intent leads in Airtable (5-10 min)
3. Follow up with promising leads (as needed)

**Time Savings**:
- Before: 10+ hours/week manual searching
- After: <15 min/day reviewing qualified leads
- **Savings: 90%+ time reduction**

## Next Steps

1. **Week 1**: Monitor daily runs, verify lead quality
2. **Week 2**: Adjust search terms if needed
3. **Week 3**: Fine-tune AI prompts if classification seems off
4. **Week 4**: Analyze conversion rates (leads → enrollments)

## Getting Help

If you're stuck:

1. Check error message in logs
2. Review README.md troubleshooting section
3. Run `python test_setup.py` to diagnose
4. Verify API keys are valid and have proper permissions

## Useful Commands

```bash
# Test setup
python test_setup.py

# Run scraper
python -m src.main

# View today's logs
tail -f logs/$(date +%Y%m%d).log

# Check last 50 lines of logs
tail -n 50 logs/$(date +%Y%m%d).log

# Re-run setup
bash setup.sh

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Time Investment Summary

- **Initial Setup**: 30-40 minutes (one-time)
- **Testing & Verification**: 15-20 minutes (one-time)
- **GitHub Actions Setup**: 10 minutes (one-time)
- **Daily Monitoring**: 5-15 minutes

**Total first-day time**: ~1 hour
**Ongoing daily time**: 5-15 minutes

---

🎉 **Congratulations!** Your automated lead generation system is now running!

Check your email daily for new leads and watch your enrollment pipeline grow.
