"""
🕉️ YOGAVANI Lead Engagement System
Beautiful, minimal, spiritually-grounded interface

Brand Colors:
- Maroon: #951B1E (accent, buttons)
- Grey: #999999 (secondary text)
- Green: #3E4938 (headings, important)
- White: #FFFFFF (background)

Design: Minimal. Calm. Harmonious. Breathable.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import os
from dotenv import load_dotenv

# Import authentication and YouTube posting
from src.auth import SimpleEmailGate
from src.youtube_poster_supabase import YouTubePoster
from src.youtube_oauth import is_oauth_configured
from src.utils import setup_logger

logger = setup_logger(__name__)

# Load environment
load_dotenv()

# ================================
# PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="Yogavani | Lead Engagement",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean up stale widget keys from previous page/session.
# Newer Streamlit versions raise KeyError when session state holds a widget key
# that no longer has a rendered widget. Purge them before any widget is drawn.
_STALE_PREFIXES = (
    'reply_', 'approve_', 'reject_', 'save_', 'copy_', 'history_',
    'act_', 'wait_', 'all_', 'oth_',
)
for _k in list(st.session_state.keys()):
    if any(_k.startswith(_p) for _p in _STALE_PREFIXES):
        try:
            del st.session_state[_k]
        except Exception:
            pass

# ================================
# YOGAVANI BRAND STYLING
# ================================
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Garet:wght@400;500;700&family=Libre+Baskerville:wght@400;700&display=swap');

    /* Global Variables - YOGAVANI Brand */
    :root {
        --color-maroon: #951B1E;
        --color-grey: #999999;
        --color-green: #3E4938;
        --color-white: #FFFFFF;
        --color-offwhite: #FAFAFA;
        --font-heading: 'Garet', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-body: 'Libre Baskerville', Georgia, serif;
    }

    /* Reset & Base */
    * {
        font-family: var(--font-body);
    }

    /* Streamlit Overrides */
    .stApp {
        background-color: var(--color-white);
    }

    /* Headings - Garet Font, Deep Green */
    h1, h2, h3, h4, h5, h6, .css-10trblm, .css-1629p8f {
        font-family: var(--font-heading) !important;
        color: var(--color-green) !important;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }

    h1 {
        font-size: 2.8rem;
        margin-bottom: 2rem;
        margin-top: 1rem;
    }

    h2 {
        font-size: 2rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    h3 {
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }

    /* Body Text - Libre Baskerville */
    p, .css-183lzff, div, span, label {
        font-family: var(--font-body);
        color: #333;
        line-height: 1.8;
    }

    /* Sidebar - Minimal Styling */
    [data-testid="stSidebar"] {
        background-color: var(--color-offwhite);
        border-right: 1px solid #E5E5E5;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--color-green) !important;
    }

    /* Buttons - Maroon with Soft Corners */
    .stButton>button {
        background-color: var(--color-maroon);
        color: var(--color-white);
        border-radius: 8px;
        padding: 0.6rem 1.8rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 8px rgba(149, 27, 30, 0.15);
        transition: all 0.3s ease;
        font-family: var(--font-heading);
        letter-spacing: 0.02em;
    }

    .stButton>button:hover {
        background-color: #7A1518;
        box-shadow: 0 4px 12px rgba(149, 27, 30, 0.25);
        transform: translateY(-1px);
    }

    .stButton>button:active {
        transform: translateY(0);
    }

    /* Metric Cards - Soft, Calm */
    [data-testid="stMetricValue"] {
        font-family: var(--font-heading);
        font-size: 2.5rem;
        color: var(--color-green);
    }

    [data-testid="stMetricLabel"] {
        font-family: var(--font-body);
        color: var(--color-grey);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Cards & Containers */
    .element-container {
        margin-bottom: 1.5rem;
    }

    /* Expanders - Soft Styling */
    .streamlit-expanderHeader {
        font-family: var(--font-heading);
        color: var(--color-green);
        background-color: var(--color-offwhite);
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #E8E8E8;
    }

    .streamlit-expanderHeader:hover {
        background-color: #F5F5F5;
        border-color: var(--color-maroon);
    }

    .streamlit-expanderContent {
        background-color: var(--color-white);
        border-radius: 0 0 8px 8px;
        padding: 1.5rem;
        border: 1px solid #E8E8E8;
        border-top: none;
    }

    /* Text Areas & Inputs - Fixed Black Background */
    .stTextArea textarea, .stTextInput input {
        border-radius: 6px;
        border: 1px solid #D0D0D0;
        padding: 0.8rem;
        font-family: var(--font-body);
        line-height: 1.6;
        background-color: #FFFFFF !important;
        color: #333333 !important;
        caret-color: #333333 !important;
    }

    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: var(--color-green);
        box-shadow: 0 0 0 2px rgba(62, 73, 56, 0.1);
        background-color: #FFFFFF !important;
        color: #333333 !important;
        caret-color: #333333 !important;
        outline: none;
    }

    /* Ensure disabled textareas also have correct contrast */
    .stTextArea textarea:disabled {
        background-color: #F8F8F8 !important;
        color: #444444 !important;
    }

    /* Fix autofill background */
    .stTextInput input:-webkit-autofill,
    .stTextInput input:-webkit-autofill:hover,
    .stTextInput input:-webkit-autofill:focus {
        -webkit-box-shadow: 0 0 0 1000px #FFFFFF inset !important;
        -webkit-text-fill-color: #333333 !important;
        transition: background-color 5000s ease-in-out 0s;
    }

    /* Dataframes - Clean Tables */
    .dataframe {
        font-family: var(--font-body);
        font-size: 0.9rem;
    }

    .dataframe thead th {
        background-color: var(--color-green) !important;
        color: var(--color-white) !important;
        font-family: var(--font-heading);
        font-weight: 600;
        padding: 1rem;
        border: none;
    }

    .dataframe tbody tr:hover {
        background-color: #F8F8F8;
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 20px;
        font-family: var(--font-heading);
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }

    .status-pending {
        background-color: #FFF4E6;
        color: #B45F06;
    }

    .status-approved {
        background-color: #E8F5E9;
        color: #2E7D32;
    }

    .status-posted {
        background-color: #E3F2FD;
        color: #1565C0;
    }

    /* Pain Type Badges */
    .pain-badge {
        display: inline-block;
        padding: 0.25rem 0.8rem;
        border-radius: 16px;
        font-size: 0.8rem;
        margin: 0.2rem;
        font-family: var(--font-heading);
    }

    .pain-spiritual {
        background-color: #F3E5F5;
        color: #6A1B9A;
    }

    .pain-mental {
        background-color: #FFEBEE;
        color: #C62828;
    }

    .pain-discipline {
        background-color: #E1F5FE;
        color: #01579B;
    }

    .pain-physical {
        background-color: #FFF3E0;
        color: #E65100;
    }

    /* Info/Success/Warning Boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid var(--color-green);
        padding: 1rem 1.2rem;
        font-family: var(--font-body);
    }

    /* Links */
    a {
        color: var(--color-maroon);
        text-decoration: none;
        transition: color 0.2s ease;
    }

    a:hover {
        color: var(--color-green);
        text-decoration: underline;
    }

    /* Selectbox, Multiselect */
    .stSelectbox, .stMultiSelect {
        font-family: var(--font-body);
    }

    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--color-grey), transparent);
        opacity: 0.3;
    }

    /* Main Content Padding */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }

    /* Remove Default Margins */
    .element-container:first-child {
        margin-top: 0;
    }

    /* Calm Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #F5F5F5;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--color-grey);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--color-green);
    }

    /* Plotly Charts - Clean Styling */
    .js-plotly-plot {
        border-radius: 8px;
    }

    /* ========================================
       MODERN UI ENHANCEMENTS
       ======================================== */

    /* Smooth Transitions for All Interactive Elements */
    .stButton>button,
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select,
    .stSlider,
    .streamlit-expanderHeader {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Slider - Enhanced Visual Feedback with Gradient */
    .stSlider {
        padding: 1.5rem 0;
    }

    .stSlider > div > div > div > div {
        background: linear-gradient(90deg,
            var(--color-grey) 0%,
            var(--color-green) 50%,
            var(--color-maroon) 100%);
        height: 8px;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .stSlider > div > div > div > div > div {
        background: linear-gradient(135deg, var(--color-maroon), #C02326);
        border: 3px solid var(--color-white);
        box-shadow: 0 4px 12px rgba(149, 27, 30, 0.4);
        width: 24px;
        height: 24px;
        border-radius: 50%;
        transition: all 0.3s ease;
        cursor: grab;
    }

    .stSlider > div > div > div > div > div:hover {
        transform: scale(1.3);
        box-shadow: 0 6px 20px rgba(149, 27, 30, 0.6);
    }

    .stSlider > div > div > div > div > div:active {
        cursor: grabbing;
        transform: scale(1.2);
    }

    /* Enhanced Cards with Hover Effects */
    .element-container {
        transition: transform 0.2s ease;
    }

    .element-container:hover {
        transform: translateY(-2px);
    }

    /* Modern Shadows for Depth */
    .stMetric {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F8F8 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }

    .stMetric:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        transform: translateY(-4px);
    }

    /* Animated Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--color-offwhite) 0%, #F0F0F0 100%);
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #F5F5F5 0%, #E8E8E8 100%);
        transform: translateX(4px);
    }

    /* Enhanced Button Animations */
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02);
    }

    .stButton>button:active {
        transform: translateY(0) scale(0.98);
    }

    /* Loading Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .element-container {
        animation: fadeIn 0.4s ease-out;
    }

    /* Modern Select Boxes */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #E0E0E0;
        transition: all 0.3s ease;
    }

    .stSelectbox > div > div:hover {
        border-color: var(--color-green);
        box-shadow: 0 0 0 3px rgba(62, 73, 56, 0.1);
    }

    /* Enhanced Link Buttons */
    .stLinkButton > a {
        background: linear-gradient(135deg, var(--color-green) 0%, #2E3828 100%);
        color: white !important;
        padding: 0.5rem 1.2rem;
        border-radius: 6px;
        text-decoration: none;
        transition: all 0.3s ease;
        display: inline-block;
    }

    .stLinkButton > a:hover {
        background: linear-gradient(135deg, #2E3828 0%, var(--color-green) 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(62, 73, 56, 0.3);
    }

    /* Glassmorphism Effect for Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, rgba(250, 250, 250, 0.95) 0%, rgba(245, 245, 245, 0.98) 100%);
        backdrop-filter: blur(10px);
    }

    /* Enhanced Status Badges with Animation */
    .status-badge {
        transition: all 0.3s ease;
    }

    .status-badge:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Pulse Animation for Pending Items */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }

    .status-pending {
        animation: pulse 2s ease-in-out infinite;
    }

    /* Modern DataFrame Styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }

    .dataframe tbody tr:nth-child(even) {
        background-color: #FAFAFA;
    }

    /* Smooth Scrolling */
    html {
        scroll-behavior: smooth;
    }

    /* Enhanced Focus States with Glow */
    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: var(--color-green);
        box-shadow: 0 0 0 4px rgba(62, 73, 56, 0.15);
        outline: none;
    }
    </style>
""", unsafe_allow_html=True)

# ================================
# INITIALIZE SUPABASE
# ================================
@st.cache_resource
def init_supabase():
    """Initialize Supabase client with error handling."""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

        if not url or not key:
            st.error("⚠️ Supabase credentials not configured")
            st.info("Add SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to .env file")
            st.stop()

        if "supabase.co" not in url:
            st.error("⚠️ Invalid Supabase URL format")
            st.stop()

        client = create_client(url, key)

        try:
            client.table('leads').select('id').limit(1).execute()
        except Exception as conn_err:
            st.warning(f"⚠️ Supabase unreachable: {conn_err}")
            st.info("Check internet connection and Supabase project status")

        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize Supabase: {e}")
        st.info("Check .env configuration and try again")
        st.stop()

supabase = init_supabase()

# ================================
# AUTHENTICATION
# ================================
auth = SimpleEmailGate()
auth.require_auth()

# ================================
# HELPER FUNCTIONS
# ================================

def get_status_badge(status: str) -> str:
    """Generate HTML for status badge."""
    emoji_map = {'pending': '⏳', 'approved': '✅', 'posted': '🚀', 'rejected': '❌'}
    emoji = emoji_map.get(status, '⚪')
    return f'<span class="status-badge status-{status}">{emoji} {status.title()}</span>'

def get_pain_badge(pain_type: str) -> str:
    """Generate HTML for pain type badge."""
    emoji_map = {
        'spiritual': '🧘',
        'mental_pain': '😰',
        'discipline': '💪',
        'physical_pain': '🤕',
        'practice_aligned': '✨',
        'low_intent': '💭'
    }
    emoji = emoji_map.get(pain_type, '❓')
    clean_name = pain_type.replace('_', ' ').title()
    css_class = pain_type.replace('_pain', '').replace('_', '-')
    return f'<span class="pain-badge pain-{css_class}">{emoji} {clean_name}</span>'

def format_timestamp(ts) -> str:
    """Format timestamp to human-readable."""
    if not ts:
        return 'N/A'
    try:
        dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo)
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds // 3600 > 0:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds // 60 > 0:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    except:
        return str(ts)

# ================================
# SIDEBAR NAVIGATION
# ================================
with st.sidebar:
    st.markdown("# 🕉️ Yogavani")
    st.markdown("*Lead Engagement System*")
    st.markdown("---")

    # Show user info
    auth.show_user_info()

    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigate",
        [
            "📊 Dashboard",
            "✅ Pending Approvals",
            "🚀 Approved Replies",
            "💬 Conversations",
            "📋 All Leads",
            "👥 Teachers",
            "📚 Resources",
            "👤 My Profile"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("💡 Review and approve AI-generated replies with one click")


# ================================
# PAGE: DASHBOARD
# ================================
if page == "📊 Dashboard":
    # Header
    st.markdown("# Dashboard")
    st.markdown("Welcome to your lead engagement hub")

    # Get current teacher (basic info only - no need for full profile on dashboard)
    teacher = auth.get_current_teacher()

    # Metrics Row
    st.markdown("### Today's Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        leads_today = supabase.table('leads').select('id', count='exact')\
            .eq('scraped_date', datetime.now().strftime('%Y-%m-%d')).execute()
        st.metric("New Leads", leads_today.count or 0)

    with col2:
        pending = supabase.table('pending_replies').select('id', count='exact')\
            .eq('approval_status', 'pending').execute()
        st.metric("⏳ Pending", pending.count or 0)

    with col3:
        approved = supabase.table('pending_replies').select('id', count='exact')\
            .eq('approval_status', 'approved').execute()
        st.metric("✅ Approved", approved.count or 0)

    with col4:
        posted_today = supabase.table('pending_replies').select('id', count='exact')\
            .eq('approval_status', 'posted')\
            .gte('posted_at', datetime.now().strftime('%Y-%m-%d')).execute()
        st.metric("🚀 Posted Today", posted_today.count or 0)

    with col5:
        active_threads = supabase.table('conversation_threads').select('id', count='exact')\
            .eq('status', 'active').execute()
        st.metric("💬 Conversations", active_threads.count or 0)

    st.markdown("---")

    # Recent Activity
    st.markdown("### Recent Activity")

    view_option = st.radio("📅 Time Period", ["Last 7 Days", "Last 30 Days", "All Time"], horizontal=True, index=2)

    if view_option == "Last 7 Days":
        cutoff = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        recent_leads = supabase.table('leads').select('*').gte('scraped_date', cutoff).execute()
    elif view_option == "Last 30 Days":
        cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        recent_leads = supabase.table('leads').select('*').gte('scraped_date', cutoff).execute()
    else:  # All Time
        recent_leads = supabase.table('leads').select('*').order('created_at', desc=True).execute()

    if recent_leads.data:
        df = pd.DataFrame(recent_leads.data)

        col1, col2 = st.columns(2)

        with col1:
            # Leads by date
            leads_by_date = df.groupby('scraped_date').size().reset_index(name='count')
            fig1 = px.area(leads_by_date, x='scraped_date', y='count',
                          title='Leads Over Time',
                          color_discrete_sequence=['#951B1E'])
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family='Libre Baskerville',
                title_font_family='Garet',
                title_font_color='#3E4938',
                xaxis_title='',
                yaxis_title='Leads'
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # Pain type distribution
            pain_dist = df['intent_type'].value_counts().reset_index()
            pain_dist.columns = ['Pain Type', 'Count']
            fig2 = px.pie(pain_dist, names='Pain Type', values='Count',
                         title='Leads by Type',
                         color_discrete_sequence=['#951B1E', '#3E4938', '#999999', '#C07F00', '#5A4A42'])
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family='Libre Baskerville',
                title_font_family='Garet',
                title_font_color='#3E4938'
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("📊 No recent data. Run the scraper to collect leads!")


# ================================
# PAGE: PENDING APPROVALS
# ================================
elif page == "✅ Pending Approvals":
    st.markdown("# Pending Approvals")
    st.markdown("Review and approve AI-generated replies")

    auth_info = auth.get_current_teacher()

    # Fetch full teacher profile from database
    teacher_result = supabase.table('teacher_profiles')\
        .select('*')\
        .eq('email', auth_info['email'])\
        .single()\
        .execute()

    if not teacher_result.data:
        st.error("Teacher profile not found. Please contact administrator.")
        st.stop()

    teacher = teacher_result.data

    # Check OAuth status
    oauth_enabled = is_oauth_configured()

    if oauth_enabled:
        st.success("✅ YouTube OAuth configured - Replies will post automatically!")
    else:
        st.warning("⚠️ YouTube OAuth not configured - Run `python setup_youtube_oauth.py` to enable auto-posting")

    # Fetch ALL pending approvals (visible to all teachers)
    st.info("💡 **New System:** All leads visible to all teachers. You can claim any lead by approving it.")

    pending = supabase.table('pending_replies')\
        .select('*, conversation_threads(*)')\
        .eq('approval_status', 'pending')\
        .order('generated_at', desc=True)\
        .execute()

    if not pending.data:
        st.success("🎉 All caught up! No pending approvals.")
    else:
        # Show all leads - teachers can pick which to respond to
        my_leads = [r for r in pending.data if r.get('assigned_teacher_id') == teacher.get('id')]
        available_leads = [r for r in pending.data if not r.get('assigned_teacher_id')]
        other_leads = [r for r in pending.data if r.get('assigned_teacher_id') and r.get('assigned_teacher_id') != teacher.get('id')]

        st.markdown(f"**Your Active Conversations:** {len(my_leads)} | **Available:** {len(available_leads)} | **Other Teachers:** {len(other_leads)}")

        # Approval Cards
        for i, reply in enumerate(pending.data, 1):
            thread = reply.get('conversation_threads', {}) or {}

            with st.expander(
                f"**#{i}** | {reply['lead_name']} | "
                f"{thread.get('pain_type', 'unknown').replace('_', ' ').title()} | "
                f"Readiness: {thread.get('readiness_score', 0)}%",
                expanded=(i == 1)
            ):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"### {reply['lead_name']}")
                    st.markdown("**Their Comment:**")
                    st.info(reply['their_last_message'])

                with col2:
                    st.markdown(get_pain_badge(thread.get('pain_type', 'unknown')), unsafe_allow_html=True)
                    st.metric("Readiness", f"{thread.get('readiness_score', 0)}%")
                    st.metric("Stage", thread.get('conversation_stage', 0))

                    if thread.get('comment_url'):
                        st.link_button("🔗 View on YouTube", thread['comment_url'])

                st.markdown("---")

                # Editable Reply
                st.markdown("**🤖 AI Generated Reply:**")
                edited_reply = st.text_area(
                    "Edit if needed:",
                    value=reply['ai_generated_reply'],
                    height=200,
                    key=f"reply_{reply['id']}"
                )

                st.markdown("---")

                # Action Buttons
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if st.button("✅ Approve & Post", key=f"approve_{reply['id']}", use_container_width=True):
                        # Assign to current teacher if not already assigned
                        if not reply.get('assigned_teacher_id'):
                            supabase.table('pending_replies').update({
                                'assigned_teacher_id': teacher['id']
                            }).eq('id', reply['id']).execute()
                            st.info(f"✓ Lead claimed by {teacher['teacher_name']}")


                        # Update reply with edited text
                        supabase.table('pending_replies').update({
                            'ai_generated_reply': edited_reply
                        }).eq('id', reply['id']).execute()

                        # Check if OAuth is configured
                        if oauth_enabled:
                            # Auto-post to YouTube
                            with st.spinner("🚀 Posting to YouTube..."):
                                try:
                                    poster = YouTubePoster(supabase)

                                    # Extract comment ID
                                    comment_url = thread.get('comment_url', '')
                                    comment_id = poster.extract_comment_id(comment_url)

                                    if not comment_id:
                                        st.error(f"❌ Could not extract comment ID from: {comment_url}")
                                    else:
                                        # Post the reply
                                        result = poster.post_comment_reply(comment_id, edited_reply)

                                        if result['status'] == 'success':
                                            # Mark as posted
                                            supabase.table('pending_replies').update({
                                                'approval_status': 'posted',
                                                'approved_at': datetime.now().isoformat(),
                                                'posted_at': result['posted_at']
                                            }).eq('id', reply['id']).execute()

                                            # Update thread + append reply to history
                                            next_stage = thread.get('conversation_stage', 0) + 1
                                            new_history = (thread.get('full_history') or '') + (
                                                f"\n\n[Stage {next_stage} - Teacher Reply | {datetime.now().strftime('%Y-%m-%d')}]\n"
                                                f"Teacher ({teacher['teacher_name']}): {edited_reply}"
                                            )
                                            supabase.table('conversation_threads').update({
                                                'conversation_stage': next_stage,
                                                'last_reply_date': datetime.now().strftime('%Y-%m-%d'),
                                                'full_history': new_history,
                                                'status': 'waiting_response'
                                            }).eq('id', thread.get('id')).execute()

                                            st.success("✅ Reply posted to YouTube and verified visible!")
                                            st.balloons()

                                        elif result['status'] == 'posted_unverified':
                                            # Posted but not verified visible
                                            supabase.table('pending_replies').update({
                                                'approval_status': 'approved',
                                                'approved_at': datetime.now().isoformat(),
                                            }).eq('id', reply['id']).execute()

                                            st.warning(f"⚠️ Posted but not verified: {result.get('error')}")
                                            st.info("Reply may be held for review. Please manually check YouTube.")
                                            st.info("👉 Go to 'Approved Replies' to post manually if needed")

                                        else:
                                            # Mark as approved but not posted
                                            supabase.table('pending_replies').update({
                                                'approval_status': 'approved',
                                                'approved_at': datetime.now().isoformat()
                                            }).eq('id', reply['id']).execute()

                                            st.error(f"❌ Failed to post: {result.get('error', 'Unknown error')}")
                                            st.info("👉 Go to 'Approved Replies' to post manually")

                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                                    # Mark as approved
                                    supabase.table('pending_replies').update({
                                        'approval_status': 'approved',
                                        'approved_at': datetime.now().isoformat()
                                    }).eq('id', reply['id']).execute()
                                    st.info("👉 Moved to 'Approved Replies' for manual posting")

                        else:
                            # OAuth not configured - mark as approved for manual posting
                            supabase.table('pending_replies').update({
                                'approval_status': 'approved',
                                'approved_at': datetime.now().isoformat()
                            }).eq('id', reply['id']).execute()

                            st.success("✅ Reply approved!")
                            st.info("👉 Go to 'Approved Replies' to post it manually")

                        st.rerun()

                with col2:
                    if st.button("❌ Reject", key=f"reject_{reply['id']}", use_container_width=True):
                        supabase.table('pending_replies').update({
                            'approval_status': 'rejected'
                        }).eq('id', reply['id']).execute()
                        st.warning("❌ Reply rejected")
                        st.rerun()

                with col3:
                    if st.button("💾 Save Changes", key=f"save_{reply['id']}", use_container_width=True):
                        supabase.table('pending_replies').update({
                            'ai_generated_reply': edited_reply
                        }).eq('id', reply['id']).execute()
                        st.success("💾 Changes saved!")

                with col4:
                    if st.button("⏭️ Skip", key=f"skip_{reply['id']}", use_container_width=True):
                        st.info("Skipped to next")


# ================================
# PAGE: APPROVED REPLIES
# ================================
elif page == "🚀 Approved Replies":
    st.markdown("# Approved Replies")
    st.markdown("Post approved replies to YouTube")

    teacher = auth.get_current_teacher()

    # Tabs for different statuses
    tab1, tab2 = st.tabs(["✅ Ready to Post", "🚀 Already Posted"])

    with tab1:
        # Fetch approved but not yet posted replies
        approved = supabase.table('pending_replies')\
            .select('*, conversation_threads(*)')\
            .eq('approval_status', 'approved')\
            .order('approved_at', desc=True)\
            .execute()

        if not approved.data:
            st.info("No approved replies waiting to be posted.")
        else:
            st.success(f"✅ **{len(approved.data)} approved replies** ready to post")

            for i, reply in enumerate(approved.data, 1):
                thread = reply.get('conversation_threads', {}) or {}

                with st.expander(
                    f"**#{i}** | {reply['lead_name']} | "
                    f"Approved {format_timestamp(reply.get('approved_at'))}",
                    expanded=(i == 1)
                ):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"### {reply['lead_name']}")

                        st.markdown("**Their Comment:**")
                        st.info(reply['their_last_message'])

                        st.markdown("**Your Approved Reply:**")
                        st.success(reply['ai_generated_reply'])

                    with col2:
                        st.markdown(get_pain_badge(thread.get('pain_type', 'unknown')), unsafe_allow_html=True)
                        st.metric("Readiness", f"{thread.get('readiness_score', 0)}%")

                        st.markdown("**Post to YouTube:**")

                        if thread.get('comment_url'):
                            st.link_button("🔗 Open YouTube Comment", thread['comment_url'], use_container_width=True)

                            st.markdown("---")

                            # Copy button for reply text
                            st.text_area(
                                "Copy this reply:",
                                value=reply['ai_generated_reply'],
                                height=150,
                                key=f"copy_{reply['id']}"
                            )

                            st.caption("👆 Copy the reply above, then click the YouTube link and paste it")

                    st.markdown("---")

                    # Mark as posted button
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("✅ Mark as Posted", key=f"mark_posted_{reply['id']}", use_container_width=True):
                            supabase.table('pending_replies').update({
                                'approval_status': 'posted',
                                'posted_at': datetime.now().isoformat()
                            }).eq('id', reply['id']).execute()

                            # Update thread stage + append reply to history
                            next_stage = thread.get('conversation_stage', 0) + 1
                            new_history = (thread.get('full_history') or '') + (
                                f"\n\n[Stage {next_stage} - Teacher Reply | {datetime.now().strftime('%Y-%m-%d')}]\n"
                                f"Teacher: {reply['ai_generated_reply']}"
                            )
                            supabase.table('conversation_threads').update({
                                'conversation_stage': next_stage,
                                'last_reply_date': datetime.now().strftime('%Y-%m-%d'),
                                'full_history': new_history,
                                'status': 'waiting_response'
                            }).eq('id', thread.get('id')).execute()

                            st.success("✅ Marked as posted!")
                            st.rerun()

                    with col2:
                        if st.button("🔙 Back to Pending", key=f"back_pending_{reply['id']}", use_container_width=True):
                            supabase.table('pending_replies').update({
                                'approval_status': 'pending'
                            }).eq('id', reply['id']).execute()
                            st.info("Moved back to pending")
                            st.rerun()

                    with col3:
                        if st.button("❌ Cancel", key=f"cancel_{reply['id']}", use_container_width=True):
                            supabase.table('pending_replies').update({
                                'approval_status': 'rejected'
                            }).eq('id', reply['id']).execute()
                            st.warning("Cancelled")
                            st.rerun()

    with tab2:
        # Fetch posted replies
        posted = supabase.table('pending_replies')\
            .select('*, conversation_threads(*)')\
            .eq('approval_status', 'posted')\
            .order('posted_at', desc=True)\
            .limit(50)\
            .execute()

        if not posted.data:
            st.info("No posted replies yet.")
        else:
            st.success(f"🚀 **{len(posted.data)} replies** posted to YouTube")

            for i, reply in enumerate(posted.data, 1):
                thread = reply.get('conversation_threads', {}) or {}

                with st.expander(
                    f"**#{i}** | {reply['lead_name']} | "
                    f"Posted {format_timestamp(reply.get('posted_at'))}"
                ):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"### {reply['lead_name']}")
                        st.markdown("**Reply Posted:**")
                        st.success(reply['ai_generated_reply'])

                    with col2:
                        st.markdown(get_status_badge('posted'), unsafe_allow_html=True)
                        st.markdown(get_pain_badge(thread.get('pain_type', 'unknown')), unsafe_allow_html=True)

                        if thread.get('comment_url'):
                            st.link_button("🔗 View on YouTube", thread['comment_url'])


# ================================
# PAGE: CONVERSATIONS
# ================================
elif page == "💬 Conversations":
    st.markdown("# Conversations")
    st.markdown("View all conversation threads with leads")

    all_threads = supabase.table('conversation_threads')\
        .select('*')\
        .order('updated_at', desc=True)\
        .execute()

    threads_data = all_threads.data or []

    # Bucket by status
    active_threads = [t for t in threads_data if t.get('status') == 'active']
    waiting_threads = [t for t in threads_data if t.get('status') == 'waiting_response']
    other_threads = [t for t in threads_data if t.get('status') not in ('active', 'waiting_response')]

    tab_all, tab_waiting, tab_active, tab_other = st.tabs([
        f"All ({len(threads_data)})",
        f"Waiting Response ({len(waiting_threads)})",
        f"Active ({len(active_threads)})",
        f"Other ({len(other_threads)})",
    ])

    def render_thread_card(thread, key_prefix=""):
        status = thread.get('status', 'unknown')
        status_emoji = {"active": "🟢", "waiting_response": "⏳", "closed": "✅"}.get(status, "⚪")
        with st.expander(
            f"{status_emoji} **{thread['comment_author']}** | "
            f"Stage {thread['conversation_stage']} | "
            f"Readiness: {thread.get('readiness_score', 0)}% | "
            f"Status: {status}"
        ):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown("**Original Comment:**")
                st.write(thread['original_comment'])

                if thread.get('full_history'):
                    st.markdown("**Conversation History:**")
                    st.text_area(
                        "",
                        value=thread['full_history'],
                        height=200,
                        disabled=True,
                        key=f"{key_prefix}history_{thread['id']}"
                    )
                else:
                    st.caption("No reply history yet.")

            with col2:
                st.markdown(get_pain_badge(thread.get('pain_type', 'unknown')), unsafe_allow_html=True)
                st.metric("Stage", thread['conversation_stage'])
                st.metric("Readiness", f"{thread.get('readiness_score', 0)}%")

                if thread.get('comment_url'):
                    st.link_button("🔗 YouTube", thread['comment_url'])

    with tab_all:
        if not threads_data:
            st.info("No conversations yet")
        else:
            st.success(f"💬 {len(threads_data)} total conversations")
            for thread in threads_data:
                render_thread_card(thread, key_prefix="all_")

    with tab_waiting:
        if not waiting_threads:
            st.info("No conversations waiting for response")
        else:
            st.success(f"⏳ {len(waiting_threads)} conversations waiting for lead response")
            for thread in waiting_threads:
                render_thread_card(thread, key_prefix="wait_")

    with tab_active:
        if not active_threads:
            st.info("No active conversations")
        else:
            st.success(f"🟢 {len(active_threads)} active conversations")
            for thread in active_threads:
                render_thread_card(thread, key_prefix="act_")

    with tab_other:
        if not other_threads:
            st.info("No other conversations")
        else:
            for thread in other_threads:
                render_thread_card(thread, key_prefix="oth_")


# ================================
# PAGE: ALL LEADS
# ================================
elif page == "📋 All Leads":
    st.markdown("# All Leads")
    st.markdown("View and filter qualified leads")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        intent_filter = st.multiselect(
            "Pain Type",
            options=['spiritual', 'mental_pain', 'discipline', 'physical_pain', 'practice_aligned', 'low_intent'],
            default=['spiritual', 'mental_pain', 'discipline', 'practice_aligned']
        )

    with col2:
        min_readiness = st.slider("Min Readiness", 0, 100, 50)
        st.caption(f"🎯 Selected: {min_readiness}%")

    with col3:
        days_back = st.selectbox("Time Period", [7, 14, 30, 90, 365, "All Time"], index=5)

    # Fetch leads
    if days_back == "All Time":
        query = supabase.table('leads')\
            .select('*')\
            .gte('readiness_score', min_readiness)
    else:
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        query = supabase.table('leads')\
            .select('*')\
            .gte('scraped_date', cutoff_date)\
            .gte('readiness_score', min_readiness)

    if intent_filter:
        query = query.in_('intent_type', intent_filter)

    leads = query.order('created_at', desc=True).execute()

    if leads.data:
        st.success(f"Found {len(leads.data)} leads")

        df = pd.DataFrame(leads.data)
        display_cols = ['name', 'intent_type', 'pain_intensity', 'readiness_score', 'scraped_date', 'comment']
        display_df = df[[c for c in display_cols if c in df.columns]]

        st.dataframe(display_df, use_container_width=True, height=600)

        # Export
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            data=csv,
            file_name=f"leads_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No leads found matching filters")


# ================================
# PAGE: TEACHERS
# ================================
elif page == "👥 Teachers":
    st.markdown("# Teachers")
    st.markdown("Manage teacher profiles")

    teachers = supabase.table('teacher_profiles').select('*').execute()

    if teachers.data:
        for t in teachers.data:
            with st.expander(f"**{t['teacher_name']}** {'✅' if t['active'] else '❌'}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Email:** {t['email']}")
                    st.write(f"**Role:** {t.get('role', 'N/A')}")
                    st.write(f"**Tone:** {t.get('tone_preference', 'N/A')}")

                with col2:
                    st.write(f"**Contact:** {t.get('contact_number', 'N/A')}")
                    st.write(f"**Daily Limit:** {t.get('daily_reply_limit', 10)}")
                    st.write(f"**Status:** {'Active' if t['active'] else 'Inactive'}")

    st.markdown("---")
    st.markdown("### Add New Teacher")

    with st.form("add_teacher"):
        name = st.text_input("Name*")
        email = st.text_input("Email*")
        contact = st.text_input("Contact")
        role = st.text_input("Role")
        tone = st.selectbox("Tone", ["Compassionate", "Casual", "Formal"])
        daily_limit = st.number_input("Daily Limit", 1, 50, 10)
        active = st.checkbox("Active", value=True)

        if st.form_submit_button("Add Teacher"):
            if name and email:
                supabase.table('teacher_profiles').insert({
                    'teacher_name': name,
                    'email': email,
                    'contact_number': contact,
                    'role': role,
                    'tone_preference': tone,
                    'daily_reply_limit': daily_limit,
                    'active': active
                }).execute()
                st.success(f"✅ Added {name}")
                st.rerun()
            else:
                st.error("Name and email required")


# ================================
# PAGE: RESOURCES
# ================================
elif page == "📚 Resources":
    st.markdown("# Resources")
    st.markdown("Manage Isha Foundation resources")

    resources = supabase.table('resources').select('*').order('times_shared', desc=True).execute()

    if resources.data:
        for r in resources.data:
            with st.expander(f"**{r['resource_name']}** {'✅' if r['active'] else '❌'} | Shared: {r['times_shared']}x"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Link:** {r.get('resource_link', 'N/A')}")
                    st.write(f"**Description:** {r.get('description', 'N/A')}")
                    st.write(f"**When to Share:** {r.get('when_to_share', 'N/A')}")

                with col2:
                    st.write(f"**Type:** {r.get('resource_type', 'N/A')}")
                    st.write(f"**Pain Types:** {', '.join(r.get('pain_types', []))}")
                    st.write(f"**Min Readiness:** {r.get('minimum_readiness_score', 0)}%")


# ================================
# PAGE: MY PROFILE
# ================================
elif page == "👤 My Profile":
    st.markdown("# My Profile")

    auth_info = auth.get_current_teacher()

    # Fetch full teacher profile from database
    teacher_result = supabase.table('teacher_profiles')\
        .select('*')\
        .eq('email', auth_info['email'])\
        .single()\
        .execute()

    if not teacher_result.data:
        st.error("Teacher profile not found. Please contact administrator.")
        st.stop()

    teacher = teacher_result.data

    st.markdown(f"### Welcome, {teacher['teacher_name']}!")

    with st.form("edit_profile"):
        st.markdown("#### Edit Your Profile")

        name = st.text_input("Name", value=teacher.get('teacher_name', ''))
        email_display = st.text_input("Email (read-only)", value=teacher.get('email', ''), disabled=True)
        contact = st.text_input("Contact", value=teacher.get('contact_number', '') or '')
        about_teacher = st.text_area(
            "About Teacher",
            value=teacher.get('role', '') or '',
            height=150,
            help="Write a complete description about yourself, your experience, and teaching style"
        )
        tone = st.selectbox(
            "Tone",
            options=["Compassionate", "Casual", "Formal"],
            index=["Compassionate", "Casual", "Formal"].index(teacher.get('tone_preference', 'Compassionate'))
        )
        sign_off = st.text_area("Sign-off", value=teacher.get('sign_off', '') or '')
        daily_limit = st.number_input("Daily Reply Limit", 1, 50, teacher.get('daily_reply_limit', 10))

        if st.form_submit_button("💾 Save Changes"):
            try:
                supabase.table('teacher_profiles').update({
                    'teacher_name': name,
                    'contact_number': contact,
                    'role': about_teacher,
                    'tone_preference': tone,
                    'sign_off': sign_off,
                    'daily_reply_limit': daily_limit
                }).eq('id', teacher['id']).execute()

                st.success("✅ Profile updated successfully!")
                st.balloons()
                # Force refresh
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving: {e}")
                st.info("Please try again or contact administrator")

    st.markdown("---")

    # Teacher Learning Section
    st.markdown("### 🎓 AI Learning from Your Edits")

    try:
        # Fetch edit count
        edits = supabase.table('teacher_edits')\
            .select('id', count='exact')\
            .eq('teacher_id', teacher['id'])\
            .execute()

        edit_count = edits.count or 0
        st.metric("Total Edits Captured", edit_count)

        if edit_count >= 10:
            learned_style = teacher.get('learned_style', {})

            if learned_style:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 📊 Your Style Profile")

                    verbosity = learned_style.get('tone_preferences', {}).get('verbosity', 'balanced')
                    st.write(f"**Response Length:** {verbosity.replace('_', ' ').title()}")

                    avg_change = learned_style.get('avg_length_change', 0)
                    if avg_change > 0:
                        st.write(f"**Editing Pattern:** You typically add ~{int(avg_change)} characters")
                    else:
                        st.write(f"**Editing Pattern:** You typically remove ~{int(abs(avg_change))} characters")

                with col2:
                    st.markdown("#### 💬 Your Common Phrases")
                    common_phrases = teacher.get('common_phrases', [])[:10]

                    if common_phrases:
                        for phrase in common_phrases:
                            st.caption(f"• {phrase}")
                    else:
                        st.info("Keep editing responses to build your phrase library!")

            # Refresh learning button
            if st.button("🔄 Refresh Learning Profile"):
                with st.spinner("Analyzing your edits..."):
                    from src.teacher_learning import TeacherLearner
                    from src.database import SupabaseDatabase

                    db = SupabaseDatabase()
                    learner = TeacherLearner(db)
                    learner.update_teacher_profile(teacher['id'])
                    st.success("✅ Learning profile updated!")
                    st.rerun()

        elif edit_count > 0:
            st.info(f"🎯 Edit {10 - edit_count} more responses to unlock AI learning!")
            st.caption("The AI will learn your style and adapt future responses automatically.")
        else:
            st.info("💡 Start editing AI responses to train the system to match your style!")

    except Exception:
        # teacher_edits table may not exist yet — show a friendly message instead of error
        st.info("💡 Start editing AI responses to train the system to match your style!")

    st.markdown("---")

    # Personal stats
    st.markdown("### My Statistics")

    col1, col2, col3 = st.columns(3)

    approved = supabase.table('pending_replies')\
        .select('id', count='exact')\
        .eq('assigned_teacher_id', teacher['id'])\
        .eq('approval_status', 'approved')\
        .execute()

    posted = supabase.table('pending_replies')\
        .select('id', count='exact')\
        .eq('assigned_teacher_id', teacher['id'])\
        .eq('approval_status', 'posted')\
        .execute()

    pending = supabase.table('pending_replies')\
        .select('id', count='exact')\
        .eq('assigned_teacher_id', teacher['id'])\
        .eq('approval_status', 'pending')\
        .execute()

    with col1:
        st.metric("Approved Replies", approved.count or 0)

    with col2:
        st.metric("Posted Replies", posted.count or 0)

    with col3:
        st.metric("Pending Reviews", pending.count or 0)


# ================================
# FOOTER
# ================================
st.sidebar.markdown("---")
st.sidebar.caption(f"""
**System Info**
Version: 2.0 (Supabase)
Updated: {datetime.now().strftime('%Y-%m-%d')}
""")
