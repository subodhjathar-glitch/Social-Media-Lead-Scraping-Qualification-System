"""
Simple email gate for internal use only.

No database, no Supabase Auth, no magic links.
Access only if email is in the allowed list (env ALLOWED_EMAILS or default).
"""

import os
import streamlit as st
from typing import Optional, Dict, List


def _allowed_emails() -> List[str]:
    """Normalized list of allowed emails (lowercase, stripped)."""
    raw = os.getenv(
        "ALLOWED_EMAILS",
        "subodh.jathar@gmail.com,durgesh.lokhande@gmail.com,yogavani.hathayoga@gmail.com,CO_TEAM_EMAIL_HERE"
    )
    return [e.strip().lower() for e in raw.split(",") if e.strip()]


class SimpleEmailGate:
    """Minimal auth: single email input, allow only if email is in allowed list."""

    def __init__(self):
        self._allowed = _allowed_emails()
        if "auth_email" not in st.session_state:
            st.session_state.auth_email = None

    def login(self, email: str) -> bool:
        """Allow access only if email is in the allowed list. Returns True if allowed."""
        normalized = (email or "").strip().lower()
        if not normalized:
            return False
        if normalized in self._allowed:
            st.session_state.auth_email = normalized
            return True
        return False

    def logout(self):
        """Clear session (email)."""
        st.session_state.auth_email = None

    def is_authenticated(self) -> bool:
        return bool(st.session_state.get("auth_email"))

    def get_current_teacher(self) -> Optional[Dict]:
        """Return a minimal teacher-like dict for compatibility with the rest of the app."""
        email = st.session_state.get("auth_email")
        if not email:
            return None
        return {
            "email": email,
            "teacher_name": email.split("@")[0].replace(".", " ").title(),
            "role": "User",
        }

    def require_auth(self):
        """Show login screen if not authenticated; otherwise allow access."""
        if not self.is_authenticated():
            self._show_login_page()
            st.stop()

    def _show_login_page(self):
        st.markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <h1 style="color: #8b4513;">🕉️ Isha Lead Engagement System</h1>
                <p style="font-size: 1.2rem; color: #666;">Internal use only</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔐 Login")
            with st.form("login_form"):
                email = st.text_input(
                    "Email",
                    placeholder="your.email@example.com",
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button("Continue")
                if submitted:
                    if email:
                        if self.login(email):
                            st.success("Welcome.")
                            st.rerun()
                        else:
                            st.error("Access Denied.")
                    else:
                        st.warning("Enter your email.")

    def show_user_info(self):
        """Show signed-in email and Logout button in sidebar."""
        if self.is_authenticated():
            teacher = self.get_current_teacher()
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 👤 Signed in")
            st.sidebar.info(teacher["email"])
            if st.sidebar.button("🚪 Logout", use_container_width=True):
                self.logout()
                st.rerun()
