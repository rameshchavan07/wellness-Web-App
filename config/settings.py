"""
DayScore - Configuration Settings
Central configuration module for all app settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    """Application-wide configuration."""
    APP_NAME = os.getenv("APP_NAME", "DayScore")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"


class FirebaseConfig:
    """Firebase connection configuration."""
    API_KEY = os.getenv("FIREBASE_API_KEY", "")
    AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN", "")
    PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
    STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "")
    MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID", "")
    APP_ID = os.getenv("FIREBASE_APP_ID", "")
    DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "")
    SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "config/serviceAccountKey.json")

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
    CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")
    SCOPES = [
        "https://www.googleapis.com/auth/fitness.activity.read",
        "https://www.googleapis.com/auth/fitness.body.read",
        "https://www.googleapis.com/auth/fitness.sleep.read",
        "https://www.googleapis.com/auth/fitness.heart_rate.read",
    ]


class OpenAIConfig:
    """OpenAI API configuration."""
    API_KEY = os.getenv("OPENAI_API_KEY", "")
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
