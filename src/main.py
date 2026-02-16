"""Main orchestrator for the lead scraping and qualification system."""

import sys
import traceback
from datetime import datetime

from src.config import settings
from src.scraper import YouTubeScraper
from src.qualifier import LeadQualifier
from src.database import AirtableDatabase
from src.notifier import EmailNotifier
from src.prefilter import CommentPreFilter
from src.keywords import KeywordDetector
from src.conversation import ConversationTracker
from src.reply_generator import ReplyGenerator
from src.utils import setup_logger, detect_language

logger = setup_logger(__name__)


def main():
    """Main workflow orchestration."""
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info(f"Starting lead scraping workflow at {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info("=" * 80)

    metrics = {
        'scraped': 0,
        'skipped_by_language': 0,
        'skipped_by_prefilter': 0,
        'passed_prefilter': 0,
        'duplicates': 0,
        'unique': 0,
        'high_intent': 0,
        'medium_intent': 0,
        'low_intent': 0,
        'spiritual': 0,
        'mental_pain': 0,
        'discipline': 0,
        'physical_pain': 0,
        'practice_aligned': 0,
        'stored': 0,
        'threads_created': 0,
        'replies_generated': 0,
        'pending_approvals': 0,
        'errors': []
    }

    try:
        # Initialize components
        logger.info("Initializing components...")
        scraper = YouTubeScraper()
        prefilter = CommentPreFilter()
        keyword_detector = KeywordDetector()
        qualifier = LeadQualifier()
        database = AirtableDatabase()
        notifier = EmailNotifier()

        # Check database status
        if database.is_available:
            logger.info("✓ Supabase: Online and ready")
        else:
            logger.warning("⚠ Supabase: Offline - leads will be saved locally to data/ folder")

        # Phase 1: Scrape YouTube comments
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 1: Scraping YouTube Comments")
        logger.info("=" * 80)
        try:
            comments = scraper.scrape_all_v2()  # Use new hardcoded channel method
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

        # Phase 1.5: Language filtering
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 1.5: Language Filtering")
        logger.info("=" * 80)
        try:
            language_filtered = []
            for comment in comments:
                lang = detect_language(comment.get('text', ''))
                comment['language'] = lang

                if lang in ['en', 'hi', 'mr']:
                    language_filtered.append(comment)
                else:
                    metrics['skipped_by_language'] += 1

            logger.info(f"✓ Language filter: {len(language_filtered)}/{len(comments)} passed")
            logger.info(f"  Skipped {metrics['skipped_by_language']} non-English/Hindi/Marathi comments")
            comments = language_filtered
        except Exception as e:
            error_msg = f"Error during language filtering: {e}\n{traceback.format_exc()}"
            logger.error(error_msg)
            metrics['errors'].append(error_msg)
            # Continue with all comments on error

        if not comments:
            logger.warning("No comments passed language filter. Exiting workflow.")
            return metrics

        # Phase 1.6: Pre-filtering (reduce AI costs)
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 1.6: Pre-Filtering Low-Quality Comments")
        logger.info("=" * 80)
        try:
            filtered_comments, prefilter_stats = prefilter.filter_batch(comments)
            metrics['skipped_by_prefilter'] = prefilter_stats['total'] - prefilter_stats['passed']
            metrics['passed_prefilter'] = prefilter_stats['passed']

            cost_reduction = (metrics['skipped_by_prefilter'] / prefilter_stats['total'] * 100) if prefilter_stats['total'] > 0 else 0
            logger.info(f"✓ Pre-filter: {metrics['passed_prefilter']}/{prefilter_stats['total']} passed ({cost_reduction:.1f}% cost reduction)")

            comments = filtered_comments
        except Exception as e:
            error_msg = f"Error during pre-filtering: {e}\n{traceback.format_exc()}"
            logger.error(error_msg)
            metrics['errors'].append(error_msg)
            # Continue with all comments on error

        if not comments:
            logger.info("No comments passed pre-filter. Exiting workflow.")
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

        # Phase 2.5: Keyword detection
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2.5: Keyword Detection")
        logger.info("=" * 80)
        try:
            unique_comments = keyword_detector.detect_batch(unique_comments)
            logger.info(f"✓ Keyword detection complete for {len(unique_comments)} comments")
        except Exception as e:
            error_msg = f"Error during keyword detection: {e}\n{traceback.format_exc()}"
            logger.error(error_msg)
            metrics['errors'].append(error_msg)
            # Continue without keyword detection on error

        # Phase 3: Qualify leads with AI
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 3: AI Lead Qualification")
        logger.info("=" * 80)
        try:
            qualified_leads = qualifier.qualify_batch(unique_comments)

            # Count by intent (legacy and new)
            for lead in qualified_leads:
                intent = lead.get('intent', 'Low')
                if intent == 'High':
                    metrics['high_intent'] += 1
                elif intent == 'Medium':
                    metrics['medium_intent'] += 1
                else:
                    metrics['low_intent'] += 1

                # Count by new intent_type
                intent_type = lead.get('intent_type', 'low_intent')
                if intent_type == 'spiritual':
                    metrics['spiritual'] += 1
                elif intent_type == 'mental_pain':
                    metrics['mental_pain'] += 1
                elif intent_type == 'discipline':
                    metrics['discipline'] += 1
                elif intent_type == 'physical_pain':
                    metrics['physical_pain'] += 1
                elif intent_type == 'practice_aligned':
                    metrics['practice_aligned'] += 1

            logger.info(f"✓ Qualified {len(qualified_leads)} leads")
            logger.info(f"  Legacy: High={metrics['high_intent']}, Medium={metrics['medium_intent']}, Low={metrics['low_intent']}")
            logger.info(f"  By type: Spiritual={metrics['spiritual']}, Mental={metrics['mental_pain']}, "
                       f"Discipline={metrics['discipline']}, Physical={metrics['physical_pain']}, "
                       f"Practice-aligned={metrics['practice_aligned']}")
        except Exception as e:
            error_msg = f"Error during qualification: {e}\n{traceback.format_exc()}"
            logger.error(error_msg)
            metrics['errors'].append(error_msg)
            qualified_leads = []

        if not qualified_leads:
            logger.warning("No qualified leads to store. Exiting workflow.")
            return metrics

        # Phase 4: Store leads in Supabase
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 4: Storing Leads in Supabase")
        logger.info("=" * 80)
        try:
            created_records = database.batch_create_leads(qualified_leads)
            metrics['stored'] = len(created_records)
            logger.info(f"✓ Stored {metrics['stored']} leads in Supabase")
        except Exception as e:
            error_msg = f"Error storing leads: {e}\n{traceback.format_exc()}"
            logger.error(error_msg)
            metrics['errors'].append(error_msg)
            created_records = []

        if not created_records:
            logger.warning("No leads were stored. Skipping conversation thread creation.")
        else:
            # Phase 5: Create conversation threads for qualified leads
            logger.info("\n" + "=" * 80)
            logger.info("PHASE 5: Creating Conversation Threads")
            logger.info("=" * 80)
            try:
                conversation_tracker = ConversationTracker(database)
                threads_created = []

                for record in created_records:
                    # Check if this lead should get a conversation thread
                    lead_data = {
                        'readiness_score': record.get('readiness_score', 0),
                        'intent_type': record.get('intent_type', 'low_intent'),
                        'pain_intensity': record.get('pain_intensity', 0)
                    }

                    if conversation_tracker.should_create_thread(lead_data):
                        # Create thread
                        thread = database.create_conversation_thread(record['id'], record)
                        if thread:
                            threads_created.append(thread)
                            logger.info(f"Created thread for {record.get('name', 'Unknown')} "
                                      f"(readiness: {record.get('readiness_score', 0)})")

                metrics['threads_created'] = len(threads_created)
                logger.info(f"✓ Created {metrics['threads_created']} conversation threads")

                # Phase 6: Generate AI replies for threads
                if threads_created:
                    logger.info("\n" + "=" * 80)
                    logger.info("PHASE 6: Generating AI Replies")
                    logger.info("=" * 80)
                    try:
                        # Get active teachers
                        teachers = database.get_active_teachers()

                        if not teachers:
                            logger.warning("No active teachers found. Skipping reply generation.")
                            logger.warning("Add teacher profiles via the dashboard to enable reply generation.")
                        else:
                            logger.info(f"Found {len(teachers)} active teacher(s)")

                            reply_generator = ReplyGenerator(database)
                            replies_generated = []

                            # Generate reply for each thread
                            for i, thread in enumerate(threads_created):
                                try:
                                    # Assign teacher (round-robin)
                                    teacher = teachers[i % len(teachers)]

                                    # Build conversation context
                                    context = {
                                        'lead_name': thread.get('comment_author', 'Unknown'),
                                        'conversation_stage': 0,  # First reply
                                        'pain_type': thread.get('pain_type', 'unknown'),
                                        'readiness_score': thread.get('readiness_score', 0),
                                        'resources_shared': [],
                                        'full_history': thread.get('full_history', '')
                                    }

                                    # Generate reply
                                    reply_data = reply_generator.generate_reply(context, {
                                        'Teacher Name': teacher.get('teacher_name', 'Teacher'),
                                        'Role': teacher.get('role', 'Isha Volunteer'),
                                        'Practice Experience': teacher.get('practice_experience', ''),
                                        'Tone Preference': teacher.get('tone_preference', 'Compassionate'),
                                        'Sign Off': teacher.get('sign_off', 'Blessings')
                                    })

                                    # Store in pending_replies
                                    pending_reply = database.create_pending_reply(
                                        thread['id'],
                                        thread,
                                        reply_data['reply_text'],
                                        teacher['id']
                                    )

                                    if pending_reply:
                                        replies_generated.append(pending_reply)
                                        logger.info(f"Generated reply for {context['lead_name']} "
                                                  f"(assigned to {teacher.get('teacher_name', 'Unknown')})")

                                except Exception as e:
                                    logger.error(f"Error generating reply for thread {thread['id']}: {e}")
                                    continue

                            metrics['replies_generated'] = len(replies_generated)
                            metrics['pending_approvals'] = len(replies_generated)
                            logger.info(f"✓ Generated {metrics['replies_generated']} AI replies")
                            logger.info(f"✓ {metrics['pending_approvals']} replies awaiting teacher approval")

                    except Exception as e:
                        error_msg = f"Error during reply generation: {e}\n{traceback.format_exc()}"
                        logger.error(error_msg)
                        metrics['errors'].append(error_msg)

            except Exception as e:
                error_msg = f"Error creating conversation threads: {e}\n{traceback.format_exc()}"
                logger.error(error_msg)
                metrics['errors'].append(error_msg)

        # Phase 7: Send email digest
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 7: Sending Email Digest")
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
        logger.info(f"Language Filtered: {metrics['skipped_by_language']}")
        logger.info(f"Pre-Filter Skipped: {metrics['skipped_by_prefilter']} ({metrics['skipped_by_prefilter']/(metrics['scraped'] or 1)*100:.1f}% cost reduction)")
        logger.info(f"Passed Pre-Filter: {metrics['passed_prefilter']}")
        logger.info(f"Duplicates: {metrics['duplicates']}")
        logger.info(f"Unique: {metrics['unique']}")
        logger.info(f"High Intent: {metrics['high_intent']}, Medium: {metrics['medium_intent']}, Low: {metrics['low_intent']}")
        logger.info(f"By Type: Spiritual={metrics['spiritual']}, Mental={metrics['mental_pain']}, "
                   f"Discipline={metrics['discipline']}, Physical={metrics['physical_pain']}, Practice={metrics['practice_aligned']}")
        logger.info(f"Stored: {metrics['stored']}")
        logger.info(f"Conversation Threads Created: {metrics['threads_created']}")
        logger.info(f"AI Replies Generated: {metrics['replies_generated']}")
        logger.info(f"Pending Teacher Approval: {metrics['pending_approvals']}")

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
