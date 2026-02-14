"""Email notification system for lead digests."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict

from src.config import settings
from src.utils import setup_logger

logger = setup_logger(__name__)


class EmailNotifier:
    """Sends email digests of qualified leads."""

    def __init__(self):
        """Initialize email configuration."""
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.from_email = settings.email_from
        self.password = settings.email_password

    def _build_html_digest(self, leads: List[Dict]) -> str:
        """
        Build HTML email content from leads (pain-based format).

        Args:
            leads: List of lead dictionaries

        Returns:
            HTML string
        """
        # Group leads by intent_type (new format)
        practice_aligned = [l for l in leads if l['fields'].get('Intent Type') == 'practice_aligned']
        spiritual = [l for l in leads if l['fields'].get('Intent Type') == 'spiritual']
        mental_pain = [l for l in leads if l['fields'].get('Intent Type') == 'mental_pain']
        discipline = [l for l in leads if l['fields'].get('Intent Type') == 'discipline']
        physical_pain = [l for l in leads if l['fields'].get('Intent Type') == 'physical_pain']
        low_intent = [l for l in leads if l['fields'].get('Intent Type') == 'low_intent' or not l['fields'].get('Intent Type')]

        total = len(leads)

        # Build HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .summary {{
                    background-color: #f4f4f4;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .lead {{
                    border: 1px solid #ddd;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 5px;
                    background-color: #fff;
                }}
                .practice_aligned {{ border-left: 4px solid #8b0000; }}
                .spiritual {{ border-left: 4px solid #9b59b6; }}
                .mental_pain {{ border-left: 4px solid #e74c3c; }}
                .discipline {{ border-left: 4px solid #f39c12; }}
                .physical_pain {{ border-left: 4px solid #3498db; }}
                .low {{ border-left: 4px solid #95a5a6; }}
                .author {{ font-weight: bold; font-size: 16px; }}
                .metrics {{ color: #666; font-size: 14px; margin: 5px 0; }}
                .metrics .badge {{ display: inline-block; padding: 2px 8px; margin-right: 10px; border-radius: 3px; background: #e0e0e0; }}
                .practice {{ color: #8b0000; font-weight: bold; }}
                .comment {{ margin: 10px 0; font-style: italic; }}
                .reasoning {{ color: #555; font-size: 14px; background-color: #f9f9f9; padding: 10px; border-radius: 3px; margin-top: 10px; }}
                .links {{ margin-top: 10px; }}
                .links a {{ margin-right: 15px; color: #1a73e8; text-decoration: none; }}
                .links a:hover {{ text-decoration: underline; }}
                h2 {{ color: #333; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
            </style>
        </head>
        <body>
            <h1>🎯 Pain-Based Lead Digest - {datetime.now().strftime('%Y-%m-%d')}</h1>

            <div class="summary">
                <h3>📊 Summary</h3>
                <ul>
                    <li><strong>Total Leads:</strong> {total}</li>
                    <li><strong>🎯 Practice-Aligned:</strong> {len(practice_aligned)} (Highest Priority)</li>
                    <li><strong>✨ Spiritual Longing:</strong> {len(spiritual)}</li>
                    <li><strong>🧠 Mental/Emotional Pain:</strong> {len(mental_pain)}</li>
                    <li><strong>🎯 Discipline Issues:</strong> {len(discipline)}</li>
                    <li><strong>💪 Physical Pain:</strong> {len(physical_pain)}</li>
                    <li><strong>📝 Low Intent:</strong> {len(low_intent)}</li>
                </ul>
            </div>
        """

        # Helper function to build lead card
        def build_lead_card(lead, css_class):
            fields = lead['fields']
            pain = fields.get('Pain Intensity', 0)
            readiness = fields.get('Readiness Score', 0)
            practice = fields.get('Practice Mention', '')
            confidence = fields.get('Confidence', 0)

            practice_html = f'<div class="practice">🎯 Practice: {practice}</div>' if practice else ''

            return f"""
            <div class="lead {css_class}">
                <div class="author">{fields.get('Name', 'Unknown')}</div>
                <div class="metrics">
                    <span class="badge">Pain: {pain}/10</span>
                    <span class="badge">Readiness: {readiness}%</span>
                    <span class="badge">Confidence: {confidence}%</span>
                </div>
                {practice_html}
                <div class="comment">"{fields.get('Comment', '')}"</div>
                <div class="reasoning"><strong>AI Analysis:</strong> {fields.get('AI Reasoning', '')}</div>
                <div class="links">
                    <a href="{fields.get('Comment URL', '')}" target="_blank">💬 View Comment</a>
                    <a href="{fields.get('Video URL', '')}" target="_blank">🎥 Watch Video</a>
                </div>
            </div>
            """

        # Practice-Aligned Leads (HIGHEST PRIORITY)
        if practice_aligned:
            html += "<h2>🎯 Practice-Aligned Leads (Highest Priority)</h2>"
            html += "<p><em>These people mentioned specific practices along with pain signals - ready to engage!</em></p>"
            for lead in practice_aligned:
                html += build_lead_card(lead, 'practice_aligned')

        # Spiritual Longing Leads
        if spiritual:
            html += "<h2>✨ Spiritual Longing Leads</h2>"
            html += "<p><em>Seeking transformation, purpose, or deeper meaning.</em></p>"
            for lead in spiritual:
                html += build_lead_card(lead, 'spiritual')

        # Mental/Emotional Pain Leads
        if mental_pain:
            html += "<h2>🧠 Mental/Emotional Pain Leads</h2>"
            html += "<p><em>Experiencing anxiety, stress, or mental struggles.</em></p>"
            for lead in mental_pain:
                html += build_lead_card(lead, 'mental_pain')

        # Discipline Struggles Leads
        if discipline:
            html += "<h2>🎯 Discipline Struggles (Re-engagement Opportunity)</h2>"
            html += "<p><em>Past practitioners who stopped or struggle with consistency.</em></p>"
            for lead in discipline:
                html += build_lead_card(lead, 'discipline')

        # Physical Pain Leads
        if physical_pain:
            html += "<h2>💪 Physical Pain Leads</h2>"
            html += "<p><em>Experiencing physical discomfort or health issues.</em></p>"
            for lead in physical_pain:
                html += build_lead_card(lead, 'physical_pain')

        # Low Intent Leads (collapsed)
        if low_intent:
            html += "<h2>📝 Low Intent Leads</h2>"
            html += f"<p><em>{len(low_intent)} low intent leads captured for completeness.</em></p>"
            html += "<details><summary>Click to expand</summary>"
            for lead in low_intent:
                html += build_lead_card(lead, 'low')
            html += "</details>"

        html += """
            <hr>
            <p style="color: #666; font-size: 12px;">
                Generated by Social Media Lead Scraper<br>
                Automated via GitHub Actions
            </p>
        </body>
        </html>
        """

        return html

    def send_digest(self, leads: List[Dict], recipients: List[str]) -> bool:
        """
        Send email digest to recipients.

        Args:
            leads: List of lead records from Airtable
            recipients: List of email addresses

        Returns:
            True if sent successfully, False otherwise
        """
        if not leads:
            logger.info("No leads to send. Skipping email.")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Lead Digest - {datetime.now().strftime('%Y-%m-%d')} ({len(leads)} leads)"
            msg['From'] = self.from_email
            msg['To'] = ', '.join(recipients)

            # Build HTML content
            html_content = self._build_html_digest(leads)
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email via Gmail SMTP
            logger.info(f"Sending digest email to {len(recipients)} recipients")
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.from_email, self.password)
                server.send_message(msg)

            logger.info("Email sent successfully")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def send_error_notification(self, error_message: str, recipients: List[str]) -> bool:
        """
        Send error notification email.

        Args:
            error_message: Error description
            recipients: List of email addresses

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 Lead Scraper Error - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.from_email
            msg['To'] = ', '.join(recipients)

            html_content = f"""
            <html>
            <body>
                <h2>🚨 Error in Lead Scraper</h2>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>Error:</strong></p>
                <pre style="background-color: #f4f4f4; padding: 15px; border-radius: 5px;">{error_message}</pre>
                <p>Please check the GitHub Actions logs for more details.</p>
            </body>
            </html>
            """

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.from_email, self.password)
                server.send_message(msg)

            logger.info("Error notification sent successfully")
            return True

        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False
