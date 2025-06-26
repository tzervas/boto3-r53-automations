"""Tests for SessionManager class."""
import pytest
from unittest.mock import patch, MagicMock
import boto3
from botocore.exceptions import NoCredentialsError, ProfileNotFound

from src.session_manager import SessionManager
from src.utils.error_handling import Route53Error


class TestSessionManager:
    """Test cases for SessionManager."""

    @patch("boto3.Session")
    def test_init_default(self, mock_session):
        """Test default initialization."""
        mock_instance = MagicMock()
        mock_session.return_value = mock_instance
        
        session_manager = SessionManager()
        assert session_manager.profile_name is None
        assert session_manager.region_name == "us-east-1"

    @patch("boto3.Session")
    def test_init_with_params(self, mock_session):
        """Test initialization with custom parameters."""
        mock_instance = MagicMock()
        mock_session.return_value = mock_instance
        
        session_manager = SessionManager(
            profile_name="test-profile", region_name="us-west-2"
        )
        assert session_manager.profile_name == "test-profile"
        assert session_manager.region_name == "us-west-2"

    @patch("boto3.Session")
    def test_get_session_success(self, mock_session):
        """Test successful session creation."""
        mock_instance = MagicMock()
        mock_session.return_value = mock_instance
        
        session_manager = SessionManager()
        result = session_manager.get_session()
        
        assert result == mock_instance
        mock_session.assert_called_once_with(
            profile_name=None, region_name="us-east-1"
        )

    @patch("boto3.Session")
    def test_get_session_with_profile(self, mock_session):
        """Test session creation with specific profile."""
        session_manager = SessionManager(profile_name="test-profile")
        mock_session.assert_called_once_with(
            profile_name="test-profile", region_name="us-east-1"
        )

    @patch("boto3.Session")
    def test_get_session_profile_not_found(self, mock_session):
        """Test session creation with invalid profile."""
        mock_session.side_effect = ProfileNotFound(profile="invalid-profile")
        
        with pytest.raises(Route53Error, match="Failed to create AWS session: The config profile.*"):
            SessionManager(profile_name="invalid-profile")

    @patch("boto3.Session")
    def test_get_session_no_credentials(self, mock_session):
        """Test session creation with no credentials."""
        mock_session.side_effect = NoCredentialsError()
        
        with pytest.raises(Route53Error, match="Failed to create AWS session"):
            SessionManager()

    @patch("boto3.Session")
    def test_get_credentials_success(self, mock_session):
        """Test successful credential information retrieval."""
        mock_creds = MagicMock()
        mock_creds.access_key = "AKIA1234TEST890"
        mock_creds.secret_key = "secret"
        mock_creds.token = None
        
        mock_instance = MagicMock()
        mock_instance.get_credentials.return_value = mock_creds
        mock_instance.region_name = "us-east-1"
        mock_session.return_value = mock_instance
        
        session_manager = SessionManager()
        result = session_manager.get_credentials()
        
        expected = {
            "region": "us-east-1",
            "access_key_id": "AKIA1234...",
            "profile": None
        }
        assert result == expected

    @patch("boto3.Session")
    def test_get_credentials_with_token(self, mock_session):
        """Test credential information retrieval with session token."""
        mock_creds = MagicMock()
        mock_creds.access_key = "AKIA1234TEST890"
        mock_creds.secret_key = "secret"
        mock_creds.token = "token123"
        
        mock_instance = MagicMock()
        mock_instance.get_credentials.return_value = mock_creds
        mock_instance.region_name = "us-west-2"
        mock_session.return_value = mock_instance
        
        session_manager = SessionManager(region_name="us-west-2")
        result = session_manager.get_credentials()
        
        expected = {
            "region": "us-west-2",
            "access_key_id": "AKIA1234...",
            "profile": None
        }
        assert result == expected

    @patch("boto3.Session")
    def test_get_credentials_no_credentials(self, mock_session):
        """Test credential information retrieval with no credentials."""
        mock_instance = MagicMock()
        mock_instance.get_credentials.return_value = None
        mock_session.return_value = mock_instance
        
        with pytest.raises(Route53Error, match="Failed to get AWS credentials"):
            SessionManager().get_credentials()
