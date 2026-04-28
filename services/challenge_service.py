"""
DayScore - Challenge Service
Manages community challenges and leaderboard.
"""

from datetime import datetime, timezone
import streamlit as st
from config.firebase_config import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter
from config.settings import AppConfig


class ChallengeService:
    """Handles community challenges and leaderboards."""

    def __init__(self):
        self.db = get_firestore_client()

    def create_challenge(self, creator_id: str, challenge_data: dict) -> str:
        """
        Create a new community challenge.

        Args:
            creator_id: User ID of the creator
            challenge_data: dict with name, description, goal, duration_days

        Returns:
            Challenge document ID
        """
        challenge = {
            "creator_id": creator_id,
            "name": challenge_data.get("name", ""),
            "description": challenge_data.get("description", ""),
            "goal": challenge_data.get("goal", ""),
            "goal_value": challenge_data.get("goal_value", 10000),
            "metric": challenge_data.get("metric", "steps"),  # steps, calories, score
            "duration_days": challenge_data.get("duration_days", 7),
            "participants": [creator_id],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
        }
        try:
            if self.db:
                doc_ref = self.db.collection("challenges").add(challenge)
                return doc_ref[1].id
            else:
                # Demo mode
                import random
                cid = f"demo_challenge_{random.randint(1000, 9999)}"
                if "demo_challenges" not in st.session_state:
                    st.session_state["demo_challenges"] = []
                challenge["id"] = cid
                st.session_state["demo_challenges"].append(challenge)
                return cid
        except Exception as e:
            st.error(f"Failed to create challenge: {e}")
            return ""

    def join_challenge(self, challenge_id: str, user_id: str) -> bool:
        """Join an existing challenge."""
        try:
            if self.db:
                from google.cloud.firestore_v1 import ArrayUnion
                self.db.collection("challenges").document(challenge_id).update({
                    "participants": ArrayUnion([user_id])
                })
                return True
            else:
                # Demo mode
                for ch in st.session_state.get("demo_challenges", []):
                    if ch.get("id") == challenge_id:
                        if user_id not in ch["participants"]:
                            ch["participants"].append(user_id)
                        return True
                return False
        except Exception as e:
            st.error(f"Failed to join challenge: {e}")
            return False

    def get_active_challenges(self) -> list:
        """Get all active challenges."""
        try:
            if self.db:
                docs = (
                    self.db.collection("challenges")
                    .where(filter=FieldFilter("status", "==", "active"))
                    .stream()
                )
                challenges = []
                for doc in docs:
                    data = doc.to_dict()
                    data["id"] = doc.id
                    challenges.append(data)
                return challenges
            else:
                return st.session_state.get("demo_challenges", self._get_demo_challenges())
        except Exception:
            return self._get_demo_challenges()

    def get_leaderboard(self, challenge_id: str = None) -> list:
        """Get leaderboard entries, optionally filtered by challenge."""
        try:
            if self.db:
                query = self.db.collection("leaderboard")
                if challenge_id:
                    query = query.where(filter=FieldFilter("challenge_id", "==", challenge_id))
                query = query.order_by("score", direction="DESCENDING").limit(20)
                return [doc.to_dict() for doc in query.stream()]
            else:
                return self._get_demo_leaderboard()
        except Exception:
            return self._get_demo_leaderboard()

    def update_leaderboard(self, user_id: str, user_name: str, score: float, challenge_id: str = None):
        """Update or create a leaderboard entry."""
        entry = {
            "user_id": user_id,
            "user_name": user_name,
            "score": score,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if challenge_id:
            entry["challenge_id"] = challenge_id

        try:
            if self.db:
                doc_id = f"{user_id}_{challenge_id}" if challenge_id else user_id
                self.db.collection("leaderboard").document(doc_id).set(entry, merge=True)
        except Exception:
            pass

    # ── Demo Data ──────────────────────────────────────────────────

    @staticmethod
    def _get_demo_challenges() -> list:
        return [
            {
                "id": "demo_ch_1",
                "name": "🚶 10K Steps Challenge",
                "description": "Walk 10,000 steps every day for a week!",
                "goal": "Walk 10,000 steps daily",
                "goal_value": 10000,
                "metric": "steps",
                "duration_days": 7,
                "participants": [AppConfig.DEMO_USER_ID, "user_alice", "user_bob"],
                "status": "active",
            },
            {
                "id": "demo_ch_2",
                "name": "😴 Sleep Well Week",
                "description": "Get 7-8 hours of sleep for 7 days straight.",
                "goal": "Sleep 7-8 hours nightly",
                "goal_value": 7,
                "metric": "sleep",
                "duration_days": 7,
                "participants": [AppConfig.DEMO_USER_ID, "user_carol"],
                "status": "active",
            },
            {
                "id": "demo_ch_3",
                "name": "🔥 Calorie Burn Fest",
                "description": "Burn 2000+ calories every day for 5 days.",
                "goal": "Burn 2000 cal/day",
                "goal_value": 2000,
                "metric": "calories",
                "duration_days": 5,
                "participants": ["user_alice", "user_bob", "user_dave", "user_eve"],
                "status": "active",
            },
        ]

    @staticmethod
    def _get_demo_leaderboard() -> list:
        return [
            {"user_id": "user_alice", "user_name": "Alice M.", "score": 92.5, "rank": 1},
            {"user_id": AppConfig.DEMO_USER_ID, "user_name": "You", "score": 85.0, "rank": 2},
            {"user_id": "user_bob", "user_name": "Bob K.", "score": 78.3, "rank": 3},
            {"user_id": "user_carol", "user_name": "Carol S.", "score": 74.1, "rank": 4},
            {"user_id": "user_dave", "user_name": "Dave R.", "score": 71.8, "rank": 5},
            {"user_id": "user_eve", "user_name": "Eve L.", "score": 65.2, "rank": 6},
        ]
