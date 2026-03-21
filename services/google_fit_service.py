"""
DayScore - Google Fit Service
Connects to Google Fit API to fetch fitness data.
"""

import streamlit as st
from datetime import datetime, timedelta
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from config.settings import GoogleFitConfig


class GoogleFitService:
    """Handles Google Fit API integration."""

    SCOPES = GoogleFitConfig.SCOPES

    def __init__(self):
        self.client_id = GoogleFitConfig.CLIENT_ID
        self.client_secret = GoogleFitConfig.CLIENT_SECRET
        self.redirect_uri = GoogleFitConfig.REDIRECT_URI

    def get_auth_url(self, user_id: str) -> str:
        """Build Google OAuth2 URL manually — no Flow, no PKCE params added."""
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
        """Exchange authorization code for tokens using a direct HTTP POST.
        Bypasses google-auth-oauthlib's PKCE requirement which breaks
        when the Flow object is recreated after a page redirect.
        """
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

    def _get_service(self, credentials_dict: dict):
        """Build the Fitness API service."""
        creds = Credentials(
            token=credentials_dict.get("token"),
            refresh_token=credentials_dict.get("refresh_token"),
            token_uri=credentials_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=credentials_dict.get("client_id", self.client_id),
            client_secret=credentials_dict.get("client_secret", self.client_secret),
        )
        return build("fitness", "v1", credentials=creds)

    def fetch_daily_data(self, credentials_dict: dict, date: datetime = None) -> dict:
        """
        Fetch fitness data for a single day.

        Returns:
            dict: {steps, calories, sleep, heart_rate}
        """
        if not credentials_dict:
            return self._generate_demo_data()

        try:
            service = self._get_service(credentials_dict)
            target_date = date or datetime.utcnow()

            start = datetime(target_date.year, target_date.month, target_date.day)
            end = start + timedelta(days=1)
            start_ms = int(start.timestamp() * 1000)
            end_ms = int(end.timestamp() * 1000)

            steps = self._fetch_steps(service, start_ms, end_ms)
            calories = self._fetch_calories(service, start_ms, end_ms)
            sleep = self._fetch_sleep(service, start_ms, end_ms)
            heart_rate = self._fetch_heart_rate(service, start_ms, end_ms)

            return {
                "steps": steps,
                "calories": calories,
                "sleep": sleep,
                "heart_rate": heart_rate,
                "date": target_date.strftime("%Y-%m-%d"),
            }
        except Exception as e:
            st.warning(f"Could not fetch Google Fit data: {e}. Using demo data.")
            return self._generate_demo_data()

    def fetch_weekly_data(self, credentials_dict: dict) -> list:
        """Fetch fitness data for the past 7 days."""
        weekly = []
        for i in range(6, -1, -1):
            day = datetime.utcnow() - timedelta(days=i)
            data = self.fetch_daily_data(credentials_dict, day)
            weekly.append(data)
        return weekly

    # ── Private Fetch Methods ──────────────────────────────────────

    def _fetch_steps(self, service, start_ms, end_ms) -> int:
        body = {
            "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
            "bucketByTime": {"durationMillis": 86400000},
            "startTimeMillis": start_ms,
            "endTimeMillis": end_ms,
        }
        resp = service.users().dataset().aggregate(userId="me", body=body).execute()
        return self._extract_int_value(resp)

    def _fetch_calories(self, service, start_ms, end_ms) -> int:
        body = {
            "aggregateBy": [{"dataTypeName": "com.google.calories.expended"}],
            "bucketByTime": {"durationMillis": 86400000},
            "startTimeMillis": start_ms,
            "endTimeMillis": end_ms,
        }
        resp = service.users().dataset().aggregate(userId="me", body=body).execute()
        return self._extract_float_value(resp)

    def _fetch_sleep(self, service, start_ms, end_ms) -> float:
        body = {
            "aggregateBy": [{"dataTypeName": "com.google.sleep.segment"}],
            "bucketByTime": {"durationMillis": 86400000},
            "startTimeMillis": start_ms,
            "endTimeMillis": end_ms,
        }
        resp = service.users().dataset().aggregate(userId="me", body=body).execute()
        # Calculate total sleep in hours
        total_minutes = 0
        for bucket in resp.get("bucket", []):
            for ds in bucket.get("dataset", []):
                for point in ds.get("point", []):
                    start_nanos = int(point.get("startTimeNanos", 0))
                    end_nanos = int(point.get("endTimeNanos", 0))
                    total_minutes += (end_nanos - start_nanos) / (1e9 * 60)
        return round(total_minutes / 60, 1)

    def _fetch_heart_rate(self, service, start_ms, end_ms) -> int:
        body = {
            "aggregateBy": [{"dataTypeName": "com.google.heart_rate.bpm"}],
            "bucketByTime": {"durationMillis": 86400000},
            "startTimeMillis": start_ms,
            "endTimeMillis": end_ms,
        }
        resp = service.users().dataset().aggregate(userId="me", body=body).execute()
        return self._extract_float_value(resp)

    # ── Extraction Helpers ─────────────────────────────────────────

    @staticmethod
    def _extract_int_value(response) -> int:
        for bucket in response.get("bucket", []):
            for ds in bucket.get("dataset", []):
                for point in ds.get("point", []):
                    for val in point.get("value", []):
                        return val.get("intVal", 0)
        return 0

    @staticmethod
    def _extract_float_value(response) -> int:
        for bucket in response.get("bucket", []):
            for ds in bucket.get("dataset", []):
                for point in ds.get("point", []):
                    for val in point.get("value", []):
                        fp = val.get("fpVal", 0)
                        return int(round(fp))
        return 0

    # ── Demo Data ──────────────────────────────────────────────────

    @staticmethod
    def _generate_demo_data() -> dict:
        """Generate realistic demo data for development/demo mode."""
        import random
        return {
            "steps": random.randint(3000, 15000),
            "calories": random.randint(1200, 2800),
            "sleep": round(random.uniform(4.5, 9.5), 1),
            "heart_rate": random.randint(55, 95),
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
        }
