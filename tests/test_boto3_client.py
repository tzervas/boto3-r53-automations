"""Tests for Route53Client class."""

from unittest.mock import MagicMock, patch

import boto3
import pytest
from botocore.exceptions import ClientError

from src.route53_client import Route53Client
from src.utils.error_handling import Route53Error


class TestRoute53Client:
    """Test cases for Route53Client."""

    def test_init(self):
        """Test initialization with session."""
        mock_session = MagicMock()
        client = Route53Client(mock_session)
        assert client.session == mock_session

    def test_get_client_success(self):
        """Test successful client creation."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        route53_client = Route53Client(mock_session)
        result = route53_client.get_client()

        assert result == mock_client
        mock_session.client.assert_called_once_with("route53")

    def test_get_client_error(self):
        """Test client creation with error."""
        mock_session = MagicMock()
        mock_session.client.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "CreateClient",
        )

        route53_client = Route53Client(mock_session)

        with pytest.raises(Route53Error, match="Failed to create Route53 client"):
            route53_client.get_client()

    def test_get_client_info_success(self):
        """Test successful client info retrieval."""
        mock_session = MagicMock()
        mock_session.region_name = "us-east-1"
        mock_session.profile_name = "default"

        mock_client = MagicMock()
        mock_client._service_model.service_name = "route53"
        mock_client._service_model.api_version = "2013-04-01"
        mock_session.client.return_value = mock_client

        route53_client = Route53Client(mock_session)
        result = route53_client.get_client_info()

        expected = {
            "service": "route53",
            "region": "us-east-1",
            "api_version": "2013-04-01",
            "profile": "default",
        }
        assert result == expected

    def test_get_client_info_no_profile(self):
        """Test client info retrieval without profile."""
        mock_session = MagicMock()
        mock_session.region_name = "us-west-2"
        mock_session.profile_name = None

        mock_client = MagicMock()
        mock_client._service_model.service_name = "route53"
        mock_client._service_model.api_version = "2013-04-01"
        mock_session.client.return_value = mock_client

        route53_client = Route53Client(mock_session)
        result = route53_client.get_client_info()

        expected = {
            "service": "route53",
            "region": "us-west-2",
            "api_version": "2013-04-01",
            "profile": None,
        }
        assert result == expected

    def test_get_client_info_error(self):
        """Test client info retrieval with error."""
        mock_session = MagicMock()
        mock_session.client.side_effect = Exception("Connection failed")

        route53_client = Route53Client(mock_session)

        with pytest.raises(Route53Error, match="Failed to get client information"):
            route53_client.get_client_info()
