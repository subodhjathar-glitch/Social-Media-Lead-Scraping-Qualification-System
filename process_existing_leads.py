"""Process existing leads to create threads and generate replies."""

from src.database import SupabaseDatabase
from src.conversation import ConversationTracker
from src.reply_generator import ReplyGenerator
from src.utils import setup_logger

logger = setup_logger(__name__)


def process_existing_leads():
    """Process existing leads and generate replies."""

    db = SupabaseDatabase()

    if not db.is_available:
        logger.error("Supabase not available")
        return False

    logger.info("=" * 80)
    logger.info("PROCESSING EXISTING LEADS")
    logger.info("=" * 80)

    # Get all leads that don't have conversation threads yet
    try:
        # Get all leads
        all_leads = db.client.table('leads').select('*').execute()

        logger.info(f"\nFound {len(all_leads.data)} total leads in database")

        # Get existing thread lead IDs
        existing_threads = db.client.table('conversation_threads').select('lead_id').execute()
        existing_lead_ids = {thread['lead_id'] for thread in existing_threads.data}

        logger.info(f"Already have {len(existing_lead_ids)} threads")

        # Filter leads that need threads
        leads_needing_threads = [
            lead for lead in all_leads.data
            if lead['id'] not in existing_lead_ids
        ]

        logger.info(f"Processing {len(leads_needing_threads)} leads...\n")

        conversation_tracker = ConversationTracker(db)
        threads_created = []

        # Create threads for qualified leads
        for lead in leads_needing_threads:
            lead_data = {
                'readiness_score': lead.get('readiness_score', 0),
                'intent_type': lead.get('intent_type', 'low_intent'),
                'pain_intensity': lead.get('pain_intensity', 0)
            }

            if conversation_tracker.should_create_thread(lead_data):
                thread = db.create_conversation_thread(lead['id'], lead)
                if thread:
                    threads_created.append(thread)
                    logger.info(f"✓ Created thread for {lead.get('name', 'Unknown')} "
                              f"(readiness: {lead.get('readiness_score', 0)}, "
                              f"type: {lead.get('intent_type', 'unknown')})")

        logger.info(f"\n✅ Created {len(threads_created)} conversation threads")

        # Generate replies if we have threads
        if not threads_created:
            logger.info("No threads created. All done!")
            return True

        # Get active teachers
        teachers = db.get_active_teachers()

        if not teachers:
            logger.warning("\n⚠ No active teachers found!")
            logger.warning("Threads created but cannot generate replies without teachers.")
            return False

        logger.info(f"\nFound {len(teachers)} active teacher(s)")
        logger.info("Generating AI replies...\n")

        reply_generator = ReplyGenerator(db)
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
                pending_reply = db.create_pending_reply(
                    thread['id'],
                    thread,
                    reply_data['reply_text'],
                    teacher['id']
                )

                if pending_reply:
                    replies_generated.append(pending_reply)
                    logger.info(f"✓ Generated reply for {context['lead_name']} "
                              f"(assigned to {teacher.get('teacher_name', 'Unknown')})")

            except Exception as e:
                logger.error(f"Error generating reply for thread {thread['id']}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue

        logger.info(f"\n" + "=" * 80)
        logger.info(f"✅ PROCESSING COMPLETE")
        logger.info(f"=" * 80)
        logger.info(f"Threads created: {len(threads_created)}")
        logger.info(f"Replies generated: {len(replies_generated)}")
        logger.info(f"Pending approval: {len(replies_generated)}")
        logger.info(f"\n👉 Open the dashboard to review and approve replies!")

        return True

    except Exception as e:
        logger.error(f"Error processing leads: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    import sys
    success = process_existing_leads()
    sys.exit(0 if success else 1)
