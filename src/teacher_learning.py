"""Teacher learning system - adapts AI responses based on teacher edits."""

from typing import Dict, List
from collections import Counter
from datetime import datetime
from src.utils import setup_logger

logger = setup_logger(__name__)


class TeacherLearner:
    """Analyzes teacher edits and builds style profiles."""

    def __init__(self, database):
        self.db = database

    def analyze_edits(self, teacher_id: str, min_edits: int = 10) -> Dict:
        """
        Analyze all edits for a teacher and extract patterns.

        Args:
            teacher_id: Teacher's UUID
            min_edits: Minimum edits needed for analysis

        Returns:
            Style profile dictionary
        """
        if not self.db.is_available or not self.db.client:
            return {}

        try:
            edits = self.db.client.table('teacher_edits')\
                .select('*')\
                .eq('teacher_id', teacher_id)\
                .order('edit_timestamp', desc=True)\
                .execute()

            if not edits.data or len(edits.data) < min_edits:
                logger.info(f"Not enough edits for analysis: {len(edits.data) if edits.data else 0}/{min_edits}")
                return {}

            logger.info(f"Analyzing {len(edits.data)} edits for teacher {teacher_id}")

            style_profile = {
                'total_edits': len(edits.data),
                'avg_length_change': 0,
                'common_additions': [],
                'common_removals': [],
                'tone_preferences': {},
                'structural_patterns': {},
                'signature_phrases': []
            }

            length_changes = []
            all_additions = []
            all_removals = []

            for edit in edits.data:
                original = edit['original_ai_text']
                edited = edit['edited_text']

                length_change = len(edited) - len(original)
                length_changes.append(length_change)

                # Simple diff analysis
                original_words = set(original.lower().split())
                edited_words = set(edited.lower().split())

                added = edited_words - original_words
                removed = original_words - edited_words

                all_additions.extend(list(added))
                all_removals.extend(list(removed))

            # Calculate patterns
            style_profile['avg_length_change'] = sum(length_changes) / len(length_changes)

            # Most common additions (teacher's preferred phrases)
            common_additions = Counter(all_additions).most_common(20)
            style_profile['common_additions'] = [word for word, count in common_additions if count >= 3]

            common_removals = Counter(all_removals).most_common(20)
            style_profile['common_removals'] = [word for word, count in common_removals if count >= 3]

            # Detect tone preferences
            if style_profile['avg_length_change'] > 50:
                style_profile['tone_preferences']['verbosity'] = 'more_detailed'
            elif style_profile['avg_length_change'] < -50:
                style_profile['tone_preferences']['verbosity'] = 'more_concise'
            else:
                style_profile['tone_preferences']['verbosity'] = 'balanced'

            logger.info(f"Style profile generated: {style_profile['tone_preferences']}")
            return style_profile

        except Exception as e:
            logger.error(f"Error analyzing teacher edits: {e}")
            return {}

    def update_teacher_profile(self, teacher_id: str):
        """Analyze edits and update teacher's learned style profile."""
        if not self.db.is_available or not self.db.client:
            return

        try:
            style_profile = self.analyze_edits(teacher_id)

            if not style_profile:
                logger.info("No style profile generated - not enough data")
                return

            self.db.client.table('teacher_profiles').update({
                'learned_style': style_profile,
                'common_phrases': style_profile.get('common_additions', []),
                'editing_patterns': style_profile.get('tone_preferences', {}),
                'last_learning_update': datetime.now().isoformat()
            }).eq('id', teacher_id).execute()

            logger.info(f"Updated teacher profile with learned style")

        except Exception as e:
            logger.error(f"Error updating teacher profile: {e}")
