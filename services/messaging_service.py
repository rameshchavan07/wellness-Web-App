"""
DayScore - Messaging Service
Handles sending and receiving direct messages between users 
via Firebase Firestore.
"""

from datetime import datetime, timedelta, timezone
from config.firebase_config import get_firestore_client
from config.settings import AppConfig

class MessagingService:
    def __init__(self):
        self.db = get_firestore_client()

    def get_users_list(self, current_user_id: str) -> list:
        """Fetch all registered users to chat with, excluding the current user."""
        if not self.db:
            return self._demo_users_list(current_user_id)

        try:
            users_ref = self.db.collection("users").get()
            users = []
            for doc in users_ref:
                data = doc.to_dict()
                if data.get("user_id") != current_user_id:
                    users.append({
                        "user_id": data.get("user_id"),
                        "name": data.get("name", "Unknown User"),
                        "email": data.get("email", ""),
                        "profile_photo": data.get("profile_photo", "")
                    })
            return sorted(users, key=lambda x: x["name"])
        except Exception as e:
            print(f"Error fetching users: {e}")
            return self._demo_users_list(current_user_id)

    def send_message(self, sender_id: str, receiver_id: str, text: str) -> bool:
        """Save a new message strictly to a shared conversation document or messages collection."""
        if not self.db:
            return True # Pretend success for demo

        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # create a unique compound ID for the conversation room
            sorted_ids = sorted([sender_id, receiver_id])
            room_id = f"{sorted_ids[0]}_{sorted_ids[1]}"
            
            message_data = {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "text": text,
                "timestamp": timestamp,
                "read": False
            }
            
            self.db.collection("chats").document(room_id).collection("messages").add(message_data)
            
            # Update the latest activity metadata on the chat room
            self.db.collection("chats").document(room_id).set({
                "participants": [sender_id, receiver_id],
                "last_message": text,
                "last_active": timestamp
            }, merge=True)
            
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def get_conversation(self, user_1: str, user_2: str) -> list:
        """Fetch all messages between two users ordered by timestamp."""
        if not self.db:
            return self._demo_conversation(user_1, user_2)

        try:
            sorted_ids = sorted([user_1, user_2])
            room_id = f"{sorted_ids[0]}_{sorted_ids[1]}"
            
            msgs_ref = self.db.collection("chats").document(room_id).collection("messages")
            docs = msgs_ref.order_by("timestamp", direction="ASCENDING").get()
            
            messages = [doc.to_dict() for doc in docs]
            return messages
        except Exception as e:
            print(f"Error fetching conversation: {e}")
            return self._demo_conversation(user_1, user_2)

    # ── Demo Mode Fallbacks ────────────────────────────
    def _demo_users_list(self, current_user_id: str) -> list:
        return [
            {"user_id": "demo_alice", "name": "Alice Wellness", "email": "alice@dayscore.app"},
            {"user_id": "demo_bob", "name": "Bob Fitness", "email": "bob@dayscore.app"},
            {"user_id": "demo_coach", "name": "Coach Sarah", "email": "sarah@dayscore.app"},
        ]
        
    def _demo_conversation(self, u1: str, u2: str) -> list:
        return [
            {
                "sender_id": ("demo_alice" if u1.startswith("demo_google") or u1 == AppConfig.DEMO_USER_ID else u1),
                "text": "Hey! How is your step count looking today?",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "sender_id": ("demo_alice" if u1.startswith("demo_google") or u1 == AppConfig.DEMO_USER_ID else u1),
                "text": "I'm trying to hit 10k but only at 4k so far 🏃‍♀️",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=1.9)).isoformat()
            }
        ]
