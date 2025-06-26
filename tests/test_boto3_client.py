"""Tests for Route53Client class."""

from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from src.route53_client import Route53Client
from src.utils.error_handling import Route53Error


class TestRoute53Client:
    """Test cases for Route53Client."""

    def test_init(self) -> None:
        """Test initialization with session."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        client = Route53Client(mock_session)
        assert client.client == mock_client

    def test_get_client_success(self) -> None:
        """Test successful client creation."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        route53_client = Route53Client(mock_session)
        result = route53_client.get_client()

        assert result == mock_client
        mock_session.client.assert_called_once_with("route53")

    def test_init_error(self) -> None:
        """Test client creation with error in constructor."""
        mock_session = MagicMock()
        mock_session.client.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "CreateClient",
        )

        with pytest.raises(Route53Error, match="Failed to create Route 53 client"):
            Route53Client(mock_session)

    def test_get_client_info_success(self) -> None:
        """Test successful client info retrieval."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_client.meta.region_name = "us-east-1"
        mock_client.meta.endpoint_url = "https://route53.amazonaws.com"
        mock_session.client.return_value = mock_client

        route53_client = Route53Client(mock_session)
        result = route53_client.get_client_info()

        expected = {
            "service": "route53",
            "region": "us-east-1",
            "endpoint_url": "https://route53.amazonaws.com",
        }
        assert result == expected

    def test_get_client_info_error(self) -> None:
        """Test client info retrieval with error."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_client.meta.region_name.side_effect = Exception("Connection failed")
        mock_session.client.return_value = mock_client

        route53_client = Route53Client(mock_session)
        result = route53_client.get_client_info()

        # Should return error message instead of raising
        assert result == {"status": "Error retrieving client info"}
