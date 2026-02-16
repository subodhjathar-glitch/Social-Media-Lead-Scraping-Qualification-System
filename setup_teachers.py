"""Setup initial teacher profiles in Supabase."""

from src.database import SupabaseDatabase
from src.utils import setup_logger

logger = setup_logger(__name__)


def setup_teachers():
    """Add sample teacher profiles to database."""

    db = SupabaseDatabase()

    if not db.is_available:
        logger.error("Supabase not available")
        return False

    # Sample teacher profiles - details can be updated later via UI
    teachers = [
        {
            'teacher_name': 'Yogavani Team',
            'email': 'yogavani.hathayoga@gmail.com',
            'contact_number': '',
            'role': 'Isha Hatha Yoga Teacher',
            'practice_experience': 'Experienced Isha Hatha Yoga practitioner and teacher',
            'tone_preference': 'Compassionate',
            'sign_off': 'Blessings,\nYogavani Team',
            'daily_reply_limit': 20,
            'active': True
        },
        {
            'teacher_name': 'Subodh',
            'email': 'subodh.jathar@gmail.com',
            'contact_number': '',
            'role': 'Isha Volunteer',
            'practice_experience': 'Dedicated practitioner',
            'tone_preference': 'Compassionate',
            'sign_off': 'Blessings,\nSubodh',
            'daily_reply_limit': 15,
            'active': True
        },
        {
            'teacher_name': 'Durgesh',
            'email': 'durgesh.lokhande@gmail.com',
            'contact_number': '',
            'role': 'Isha Volunteer',
            'practice_experience': 'Passionate about sharing practices',
            'tone_preference': 'Casual',
            'sign_off': 'Blessings,\nDurgesh',
            'daily_reply_limit': 15,
            'active': True
        }
    ]

    logger.info(f"Adding {len(teachers)} teacher profiles...")

    added_count = 0
    for teacher in teachers:
        try:
            # Check if teacher already exists
            existing = db.client.table('teacher_profiles')\
                .select('id')\
                .eq('email', teacher['email'])\
                .execute()

            if existing.data:
                logger.info(f"✓ Teacher {teacher['teacher_name']} already exists, skipping")
                continue

            # Add teacher
            response = db.client.table('teacher_profiles').insert(teacher).execute()

            if response.data:
                added_count += 1
                logger.info(f"✓ Added teacher: {teacher['teacher_name']} ({teacher['email']})")
            else:
                logger.warning(f"Failed to add teacher: {teacher['teacher_name']}")

        except Exception as e:
            logger.error(f"Error adding teacher {teacher['teacher_name']}: {e}")
            continue

    logger.info(f"\n✅ Setup complete: {added_count} teachers added")
    logger.info(f"Teachers can update their profiles via the dashboard later")

    return True


if __name__ == "__main__":
    import sys
    success = setup_teachers()
    sys.exit(0 if success else 1)
