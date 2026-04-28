import pytest
from unittest.mock import MagicMock, patch
from services.streak_service import StreakService
import streamlit as st
from datetime import datetime, timedelta

def test_streak_service_demo_mode():
    service = StreakService()
    service.db = None  # Force demo mode
    
    st.session_state = {}
    
    # Test update streak
    assert service.update_streak("demo_user") == 1
    assert "demo_streak" in st.session_state
    
    # Test update sleep streak
    assert service.update_sleep_streak("demo_user", 7.5) == 1
    assert "demo_sleep_streak" in st.session_state
    
    assert service.update_sleep_streak("demo_user", 5.0) == 0
    assert st.session_state["demo_sleep_streak"] == 0

@patch("services.streak_service.get_firestore_client")
def test_get_sleep_streak(mock_get_client):
    mock_db = MagicMock()
    mock_get_client.return_value = mock_db
    
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"sleep_streak": 5}
    
    mock_db.collection().document().get.return_value = mock_doc
    
    service = StreakService()
    service.db = mock_db
    
    assert service.get_sleep_streak("user_123") == 5
