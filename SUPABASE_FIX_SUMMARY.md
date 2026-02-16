# Supabase Fix Summary

## Problem
Data was being scraped successfully but saved to local JSON files instead of Supabase database. The scraper showed "Supabase unavailable" and saved data to `data/leads_offline_*.json`.

## Root Cause
**Row Level Security (RLS)** was enabled on the Supabase `leads` table, and the scraper was using the `SUPABASE_KEY` (anon/public key) which doesn't have permission to bypass RLS policies. This caused all write operations to fail with:

```
new row violates row-level security policy for table "leads"
```

## Solution
Updated the code to use `SUPABASE_SERVICE_ROLE_KEY` instead of `SUPABASE_KEY` for backend operations. The service role key has full database access and bypasses RLS policies.

### Files Modified

1. **src/config.py** (line 34)
   - Added `supabase_service_role_key` setting

2. **src/database.py** (line 24)
   - Updated initialization to prefer `SUPABASE_SERVICE_ROLE_KEY` over `SUPABASE_KEY`
   - Changed: `key = settings.supabase_service_role_key or settings.supabase_key`

## Results

✅ **All 87 scraped leads uploaded to Supabase**
- Previously saved in: `data/leads_offline_20260215_090236.json`
- Now stored in Supabase `leads` table

✅ **Connection tests passing**
- Read access: Working
- Write access: Working
- Duplicate detection: Working

✅ **Future scrapes will save directly to Supabase**
- No more offline JSON files (unless Supabase is truly unavailable)
- Data immediately available in dashboard

## Verification

Run these commands to verify everything is working:

```bash
# Test Supabase connection
source .venv/bin/activate && python test_supabase_connection.py

# Verify data in database
source .venv/bin/activate && python verify_supabase_data.py

# Run a test scrape (will use your YouTube API quota)
source .venv/bin/activate && python src/main.py
```

## Environment Variables

Ensure your `.env` file has these set:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_public_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key  # This is now required!
```

**Important:** Get your `SUPABASE_SERVICE_ROLE_KEY` from:
Supabase Dashboard → Project Settings → API → service_role (secret)

## Dashboard Access

Your Streamlit dashboard already uses the service role key (from line 183 in streamlit_app.py), so it will continue working with the same data.

## Cost Savings

No more wasted API credits! All scraped data will now be:
- ✅ Saved to Supabase immediately
- ✅ Accessible via dashboard
- ✅ No duplicate processing
- ✅ Full analytics available

## Next Steps

1. Run your next scrape:
   ```bash
   python src/main.py
   ```

2. Check the dashboard:
   ```bash
   streamlit run streamlit_app.py
   ```

3. Verify new leads appear in the dashboard's "Leads" page

## Cleanup (Optional)

The offline JSON files in `data/` directory can be deleted now since the data is in Supabase:

```bash
# Backup first (optional)
mkdir -p data/backup
mv data/leads_offline_*.json data/backup/

# Or delete if you're confident
rm data/leads_offline_*.json
```

## Test Scripts

These utility scripts are available for testing:

- `test_supabase_connection.py` - Comprehensive connection test
- `upload_offline_data.py` - Upload any offline JSON to Supabase
- `verify_supabase_data.py` - Check data in Supabase

---

**Status:** ✅ FIXED - Supabase is now fully functional and saving data correctly.

**Date:** 2026-02-15
