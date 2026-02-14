"""Email-based approval system for generated replies."""

import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional, List

from src.config import settings
from src.database import AirtableDatabase
from src.utils import setup_logger

logger = setup_logger(__name__)


class EmailApprovalSystem:
    """Manages email-based approval workflow for replies."""

    def __init__(self, database: AirtableDatabase):
        """Initialize email approval system."""
        self.database = database
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.from_email = settings.email_from
        self.password = settings.email_password

    def send_approval_email(self, reply_data: Dict, pending_reply_id: str) -> bool:
        """
        Send approval email for a generated reply.

        Args:
            reply_data: Generated reply data dictionary
            pending_reply_id: Airtable record ID of pending reply

        Returns:
            True if email sent successfully
        """
        try:
            thread_data = reply_data.get('thread_data', {})
            teacher_record = reply_data.get('teacher_record', {})
            teacher_email = teacher_record['fields'].get('Email', '')
            teacher_name = teacher_record['fields'].get('Teacher Name', 'Teacher')

            if not teacher_email:
                logger.error("No teacher email found")
                return False

            # Build email content
            subject = self._build_email_subject(reply_data)
            html_content = self._build_email_body(reply_data, pending_reply_id)

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = teacher_email
            msg['Reply-To'] = self.from_email  # Important for parsing replies

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            logger.info(f"Sending approval email to {teacher_email}")
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.from_email, self.password)
                server.send_message(msg)

            logger.info(f"Approval email sent to {teacher_name} ({teacher_email})")
            return True

        except Exception as e:
            logger.error(f"Error sending approval email: {e}")
            return False

    def _build_email_subject(self, reply_data: Dict) -> str:
        """Build email subject line."""
        thread_data = reply_data.get('thread_data', {})
        lead_name = thread_data.get('Comment Author', 'Unknown')
        pain_type = thread_data.get('Pain Type', 'general')
        stage = thread_data.get('Conversation Stage', 0)
        teacher_name = reply_data.get('teacher_record', {})['fields'].get('Teacher Name', '')

        # Short pain type labels
        pain_labels = {
            'spiritual': 'Spiritual Seeking',
            'mental_pain': 'Anxiety/Stress',
            'discipline': 'Discipline Help',
            'physical_pain': 'Physical Issue',
            'practice_aligned': 'Practice Question'
        }

        pain_label = pain_labels.get(pain_type, 'General')

        return f"[For {teacher_name}] Reply Needed: {pain_label} - {lead_name} (Stage {stage + 1})"

    def _build_email_body(self, reply_data: Dict, pending_reply_id: str) -> str:
        """Build HTML email body."""
        thread_data = reply_data.get('thread_data', {})
        lead_name = thread_data.get('Comment Author', 'Unknown')
        original_comment = thread_data.get('Original Comment', '')
        conversation_stage = thread_data.get('Conversation Stage', 0)
        pain_type = thread_data.get('Pain Type', 'unknown')
        readiness = thread_data.get('Readiness Score', 0)
        full_history = thread_data.get('Full History', '')
        resources_shared = thread_data.get('Resources Shared', '')
        comment_url = thread_data.get('Comment URL', '#')
        video_url = thread_data.get('Video URL', '#')

        generated_reply = reply_data.get('reply_text', '')
        suggested_resource = reply_data.get('suggested_resource', 'None')

        # Format conversation history for email
        history_lines = full_history.split('\n')
        formatted_history = '<br>'.join(history_lines)

        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 700px;
                    margin: 0 auto;
                }}
                .header {{
                    background-color: #8b4513;
                    color: white;
                    padding: 20px;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    border: 1px solid #ddd;
                    border-top: none;
                    padding: 20px;
                    background-color: #fff;
                }}
                .section {{
                    margin-bottom: 25px;
                    padding: 15px;
                    background-color: #f9f9f9;
                    border-left: 4px solid #8b4513;
                    border-radius: 3px;
                }}
                .section-title {{
                    font-weight: bold;
                    color: #8b4513;
                    margin-bottom: 10px;
                    font-size: 16px;
                }}
                .reply-box {{
                    background-color: #fff;
                    border: 2px solid #4CAF50;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 5px;
                    white-space: pre-wrap;
                    font-family: 'Courier New', monospace;
                }}
                .instructions {{
                    background-color: #e3f2fd;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .metric {{
                    display: inline-block;
                    padding: 5px 12px;
                    margin: 5px 5px 5px 0;
                    background-color: #e0e0e0;
                    border-radius: 15px;
                    font-size: 14px;
                }}
                .links {{
                    margin-top: 15px;
                }}
                .links a {{
                    color: #1a73e8;
                    text-decoration: none;
                    margin-right: 20px;
                }}
                .links a:hover {{
                    text-decoration: underline;
                }}
                .important {{
                    color: #d32f2f;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📧 Reply Approval Needed - Conversation #{pending_reply_id}</h2>
                <p>Stage {conversation_stage + 1} Reply</p>
            </div>

            <div class="content">
                <!-- Lead Info -->
                <div class="section">
                    <div class="section-title">👤 LEAD INFORMATION</div>
                    <strong>Name:</strong> {lead_name}<br>
                    <strong>Pain Type:</strong> {pain_type}<br>
                    <div class="metric">Pain Intensity: {thread_data.get('Pain Intensity', 'N/A')}/10</div>
                    <div class="metric">Readiness: {readiness}%</div>
                    <div class="metric">Stage: {conversation_stage + 1}</div>
                </div>

                <!-- Their Message -->
                <div class="section">
                    <div class="section-title">💬 THEIR LAST MESSAGE</div>
                    <em>"{original_comment}"</em>
                </div>

                <!-- AI Generated Reply -->
                <div class="section">
                    <div class="section-title">🤖 AI SUGGESTED REPLY</div>
                    <div class="reply-box">{generated_reply}</div>
                    {f'<p><strong>📚 Resource Suggested:</strong> {suggested_resource}</p>' if suggested_resource and suggested_resource != 'None' else ''}
                </div>

                <!-- Approval Instructions -->
                <div class="instructions">
                    <div class="section-title">✏️ TO APPROVE/EDIT THIS REPLY:</div>
                    <p><strong>Reply to this email with ONE of these options:</strong></p>
                    <ol>
                        <li><strong>APPROVE</strong> - Post the reply exactly as shown above</li>
                        <li><strong>Type your EDITED version</strong> - Your text will replace the AI version</li>
                        <li><strong>REJECT</strong> - Skip this reply (won't be posted)</li>
                        <li><strong>WAIT</strong> - Remind me in 2 hours</li>
                    </ol>
                    <p class="important">⚠️ Simply reply to this email - do NOT forward or create new email thread!</p>
                </div>

                <!-- Context -->
                <div class="section">
                    <div class="section-title">📊 CONVERSATION CONTEXT</div>
                    <strong>Previous Exchanges:</strong> {conversation_stage}<br>
                    <strong>Resources Already Shared:</strong> {resources_shared if resources_shared else 'None'}<br><br>
                    <strong>Full Conversation History:</strong><br>
                    <div style="margin-top: 10px; padding: 10px; background: white; border-radius: 3px; font-size: 13px;">
                        {formatted_history}
                    </div>
                </div>

                <!-- Links -->
                <div class="links">
                    <a href="{comment_url}" target="_blank">💬 View YouTube Comment</a>
                    <a href="{video_url}" target="_blank">🎥 Watch Video</a>
                </div>

                <!-- Footer -->
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                    <p>Reply ID: {pending_reply_id}<br>
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                    Automated by Isha Lead Engagement System</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def parse_email_response(self, email_body: str) -> Dict:
        """
        Parse teacher's email response.

        Args:
            email_body: Raw email body text

        Returns:
            Dictionary with parsed action and content
        """
        # Clean email body (remove quoted text, signatures, etc.)
        cleaned_body = self._clean_email_body(email_body)

        # Check for action keywords
        upper_body = cleaned_body.upper()

        if 'APPROVE' in upper_body:
            return {
                'action': 'approve',
                'edited_reply': None
            }
        elif 'REJECT' in upper_body:
            return {
                'action': 'reject',
                'edited_reply': None
            }
        elif 'WAIT' in upper_body:
            return {
                'action': 'wait',
                'edited_reply': None
            }
        else:
            # Assume it's an edited reply
            return {
                'action': 'edit',
                'edited_reply': cleaned_body
            }

    def _clean_email_body(self, email_body: str) -> str:
        """Clean email body by removing quotes and signatures."""
        # Remove quoted text (lines starting with >)
        lines = email_body.split('\n')
        cleaned_lines = []

        for line in lines:
            # Skip quoted lines
            if line.strip().startswith('>'):
                continue
            # Skip common email signatures
            if any(sig in line.lower() for sig in ['sent from', 'get outlook', 'best regards', 'thanks,']):
                break
            cleaned_lines.append(line)

        cleaned = '\n'.join(cleaned_lines).strip()
        return cleaned

    def process_approval_response(self, reply_id: str, response_data: Dict) -> bool:
        """
        Process teacher's approval response and update Airtable.

        Args:
            reply_id: Pending reply record ID
            response_data: Parsed response data

        Returns:
            True if processed successfully
        """
        try:
            action = response_data['action']
            edited_reply = response_data.get('edited_reply')

            updates = {
                'Approved At': datetime.now().isoformat()
            }

            if action == 'approve':
                updates['Approval Status'] = 'approved'
                logger.info(f"Reply {reply_id} approved")

            elif action == 'edit':
                updates['Approval Status'] = 'approved'
                updates['AI Generated Reply'] = edited_reply  # Update with teacher's version
                updates['Your Notes'] = 'Edited by teacher'
                logger.info(f"Reply {reply_id} approved with edits")

            elif action == 'reject':
                updates['Approval Status'] = 'rejected'
                logger.info(f"Reply {reply_id} rejected")

            elif action == 'wait':
                updates['Your Notes'] = f'Wait requested at {datetime.now().strftime("%Y-%m-%d %H:%M")}'
                logger.info(f"Reply {reply_id} - wait requested")
                # Don't change status, will re-send later
                return True

            return self.database.update_pending_reply(reply_id, updates)

        except Exception as e:
            logger.error(f"Error processing approval response: {e}")
            return False

    def send_batch_approval_emails(self, reply_data_list: List[Dict]) -> int:
        """
        Send approval emails for multiple generated replies.

        Args:
            reply_data_list: List of generated reply data

        Returns:
            Number of emails sent successfully
        """
        sent_count = 0

        for reply_data in reply_data_list:
            # Create pending reply record in Airtable first
            thread_id = reply_data['thread_id']
            thread_data = reply_data['thread_data']
            teacher_record = reply_data['teacher_record']
            generated_reply = reply_data['reply_text']

            pending_reply = self.database.create_pending_reply(
                thread_id,
                thread_data,
                generated_reply,
                teacher_record['id']
            )

            if pending_reply:
                # Send approval email
                if self.send_approval_email(reply_data, pending_reply['id']):
                    sent_count += 1

        logger.info(f"Sent {sent_count}/{len(reply_data_list)} approval emails")
        return sent_count
