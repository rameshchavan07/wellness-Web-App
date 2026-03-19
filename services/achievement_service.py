"""
DayScore - Achievement Service
Tracks and awards user achievements / badges.
"""

from datetime import datetime
import streamlit as st
from config.firebase_config import get_firestore_client


# Achievement definitions
ACHIEVEMENTS = {
    "first_steps_10k": {
        "id": "first_steps_10k",
        "name": "Marathon Walker",
        "description": "Walk 10,000 steps in a single day",
        "icon": "🏃",
        "category": "steps",
        "condition": lambda data: data.get("steps", 0) >= 10000,
    },
    "streak_7": {
        "id": "streak_7",
        "name": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "icon": "🔥",
        "category": "streak",
        "condition": lambda data: data.get("streak", 0) >= 7,
    },
    "high_score_80": {
        "id": "high_score_80",
        "name": "High Achiever",
        "description": "Score 80+ on your DayScore",
        "icon": "⭐",
        "category": "score",
        "condition": lambda data: data.get("total_score", 0) >= 80,
    },
    "high_score_90": {
        "id": "high_score_90",
        "name": "Health Master",
        "description": "Score 90+ on your DayScore",
        "icon": "🌟",
        "category": "score",
        "condition": lambda data: data.get("total_score", 0) >= 90,
    },
    "sleep_consistency": {
        "id": "sleep_consistency",
        "name": "Sleep Champion",
        "description": "Get 7-8 hours of sleep for 5 consecutive days",
        "icon": "😴",
        "category": "sleep",
        "condition": lambda data: data.get("sleep_streak", 0) >= 5,
    },
    "streak_30": {
        "id": "streak_30",
        "name": "Monthly Maestro",
        "description": "Maintain a 30-day streak",
        "icon": "🏆",
        "category": "streak",
        "condition": lambda data: data.get("streak", 0) >= 30,
    },
    "calorie_king": {
        "id": "calorie_king",
        "name": "Calorie King",
        "description": "Burn 2500+ calories in a day",
        "icon": "👑",
        "category": "calories",
        "condition": lambda data: data.get("calories", 0) >= 2500,
    },
    "first_login": {
        "id": "first_login",
        "name": "Welcome Aboard",
        "description": "Log in for the first time",
        "icon": "🎉",
        "category": "general",
        "condition": lambda data: True,  # Unlocked on first login
    },
    "steps_20k": {
        "id": "steps_20k",
        "name": "Ultra Walker",
        "description": "Walk 20,000 steps in a single day",
        "icon": "🦶",
        "category": "steps",
        "condition": lambda data: data.get("steps", 0) >= 20000,
    },
    "perfect_score": {
        "id": "perfect_score",
        "name": "Perfect Day",
        "description": "Achieve a perfect 100 DayScore",
        "icon": "💯",
        "category": "score",
        "condition": lambda data: data.get("total_score", 0) >= 100,
    },
}


class AchievementService:
    """Manages user achievements."""

    def __init__(self):
        self.db = get_firestore_client()
        self.achievements = ACHIEVEMENTS

    def check_achievements(self, user_id: str, data: dict) -> list:
        """
        Check and unlock any new achievements based on current data.

        Args:
            user_id: Firebase user ID
            data: dict containing metrics + score info

        Returns:
            list of newly unlocked achievement dicts
        """
        unlocked = self.get_user_achievements(user_id)
        unlocked_ids = {a["id"] for a in unlocked}
        newly_unlocked = []

        for ach_id, ach in self.achievements.items():
            if ach_id not in unlocked_ids:
                try:
                    if ach["condition"](data):
                        self._unlock_achievement(user_id, ach)
                        newly_unlocked.append(ach)
                except Exception:
                    continue

        return newly_unlocked

    def get_user_achievements(self, user_id: str) -> list:
        """Get all unlocked achievements for a user."""
        try:
            if self.db:
                docs = (
                    self.db.collection("achievements")
                    .where("user_id", "==", user_id)
                    .stream()
                )
                return [doc.to_dict() for doc in docs]
            # Demo mode
            return st.session_state.get("demo_achievements", [])
        except Exception:
            return st.session_state.get("demo_achievements", [])

    def _unlock_achievement(self, user_id: str, achievement: dict):
        """Save an unlocked achievement to Firestore."""
        record = {
            "user_id": user_id,
            "id": achievement["id"],
            "name": achievement["name"],
            "description": achievement["description"],
            "icon": achievement["icon"],
            "category": achievement["category"],
            "unlocked_at": datetime.utcnow().isoformat(),
        }
        try:
            if self.db:
                doc_id = f"{user_id}_{achievement['id']}"
                self.db.collection("achievements").document(doc_id).set(record)
            else:
                # Demo mode
                if "demo_achievements" not in st.session_state:
                    st.session_state["demo_achievements"] = []
                st.session_state["demo_achievements"].append(record)
        except Exception as e:
            st.warning(f"Could not save achievement: {e}")

    def get_all_achievements(self) -> dict:
        """Return full achievement catalog."""
        return {
            k: {
                "id": v["id"],
                "name": v["name"],
                "description": v["description"],
                "icon": v["icon"],
                "category": v["category"],
            }
            for k, v in self.achievements.items()
        }
