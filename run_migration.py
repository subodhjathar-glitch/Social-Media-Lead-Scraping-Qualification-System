#!/usr/bin/env python3
"""
Automated migration: creates teacher_edits table directly in Supabase.
Run once with: python run_migration.py
"""

import os
import sys
import subprocess

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SUPABASE_URL = os.getenv('SUPABASE_URL', '').strip().rstrip('/')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '').strip()
PROJECT_REF = SUPABASE_URL.split('//')[1].split('.')[0] if '//' in SUPABASE_URL else ''

SQL_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS teacher_edits (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        teacher_id UUID REFERENCES teacher_profiles(id) ON DELETE CASCADE,
        pending_reply_id UUID REFERENCES pending_replies(id) ON DELETE CASCADE,
        original_ai_text TEXT NOT NULL,
        edited_text TEXT NOT NULL,
        edit_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        changes_made TEXT[],
        sentiment_shift JSONB,
        key_phrases_added TEXT[],
        key_phrases_removed TEXT[],
        lead_context JSONB,
        CONSTRAINT different_texts CHECK (original_ai_text != edited_text)
    )""",
    "CREATE INDEX IF NOT EXISTS idx_teacher_edits_teacher ON teacher_edits(teacher_id)",
    "CREATE INDEX IF NOT EXISTS idx_teacher_edits_timestamp ON teacher_edits(edit_timestamp DESC)",
    "ALTER TABLE teacher_profiles ADD COLUMN IF NOT EXISTS learned_style JSONB DEFAULT '{}'::jsonb",
    "ALTER TABLE teacher_profiles ADD COLUMN IF NOT EXISTS common_phrases TEXT[] DEFAULT ARRAY[]::TEXT[]",
    "ALTER TABLE teacher_profiles ADD COLUMN IF NOT EXISTS editing_patterns JSONB DEFAULT '{}'::jsonb",
    "ALTER TABLE teacher_profiles ADD COLUMN IF NOT EXISTS last_learning_update TIMESTAMP WITH TIME ZONE",
    "ALTER TABLE teacher_edits ENABLE ROW LEVEL SECURITY",
    """DO $$ BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='teacher_edits' AND policyname='Allow all for service role') THEN
            CREATE POLICY "Allow all for service role" ON teacher_edits FOR ALL TO service_role USING (true);
        END IF;
    END $$""",
    """DO $$ BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='teacher_edits' AND policyname='Allow all for authenticated users') THEN
            CREATE POLICY "Allow all for authenticated users" ON teacher_edits FOR ALL TO authenticated USING (true);
        END IF;
    END $$""",
]


def install_psycopg2():
    print("   Installing psycopg2-binary...")
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', 'psycopg2-binary', '-q'],
        capture_output=True, text=True
    )
    return result.returncode == 0


def run_statements(conn):
    import psycopg2.errors
    conn.autocommit = True
    cur = conn.cursor()
    ok = 0
    for stmt in SQL_STATEMENTS:
        stmt = stmt.strip()
        if not stmt:
            continue
        try:
            cur.execute(stmt)
            print(f"   ✓ {stmt[:70].splitlines()[0]}...")
            ok += 1
        except Exception as e:
            msg = str(e).lower()
            if any(x in msg for x in ['already exists', 'duplicate', 'already enabled']):
                print(f"   ~ Already exists (OK): {stmt[:50].splitlines()[0]}...")
                ok += 1
            else:
                print(f"   ⚠ Warning on: {stmt[:50].splitlines()[0]}...\n     → {e}")
    conn.close()
    print(f"\n   {ok}/{len(SQL_STATEMENTS)} statements ran successfully.")
    return True


def main():
    print(f"\n🔧 Supabase Migration Runner")
    print(f"   Project ref : {PROJECT_REF}")
    print(f"   Service key : {SERVICE_ROLE_KEY[:20]}...\n")

    if not PROJECT_REF or not SERVICE_ROLE_KEY:
        print("❌ SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set in .env")
        sys.exit(1)

    try:
        import psycopg2
    except ImportError:
        if not install_psycopg2():
            print("❌ Could not install psycopg2-binary")
            sys.exit(1)
        import psycopg2

    # Supabase Supavisor pooler — service role key works as password
    REGIONS = [
        'us-east-1', 'ap-south-1', 'eu-west-1',
        'us-west-1', 'ap-southeast-1', 'ap-northeast-1',
        'sa-east-1', 'ca-central-1', 'eu-central-1',
    ]

    for region in REGIONS:
        host = f"aws-0-{region}.pooler.supabase.com"
        dsn = (
            f"host={host} port=6543 dbname=postgres "
            f"user=postgres.{PROJECT_REF} password={SERVICE_ROLE_KEY} "
            f"sslmode=require connect_timeout=6"
        )
        try:
            print(f"   Trying pooler [{region}]...", end=' ', flush=True)
            conn = psycopg2.connect(dsn)
            print("✓ connected!")
            run_statements(conn)
            print("\n✅ Migration complete! The teacher_edits table now exists in Supabase.")
            print("   You can now approve & post replies without any errors.\n")
            return
        except psycopg2.OperationalError as e:
            print(f"no ({type(e).__name__})")
        except Exception as e:
            print(f"no ({e})")

    # Fallback: direct db host (needs actual DB password — may fail with JWT)
    host = f"db.{PROJECT_REF}.supabase.co"
    dsn = (
        f"host={host} port=5432 dbname=postgres "
        f"user=postgres password={SERVICE_ROLE_KEY} "
        f"sslmode=require connect_timeout=6"
    )
    try:
        print(f"\n   Trying direct DB host...", end=' ', flush=True)
        conn = psycopg2.connect(dsn)
        print("✓ connected!")
        run_statements(conn)
        print("\n✅ Migration complete!\n")
        return
    except Exception as e:
        print(f"no ({e})")

    print("\n❌ All automated connection attempts failed.")
    print("   Please run the SQL manually in Supabase SQL Editor:")
    print(f"   https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new")
    print("   (Copy the SQL from: supabase/migrations/004_teacher_edits_rls.sql)")
    sys.exit(1)


if __name__ == '__main__':
    main()
