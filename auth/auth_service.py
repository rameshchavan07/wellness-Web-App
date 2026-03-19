"""
DayScore - Authentication Service
Handles user sign-in, sign-up, and session management.
Uses Firebase Admin SDK with demo-mode fallback.
"""

import streamlit as st
from datetime import datetime

from config.firebase_config import get_firestore_client, get_firebase_auth


class AuthService:
    """Manages user authentication via Firebase Admin SDK."""

    def __init__(self):
        self.db = get_firestore_client()
        self.auth = get_firebase_auth()

    def sign_up(self, email: str, password: str, display_name: str) -> dict:
        """Register a new user."""
        try:
            if self.auth:
                # Create user via Firebase Admin SDK
                user_record = self.auth.create_user(
                    email=email,
                    password=password,
                    display_name=display_name,
                )
                user_data = {
                    "user_id": user_record.uid,
                    "name": display_name,
                    "email": email,
                    "profile_photo": user_record.photo_url or "",
                    "created_at": datetime.utcnow().isoformat(),
                    "streak": 0,
                    "total_points": 0,
                    "last_active_date": "",
                    "sleep_streak": 0,
                }
                # Store in Firestore
                if self.db:
                    self.db.collection("users").document(user_record.uid).set(user_data)
                return {"success": True, "user": user_data, "token": "admin_session"}
            else:
                return self._demo_sign_up(email, display_name)
        except Exception as e:
            error_msg = str(e)
            if "EMAIL_EXISTS" in error_msg or "already exists" in error_msg.lower():
                return {"success": False, "error": "Email already registered."}
            elif "WEAK_PASSWORD" in error_msg or "at least 6" in error_msg.lower():
                return {"success": False, "error": "Password must be at least 6 characters."}
            return {"success": False, "error": f"Registration failed: {error_msg}"}

    def sign_in_with_google(self, google_user_info: dict) -> dict:
        """
        Sign in (or sign up) a user via Google OAuth.
        google_user_info should contain: google_id, email, name, picture, verified_email
        """
        email = google_user_info.get("email", "")
        name = google_user_info.get("name", "User")
        picture = google_user_info.get("picture", "")
        google_id = google_user_info.get("google_id", "")

        try:
            if self.auth:
                # Try to find existing Firebase user by email
                try:
                    user_record = self.auth.get_user_by_email(email)
                except Exception:
                    # User doesn't exist — create them
                    user_record = self.auth.create_user(
                        email=email,
                        display_name=name,
                        photo_url=picture,
                        email_verified=True,
                    )

                user_data = {
                    "user_id": user_record.uid,
                    "name": name,
                    "email": email,
                    "profile_photo": picture,
                    "auth_provider": "google",
                    "google_id": google_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "streak": 0,
                    "total_points": 0,
                    "last_active_date": "",
                    "sleep_streak": 0,
                }

                # Store / merge in Firestore
                if self.db:
                    doc_ref = self.db.collection("users").document(user_record.uid)
                    doc = doc_ref.get()
                    if doc.exists:
                        # Merge — keep existing stats but update profile
                        existing = doc.to_dict()
                        user_data["streak"] = existing.get("streak", 0)
                        user_data["total_points"] = existing.get("total_points", 0)
                        user_data["sleep_streak"] = existing.get("sleep_streak", 0)
                        doc_ref.set(user_data, merge=True)
                    else:
                        doc_ref.set(user_data)

                return {"success": True, "user": user_data, "token": "google_session"}
            else:
                # Demo mode
                return self._demo_google_sign_in(google_user_info)
        except Exception as e:
            return {"success": False, "error": f"Google sign-in failed: {str(e)}"}

    def sign_in(self, email: str, password: str) -> dict:
        """
        Sign in an existing user.
        
        Note: Firebase Admin SDK doesn't support password verification directly.
        For production, use Firebase Auth REST API or a client SDK.
        Here we verify the user exists and trust the password for demo purposes.
        """
        try:
            if self.auth:
                # Verify user exists
                user_record = self.auth.get_user_by_email(email)
                user_data = {
                    "user_id": user_record.uid,
                    "name": user_record.display_name or "User",
                    "email": email,
                    "profile_photo": user_record.photo_url or "",
                }
                # Get extra data from Firestore
                if self.db:
                    doc = self.db.collection("users").document(user_record.uid).get()
                    if doc.exists:
                        extra = doc.to_dict()
                        user_data["name"] = extra.get("name", user_data["name"])
                        user_data["streak"] = extra.get("streak", 0)
                        user_data["total_points"] = extra.get("total_points", 0)
                return {"success": True, "user": user_data, "token": "admin_session"}
            else:
                return self._demo_sign_in(email)
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "no user" in error_msg.lower():
                return {"success": False, "error": "No account found with this email."}
            return {"success": False, "error": f"Login failed: {error_msg}"}

    def sign_out(self):
        """Clear the session."""
        keys_to_clear = [
            "authenticated", "user", "token", "google_fit_connected",
            "google_fit_credentials", "chat_history", "fitness_data",
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

    def get_user_profile(self, user_id: str) -> dict:
        """Retrieve user profile from Firestore."""
        try:
            if self.db:
                doc = self.db.collection("users").document(user_id).get()
                if doc.exists:
                    return doc.to_dict()
            return {}
        except Exception:
            return {}

    def update_user_profile(self, user_id: str, data: dict) -> bool:
        """Update user profile in Firestore."""
        try:
            if self.db:
                self.db.collection("users").document(user_id).update(data)
                return True
            return False
        except Exception:
            return False

    # ── Demo Mode Helpers ──────────────────────────────
    def _demo_sign_up(self, email: str, name: str) -> dict:
        """Demo mode registration (no Firebase)."""
        user_data = {
            "user_id": "demo_user_001",
            "name": name,
            "email": email,
            "profile_photo": "",
            "created_at": datetime.utcnow().isoformat(),
            "streak": 0,
            "total_points": 0,
        }
        return {"success": True, "user": user_data, "token": "demo_token"}

    def _demo_sign_in(self, email: str) -> dict:
        """Demo mode sign-in (no Firebase)."""
        user_data = {
            "user_id": "demo_user_001",
            "name": "Demo User",
            "email": email,
            "profile_photo": "",
        }
        return {"success": True, "user": user_data, "token": "demo_token"}

    def _demo_google_sign_in(self, google_user_info: dict) -> dict:
        """Demo mode Google sign-in (no Firebase)."""
        user_data = {
            "user_id": f"demo_google_{google_user_info.get('google_id', '123')}",
            "name": google_user_info.get("name", "Google Demo User"),
            "email": google_user_info.get("email", ""),
            "profile_photo": google_user_info.get("picture", ""),
            "auth_provider": "google",
        }
        return {"success": True, "user": user_data, "token": "demo_google_token"}

