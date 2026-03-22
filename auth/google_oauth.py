"""
DayScore - Google OAuth2 Sign-In
Handles the Google Sign-In / Sign-Up flow using OAuth2 Authorization Code.
Works with Streamlit's query parameter callback mechanism.
"""

import os
import json
import streamlit as st
import requests
from urllib.parse import urlencode

from config.settings import GoogleFitConfig


# ── Google OAuth Endpoints ──────────────────────────────
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Scopes needed for profile + email + fitness
GOOGLE_SIGN_IN_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
] + GoogleFitConfig.SCOPES


def get_google_auth_url() -> str:
    """
    Build the Google OAuth2 authorization URL.
    Redirects the user to Google's consent screen.
    """
    client_id = GoogleFitConfig.CLIENT_ID
    redirect_uri = GoogleFitConfig.REDIRECT_URI

    if not client_id:
        return ""

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(GOOGLE_SIGN_IN_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": "google_signin",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


def exchange_code_for_tokens(auth_code: str) -> dict:
    """
    Exchange the authorization code for access & ID tokens.
    Returns token data or error.
    """
    client_id = GoogleFitConfig.CLIENT_ID
    client_secret = GoogleFitConfig.CLIENT_SECRET
    redirect_uri = GoogleFitConfig.REDIRECT_URI

    try:
        response = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": auth_code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        if response.status_code == 200:
            return {"success": True, "tokens": response.json()}
        else:
            error_data = response.json()
            return {
                "success": False,
                "error": error_data.get("error_description", "Token exchange failed."),
            }
    except Exception as e:
        return {"success": False, "error": f"Token exchange error: {str(e)}"}


def get_google_user_info(access_token: str) -> dict:
    """
    Fetch the user's profile information from Google.
    Returns user info dict or error.
    """
    try:
        response = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        if response.status_code == 200:
            return {"success": True, "user_info": response.json()}
        else:
            return {"success": False, "error": "Failed to fetch user info."}
    except Exception as e:
        return {"success": False, "error": f"User info error: {str(e)}"}


def handle_google_callback() -> dict | None:
    """
    Check if the current page load carries a Google OAuth callback.
    If query params contain 'code' and 'state=google_signin',
    exchange the code, fetch user profile, and return user data.
    Returns None if no callback is detected.
    """
    query_params = st.query_params

    code = query_params.get("code")
    state = query_params.get("state")

    if "error" in query_params:
        return {"success": False, "error": f"Google Auth Error: {query_params.get('error')}"}

    if not code or state != "google_signin":
        return None

    # Clear query params so the callback doesn't re-trigger
    st.query_params.clear()

    # Step 1: Exchange code for tokens
    token_result = exchange_code_for_tokens(code)
    if not token_result["success"]:
        return {"success": False, "error": token_result["error"]}

    tokens = token_result["tokens"]
    access_token = tokens.get("access_token")

    if not access_token:
        return {"success": False, "error": "No access token received."}

    # Step 2: Get user profile
    user_result = get_google_user_info(access_token)
    if not user_result["success"]:
        return {"success": False, "error": user_result["error"]}

    user_info = user_result["user_info"]

    return {
        "success": True,
        "user_info": {
            "google_id": user_info.get("id", ""),
            "email": user_info.get("email", ""),
            "name": user_info.get("name", ""),
            "picture": user_info.get("picture", ""),
            "verified_email": user_info.get("verified_email", False),
        },
        "raw_tokens": {
            "token": access_token,
            "refresh_token": tokens.get("refresh_token", ""),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": GoogleFitConfig.CLIENT_ID,
            "client_secret": GoogleFitConfig.CLIENT_SECRET,
            "scopes": tokens.get("scope", "").split(),
        },
        "access_token": access_token,
        "id_token": tokens.get("id_token", ""),
    }
