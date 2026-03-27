"""
DayScore - Configuration Settings
Central configuration module for all app settings.
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)


def get_secret(key: str, default: str = "") -> str:
    """Retrieve secret from env var, then st.secrets (root), then st.secrets['firebase']."""
    val = os.getenv(key)
    if val:
        return val
    try:
        if key in st.secrets:
            return st.secrets[key]
        if "firebase" in st.secrets and key in st.secrets["firebase"]:
            return st.secrets["firebase"][key]
    except Exception:
        pass
    return default


class AppConfig:
    """Application-wide configuration."""
    APP_NAME = get_secret("APP_NAME", "DayScore")
    APP_VERSION = get_secret("APP_VERSION", "1.0.0")
    DEBUG = get_secret("DEBUG", "False").lower() == "true"
    DEMO_USER_ID = "demo_user_001"


class FirebaseConfig:
    """Firebase connection configuration."""
    API_KEY = get_secret("FIREBASE_API_KEY", "")
    AUTH_DOMAIN = get_secret("FIREBASE_AUTH_DOMAIN", "")
    PROJECT_ID = get_secret("FIREBASE_PROJECT_ID", "")
    STORAGE_BUCKET = get_secret("FIREBASE_STORAGE_BUCKET", "")
    MESSAGING_SENDER_ID = get_secret("FIREBASE_MESSAGING_SENDER_ID", "")
    APP_ID = get_secret("FIREBASE_APP_ID", "")
    DATABASE_URL = get_secret("FIREBASE_DATABASE_URL", "")
    SERVICE_ACCOUNT_PATH = get_secret("FIREBASE_SERVICE_ACCOUNT_PATH", "config/serviceAccountKey.json")

    @classmethod
    def to_pyrebase_config(cls):
        return {
            "apiKey": cls.API_KEY,
            "authDomain": cls.AUTH_DOMAIN,
            "projectId": cls.PROJECT_ID,
            "storageBucket": cls.STORAGE_BUCKET,
            "messagingSenderId": cls.MESSAGING_SENDER_ID,
            "appId": cls.APP_ID,
            "databaseURL": cls.DATABASE_URL,
        }


class GoogleFitConfig:
    """Google Fit API configuration."""
    CLIENT_ID = get_secret("GOOGLE_CLIENT_ID", "")
    CLIENT_SECRET = get_secret("GOOGLE_CLIENT_SECRET", "")
    REDIRECT_URI = get_secret("GOOGLE_REDIRECT_URI", "https://wellness-web-app-rutu.streamlit.app")
    SCOPES = [
        "https://www.googleapis.com/auth/fitness.activity.read",
        "https://www.googleapis.com/auth/fitness.body.read",
        "https://www.googleapis.com/auth/fitness.sleep.read",
        "https://www.googleapis.com/auth/fitness.heart_rate.read",
    ]


class OpenAIConfig:
    """OpenAI API configuration."""
    API_KEY = get_secret("OPENAI_API_KEY", "")
    MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 500
    TEMPERATURE = 0.7


class ScoringConfig:
    """DayScore calculation weights and ideals."""
    WEIGHTS = {
        "steps": 0.30,
        "sleep": 0.30,
        "calories": 0.20,
        "heart_rate": 0.20,
    }
    IDEALS = {
        "steps": 10000,
        "sleep_min": 7.0,   # hours
        "sleep_max": 8.0,   # hours
        "calories": 2000,
        "heart_rate_min": 60,
        "heart_rate_max": 100,
    }


class SMTPConfig:
    """SMTP Email configuration."""
    SERVER = get_secret("SMTP_SERVER", "smtp.gmail.com")
    PORT = int(get_secret("SMTP_PORT", "587"))
    USERNAME = get_secret("SMTP_USERNAME", "")
    PASSWORD = get_secret("SMTP_PASSWORD", "")
    FROM_EMAIL = get_secret("SMTP_FROM_EMAIL", USERNAME)
