#!/bin/bash

# This script helps verify that all required GitHub secrets are set
# Run this locally to check what secrets are configured in your GitHub repo

echo "Checking GitHub Secrets for your repository..."
echo "=============================================="
echo ""

# Required secrets
REQUIRED_SECRETS=(
    "YOUTUBE_API_KEY"
    "OPENAI_API_KEY"
    "SUPABASE_URL"
    "SUPABASE_KEY"
    "EMAIL_FROM"
    "EMAIL_TO"
    "EMAIL_PASSWORD"
)

echo "Required secrets:"
for secret in "${REQUIRED_SECRETS[@]}"; do
    echo "  - $secret"
done

echo ""
echo "To verify secrets are set in GitHub:"
echo "1. Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
echo "2. Check that ALL secrets above are listed"
echo "3. If any are missing, click 'New repository secret' to add them"
echo ""
echo "To get your Supabase credentials:"
echo "1. Go to: https://app.supabase.com"
echo "2. Select your project"
echo "3. Go to Settings → API"
echo "4. Copy 'Project URL' → Use as SUPABASE_URL"
echo "5. Copy 'anon public' key → Use as SUPABASE_KEY"
echo ""
echo "IMPORTANT: Secret names are case-sensitive!"
echo "Make sure they match EXACTLY: SUPABASE_URL and SUPABASE_KEY"
