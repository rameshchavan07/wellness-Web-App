"""
DayScore - Session Management Service
Centralized abstraction for Streamlit session state.
"""

import streamlit as st
from typing import Any, Dict, List, Optional


class SessionManager:
    """Manages Streamlit session state keys and defaults."""

    # Default keys and their initial values
    DEFAULTS = {
        "authenticated": False,
        "user": {},
        "token": "",
        "google_fit_connected": False,
        "google_fit_credentials": {},
        "chat_history": [],
        "fitness_data": {},
        "selected_page": "Dashboard",
        "mood_logged": False,
        "dashboard_fitness_data": None,
        "chat_personality": "Friendly",
        "chat_open": False,
        "app_initialized": True,
        "_oauth_csrf_token": None,
    }

    @staticmethod
    def initialize():
        """Ensure all default session state keys exist."""
        for key, value in SessionManager.DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @property
    def is_authenticated(self) -> bool:
        return st.session_state.get("authenticated", False)

    @is_authenticated.setter
    def is_authenticated(self, value: bool):
        st.session_state["authenticated"] = value

    @property
    def user(self) -> Dict[str, Any]:
        return st.session_state.get("user", {})

    @user.setter
    def user(self, value: Dict[str, Any]):
        st.session_state["user"] = value

    @property
    def user_id(self) -> Optional[str]:
        return self.user.get("user_id")

    @property
    def token(self) -> str:
        return st.session_state.get("token", "")

    @token.setter
    def token(self, value: str):
        st.session_state["token"] = value

    @property
    def google_fit_connected(self) -> bool:
        return st.session_state.get("google_fit_connected", False)

    @google_fit_connected.setter
    def google_fit_connected(self, value: bool):
        st.session_state["google_fit_connected"] = value

    @property
    def google_fit_credentials(self) -> Dict[str, Any]:
        return st.session_state.get("google_fit_credentials", {})

    @google_fit_credentials.setter
    def google_fit_credentials(self, value: Dict[str, Any]):
        st.session_state["google_fit_credentials"] = value

    @property
    def chat_history(self) -> List[Dict[str, str]]:
        return st.session_state.get("chat_history", [])

    @chat_history.setter
    def chat_history(self, value: List[Dict[str, str]]):
        st.session_state["chat_history"] = value

    @property
    def mood_logged(self) -> Any:
        return st.session_state.get("mood_logged", False)

    @mood_logged.setter
    def mood_logged(self, value: Any):
        st.session_state["mood_logged"] = value

    @property
    def dashboard_fitness_data(self) -> Optional[Dict[str, Any]]:
        return st.session_state.get("dashboard_fitness_data")

    @dashboard_fitness_data.setter
    def dashboard_fitness_data(self, value: Optional[Dict[str, Any]]):
        st.session_state["dashboard_fitness_data"] = value

    @property
    def chat_personality(self) -> str:
        return st.session_state.get("chat_personality", "Friendly")

    @chat_personality.setter
    def chat_personality(self, value: str):
        st.session_state["chat_personality"] = value

    @property
    def chat_open(self) -> bool:
        return st.session_state.get("chat_open", False)

    @chat_open.setter
    def chat_open(self, value: bool):
        st.session_state["chat_open"] = value

    def clear(self):
        """Reset the session state (Sign Out)."""
        for key in self.DEFAULTS.keys():
            if key in st.session_state:
                del st.session_state[key]
        self.initialize()
