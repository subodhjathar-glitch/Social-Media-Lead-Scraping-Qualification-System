# Social Media Lead Scraping & Qualification System

Automated lead generation system that monitors Sadhguru-related YouTube content, qualifies leads using AI, and delivers daily email digests.

## 🎯 Features

- **Automated Scraping**: Monitors YouTube channels for comments from potential students
- **AI Qualification**: Uses GPT-4o-mini to classify lead intent (High/Medium/Low)
- **Duplicate Detection**: SHA-256 hash-based deduplication to avoid reprocessing
- **Airtable Storage**: Visual database for manual review and follow-up
- **Email Digests**: Daily HTML emails with grouped leads
- **GitHub Actions**: Automated scheduling (2x daily at 6 AM and 6 PM UTC)
- **Quota Management**: Conservative YouTube API quota tracking

## 📋 Prerequisites

Before setting up, you'll need:

1. **YouTube Data API Key**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable "YouTube Data API v3"
   - Create credentials (API key)
   - Time: ~5 minutes

2. **OpenAI API Key**
   - Sign up at [platform.openai.com](https://platform.openai.com/)
   - Navigate to API Keys section
   - Create new secret key
   - Time: ~2 minutes

3. **Airtable Account & Token**
   - Sign up at [airtable.com](https://airtable.com/)
   - Create a new base
   - Create a table named "Leads" with these fields:
     - `Name` (Single line text)
     - `Platform` (Single select: YouTube)
     - `Comment` (Long text)
     - `Video URL` (URL)
     - `Comment URL` (URL)
     - `Intent` (Single select: High, Medium, Low)
     - `Confidence` (Number)
     - `AI Reasoning` (Long text)
     - `Lead Hash` (Single line text)
     - `Scraped Date` (Date)
     - `Created Time` (Created time - auto)
   - Get your Base ID (from URL: `https://airtable.com/BASE_ID/...`)
   - Create Personal Access Token:
     - Go to Account Settings → Developer Hub
     - Create token with `data.records:read` and `data.records:write` scopes
     - Add access to your base
   - Time: ~10 minutes

4. **Gmail App Password**
   - Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Generate app password for "Mail"
   - Save the 16-character password
   - Time: ~2 minutes

5. **GitHub Account**
   - Sign up at [github.com](https://github.com/)
   - Create a new repository for this project
   - Time: ~3 minutes

**Total setup time: ~25-30 minutes**

## 🚀 Setup Instructions

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd <repo-name>
```

### 2. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```env
# YouTube Data API
YOUTUBE_API_KEY=your_youtube_api_key_here

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Airtable
AIRTABLE_TOKEN=your_airtable_personal_access_token_here
AIRTABLE_BASE_ID=your_airtable_base_id_here

# Email Configuration
EMAIL_PASSWORD=your_gmail_app_password_here
```

### 4. Test Locally

Run a test scrape:

```bash
python -m src.main
```

Check the output:
- Console logs should show progress through all phases
- Check `logs/` directory for detailed logs
- Verify leads appear in your Airtable base
- Check your email for the digest

### 5. Set Up GitHub Actions

Add secrets to your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to **Settings → Secrets and variables → Actions**
3. Click **New repository secret**
4. Add the following secrets:

   | Secret Name | Value |
   |-------------|-------|
   | `YOUTUBE_API_KEY` | Your YouTube API key |
   | `OPENAI_API_KEY` | Your OpenAI API key |
   | `AIRTABLE_TOKEN` | Your Airtable Personal Access Token |
   | `AIRTABLE_BASE_ID` | Your Airtable Base ID |
   | `EMAIL_PASSWORD` | Your Gmail app password |

**Security Note**: GitHub Secrets are fully encrypted and secure:
- ✓ Never visible in logs (automatically redacted as `***`)
- ✓ Never visible in code or workflow outputs
- ✓ Only accessible to repository admins
- ✓ Encrypted at rest using AES-256
- ✓ Only injected as environment variables during workflow execution

### 6. Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. Enable workflows if prompted
3. The workflow will run automatically at 6 AM and 6 PM UTC
4. You can also trigger manually using **Run workflow** button

## 📊 System Architecture

```
GitHub Actions (cron: 6 AM, 6 PM UTC)
    ↓
Main Orchestrator (src/main.py)
    ↓
┌─────────────┬──────────────┬──────────────┬─────────────┐
│   Scraper   │  Qualifier   │   Database   │  Notifier   │
│ (YouTube)   │  (OpenAI)    │  (Airtable)  │  (Email)    │
└─────────────┴──────────────┴──────────────┴─────────────┘
```

**Data Flow**:
1. Scraper discovers channels → fetches videos → extracts comments
2. Duplicate detection via hash check (username|platform|text)
3. Qualifier sends unique comments to GPT-4o-mini
4. Database stores qualified leads in Airtable
5. Notifier sends HTML digest email

## ⚙️ Configuration

All settings can be customized in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARCH_TERMS` | Sadhguru official,Sadhguru meditation,Sadhguru yoga | Comma-separated search terms |
| `DAYS_BACK` | 7 | How many days back to search |
| `MAX_VIDEOS_PER_CHANNEL` | 10 | Videos to check per channel |
| `MAX_COMMENTS_PER_VIDEO` | 100 | Comments to fetch per video |
| `YOUTUBE_QUOTA_LIMIT` | 3330 | Max quota per run (conservative) |
| `MIN_SUBSCRIBER_COUNT` | 100000 | Min subscribers for channel |
| `OPENAI_MODEL` | gpt-4o-mini | OpenAI model to use |
| `OPENAI_TEMPERATURE` | 0.3 | AI temperature (0-1) |

## 📈 Monitoring

### View Logs

**Locally**:
```bash
tail -f logs/$(date +%Y%m%d).log
```

**GitHub Actions**:
1. Go to **Actions** tab
2. Click on latest workflow run
3. Click on "scrape" job
4. View console output or download log artifacts

### Success Metrics

Track these in your logs:
- Comments scraped
- Duplicates filtered
- Unique leads qualified
- High/Medium/Low intent counts
- Leads stored in Airtable

### Email Digest

You'll receive HTML emails with:
- Summary statistics
- High intent leads (expanded with full details)
- Medium intent leads (expanded)
- Low intent leads (collapsed)
- Direct links to comments and videos

## 🐛 Troubleshooting

### YouTube API Quota Exceeded

**Error**: `403 quotaExceeded`

**Solutions**:
- Reduce `MAX_VIDEOS_PER_CHANNEL` or `MAX_COMMENTS_PER_VIDEO`
- Lower `YOUTUBE_QUOTA_LIMIT` to be more conservative
- Check [quota usage](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas)

### OpenAI API Rate Limit

**Error**: `429 Rate limit exceeded`

**Solutions**:
- System automatically retries with exponential backoff
- Upgrade OpenAI account tier if persistent
- Contact OpenAI support for higher limits

### Airtable Rate Limit

**Error**: `429 Too Many Requests`

**Solutions**:
- System uses batch operations (10 records/request)
- Automatic retry with exponential backoff
- Check Airtable plan limits

### Email Not Sending

**Error**: SMTP authentication failed

**Solutions**:
- Verify Gmail app password is correct
- Ensure 2-factor authentication is enabled on Google account
- Check EMAIL_FROM and EMAIL_PASSWORD in secrets
- Try generating a new app password

### No Leads Found

**Possible reasons**:
- No new content in specified date range (increase `DAYS_BACK`)
- All comments are duplicates (expected behavior)
- Channels have comments disabled
- Search terms not matching relevant channels

**Solutions**:
- Review scraper logs for channels discovered
- Adjust `SEARCH_TERMS` to be more specific
- Manually verify channels have recent videos with comments

### GitHub Actions Failing

**Steps**:
1. Check secrets are correctly added
2. View workflow logs for specific error
3. Test locally first with `.env` file
4. Ensure all required secrets are present

## 💰 Cost Estimates

**Monthly costs** (based on 60 runs/month, 50 leads/run):

- **YouTube API**: Free (within quota limits)
- **OpenAI API**: ~$5-10/month
  - 3,000 leads × ~500 tokens = ~$0.20/month at $0.15/1M tokens
- **Airtable**: Free tier (up to 1,200 records/base)
- **GitHub Actions**: Free tier (2,000 minutes/month)
- **Gmail**: Free

**Total**: $5-10/month (primarily OpenAI)

## 📝 Development

### Project Structure

```
.
├── src/
│   ├── config.py          # Configuration management
│   ├── utils.py           # Logging and utilities
│   ├── scraper.py         # YouTube scraper
│   ├── qualifier.py       # AI lead qualifier
│   ├── database.py        # Airtable operations
│   ├── notifier.py        # Email notifications
│   └── main.py           # Main orchestrator
├── .github/
│   └── workflows/
│       └── scrape.yml    # GitHub Actions workflow
├── logs/                 # Daily log files
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
└── README.md           # This file
```

### Running Tests

```bash
pytest tests/
```

### Adding New Features

1. Create feature branch
2. Implement changes
3. Test locally
4. Commit and push
5. Monitor GitHub Actions run

## 🤝 Support

For issues or questions:
1. Check logs first: `logs/YYYYMMDD.log`
2. Review troubleshooting section above
3. Check GitHub Actions workflow logs
4. Verify all API keys are valid and have sufficient quota

## 📄 License

MIT License - feel free to modify and use for your needs.

## 🎉 Success Criteria

After 12 weeks of operation, target metrics:

- ✓ System runs automatically 2x daily without intervention
- ✓ 50+ leads captured per week
- ✓ 30%+ high intent leads
- ✓ 5-8 enrollments from system leads
- ✓ <15 min/day review time
- ✓ $25-35/month operating cost
