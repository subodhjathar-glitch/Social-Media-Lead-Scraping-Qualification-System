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
        Build HTML email content from leads.

        Args:
            leads: List of lead dictionaries

        Returns:
            HTML string
        """
        # Group leads by intent
        high_leads = [l for l in leads if l['fields'].get('Intent') == 'High']
        medium_leads = [l for l in leads if l['fields'].get('Intent') == 'Medium']
        low_leads = [l for l in leads if l['fields'].get('Intent') == 'Low']

        total = len(leads)
        high_count = len(high_leads)
        medium_count = len(medium_leads)
        low_count = len(low_leads)

        high_pct = (high_count / total * 100) if total > 0 else 0
        medium_pct = (medium_count / total * 100) if total > 0 else 0
        low_pct = (low_count / total * 100) if total > 0 else 0

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
                .high {{ border-left: 4px solid #ff6b6b; }}
                .medium {{ border-left: 4px solid #ffa500; }}
                .low {{ border-left: 4px solid #4CAF50; }}
                .author {{ font-weight: bold; font-size: 16px; }}
                .confidence {{ color: #666; font-size: 14px; }}
                .comment {{ margin: 10px 0; font-style: italic; }}
                .reasoning {{ color: #555; font-size: 14px; background-color: #f9f9f9; padding: 10px; border-radius: 3px; }}
                .links {{ margin-top: 10px; }}
                .links a {{ margin-right: 15px; color: #1a73e8; text-decoration: none; }}
                .links a:hover {{ text-decoration: underline; }}
                h2 {{ color: #333; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
            </style>
        </head>
        <body>
            <h1>🎯 Lead Digest - {datetime.now().strftime('%Y-%m-%d')}</h1>

            <div class="summary">
                <h3>📊 Summary</h3>
                <ul>
                    <li><strong>Total Leads:</strong> {total}</li>
                    <li><strong>🔥 High Intent:</strong> {high_count} ({high_pct:.1f}%)</li>
                    <li><strong>📌 Medium Intent:</strong> {medium_count} ({medium_pct:.1f}%)</li>
                    <li><strong>📝 Low Intent:</strong> {low_count} ({low_pct:.1f}%)</li>
                </ul>
            </div>
        """

        # High Intent Leads
        if high_leads:
            html += "<h2>🔥 High Intent Leads</h2>"
            for lead in high_leads:
                fields = lead['fields']
                html += f"""
                <div class="lead high">
                    <div class="author">{fields.get('Name', 'Unknown')}</div>
                    <div class="confidence">Confidence: {fields.get('Confidence', 0)}%</div>
                    <div class="comment">"{fields.get('Comment', '')}"</div>
                    <div class="reasoning"><strong>AI Reasoning:</strong> {fields.get('AI Reasoning', '')}</div>
                    <div class="links">
                        <a href="{fields.get('Comment URL', '')}" target="_blank">💬 View Comment</a>
                        <a href="{fields.get('Video URL', '')}" target="_blank">🎥 Watch Video</a>
                    </div>
                </div>
                """

        # Medium Intent Leads
        if medium_leads:
            html += "<h2>📌 Medium Intent Leads</h2>"
            for lead in medium_leads:
                fields = lead['fields']
                html += f"""
                <div class="lead medium">
                    <div class="author">{fields.get('Name', 'Unknown')}</div>
                    <div class="confidence">Confidence: {fields.get('Confidence', 0)}%</div>
                    <div class="comment">"{fields.get('Comment', '')}"</div>
                    <div class="reasoning"><strong>AI Reasoning:</strong> {fields.get('AI Reasoning', '')}</div>
                    <div class="links">
                        <a href="{fields.get('Comment URL', '')}" target="_blank">💬 View Comment</a>
                        <a href="{fields.get('Video URL', '')}" target="_blank">🎥 Watch Video</a>
                    </div>
                </div>
                """

        # Low Intent Leads (optional, can be collapsed)
        if low_leads:
            html += "<h2>📝 Low Intent Leads</h2>"
            html += f"<p><em>{len(low_leads)} low intent leads captured for completeness.</em></p>"
            html += "<details><summary>Click to expand</summary>"
            for lead in low_leads:
                fields = lead['fields']
                html += f"""
                <div class="lead low">
                    <div class="author">{fields.get('Name', 'Unknown')}</div>
                    <div class="confidence">Confidence: {fields.get('Confidence', 0)}%</div>
                    <div class="comment">"{fields.get('Comment', '')}"</div>
                    <div class="links">
                        <a href="{fields.get('Comment URL', '')}" target="_blank">💬 View Comment</a>
                    </div>
                </div>
                """
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
