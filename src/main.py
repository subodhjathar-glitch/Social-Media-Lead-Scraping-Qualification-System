"""Main orchestrator for the lead scraping and qualification system."""

import sys
import traceback
from datetime import datetime

from src.config import settings
from src.scraper import YouTubeScraper
from src.qualifier import LeadQualifier
from src.database import AirtableDatabase
from src.notifier import EmailNotifier
from src.utils import setup_logger

logger = setup_logger(__name__)


def main():
    """Main workflow orchestration."""
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info(f"Starting lead scraping workflow at {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info("=" * 80)

    metrics = {
        'scraped': 0,
        'duplicates': 0,
        'unique': 0,
        'high_intent': 0,
        'medium_intent': 0,
        'low_intent': 0,
        'stored': 0,
        'errors': []
    }

    try:
        # Initialize components
        logger.info("Initializing components...")
        scraper = YouTubeScraper()
        qualifier = LeadQualifier()
        database = AirtableDatabase()
        notifier = EmailNotifier()

        # Phase 1: Scrape YouTube comments
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 1: Scraping YouTube Comments")
        logger.info("=" * 80)
        try:
            comments = scraper.scrape_all()
            metrics['scraped'] = len(comments)
            logger.info(f"✓ Scraped {metrics['scraped']} comments")
        except Exception as e:
            error_msg = f"Error during scraping: {e}\n{traceback.format_exc()}"
            logger.error(error_msg)
            metrics['errors'].append(error_msg)
            comments = []

        if not comments:
            logger.warning("No comments scraped. Exiting workflow.")
            return metrics

        # Phase 2: Filter duplicates
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2: Filtering Duplicates")
        logger.info("=" * 80)
        try:
            unique_comments, duplicate_comments = database.process_comments(comments)
            metrics['duplicates'] = len(duplicate_comments)
            metrics['unique'] = len(unique_comments)
            logger.info(f"✓ Unique: {metrics['unique']}, Duplicates: {metrics['duplicates']}")
        except Exception as e:
            error_msg = f"Error during duplicate detection: {e}\n{traceback.format_exc()}"
            logger.error(error_msg)
            metrics['errors'].append(error_msg)
            unique_comments = comments  # Continue with all comments on error

        if not unique_comments:
            logger.info("No unique comments to qualify. Exiting workflow.")
            return metrics

        # Phase 3: Qualify leads with AI
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 3: AI Lead Qualification")
        logger.info("=" * 80)
        try:
            qualified_leads = qualifier.qualify_batch(unique_comments)

            # Count by intent
            for lead in qualified_leads:
                intent = lead.get('intent', 'Low')
                if intent == 'High':
                    metrics['high_intent'] += 1
                elif intent == 'Medium':
                    metrics['medium_intent'] += 1
                else:
                    metrics['low_intent'] += 1

            logger.info(f"✓ Qualified {len(qualified_leads)} leads")
            logger.info(f"  High: {metrics['high_intent']}, Medium: {metrics['medium_intent']}, Low: {metrics['low_intent']}")
        except Exception as e:
            error_msg = f"Error during qualification: {e}\n{traceback.format_exc()}"
            logger.error(error_msg)
            metrics['errors'].append(error_msg)
            qualified_leads = []

        if not qualified_leads:
            logger.warning("No qualified leads to store. Exiting workflow.")
            return metrics

        # Phase 4: Store leads in Airtable
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 4: Storing Leads in Airtable")
        logger.info("=" * 80)
        try:
            created_records = database.batch_create_leads(qualified_leads)
            metrics['stored'] = len(created_records)
            logger.info(f"✓ Stored {metrics['stored']} leads in Airtable")
        except Exception as e:
            error_msg = f"Error storing leads: {e}\n{traceback.format_exc()}"
            logger.error(error_msg)
            metrics['errors'].append(error_msg)
            created_records = []

        # Phase 5: Send email digest
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 5: Sending Email Digest")
        logger.info("=" * 80)
        try:
            # Get recent leads (last 24 hours)
            recent_leads = database.get_recent_leads(hours=24)

            if recent_leads:
                success = notifier.send_digest(recent_leads, settings.email_recipients)
                if success:
                    logger.info(f"✓ Email digest sent to {len(settings.email_recipients)} recipients")
                else:
                    logger.warning("Failed to send email digest")
            else:
                logger.info("No recent leads to include in digest")
        except Exception as e:
            error_msg = f"Error sending email: {e}\n{traceback.format_exc()}"
            logger.error(error_msg)
            metrics['errors'].append(error_msg)

        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Scraped: {metrics['scraped']}")
        logger.info(f"Duplicates: {metrics['duplicates']}")
        logger.info(f"Unique: {metrics['unique']}")
        logger.info(f"High Intent: {metrics['high_intent']}")
        logger.info(f"Medium Intent: {metrics['medium_intent']}")
        logger.info(f"Low Intent: {metrics['low_intent']}")
        logger.info(f"Stored: {metrics['stored']}")

        if metrics['errors']:
            logger.warning(f"Errors encountered: {len(metrics['errors'])}")
            for i, error in enumerate(metrics['errors'], 1):
                logger.warning(f"Error {i}: {error}")

        return metrics

    except Exception as e:
        # Critical error - send notification
        error_msg = f"Critical error in main workflow: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        metrics['errors'].append(error_msg)

        try:
            notifier = EmailNotifier()
            notifier.send_error_notification(error_msg, settings.email_recipients)
        except:
            logger.error("Failed to send error notification email")

        return metrics


if __name__ == "__main__":
    try:
        metrics = main()

        # Exit with error code if critical failures occurred
        if metrics.get('stored', 0) == 0 and metrics.get('scraped', 0) > 0:
            logger.error("Workflow failed to store any leads despite scraping comments")
            sys.exit(1)

        sys.exit(0)

    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
