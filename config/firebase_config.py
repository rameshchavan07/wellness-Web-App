"""
DayScore - Firebase Configuration
Initializes Firebase Admin SDK for server-side operations.
"""

import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth

from config.settings import FirebaseConfig

# Track initialization state to avoid repeated warnings
_firebase_init_attempted = False
_firebase_available = False


def initialize_firebase():
    """Initialize Firebase Admin SDK (singleton). Returns True if available."""
    global _firebase_init_attempted, _firebase_available

    if firebase_admin._apps:
        _firebase_available = True
        return firebase_admin.get_app()

    if _firebase_init_attempted:
        return None if not _firebase_available else firebase_admin.get_app()

    _firebase_init_attempted = True

    # Try st.secrets first (for Streamlit Community Cloud)
    try:
        if "firebase" in st.secrets:
            secrets_dict = dict(st.secrets["firebase"])
            # Ensure private key is correctly formatted if it came from environment/toml
            if "private_key" in secrets_dict:
                secrets_dict["private_key"] = secrets_dict["private_key"].replace("\\n", "\n")
            
            cred = credentials.Certificate(secrets_dict)
            firebase_admin.initialize_app(cred)
            _firebase_available = True
            return firebase_admin.get_app()
    except Exception as e:
        print(f"st.secrets['firebase'] parsing failed: {e}")

    # Fallback to local service account file
    service_account_path = FirebaseConfig.SERVICE_ACCOUNT_PATH
    if os.path.exists(service_account_path):
        try:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            _firebase_available = True
            return firebase_admin.get_app()
        except Exception:
            _firebase_available = False
            return None
    else:
        _firebase_available = False
        return None


def is_firebase_available() -> bool:
    """Check if Firebase is configured and available."""
    global _firebase_init_attempted
    if not _firebase_init_attempted:
        initialize_firebase()
    return _firebase_available


@st.cache_resource
def get_firestore_client():
    """Get Firestore database client."""
    try:
        app = initialize_firebase()
        if app:
            return firestore.client()
        return None
    except Exception:
        return None


@st.cache_resource
def get_firebase_auth():
    """Get Firebase Auth instance."""
    try:
        app = initialize_firebase()
        if app:
            return firebase_auth
        return None
    except Exception:
        return None
