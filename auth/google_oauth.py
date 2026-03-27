"""
DayScore - Google OAuth2 Sign-In
Handles the Google Sign-In / Sign-Up flow using OAuth2 Authorization Code.
Works with Streamlit's query parameter callback mechanism.

NOTE ON CSRF PROTECTION:
Streamlit loses session_state when the browser follows an OAuth redirect and
returns (it creates a fresh WebSocket connection). Therefore we persist the
CSRF token to a short-lived temp file keyed by the token itself, rather than
relying on st.session_state. The token is validated and deleted on use.
"""

import os
import tempfile
import secrets
import streamlit as st
import requests
from urllib.parse import urlencode

from config.settings import GoogleFitConfig


# ── Google OAuth Endpoints ──────────────────────────────
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Scopes for sign-in only (no sensitive Fit scopes — avoids 403 on Streamlit Cloud)
# Google Fit scopes are requested separately via Settings → Connect Google Fit
GOOGLE_SIGN_IN_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Temp dir for persisted CSRF tokens
_CSRF_TOKEN_DIR = os.path.join(tempfile.gettempdir(), "dayscore_oauth")


def _save_csrf_token(token: str) -> None:
    """Persist a CSRF token to a temp file so it survives Streamlit reruns/redirects."""
    os.makedirs(_CSRF_TOKEN_DIR, exist_ok=True)
    token_path = os.path.join(_CSRF_TOKEN_DIR, f"csrf_{token}.tmp")
    with open(token_path, "w") as f:
        f.write(token)


def _verify_and_consume_csrf_token(token: str) -> bool:
    """
    Check if the token matches a stored temp file.
    Deletes the file so each token is single-use.
    Returns True if valid, False otherwise.
    """
    token_path = os.path.join(_CSRF_TOKEN_DIR, f"csrf_{token}.tmp")
    if os.path.exists(token_path):
        try:
            os.remove(token_path)
        except OSError:
            pass
        return True
    return False


def get_google_auth_url() -> str:
    """
    Build the Google OAuth2 authorization URL.
    Redirects the user to Google's consent screen.
    """
    client_id = GoogleFitConfig.CLIENT_ID
    redirect_uri = GoogleFitConfig.REDIRECT_URI

    if not client_id:
        return ""

    # Generate a fresh CSRF token on each call and persist it to disk.
    # This is necessary because Streamlit's session_state is lost across
    # the OAuth redirect cycle.
    csrf_token = secrets.token_urlsafe(32)
    _save_csrf_token(csrf_token)
    # Also store in session for same-session reuse (best effort)
    st.session_state["_oauth_csrf_token"] = csrf_token

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(GOOGLE_SIGN_IN_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": f"google_signin_{csrf_token}",
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
    If query params contain 'code' and 'state=google_signin_<token>',
    verify the CSRF token (from disk), exchange the code, fetch user
    profile, and return user data.
    Returns None if no callback is detected.
    """
    query_params = st.query_params

    code = query_params.get("code")
    state = query_params.get("state")

    if "error" in query_params:
        return {"success": False, "error": f"Google Auth Error: {query_params.get('error')}"}

    if not code or not state or not state.startswith("google_signin_"):
        return None

    # Extract the token from state
    received_csrf = state[len("google_signin_"):]

    # Verify against disk-persisted token (survives the redirect cycle)
    if not _verify_and_consume_csrf_token(received_csrf):
        # Fallback: also check in-memory session state (same-tab quick flow)
        expected_csrf = st.session_state.pop("_oauth_csrf_token", "")
        if not expected_csrf or received_csrf != expected_csrf:
            return {"success": False, "error": "Invalid OAuth state — possible CSRF attack."}

    # Clear session token if still present
    st.session_state.pop("_oauth_csrf_token", None)

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
