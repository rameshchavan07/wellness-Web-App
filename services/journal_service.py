"""
DayScore - Journal Service
Manages mood journal entries with Firestore persistence and demo mode fallback.
"""

import streamlit as st
from datetime import datetime, timezone, timedelta
from config.firebase_config import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter


# Mood scale: emoji → numeric value for charting
MOOD_SCALE = {
    "🤩": {"label": "Amazing", "value": 5, "color": "#4ECDC4"},
    "😊": {"label": "Good", "value": 4, "color": "#6C63FF"},
    "😐": {"label": "Okay", "value": 3, "color": "#FFD93D"},
    "😞": {"label": "Low", "value": 2, "color": "#FF8C42"},
    "😢": {"label": "Awful", "value": 1, "color": "#FF6B6B"},
}

# Pre-defined emotion tags
EMOTION_TAGS = [
    "😊 Happy", "😌 Calm", "💪 Motivated", "🙏 Grateful",
    "😰 Anxious", "😔 Sad", "😤 Frustrated", "😴 Tired",
    "🤔 Thoughtful", "🥰 Loved", "😬 Stressed", "🎉 Excited",
]


class JournalService:
    """Manages mood journal entries in Firestore with demo fallback."""

    def __init__(self):
        self.db = get_firestore_client()

    def save_entry(self, user_id: str, mood_emoji: str, journal_text: str,
                   gratitude_items: list, tags: list) -> dict:
        """
        Save a journal entry for today.

        Args:
            user_id: Firebase user ID
            mood_emoji: The selected mood emoji (e.g. "😊")
            journal_text: Free-text reflection
            gratitude_items: List of up to 3 gratitude strings
            tags: List of selected emotion tags

        Returns:
            dict with success status
        """
        today = datetime.now().strftime("%Y-%m-%d")
        mood_info = MOOD_SCALE.get(mood_emoji, {"label": "Unknown", "value": 3})

        entry = {
            "user_id": user_id,
            "date": today,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mood_emoji": mood_emoji,
            "mood_label": mood_info["label"],
            "mood_value": mood_info["value"],
            "journal_text": journal_text,
            "gratitude": [g for g in gratitude_items if g.strip()],
            "tags": tags,
        }

        try:
            if self.db:
                doc_id = f"{user_id}_{today}"
                self.db.collection("journal_entries").document(doc_id).set(entry)
                return {"success": True, "entry": entry}
            else:
                return self._demo_save_entry(entry)
        except Exception as e:
            st.warning(f"Could not save journal entry: {e}")
            return self._demo_save_entry(entry)

    def get_entries(self, user_id: str, days: int = 30) -> list:
        """Fetch recent journal entries for a user."""
        try:
            if self.db:
                cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                docs = (
                    self.db.collection("journal_entries")
                    .where(filter=FieldFilter("user_id", "==", user_id))
                    .where(filter=FieldFilter("date", ">=", cutoff))
                    .order_by("date", direction="DESCENDING")
                    .get()
                )
                entries = [doc.to_dict() for doc in docs]
                return entries if entries else self._get_demo_entries(days)
            else:
                return self._get_demo_entries(days)
        except Exception:
            return self._get_demo_entries(days)

    def get_entry_for_today(self, user_id: str) -> dict:
        """Get today's journal entry if it exists."""
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            if self.db:
                doc_id = f"{user_id}_{today}"
                doc = self.db.collection("journal_entries").document(doc_id).get()
                if doc.exists:
                    return doc.to_dict()
            # Check demo storage
            for entry in st.session_state.get("demo_journal_entries", []):
                if entry.get("date") == today:
                    return entry
            return {}
        except Exception:
            return {}

    def get_mood_stats(self, user_id: str, days: int = 30) -> dict:
        """
        Calculate mood statistics from journal entries.

        Returns:
            dict with mood_distribution, average_mood, mood_trend, correlations
        """
        entries = self.get_entries(user_id, days)

        if not entries:
            return {"has_data": False}

        # Mood distribution
        distribution = {}
        for emoji, info in MOOD_SCALE.items():
            count = sum(1 for e in entries if e.get("mood_emoji") == emoji)
            distribution[emoji] = {
                "label": info["label"],
                "count": count,
                "color": info["color"],
            }

        # Average mood value
        mood_values = [e.get("mood_value", 3) for e in entries]
        avg_mood = sum(mood_values) / len(mood_values) if mood_values else 3.0

        # Mood trend (last 7 vs previous 7)
        if len(entries) >= 7:
            recent = [e.get("mood_value", 3) for e in entries[:7]]
            earlier = [e.get("mood_value", 3) for e in entries[7:14]] if len(entries) >= 14 else recent
            recent_avg = sum(recent) / len(recent)
            earlier_avg = sum(earlier) / len(earlier)
            if recent_avg > earlier_avg + 0.3:
                trend = "improving"
            elif recent_avg < earlier_avg - 0.3:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        # Tag frequency
        tag_counts = {}
        for entry in entries:
            for tag in entry.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return {
            "has_data": True,
            "distribution": distribution,
            "average_mood": round(avg_mood, 1),
            "trend": trend,
            "total_entries": len(entries),
            "tag_counts": tag_counts,
            "entries": entries,
        }

    def get_journal_streak(self, user_id: str) -> int:
        """Calculate the consecutive journaling streak."""
        entries = self.get_entries(user_id, days=60)
        if not entries:
            return 0

        dates = sorted(set(e.get("date", "") for e in entries), reverse=True)
        streak = 0
        today = datetime.now().strftime("%Y-%m-%d")

        for i, date_str in enumerate(dates):
            expected = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if date_str == expected:
                streak += 1
            else:
                break

        return streak

    # ── Demo Mode Helpers ──────────────────────────────

    @staticmethod
    def _demo_save_entry(entry: dict) -> dict:
        """Save entry to session state for demo mode."""
        if "demo_journal_entries" not in st.session_state:
            st.session_state["demo_journal_entries"] = []

        # Replace existing entry for today if it exists
        existing = st.session_state["demo_journal_entries"]
        st.session_state["demo_journal_entries"] = [
            e for e in existing if e.get("date") != entry.get("date")
        ]
        st.session_state["demo_journal_entries"].insert(0, entry)
        return {"success": True, "entry": entry}

    @staticmethod
    def _get_demo_entries(days: int = 30) -> list:
        """Generate or retrieve demo journal entries."""
        # Return saved demo entries if they exist
        saved = st.session_state.get("demo_journal_entries", [])
        if saved:
            return saved

        # Generate realistic demo data
        import random
        moods = list(MOOD_SCALE.keys())
        mood_weights = [0.15, 0.35, 0.25, 0.15, 0.10]  # Weighted toward positive
        sample_gratitude = [
            "Had a great workout today",
            "Enjoyed coffee with friends",
            "Beautiful weather outside",
            "Got a good night's sleep",
            "Finished a challenging task",
            "Spent time with family",
            "Learned something new",
            "Ate a healthy homemade meal",
            "Took a relaxing walk in the park",
            "Read an interesting book chapter",
        ]
        sample_reflections = [
            "Today was productive. I managed to complete most of my tasks and still had time to exercise.",
            "Feeling a bit tired but overall positive. Need to prioritize sleep tonight.",
            "Great day! Hit my step goal and had meaningful conversations.",
            "Struggled with focus today. Maybe I need to reduce screen time before bed.",
            "Mixed feelings — work was stressful but evening walk helped clear my mind.",
            "Felt really energized today. Morning meditation made a big difference.",
            "A quiet, peaceful day. Sometimes you need those.",
        ]

        entries = []
        for i in range(min(days, 14)):
            dt = datetime.now() - timedelta(days=i)
            mood = random.choices(moods, weights=mood_weights, k=1)[0]
            mood_info = MOOD_SCALE[mood]

            entries.append({
                "user_id": "demo_user_001",
                "date": dt.strftime("%Y-%m-%d"),
                "timestamp": dt.isoformat(),
                "mood_emoji": mood,
                "mood_label": mood_info["label"],
                "mood_value": mood_info["value"],
                "journal_text": random.choice(sample_reflections),
                "gratitude": random.sample(sample_gratitude, k=random.randint(1, 3)),
                "tags": random.sample(EMOTION_TAGS[:8], k=random.randint(1, 3)),
            })

        st.session_state["demo_journal_entries"] = entries
        return entries
