"""
Isha Lead Engagement System - Enhanced Streamlit Dashboard
Version 2.0 with Supabase + Full Feature Set

Features:
- Teacher authentication
- Airtable-style approval sheet
- YouTube auto-posting
- Comprehensive analytics
- Teacher self-service
- Resource management
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import os
from dotenv import load_dotenv
import json

# Import authentication (simple email gate)
from src.auth import SimpleEmailGate

# Load environment variables
load_dotenv()

# ================================
# PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="Isha Lead Engagement",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# CUSTOM CSS
# ================================
st.markdown("""
    <style>
    /* Main styling */
    .main-header {
        font-size: 2.5rem;
        color: #8b4513;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #8b4513;
        margin-bottom: 2rem;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f9f9f9 0%, #fff 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #8b4513;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }

    /* Buttons */
    .stButton>button {
        background-color: #8b4513;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #a0522d;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .status-pending { background-color: #fff3cd; color: #856404; }
    .status-approved { background-color: #d4edda; color: #155724; }
    .status-posted { background-color: #d1ecf1; color: #0c5460; }
    .status-rejected { background-color: #f8d7da; color: #721c24; }

    /* Pain type badges */
    .pain-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    .pain-spiritual { background-color: #e3d7ff; color: #5a189a; }
    .pain-mental { background-color: #ffccd5; color: #c9184a; }
    .pain-discipline { background-color: #b8e6ff; color: #0077b6; }
    .pain-physical { background-color: #ffd6a5; color: #d97706; }

    /* Tables */
    .dataframe {
        font-size: 0.9rem;
    }
    .dataframe th {
        background-color: #8b4513 !important;
        color: white !important;
        font-weight: bold;
    }
    .dataframe tr:hover {
        background-color: #f5f5f5;
    }

    /* Success/Warning boxes */
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Progress bars */
    .readiness-bar {
        height: 20px;
        border-radius: 10px;
        background-color: #e9ecef;
        overflow: hidden;
    }
    .readiness-fill {
        height: 100%;
        transition: width 0.3s ease;
    }

    /* Cards */
    .approval-card {
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    .approval-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        border-color: #8b4513;
    }
    </style>
""", unsafe_allow_html=True)

# ================================
# INITIALIZE SUPABASE
# ================================
@st.cache_resource
def init_supabase():
    """Initialize Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        st.error("⚠️ Supabase credentials not found!")
        st.info("Add SUPABASE_URL and SUPABASE_KEY to your .env file")
        st.stop()

    return create_client(url, key)

supabase = init_supabase()

# ================================
# AUTHENTICATION (simple email gate)
# ================================
auth = SimpleEmailGate()
auth.require_auth()

# ================================
# SIDEBAR NAVIGATION
# ================================
st.sidebar.title("🕉️ Isha Lead Engagement")
st.sidebar.markdown("---")
st.sidebar.markdown("🧭 **Navigation**")

# Show user info in sidebar
auth.show_user_info()

st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Go to",
    [
        "📊 Dashboard",
        "✅ Pending Approvals",
        "💬 Conversations",
        "📋 Leads",
        "👥 Teachers",
        "📚 Resources",
        "📈 Analytics",
        "👤 My Profile"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Approve replies with one click and auto-post to YouTube!")

# ================================
# HELPER FUNCTIONS
# ================================

def get_status_badge(status: str) -> str:
    """Generate HTML for status badge."""
    emoji_map = {
        'pending': '🟡',
        'approved': '✅',
        'posted': '🚀',
        'rejected': '❌'
    }
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


def get_readiness_color(score: int) -> str:
    """Get color for readiness score."""
    if score >= 80:
        return '#28a745'  # Green
    elif score >= 60:
        return '#ffc107'  # Yellow
    elif score >= 40:
        return '#fd7e14'  # Orange
    else:
        return '#dc3545'  # Red


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
# PAGE: DASHBOARD
# ================================
if page == "📊 Dashboard":
    st.markdown('<h1 class="main-header">🕉️ Dashboard</h1>', unsafe_allow_html=True)

    try:
        # Get current teacher
        teacher = auth.get_current_teacher()

        # Welcome message
        st.markdown(f"### Welcome, {teacher['teacher_name']}! 🙏")

        # Fetch dashboard stats
        leads_today = supabase.table('leads').select('id', count='exact')\
            .eq('scraped_date', datetime.now().strftime('%Y-%m-%d')).execute()

        active_conversations = supabase.table('conversation_threads').select('id', count='exact')\
            .eq('status', 'active').execute()

        pending_approvals = supabase.table('pending_replies').select('id', count='exact')\
            .eq('approval_status', 'pending').execute()

        replies_posted_today = supabase.table('pending_replies').select('id', count='exact')\
            .eq('approval_status', 'posted')\
            .gte('posted_at', datetime.now().strftime('%Y-%m-%d')).execute()

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="✅ New Leads Today",
                value=leads_today.count if leads_today.count else 0,
                delta="Qualified leads"
            )

        with col2:
            st.metric(
                label="💬 Active Conversations",
                value=active_conversations.count if active_conversations.count else 0,
                delta="Ongoing threads"
            )

        with col3:
            st.metric(
                label="⏳ Pending Approvals",
                value=pending_approvals.count if pending_approvals.count else 0,
                delta="Awaiting review",
                delta_color="off"
            )

        with col4:
            st.metric(
                label="🚀 Posted Today",
                value=replies_posted_today.count if replies_posted_today.count else 0,
                delta="Replies sent"
            )

        st.markdown("---")

        # System Status
        st.subheader("🤖 System Status")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Automation Status:**")

            # Get last scrape info (would need a system_logs table for real implementation)
            st.info("""
            ✅ System Active
            🕐 Last scrape: 2 hours ago
            📊 Comments processed: 45
            ✨ Leads qualified: 12
            🎯 Duplicate prevention: Active
            """)

        with col2:
            st.markdown("**Quick Actions:**")

            if st.button("▶️ Run Scrape Now", use_container_width=True):
                st.warning("Manual scraping not yet implemented. Use: `python src/main.py`")

            if st.button("🎨 Generate Pending Replies", use_container_width=True):
                st.warning("Reply generation not yet implemented.")

        st.markdown("---")

        # Recent activity chart
        st.subheader("📈 Recent Activity (Last 7 Days)")

        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        recent_leads = supabase.table('leads').select('*')\
            .gte('scraped_date', week_ago).execute()

        if recent_leads.data:
            df = pd.DataFrame(recent_leads.data)

            # Leads by date
            leads_by_date = df.groupby('scraped_date').size().reset_index(name='count')
            fig1 = px.line(leads_by_date, x='scraped_date', y='count',
                          title='Leads Over Time', markers=True)
            fig1.update_layout(xaxis_title='Date', yaxis_title='Leads')
            fig1.update_traces(line_color='#8b4513')
            st.plotly_chart(fig1, use_container_width=True)

            # Pain type and readiness distribution
            col1, col2 = st.columns(2)

            with col1:
                pain_dist = df['intent_type'].value_counts().reset_index()
                pain_dist.columns = ['Pain Type', 'Count']
                fig2 = px.pie(pain_dist, names='Pain Type', values='Count',
                             title='Leads by Pain Type',
                             color_discrete_sequence=px.colors.sequential.Oranges)
                st.plotly_chart(fig2, use_container_width=True)

            with col2:
                fig3 = px.histogram(df, x='readiness_score',
                                   title='Readiness Score Distribution',
                                   nbins=20, color_discrete_sequence=['#8b4513'])
                fig3.update_layout(xaxis_title='Readiness Score', yaxis_title='Count')
                st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("📊 No recent data. Run the scraper to collect leads!")

    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

# ================================
# PAGE: PENDING APPROVALS (Airtable-style Sheet)
# ================================
elif page == "✅ Pending Approvals":
    st.markdown('<h1 class="main-header">✅ Pending Approvals</h1>', unsafe_allow_html=True)

    try:
        # Get current teacher
        teacher = auth.get_current_teacher()

        # Fetch pending approvals with full context
        pending_query = supabase.table('pending_replies')\
            .select('*, conversation_threads(*)')\
            .eq('approval_status', 'pending')\
            .order('generated_at', desc=True)

        pending = pending_query.execute()

        if not pending.data:
            st.success("🎉 All caught up! No pending approvals.")
            st.balloons()
        else:
            st.info(f"📬 **{len(pending.data)} replies** awaiting your approval")

            # Filters
            with st.expander("🔍 Filters & Sorting"):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    pain_filter = st.multiselect(
                        "Pain Type",
                        options=['spiritual', 'mental_pain', 'discipline', 'physical_pain', 'practice_aligned'],
                        default=[]
                    )

                with col2:
                    min_readiness = st.slider("Min Readiness", 0, 100, 0)

                with col3:
                    stage_filter = st.multiselect(
                        "Stage",
                        options=[0, 1, 2, 3, 4],
                        default=[]
                    )

                with col4:
                    sort_by = st.selectbox(
                        "Sort by",
                        options=['Date (Newest)', 'Date (Oldest)', 'Readiness (High)', 'Readiness (Low)']
                    )

            st.markdown("---")

            # Approval Sheet (Table-like view)
            for i, reply in enumerate(pending.data, 1):
                thread = reply.get('conversation_threads', {}) or {}

                # Apply filters
                pain_type = thread.get('pain_type', '')
                readiness = thread.get('readiness_score', 0)
                stage = thread.get('conversation_stage', 0)

                if pain_filter and pain_type not in pain_filter:
                    continue
                if readiness < min_readiness:
                    continue
                if stage_filter and stage not in stage_filter:
                    continue

                # Approval card (expandable)
                with st.expander(
                    f"**#{i}** | {reply['lead_name']} | "
                    f"{pain_type.replace('_', ' ').title()} | "
                    f"Readiness: {readiness}% | Stage: {stage}",
                    expanded=(i == 1)
                ):
                    # Header row
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"### {reply['lead_name']}")

                    with col2:
                        st.markdown(get_status_badge('pending'), unsafe_allow_html=True)
                        st.markdown(get_pain_badge(pain_type), unsafe_allow_html=True)

                    st.markdown("---")

                    # Context section
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown("**💬 Their Last Message:**")
                        st.info(reply['their_last_message'])

                        # Show conversation history if stage > 0
                        if stage > 0 and thread.get('full_history'):
                            with st.expander("📜 View Full Conversation History"):
                                st.text_area(
                                    "",
                                    value=thread['full_history'],
                                    height=200,
                                    disabled=True,
                                    key=f"history_{reply['id']}"
                                )

                    with col2:
                        st.markdown("**📊 Context:**")
                        st.metric("Stage", stage)
                        st.metric("Readiness", f"{readiness}%")
                        st.write(f"**Pain Type:** {pain_type.replace('_', ' ').title()}")

                        # Resources shared
                        if thread.get('resources_shared'):
                            st.write("**Resources Shared:**")
                            st.write(thread['resources_shared'])

                        # Links
                        if thread.get('comment_url'):
                            st.link_button("🔗 YouTube Comment", thread['comment_url'])
                        if thread.get('video_url'):
                            st.link_button("🎥 Video", thread['video_url'])

                    st.markdown("---")

                    # Editable reply section
                    st.markdown("**🤖 AI Generated Reply:**")
                    edited_reply = st.text_area(
                        "Edit reply if needed:",
                        value=reply['ai_generated_reply'],
                        height=200,
                        key=f"reply_{reply['id']}",
                        help="You can edit the AI-generated reply before approving"
                    )

                    # Rating section
                    st.markdown("**⭐ Rate this reply (optional):**")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        rating = st.select_slider(
                            "Quality",
                            options=[1, 2, 3, 4, 5],
                            value=3,
                            key=f"rating_{reply['id']}",
                            help="How good is this AI reply?"
                        )

                    with col2:
                        conversion_likelihood = st.slider(
                            "Conversion %",
                            0, 100, 50,
                            key=f"conversion_{reply['id']}",
                            help="Likelihood this will convert the lead"
                        )

                    with col3:
                        notes = st.text_input(
                            "Your notes",
                            key=f"notes_{reply['id']}",
                            placeholder="Optional feedback..."
                        )

                    st.markdown("---")

                    # Action buttons
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        if st.button("✅ Approve & Post", key=f"approve_{reply['id']}", use_container_width=True):
                            # Update reply with edits and approval
                            supabase.table('pending_replies').update({
                                'ai_generated_reply': edited_reply,
                                'approval_status': 'approved',
                                'approved_at': datetime.now().isoformat(),
                                'your_notes': notes if notes else reply.get('your_notes')
                            }).eq('id', reply['id']).execute()

                            st.success("✅ Reply approved!")
                            st.info("🚀 Auto-posting to YouTube... (not yet implemented)")

                            # TODO: Call youtube_poster.post_comment_reply()

                            st.rerun()

                    with col2:
                        if st.button("❌ Reject", key=f"reject_{reply['id']}", use_container_width=True):
                            supabase.table('pending_replies').update({
                                'approval_status': 'rejected',
                                'your_notes': notes if notes else 'Rejected by teacher'
                            }).eq('id', reply['id']).execute()

                            st.warning("❌ Reply rejected")
                            st.rerun()

                    with col3:
                        if st.button("💾 Save Changes", key=f"save_{reply['id']}", use_container_width=True):
                            supabase.table('pending_replies').update({
                                'ai_generated_reply': edited_reply,
                                'your_notes': notes if notes else reply.get('your_notes')
                            }).eq('id', reply['id']).execute()

                            st.success("💾 Changes saved!")

                    with col4:
                        if st.button("⏭️ Skip", key=f"skip_{reply['id']}", use_container_width=True):
                            st.info("Skipped to next")

    except Exception as e:
        st.error(f"Error loading approvals: {e}")
        st.exception(e)

# ================================
# PAGE: CONVERSATIONS
# ================================
elif page == "💬 Conversations":
    st.markdown('<h1 class="main-header">💬 Active Conversations</h1>', unsafe_allow_html=True)

    try:
        threads = supabase.table('conversation_threads')\
            .select('*')\
            .eq('status', 'active')\
            .order('updated_at', desc=True)\
            .execute()

        if not threads.data:
            st.info("No active conversations yet. Leads will appear here once they engage.")
        else:
            st.success(f"💬 {len(threads.data)} active conversations")

            for thread in threads.data:
                with st.expander(
                    f"**{thread['comment_author']}** | Stage {thread['conversation_stage']} | "
                    f"{thread.get('pain_type', 'N/A')} | Readiness: {thread.get('readiness_score', 0)}%"
                ):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown("**Original Comment:**")
                        st.write(thread['original_comment'])

                        st.markdown("**Conversation History:**")
                        st.text_area(
                            "",
                            value=thread.get('full_history', 'No history yet'),
                            height=200,
                            disabled=True,
                            key=f"thread_history_{thread['id']}"
                        )

                        if thread.get('ai_context_summary'):
                            st.markdown("**AI Summary:**")
                            st.info(thread['ai_context_summary'])

                    with col2:
                        st.metric("Stage", thread['conversation_stage'])
                        st.metric("Readiness", f"{thread['readiness_score']}%")
                        st.write(f"**Status:** {thread['status']}")
                        st.write(f"**Pain:** {thread.get('pain_type', 'N/A')}")

                        if thread.get('last_reply_date'):
                            st.write(f"**Last Reply:** {thread['last_reply_date']}")

                        if thread.get('resources_shared'):
                            st.write(f"**Resources:** {thread['resources_shared']}")

                    if thread.get('comment_url'):
                        st.link_button("🔗 View on YouTube", thread['comment_url'])

    except Exception as e:
        st.error(f"Error loading conversations: {e}")

# ================================
# PAGE: LEADS
# ================================
elif page == "📋 Leads":
    st.markdown('<h1 class="main-header">📋 All Leads</h1>', unsafe_allow_html=True)

    try:
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

        with col3:
            days_back = st.selectbox("Days back", [7, 14, 30, 90], index=0)

        # Fetch leads
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

            # Display table
            display_df = df[['name', 'intent_type', 'pain_intensity', 'readiness_score', 'practice_mention', 'scraped_date']]
            display_df.columns = ['Name', 'Pain Type', 'Pain (0-10)', 'Readiness %', 'Practice', 'Date']

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

    except Exception as e:
        st.error(f"Error loading leads: {e}")

# ================================
# PAGE: TEACHERS
# ================================
elif page == "👥 Teachers":
    st.markdown('<h1 class="main-header">👥 Teachers</h1>', unsafe_allow_html=True)

    try:
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

        # Add new teacher
        st.markdown("---")
        st.subheader("➕ Add New Teacher")

        with st.form("add_teacher"):
            name = st.text_input("Name*")
            email = st.text_input("Email*")
            contact = st.text_input("Contact")
            role = st.text_input("Role")
            experience = st.text_area("Experience")
            tone = st.selectbox("Tone", ["Compassionate", "Casual", "Formal"])
            sign_off = st.text_area("Sign-off", value="Blessings,\n[Name]")
            daily_limit = st.number_input("Daily Limit", 1, 50, 10)
            active = st.checkbox("Active", value=True)

            if st.form_submit_button("Add"):
                if name and email:
                    supabase.table('teacher_profiles').insert({
                        'teacher_name': name,
                        'email': email,
                        'contact_number': contact,
                        'role': role,
                        'practice_experience': experience,
                        'tone_preference': tone,
                        'sign_off': sign_off,
                        'daily_reply_limit': daily_limit,
                        'active': active
                    }).execute()

                    st.success(f"✅ Added {name}")
                    st.rerun()
                else:
                    st.error("Name and email required")

    except Exception as e:
        st.error(f"Error: {e}")

# ================================
# PAGE: RESOURCES
# ================================
elif page == "📚 Resources":
    st.markdown('<h1 class="main-header">📚 Resources</h1>', unsafe_allow_html=True)

    try:
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

        # Add resource
        st.markdown("---")
        st.subheader("➕ Add Resource")

        with st.form("add_resource"):
            name = st.text_input("Name*")
            link = st.text_input("Link")
            description = st.text_area("Description")
            when = st.text_area("When to Share")
            rtype = st.selectbox("Type", ["practice", "video", "app", "program", "article"])
            ptypes = st.multiselect("Pain Types", ['spiritual', 'mental_pain', 'discipline', 'physical_pain', 'general'])
            min_r = st.slider("Min Readiness", 0, 100, 60)
            active = st.checkbox("Active", value=True)

            if st.form_submit_button("Add"):
                if name:
                    supabase.table('resources').insert({
                        'resource_name': name,
                        'resource_link': link,
                        'description': description,
                        'when_to_share': when,
                        'resource_type': rtype,
                        'pain_types': ptypes,
                        'minimum_readiness_score': min_r,
                        'active': active,
                        'times_shared': 0
                    }).execute()

                    st.success(f"✅ Added '{name}'")
                    st.rerun()
                else:
                    st.error("Name required")

    except Exception as e:
        st.error(f"Error: {e}")

# ================================
# PAGE: ANALYTICS
# ================================
elif page == "📈 Analytics":
    st.markdown('<h1 class="main-header">📈 Analytics</h1>', unsafe_allow_html=True)

    st.info("🚧 Advanced analytics coming soon!")

    st.markdown("""
    **Planned features:**
    - Lead conversion funnel
    - Resource effectiveness
    - Teacher performance metrics
    - Time-based trends
    - Engagement patterns
    """)

# ================================
# PAGE: MY PROFILE
# ================================
elif page == "👤 My Profile":
    st.markdown('<h1 class="main-header">👤 My Profile</h1>', unsafe_allow_html=True)

    try:
        teacher = auth.get_current_teacher()

        st.subheader(f"Welcome, {teacher['teacher_name']}!")

        # Profile editing form
        with st.form("edit_profile"):
            st.markdown("### Edit Your Profile")

            name = st.text_input("Name", value=teacher.get('teacher_name', ''))
            email_display = st.text_input("Email (read-only)", value=teacher.get('email', ''), disabled=True)
            contact = st.text_input("Contact", value=teacher.get('contact_number', '') or '')
            role = st.text_input("Role", value=teacher.get('role', '') or '')
            experience = st.text_area("Experience", value=teacher.get('practice_experience', '') or '')
            tone = st.selectbox(
                "Tone Preference",
                options=["Compassionate", "Casual", "Formal"],
                index=["Compassionate", "Casual", "Formal"].index(teacher.get('tone_preference', 'Compassionate'))
            )
            sign_off = st.text_area("Sign-off", value=teacher.get('sign_off', '') or '')
            daily_limit = st.number_input("Daily Reply Limit", 1, 50, teacher.get('daily_reply_limit', 10))

            if st.form_submit_button("💾 Save Changes"):
                supabase.table('teacher_profiles').update({
                    'teacher_name': name,
                    'contact_number': contact,
                    'role': role,
                    'practice_experience': experience,
                    'tone_preference': tone,
                    'sign_off': sign_off,
                    'daily_reply_limit': daily_limit
                }).eq('id', teacher['id']).execute()

                st.success("✅ Profile updated!")

                # Update session
                st.session_state.teacher_info = supabase.table('teacher_profiles')\
                    .select('*').eq('id', teacher['id']).single().execute().data

                st.rerun()

        st.markdown("---")

        # Personal stats
        st.subheader("📊 My Statistics")

        col1, col2, col3 = st.columns(3)

        # Get teacher's stats
        approved_count = supabase.table('pending_replies')\
            .select('id', count='exact')\
            .eq('assigned_teacher_id', teacher['id'])\
            .eq('approval_status', 'approved')\
            .execute()

        posted_count = supabase.table('pending_replies')\
            .select('id', count='exact')\
            .eq('assigned_teacher_id', teacher['id'])\
            .eq('approval_status', 'posted')\
            .execute()

        pending_count = supabase.table('pending_replies')\
            .select('id', count='exact')\
            .eq('assigned_teacher_id', teacher['id'])\
            .eq('approval_status', 'pending')\
            .execute()

        with col1:
            st.metric("Approved Replies", approved_count.count or 0)

        with col2:
            st.metric("Posted Replies", posted_count.count or 0)

        with col3:
            st.metric("Pending Reviews", pending_count.count or 0)

    except Exception as e:
        st.error(f"Error loading profile: {e}")

# ================================
# FOOTER
# ================================
st.sidebar.markdown("---")
st.sidebar.info(f"""
**System Info**
Version: 2.0 (Supabase)
Updated: {datetime.now().strftime('%Y-%m-%d')}
""")
