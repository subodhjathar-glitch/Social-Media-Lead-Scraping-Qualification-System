# Testing Guide

This guide helps you test the lead scraper system before deploying to production.

## Quick Start Testing

### 1. Run Setup Script

```bash
bash setup.sh
```

This will:
- Check Python version
- Install dependencies
- Create .env file
- Create logs directory

### 2. Configure Environment

Edit `.env` file with your API keys:

```bash
nano .env
```

Fill in all required fields (see README.md for how to obtain each key).

### 3. Test Environment Setup

Run the test script to verify all API connections:

```bash
python test_setup.py
```

This tests:
- Python package imports
- Configuration loading
- YouTube API connection
- OpenAI API connection
- Airtable API connection
- Email configuration

**Expected output**: All tests should pass with ✓ marks.

### 4. Run First Scrape (Conservative Mode)

For your first run, use conservative settings to avoid quota issues.

Edit `.env` temporarily:

```env
MAX_VIDEOS_PER_CHANNEL=2
MAX_COMMENTS_PER_VIDEO=20
YOUTUBE_QUOTA_LIMIT=500
```

Then run:

```bash
python -m src.main
```

### 5. Verify Results

Check the following:

**Console Output**:
```
Starting lead scraping workflow...
PHASE 1: Scraping YouTube Comments
  ✓ Scraped X comments
PHASE 2: Filtering Duplicates
  ✓ Unique: X, Duplicates: 0
PHASE 3: AI Lead Qualification
  ✓ Qualified X leads
PHASE 4: Storing Leads in Airtable
  ✓ Stored X leads
PHASE 5: Sending Email Digest
  ✓ Email digest sent
```

**Log File**:
```bash
tail -f logs/$(date +%Y%m%d).log
```

**Airtable**:
- Open your Airtable base
- Check the "Leads" table
- Verify records were created with all fields populated

**Email**:
- Check your inbox (and spam folder)
- Verify you received HTML email digest
- Verify direct comment links work

## Manual Component Testing

### Test YouTube Scraper Only

```python
from src.scraper import YouTubeScraper
from src.config import settings

scraper = YouTubeScraper()
channels = scraper.discover_channels(['Sadhguru official'])
print(f"Found {len(channels)} channels")

if channels:
    videos = scraper.get_recent_videos(channels[0]['id'], days_back=3)
    print(f"Found {len(videos)} videos")

    if videos:
        comments = scraper.get_video_comments(videos[0]['id'], max_results=10)
        print(f"Found {len(comments)} comments")
```

### Test AI Qualifier Only

```python
from src.qualifier import LeadQualifier

qualifier = LeadQualifier()

test_comment = {
    'text': 'How can I register for Inner Engineering program?',
    'author': 'Test User'
}

result = qualifier.qualify_lead(test_comment)
print(f"Intent: {result['intent']}")
print(f"Confidence: {result['confidence']}%")
print(f"Reasoning: {result['reasoning']}")
```

Expected: High intent (80-100 confidence)

### Test Airtable Database Only

```python
from src.database import AirtableDatabase
from src.utils import generate_lead_hash

db = AirtableDatabase()

# Test duplicate check
test_hash = generate_lead_hash('TestUser', 'youtube', 'Test comment')
is_dup = db.check_duplicate(test_hash)
print(f"Duplicate: {is_dup}")

# Test create lead
test_lead = {
    'author': 'Test User',
    'text': 'Test comment',
    'video_url': 'https://youtube.com/watch?v=test',
    'comment_url': 'https://youtube.com/watch?v=test&lc=123',
    'intent': 'Medium',
    'confidence': 75,
    'reasoning': 'Test reasoning',
    'hash': test_hash
}

record = db.create_lead(test_lead)
print(f"Created: {record['id']}")
```

### Test Email Notifier Only

```python
from src.notifier import EmailNotifier
from src.database import AirtableDatabase
from src.config import settings

notifier = EmailNotifier()
db = AirtableDatabase()

# Get recent leads
leads = db.get_recent_leads(hours=24)

if leads:
    success = notifier.send_digest(leads, settings.email_recipients)
    print(f"Email sent: {success}")
else:
    print("No leads to send")
```

## Test Scenarios

### Scenario 1: No New Content

**Setup**: Set `DAYS_BACK=1` during low activity period

**Expected Result**:
- Scraper finds 0-5 comments
- System completes successfully
- No email sent (or email with few leads)

**Validation**: System handles empty results gracefully

### Scenario 2: Many Duplicates

**Setup**: Run scraper twice in quick succession

**Expected Result**:
- First run: X unique leads
- Second run: X duplicates, 0 unique leads
- No duplicate storage
- Email only sent on first run

**Validation**: Duplicate detection works

### Scenario 3: API Quota Exceeded

**Setup**: Set `YOUTUBE_QUOTA_LIMIT=100`

**Expected Result**:
- Scraper stops when quota reached
- Partial results returned
- System continues with available data
- No errors

**Validation**: Quota management works

### Scenario 4: API Errors

**Setup**: Use invalid API key temporarily

**Expected Result**:
- Clear error message logged
- Error notification email sent
- System doesn't crash

**Validation**: Error handling works

## GitHub Actions Testing

### 1. Test Workflow Syntax

```bash
# Install act (GitHub Actions local runner)
# macOS: brew install act
# Linux: see https://github.com/nektos/act

act -l
```

### 2. Manual Trigger Test

1. Push code to GitHub
2. Go to Actions tab
3. Select "Scrape and Qualify Leads" workflow
4. Click "Run workflow"
5. Monitor execution

**Expected**: Workflow completes successfully

### 3. Verify Secrets

In GitHub Actions run output, verify secrets are redacted:

```
YOUTUBE_API_KEY=***
OPENAI_API_KEY=***
```

### 4. Check Artifacts

After workflow completes:
1. Go to workflow run
2. Check "Artifacts" section
3. Download "scraper-logs"
4. Review log files

## Performance Benchmarks

Expected performance on a typical run:

- **Scraping**: 2-5 minutes (depends on API response time)
- **Qualification**: 30-60 seconds (50 comments)
- **Storage**: 5-10 seconds (batch operations)
- **Email**: 1-2 seconds

**Total runtime**: 3-7 minutes per run

## Troubleshooting Tests

### Import Errors

```bash
pip install -r requirements.txt --upgrade
```

### Configuration Errors

```bash
# Verify .env exists and has content
cat .env | grep -v "^#" | grep "="

# Check for valid values (not placeholders)
cat .env | grep "your_"
```

### API Connection Errors

```bash
# Test internet connectivity
curl -I https://www.googleapis.com

# Test API endpoints
python test_setup.py
```

### Permission Errors

```bash
# Check file permissions
ls -la logs/
ls -la .env

# Fix if needed
chmod 755 logs/
chmod 600 .env
```

## Success Checklist

Before deploying to production, verify:

- [ ] All tests in `test_setup.py` pass
- [ ] Full scrape completes successfully
- [ ] Leads appear in Airtable with all fields
- [ ] Email digest received with correct formatting
- [ ] Direct comment links work
- [ ] Duplicate detection prevents re-scraping
- [ ] GitHub Actions workflow runs successfully
- [ ] Secrets are properly configured and redacted in logs
- [ ] Log files created in `logs/` directory
- [ ] No API quota issues

## Next Steps

Once all tests pass:

1. Reset `.env` to production settings (remove conservative limits)
2. Enable GitHub Actions schedule
3. Monitor first few automated runs
4. Review email digests for quality
5. Adjust AI prompts if needed based on classification accuracy

## Support

If tests fail:
1. Check error messages in console and logs
2. Verify API keys are valid and have permissions
3. Review README.md troubleshooting section
4. Ensure all prerequisites are met
