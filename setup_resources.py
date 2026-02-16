"""Setup essential Isha resources in Supabase."""

from src.database import SupabaseDatabase
from src.utils import setup_logger

logger = setup_logger(__name__)


def setup_resources():
    """Add essential Isha resources to database."""

    db = SupabaseDatabase()

    if not db.is_available:
        logger.error("Supabase not available")
        return False

    # Essential Isha resources
    resources = [
        {
            'resource_name': 'Isha Kriya - Free Guided Meditation',
            'resource_link': 'https://www.ishafoundation.org/isha-kriya/',
            'description': 'A simple yet powerful 12-minute meditation created by Sadhguru. Perfect for beginners dealing with anxiety, stress, or seeking inner peace.',
            'when_to_share': 'Share with leads experiencing mental struggles, anxiety, stress, or spiritual seeking. Great for first-time practitioners. Readiness >= 60.',
            'resource_type': 'practice',
            'pain_types': ['spiritual', 'mental_pain', 'general'],
            'minimum_readiness_score': 60,
            'active': True,
            'times_shared': 0
        },
        {
            'resource_name': 'Sadhguru App - Practice Tracker',
            'resource_link': 'https://play.google.com/store/apps/details?id=org.ishafoundation.sadhguru',
            'description': 'Free Sadhguru app with guided practices, meditation timer, and practice tracking. Helps build consistency and discipline.',
            'when_to_share': 'Share with leads struggling with discipline, consistency, or irregular practice. Also for those who mentioned practicing Shambhavi, Shoonya, or other Isha practices.',
            'resource_type': 'app',
            'pain_types': ['discipline', 'practice_aligned', 'general'],
            'minimum_readiness_score': 50,
            'active': True,
            'times_shared': 0
        },
        {
            'resource_name': 'Inner Engineering Online - Free Introduction',
            'resource_link': 'https://www.innerengineering.com/',
            'description': 'Free introductory session of Inner Engineering. A comprehensive program for inner wellbeing taught by Sadhguru.',
            'when_to_share': 'Share with highly ready leads (75+) who are seriously seeking transformation. Those asking about programs or expressing strong spiritual yearning.',
            'resource_type': 'program',
            'pain_types': ['spiritual', 'mental_pain', 'general'],
            'minimum_readiness_score': 75,
            'active': True,
            'times_shared': 0
        },
        {
            'resource_name': 'Surya Kriya - Classical Hatha Yoga',
            'resource_link': 'https://www.ishahathayoga.com/programs/surya-kriya/',
            'description': 'A potent yogic practice of tremendous antiquity, designed as a holistic process for health, wellness, and complete wellbeing.',
            'when_to_share': 'Share with those interested in serious yoga practice, physical health, or those who have completed Inner Engineering.',
            'resource_type': 'program',
            'pain_types': ['physical_pain', 'discipline', 'practice_aligned'],
            'minimum_readiness_score': 70,
            'active': True,
            'times_shared': 0
        },
        {
            'resource_name': 'Hatha Yoga Programs - Angamardana & Yogasanas',
            'resource_link': 'https://www.ishahathayoga.com/',
            'description': 'Classical Hatha Yoga programs including Angamardana (fitness), Surya Shakti (strength), and Yogasanas (flexibility).',
            'when_to_share': 'Share with those seeking physical health, fitness, flexibility, or strength. Also for those interested in traditional yoga.',
            'resource_type': 'program',
            'pain_types': ['physical_pain', 'discipline', 'general'],
            'minimum_readiness_score': 65,
            'active': True,
            'times_shared': 0
        },
        {
            'resource_name': 'Free Wisdom & Talks from Sadhguru',
            'resource_link': 'https://www.youtube.com/@sadhguru',
            'description': 'Sadhguru\'s official YouTube channel with thousands of hours of wisdom, guidance, and insights on life, yoga, and spirituality.',
            'when_to_share': 'Share with anyone beginning their journey or seeking answers to life\'s deeper questions. Low barrier to entry.',
            'resource_type': 'video',
            'pain_types': ['general', 'spiritual', 'mental_pain'],
            'minimum_readiness_score': 30,
            'active': True,
            'times_shared': 0
        },
        {
            'resource_name': 'Isha Blog - Articles & Insights',
            'resource_link': 'https://isha.sadhguru.org/en/wisdom',
            'description': 'In-depth articles on yoga, meditation, health, wellbeing, and spirituality from the Isha Foundation.',
            'when_to_share': 'Share with intellectually curious individuals who prefer reading over videos.',
            'resource_type': 'article',
            'pain_types': ['general', 'spiritual'],
            'minimum_readiness_score': 40,
            'active': True,
            'times_shared': 0
        },
        {
            'resource_name': 'Free Online Meditation Session',
            'resource_link': 'https://www.ishafoundation.org/events/',
            'description': 'Regular free online meditation sessions and satsangs conducted by Isha volunteers.',
            'when_to_share': 'Share with those seeking community connection or guided group practice. Especially for those feeling isolated.',
            'resource_type': 'program',
            'pain_types': ['spiritual', 'mental_pain', 'general'],
            'minimum_readiness_score': 55,
            'active': True,
            'times_shared': 0
        }
    ]

    logger.info(f"Adding {len(resources)} essential Isha resources...")

    added_count = 0
    for resource in resources:
        try:
            # Check if resource already exists
            existing = db.client.table('resources')\
                .select('id')\
                .eq('resource_name', resource['resource_name'])\
                .execute()

            if existing.data:
                logger.info(f"✓ Resource '{resource['resource_name']}' already exists, skipping")
                continue

            # Add resource
            response = db.client.table('resources').insert(resource).execute()

            if response.data:
                added_count += 1
                logger.info(f"✓ Added: {resource['resource_name']}")
            else:
                logger.warning(f"Failed to add: {resource['resource_name']}")

        except Exception as e:
            logger.error(f"Error adding resource '{resource['resource_name']}': {e}")
            continue

    logger.info(f"\n✅ Setup complete: {added_count} resources added")
    logger.info(f"Total resources in database: {len(resources)}")

    return True


if __name__ == "__main__":
    import sys
    success = setup_resources()
    sys.exit(0 if success else 1)
