"""
DayScore - Authentication Service
Handles user sign-in, sign-up, and session management.
Uses Firebase Admin SDK with demo-mode fallback.
"""

import streamlit as st
from datetime import datetime, timezone

from config.firebase_config import get_firestore_client, get_firebase_auth
from utils.session_manager import SessionManager



class AuthService:
    """Manages user authentication via Firebase Admin SDK."""

    def __init__(self):
        self.db = get_firestore_client()
        self.auth = get_firebase_auth()

    def _check_rate_limit(self, action: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
        """Basic rate limiting using session state."""
        try:
            key = f"rate_limit_{action}"
            if key not in st.session_state:
                st.session_state[key] = {"attempts": 0, "first_attempt": datetime.now()}
                
            rate_info = st.session_state[key]
            now = datetime.now()
            
            # Reset if window has passed
            if (now - rate_info["first_attempt"]).total_seconds() > window_minutes * 60:
                st.session_state[key] = {"attempts": 1, "first_attempt": now}
                return True
                
            # Check attempts
            if rate_info["attempts"] >= max_attempts:
                return False
                
            # Increment
            rate_info["attempts"] += 1
            st.session_state[key] = rate_info
            return True
        except Exception:
            return True  # Fail open if session state not available

    def sign_up(self, email: str, password: str, display_name: str, is_counselor: bool = False, specialty: str = "", clinic: str = "") -> dict:
        """Register a new user."""
        import re
        
        if not self._check_rate_limit("signup"):
            return {"success": False, "error": "Too many attempts. Please try again later."}
            
        # Input validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"success": False, "error": "Invalid email format."}
        if len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters."}
        if len(display_name.strip()) < 2:
            return {"success": False, "error": "Name must be at least 2 characters."}
            
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
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "streak": 0,
                    "total_points": 0,
                    "last_active_date": "",
                    "sleep_streak": 0,
                    "role": "counselor" if is_counselor else "patient",
                }
                if is_counselor:
                    user_data["counselor_id"] = user_record.uid
                # Store in Firestore
                if self.db:
                    self.db.collection("users").document(user_record.uid).set(user_data)
                    
                    if is_counselor:
                        counselor_profile = {
                            "id": user_record.uid,
                            "name": display_name,
                            "specialty": specialty,
                            "clinic": clinic,
                            "email": email,
                            "profile_photo": user_record.photo_url or "",
                            "tags": [specialty.strip()] if specialty else [],
                            "rating": 5.0,
                            "reviews": 0
                        }
                        self.db.collection("counselors").document(user_record.uid).set(counselor_profile)
                
                # Reset rate limit on success
                if "rate_limit_signup" in st.session_state:
                    del st.session_state["rate_limit_signup"]
                    
                return {"success": True, "user": user_data, "token": "admin_session"}
            else:
                return self._demo_sign_up(email, display_name, is_counselor, specialty, clinic)
        except Exception as e:
            error_msg = str(e)
            if "EMAIL_EXISTS" in error_msg or "already exists" in error_msg.lower():
                return {"success": False, "error": "Email already registered."}
            elif any(k in error_msg for k in ("ConnectionPool", "RemoteDisconnected", "ProtocolError", "Max retries", "Connection aborted", "HTTPSConnectionPool")):
                return {"success": False, "error": "⚠️ Cannot reach Firebase — check your internet connection and ensure Google APIs are not blocked by a firewall or proxy."}
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
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "streak": 0,
                    "total_points": 0,
                    "last_active_date": "",
                    "sleep_streak": 0,
                    "role": "patient",
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
                        user_data["last_active_date"] = existing.get("last_active_date", "")
                        user_data["created_at"] = existing.get("created_at", user_data["created_at"])
                        if "google_fit_credentials" in existing:
                            user_data["google_fit_credentials"] = existing["google_fit_credentials"]
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
        Sign in an existing user securely using the Firebase REST API.
        """
        import requests
        from config.settings import FirebaseConfig
        
        if not self._check_rate_limit("login"):
            return {"success": False, "error": "Too many attempts. Please try again later."}
        
        try:
            if self.auth:
                # Need API_KEY to verify password via REST API
                if not FirebaseConfig.API_KEY:
                    return {"success": False, "error": "Server misconfiguration. Missing API Key."}
                
                # Verify password via REST API
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FirebaseConfig.API_KEY}"
                payload = {"email": email, "password": password, "returnSecureToken": True}
                res = requests.post(url, json=payload)
                
                if res.status_code != 200:
                    error_msg = res.json().get("error", {}).get("message", "Login failed")
                    if error_msg in ["EMAIL_NOT_FOUND", "INVALID_PASSWORD", "INVALID_LOGIN_CREDENTIALS"]:
                        return {"success": False, "error": "Invalid email or password."}
                    return {"success": False, "error": f"Login failed: {error_msg}"}
                
                auth_data = res.json()
                uid = auth_data["localId"]
                
                # Get user record
                user_record = self.auth.get_user(uid)
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
                        if "google_fit_credentials" in extra:
                            user_data["google_fit_credentials"] = extra["google_fit_credentials"]
                        if "role" in extra:
                            user_data["role"] = extra["role"]
                        if "counselor_id" in extra:
                            user_data["counselor_id"] = extra["counselor_id"]
                
                # Check for counselor role (legacy predefined counselors)
                from services.counselor_service import CounselorService
                counselor = CounselorService().get_counselor_by_email(email)
                if counselor:
                    user_data["role"] = "counselor"
                    user_data["counselor_id"] = counselor["id"]
                
                # Ensure counselor_id is set for any user with counselor role
                if user_data.get("role") == "counselor" and "counselor_id" not in user_data:
                    user_data["counselor_id"] = user_record.uid

                # Reset rate limit on success
                if "rate_limit_login" in st.session_state:
                    del st.session_state["rate_limit_login"]

                return {"success": True, "user": user_data, "token": auth_data.get("idToken", "admin_session")}
            else:
                return self._demo_sign_in(email)
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "no user" in error_msg.lower():
                return {"success": False, "error": "No account found with this email."}
            return {"success": False, "error": f"Login failed: {error_msg}"}

    def sign_out(self):
        """Clear the session using SessionManager."""
        SessionManager().clear()

    def get_user_profile(self, user_id: str) -> dict:
        """Retrieve user profile from Firestore."""
        try:
            if self.db:
                doc = self.db.collection("users").document(user_id).get()
                if doc.exists:
                    return doc.to_dict()
            return {}
        except Exception as e:
            st.warning(f"Could not retrieve user profile: {e}")
            return {}

    def update_user_profile(self, user_id: str, data: dict) -> bool:
        """Update user profile in Firestore."""
        try:
            if self.db:
                self.db.collection("users").document(user_id).update(data)
                return True
            return False
        except Exception as e:
            st.warning(f"Could not update user profile: {e}")
            return False

    # ── Demo Mode Helpers ──────────────────────────────
    def _demo_sign_up(self, email: str, name: str, is_counselor: bool = False, specialty: str = "", clinic: str = "") -> dict:
        """Demo mode registration (no Firebase)."""
        from config.settings import AppConfig
        user_data = {
            "user_id": AppConfig.DEMO_USER_ID,
            "name": name,
            "email": email,
            "profile_photo": "",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "streak": 0,
            "total_points": 0,
            "role": "counselor" if is_counselor else "patient"
        }
        if is_counselor:
            user_data["counselor_id"] = user_data["user_id"]
            user_data["specialty"] = specialty
            user_data["clinic"] = clinic
        return {"success": True, "user": user_data, "token": "demo_token"}

    def _demo_sign_in(self, email: str) -> dict:
        """Demo mode sign-in (no Firebase)."""
        from config.settings import AppConfig
        user_data = {
            "user_id": AppConfig.DEMO_USER_ID,
            "name": "Demo User",
            "email": email,
            "profile_photo": "",
        }

        # Check for counselor role
        from services.counselor_service import CounselorService
        counselor = CounselorService().get_counselor_by_email(email)
        if counselor:
            user_data["name"] = counselor["name"]
            user_data["role"] = "counselor"
            user_data["counselor_id"] = counselor["id"]
            user_data["user_id"] = counselor["id"] # Use counselor ID for demo bookings

        return {"success": True, "user": user_data, "token": "demo_token"}

    def _demo_google_sign_in(self, google_user_info: dict) -> dict:
        """Demo mode Google sign-in (no Firebase)."""
        user_data = {
            "user_id": f"demo_google_{google_user_info.get('google_id', '123')}",
            "name": google_user_info.get("name", "Google Demo User"),
            "email": google_user_info.get("email", ""),
            "profile_photo": google_user_info.get("picture", ""),
            "auth_provider": "google",
            "role": "patient",
        }
        return {"success": True, "user": user_data, "token": "demo_google_token"}

