"""
System Health Check - Verify all components are working

Run this before starting the system to ensure everything is configured correctly.
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print colored header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_success(text):
    """Print success message."""
    print(f"✅ {text}")

def print_error(text):
    """Print error message."""
    print(f"❌ {text}")

def print_warning(text):
    """Print warning message."""
    print(f"⚠️  {text}")

def check_environment():
    """Check Python environment and dependencies."""
    print_header("1. Environment Check")

    # Python version
    version = sys.version_info
    if version >= (3, 9):
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    else:
        print_error(f"Python {version.major}.{version.minor} - Need 3.9+")
        return False

    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success("Virtual environment activated")
    else:
        print_warning("Virtual environment NOT activated (run: source venv/bin/activate)")

    return True

def check_dependencies():
    """Check if all required packages are installed."""
    print_header("2. Dependencies Check")

    required = {
        'supabase': 'Supabase client',
        'streamlit': 'Streamlit UI',
        'openai': 'OpenAI API',
        'googleapiclient': 'YouTube API',
        'pandas': 'Data handling',
        'plotly': 'Charts',
        'dotenv': 'Environment variables'
    }

    all_installed = True

    for package, description in required.items():
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{description} ({package})")
        except ImportError:
            print_error(f"{description} ({package}) - NOT INSTALLED")
            all_installed = False

    return all_installed

def check_env_file():
    """Check .env file and required variables."""
    print_header("3. Environment Variables Check")

    if not Path('.env').exists():
        print_error(".env file not found!")
        print("   Run: cp .env.example .env")
        return False

    print_success(".env file exists")

    # Load .env
    from dotenv import load_dotenv
    load_dotenv()

    # Check required variables
    required_vars = {
        'SUPABASE_URL': 'Supabase database URL',
        'SUPABASE_KEY': 'Supabase API key',
        'OPENAI_API_KEY': 'OpenAI API key',
        'YOUTUBE_API_KEY': 'YouTube API key'
    }

    all_set = True

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and 'your_' not in value:
            # Mask sensitive values
            if 'KEY' in var or 'URL' in var:
                masked = value[:10] + '...' + value[-10:] if len(value) > 20 else value[:5] + '...'
                print_success(f"{description}: {masked}")
            else:
                print_success(f"{description}: Set")
        else:
            print_error(f"{description} ({var}) - NOT SET or using placeholder")
            all_set = False

    return all_set

def check_database_connection():
    """Test Supabase database connection."""
    print_header("4. Database Connection Check")

    try:
        from src.database import SupabaseDatabase

        print("   Connecting to Supabase...")
        db = SupabaseDatabase()
        print_success("Database connection successful")

        # Try to query teacher_profiles
        print("   Testing query: teacher_profiles...")
        teachers = db.get_active_teachers()
        print_success(f"Found {len(teachers)} teacher(s) in database")

        # Check tables exist
        print("   Checking tables...")
        tables = ['leads', 'teacher_profiles', 'conversation_threads', 'pending_replies', 'resources']
        for table in tables:
            try:
                result = db.client.table(table).select('id', count='exact').limit(1).execute()
                print_success(f"Table '{table}' exists ({result.count or 0} records)")
            except Exception as e:
                print_error(f"Table '{table}' error: {str(e)}")

        return True

    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        print("\n   Troubleshooting:")
        print("   1. Check SUPABASE_URL and SUPABASE_KEY in .env")
        print("   2. Verify internet connection")
        print("   3. Check if Supabase project is active")
        print("   4. Run migration: supabase/migrations/001_initial_schema.sql")
        return False

def check_file_structure():
    """Verify required files and directories exist."""
    print_header("5. File Structure Check")

    required_files = [
        'src/database.py',
        'src/auth.py',
        'src/scraper.py',
        'src/qualifier.py',
        'streamlit_app.py',
        'requirements.txt'
    ]

    required_dirs = [
        'src',
        'supabase',
        'logs'
    ]

    all_exist = True

    for file in required_files:
        if Path(file).exists():
            print_success(f"File: {file}")
        else:
            print_error(f"File missing: {file}")
            all_exist = False

    for dir in required_dirs:
        if Path(dir).exists():
            print_success(f"Directory: {dir}")
        else:
            if dir == 'logs':
                # Create logs directory if missing
                Path(dir).mkdir(exist_ok=True)
                print_warning(f"Directory created: {dir}")
            else:
                print_error(f"Directory missing: {dir}")
                all_exist = False

    return all_exist

def check_authentication():
    """Test authentication system."""
    print_header("6. Authentication Check")

    try:
        from src.auth import SimpleEmailGate

        auth = SimpleEmailGate()
        print_success("Authentication module loaded")

        # Check allowed emails
        allowed = os.getenv('ALLOWED_EMAILS', '')
        if allowed:
            emails = [e.strip() for e in allowed.split(',') if e.strip()]
            print_success(f"Allowed emails configured: {len(emails)} email(s)")
            for email in emails:
                print(f"   - {email}")
        else:
            print_warning("No ALLOWED_EMAILS set (will use defaults)")

        return True

    except Exception as e:
        print_error(f"Authentication check failed: {str(e)}")
        return False

def main():
    """Run all checks."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🕉️  Isha Lead Engagement System - Health Check            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    checks = [
        ("Environment", check_environment),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_env_file),
        ("Database Connection", check_database_connection),
        ("File Structure", check_file_structure),
        ("Authentication", check_authentication)
    ]

    results = []

    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Check '{name}' crashed: {str(e)}")
            results.append((name, False))

    # Summary
    print_header("Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        if result:
            print_success(f"{name}: PASS")
        else:
            print_error(f"{name}: FAIL")

    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} checks passed")
    print(f"{'='*60}\n")

    if passed == total:
        print("🎉 All checks passed! System is ready to run.")
        print("\nNext steps:")
        print("   1. Run scraper: ./venv/bin/python3 src/main.py")
        print("   2. Launch UI: ./venv/bin/streamlit run streamlit_app.py")
        print()
        return True
    else:
        print("⚠️  Some checks failed. Please fix the issues above before running the system.")
        print()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
