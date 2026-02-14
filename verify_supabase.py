#!/usr/bin/env python3
"""
Verify Supabase Credentials
This script helps you verify and update your Supabase credentials.
"""

import os
from pathlib import Path

print("=" * 70)
print("SUPABASE CREDENTIAL VERIFICATION")
print("=" * 70)

# Read current .env
env_path = Path(".env")
if not env_path.exists():
    print("❌ .env file not found!")
    exit(1)

with open(env_path) as f:
    content = f.read()

# Extract current values
current_url = None
current_key = None

for line in content.split('\n'):
    if line.startswith('SUPABASE_URL='):
        current_url = line.split('=', 1)[1].strip()
    elif line.startswith('SUPABASE_KEY='):
        current_key = line.split('=', 1)[1].strip()

print(f"\n📋 Current Configuration:")
print(f"   URL: {current_url}")
print(f"   Key: {current_key[:20]}...{current_key[-20:] if len(current_key) > 40 else ''}")

print("\n" + "=" * 70)
print("PLEASE VERIFY YOUR SUPABASE PROJECT")
print("=" * 70)

print("""
1. Go to: https://supabase.com/dashboard

2. Select your project (or create a new one if needed)

3. Go to: Settings → API (in the left sidebar)

4. Copy these values:
   - Project URL (looks like: https://xxxxx.supabase.co)
   - anon/public key (long string starting with 'eyJ...')

5. The URL should match your current URL above
   If it doesn't match, your .env has the wrong URL

""")

print("=" * 70)
print("TESTING DNS RESOLUTION")
print("=" * 70)

if current_url:
    import socket
    # Extract hostname from URL
    hostname = current_url.replace('https://', '').replace('http://', '').split('/')[0]

    print(f"\nTesting: {hostname}")

    try:
        ip = socket.gethostbyname(hostname)
        print(f"✅ SUCCESS - Resolves to: {ip}")
        print("\nYour URL is valid! The issue might be temporary.")
        print("Try running the system again.")
    except socket.gaierror:
        print(f"❌ FAILED - This URL does not exist in DNS")
        print("\n⚠️  ACTION REQUIRED:")
        print("   1. Log into https://supabase.com/dashboard")
        print("   2. Check if your project exists")
        print("   3. If yes: Copy the correct URL from Settings → API")
        print("   4. If no: Create a new project")
        print("   5. Update your .env file with the correct URL and key")
        print("\nWould you like to update your .env now? (y/n): ", end='')

        response = input().strip().lower()
        if response == 'y':
            print("\nEnter your correct Supabase URL (from Settings → API):")
            new_url = input("URL: ").strip()

            print("\nEnter your correct Supabase anon key (from Settings → API):")
            new_key = input("Key: ").strip()

            # Validate inputs
            if new_url and new_key and 'supabase.co' in new_url:
                # Update .env
                new_content = content.replace(f'SUPABASE_URL={current_url}', f'SUPABASE_URL={new_url}')
                new_content = new_content.replace(f'SUPABASE_KEY={current_key}', f'SUPABASE_KEY={new_key}')

                with open(env_path, 'w') as f:
                    f.write(new_content)

                print("\n✅ .env file updated!")
                print("Now run the system again: python -m src.main")
            else:
                print("\n❌ Invalid input. Please check and try again.")

print("\n" + "=" * 70)
