"""
DayScore - Streak Service
Tracks daily usage streaks and sleep consistency streaks.
"""

from datetime import datetime, timedelta, timezone
import streamlit as st
from config.firebase_config import get_firestore_client


class StreakService:
    """Manages user streak tracking."""

    def __init__(self):
        self.db = get_firestore_client()

    def update_streak(self, user_id: str) -> int:
        """
        Update user's daily streak. Returns the current streak count.
        """
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            if self.db:
                user_ref = self.db.collection("users").document(user_id)
                user_doc = user_ref.get()

                if user_doc.exists:
                    data = user_doc.to_dict()
                    last_active = data.get("last_active_date", "")
                    streak = data.get("streak", 0)

                    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

                    if last_active == today:
                        return streak  # Already counted today
                    elif last_active == yesterday:
                        streak += 1  # Consecutive day
                    else:
                        streak = 1  # Streak broken, restart

                    user_ref.update({
                        "streak": streak,
                        "last_active_date": today,
                    })
                    return streak
                else:
                    # New user or demo user without Firestore doc
                    return self._demo_update_streak(today)
            else:
                # Demo mode
                return self._demo_update_streak(today)
        except Exception:
            return self._demo_update_streak(today)

    def get_streak(self, user_id: str) -> int:
        """Get current streak count for user."""
        try:
            if self.db:
                doc = self.db.collection("users").document(user_id).get()
                if doc.exists:
                    return doc.to_dict().get("streak", 0)
            return st.session_state.get("demo_streak", 1)
        except Exception:
            return st.session_state.get("demo_streak", 1)

    def get_sleep_streak(self, user_id: str) -> int:
        """Get current sleep streak count for user."""
        try:
            if self.db:
                doc = self.db.collection("users").document(user_id).get()
                if doc.exists:
                    return doc.to_dict().get("sleep_streak", 0)
            return st.session_state.get("demo_sleep_streak", 0)
        except Exception:
            return st.session_state.get("demo_sleep_streak", 0)

    def update_sleep_streak(self, user_id: str, sleep_hours: float) -> int:
        """
        Track sleep consistency streak (7-8 hours).
        Returns current sleep streak. Only updates once per day.
        """
        good_sleep = 7.0 <= sleep_hours <= 8.0
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            if self.db:
                user_ref = self.db.collection("users").document(user_id)
                user_doc = user_ref.get()

                if user_doc.exists:
                    data = user_doc.to_dict()
                    sleep_streak = data.get("sleep_streak", 0)
                    last_sleep_date = data.get("last_sleep_streak_date", "")

                    if last_sleep_date == today:
                        return sleep_streak  # Already counted today

                    if good_sleep:
                        sleep_streak += 1
                    else:
                        sleep_streak = 0

                    user_ref.update({
                        "sleep_streak": sleep_streak,
                        "last_sleep_streak_date": today,
                    })
                    return sleep_streak
                else:
                    return self._demo_sleep_streak(good_sleep)
            else:
                return self._demo_sleep_streak(good_sleep)
        except Exception:
            return self._demo_sleep_streak(good_sleep)

    # ── Demo helpers ───────────────────────────────────────────────

    @staticmethod
    def _demo_update_streak(today: str) -> int:
        last = st.session_state.get("demo_last_active", "")
        streak = st.session_state.get("demo_streak", 0)
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

        if last == today:
            return streak
        elif last == yesterday:
            streak += 1
        else:
            streak = 1

        st.session_state["demo_streak"] = streak
        st.session_state["demo_last_active"] = today
        return streak

    @staticmethod
    def _demo_sleep_streak(good_sleep: bool) -> int:
        streak = st.session_state.get("demo_sleep_streak", 0)
        if good_sleep:
            streak += 1
        else:
            streak = 0
        st.session_state["demo_sleep_streak"] = streak
        return streak
