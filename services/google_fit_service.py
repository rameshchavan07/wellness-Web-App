"""
DayScore - Google Fit Service
Connects to Google Fit API to fetch fitness data, caches results, and syncs to Firestore.
"""

import streamlit as st
from datetime import datetime, timedelta
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from concurrent.futures import ThreadPoolExecutor

from config.settings import GoogleFitConfig
from config.firebase_config import get_firestore_client
from services.scoring_service import ScoringService


@st.cache_data(ttl=300, show_spinner=False)
def _cached_fetch_daily_stats(token: str, refresh_token: str, client_id: str, client_secret: str, target_timestamp: float) -> dict:
    """Cached static method to fetch Google Fit data to bypass unhashable dicts/classes."""
    creds = Credentials(
        token=token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )
    service = build("fitness", "v1", credentials=creds)
    target_date = datetime.fromtimestamp(target_timestamp)
    
    start = datetime(target_date.year, target_date.month, target_date.day)
    end = start + timedelta(days=1)
    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)

    # Scopes/Buckets
    def _get_int(dataTypeName, dataSourceId=None):
        try:
            agg = {"dataTypeName": dataTypeName}
            if dataSourceId:
                agg["dataSourceId"] = dataSourceId
            body = {
                "aggregateBy": [agg],
                "bucketByTime": {"durationMillis": 86400000},
                "startTimeMillis": start_ms,
                "endTimeMillis": end_ms,
            }
            resp = service.users().dataset().aggregate(userId="me", body=body).execute()
            total = 0
            for bucket in resp.get("bucket", []):
                for ds in bucket.get("dataset", []):
                    for point in ds.get("point", []):
                        for val in point.get("value", []):
                            total += val.get("intVal", 0)
            return total
        except Exception as e:
            print(f"Error fetching {dataTypeName}: {e}")
        return 0

    def _get_float(dataTypeName, dataSourceId=None):
        try:
            agg = {"dataTypeName": dataTypeName}
            if dataSourceId:
                agg["dataSourceId"] = dataSourceId
            body = {
                "aggregateBy": [agg],
                "bucketByTime": {"durationMillis": 86400000},
                "startTimeMillis": start_ms,
                "endTimeMillis": end_ms,
            }
            resp = service.users().dataset().aggregate(userId="me", body=body).execute()
            total = 0.0
            for bucket in resp.get("bucket", []):
                for ds in bucket.get("dataset", []):
                    for point in ds.get("point", []):
                        for val in point.get("value", []):
                            total += val.get("fpVal", 0.0)
            return int(round(total))
        except Exception as e:
            print(f"Error fetching {dataTypeName}: {e}")
        return 0

    def _get_sleep():
        try:
            body = {
                "aggregateBy": [{"dataTypeName": "com.google.sleep.segment"}],
                "bucketByTime": {"durationMillis": 86400000},
                "startTimeMillis": start_ms,
                "endTimeMillis": end_ms,
            }
            resp = service.users().dataset().aggregate(userId="me", body=body).execute()
            total_minutes = 0
            for bucket in resp.get("bucket", []):
                for ds in bucket.get("dataset", []):
                    for point in ds.get("point", []):
                        sn = int(point.get("startTimeNanos", 0))
                        en = int(point.get("endTimeNanos", 0))
                        total_minutes += (en - sn) / (1e9 * 60)
            return round(total_minutes / 60, 1)
        except Exception:
            pass
        return 0.0

    with ThreadPoolExecutor(max_workers=4) as executor:
        f_steps = executor.submit(_get_int, "com.google.step_count.delta", "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps")
        f_calories = executor.submit(_get_float, "com.google.calories.expended")
        f_heart = executor.submit(_get_float, "com.google.heart_rate.bpm")
        f_sleep = executor.submit(_get_sleep)
        
        steps = f_steps.result()
        calories = f_calories.result()
        sleep = f_sleep.result()
        heart_rate = f_heart.result()

    return {
        "steps": steps,
        "calories": calories,
        "sleep": sleep,
        "heart_rate": heart_rate,
        "date": target_date.strftime("%Y-%m-%d"),
    }


class GoogleFitService:
    """Handles Google Fit API integration and Firestore sync."""

    SCOPES = GoogleFitConfig.SCOPES

    def __init__(self):
        self.client_id = GoogleFitConfig.CLIENT_ID
        self.client_secret = GoogleFitConfig.CLIENT_SECRET
        self.redirect_uri = GoogleFitConfig.REDIRECT_URI
        self.db = get_firestore_client()
        self.scoring_service = ScoringService()

    def get_auth_url(self, user_id: str) -> str:
        """Build Google OAuth2 URL manually."""
        from urllib.parse import urlencode
        if not self.client_id:
            return ""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": f"gfit__{user_id}",
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    def exchange_code(self, code: str) -> dict:
        """Exchange authorization code for tokens."""
        try:
            resp = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=15,
            )
            if resp.status_code != 200:
                st.error(f"Token exchange failed: {resp.json().get('error_description', resp.text)}")
                return {}
            
            token_data = resp.json()
            return {
                "token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scopes": token_data.get("scope", "").split(),
            }
        except Exception as e:
            st.error(f"Token exchange error: {e}")
            return {}

    def fetch_daily_data(self, credentials_dict: dict, date: datetime = None) -> dict:
        """Fetch fitness data for a single day using cache."""
        if not credentials_dict:
            return self._generate_demo_data()

        try:
            target_date = date or datetime.now()
            target_timestamp = target_date.timestamp()
            
            return _cached_fetch_daily_stats(
                token=credentials_dict.get("token", ""),
                refresh_token=credentials_dict.get("refresh_token", ""),
                client_id=credentials_dict.get("client_id", self.client_id),
                client_secret=credentials_dict.get("client_secret", self.client_secret),
                target_timestamp=target_timestamp
            )
        except Exception as e:
            st.warning(f"Could not fetch Google Fit data: {e}. Using demo data.")
            return self._generate_demo_data()

    def fetch_weekly_data(self, credentials_dict: dict) -> list:
        """Fetch fitness data for the past 7 days in parallel."""
        from concurrent.futures import ThreadPoolExecutor
        days = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(
                lambda d: self.fetch_daily_data(credentials_dict, d), days
            ))
        return results

    def sync_daily_data_to_firestore(self, user_id: str, credentials_dict: dict, date: datetime = None):
        """
        Fetch weekly data, calculate DayScore, and sync purely to Firestore. 
        Creates a permanent historical record in 'daily_scores' collection for the last 7 days
        so no days are missed if the user doesn't log in daily.
        """
        if not self.db or not credentials_dict:
            return

        # Fetch the last 7 days of data
        weekly_stats = self.fetch_weekly_data(credentials_dict)
        
        for daily_stats in weekly_stats:
            date_str = daily_stats.get("date")
            if not date_str:
                continue
                
            # Calculate Score
            score_data = self.scoring_service.calculate_score(daily_stats)
            
            # Build document payload
            doc_data = {
                "user_id": user_id,
                "date": date_str,
                "timestamp": datetime.now().isoformat(),
                "steps": daily_stats.get("steps", 0),
                "calories": daily_stats.get("calories", 0),
                "sleep": daily_stats.get("sleep", 0.0),
                "heart_rate": daily_stats.get("heart_rate", 0),
                "day_score": score_data.get("total_score", 0),
                "score_breakdown": score_data.get("breakdown", {})
            }

            # Write to daily_scores collection (upsert based on user_id + date)
            try:
                doc_id = f"{user_id}_{date_str}"
                self.db.collection("daily_scores").document(doc_id).set(doc_data)
            except Exception as e:
                print(f"Failed to sync daily score to Firestore for {date_str}: {e}")

    # ── Demo Data ──────────────────────────────────────────────────
    @staticmethod
    def _generate_demo_data() -> dict:
        import random
        return {
            "steps": random.randint(3000, 15000),
            "calories": random.randint(1200, 2800),
            "sleep": round(random.uniform(4.5, 9.5), 1),
            "heart_rate": random.randint(55, 95),
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
