import pytest
from unittest.mock import MagicMock, patch
from auth.auth_service import AuthService
from config.settings import AppConfig

@patch("auth.auth_service.get_firebase_auth_client")
@patch("auth.auth_service.get_firestore_client")
def test_create_user_profile(mock_firestore, mock_auth):
    service = AuthService()
    
    mock_db = MagicMock()
    mock_firestore.return_value = mock_db
    service.db = mock_db
    
    service.create_user_profile("user_123", "Test User", "test@example.com")
    
    # Should call set with specific fields
    mock_db.collection().document().set.assert_called_once()
    args, kwargs = mock_db.collection().document().set.call_args
    data = args[0]
    
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["role"] == "patient"
    assert data["score"] == 0
    assert data["streak"] == 0
    assert "created_at" in data

def test_demo_mode_sign_in():
    service = AuthService()
    
    # Ensure demo mode uses the demo user ID
    user_info = service._handle_demo_login()
    
    assert user_info["user_id"] == AppConfig.DEMO_USER_ID
    assert user_info["role"] == "patient"
    assert user_info["name"] == "Demo User"
    assert user_info["email"] == "demo@dayscore.app"
