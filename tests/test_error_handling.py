"""Tests for error handling utilities."""

from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from src.utils.error_handling import (
    Route53Error,
    Route53NotFoundError,
    Route53PermissionError,
    Route53ThrottleError,
    Route53ValidationError,
    handle_aws_errors,
    validate_domain_name,
    validate_hosted_zone_id,
)


class TestRoute53Exceptions:
    """Test custom exception classes."""

    def test_route53_error(self):
        """Test base Route53Error exception."""
        error = Route53Error("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_route53_not_found_error(self):
        """Test Route53NotFoundError exception."""
        error = Route53NotFoundError("Resource not found")
        assert str(error) == "Resource not found"
        assert isinstance(error, Route53Error)

    def test_route53_validation_error(self):
        """Test Route53ValidationError exception."""
        error = Route53ValidationError("Invalid input")
        assert str(error) == "Invalid input"
        assert isinstance(error, Route53Error)

    def test_route53_permission_error(self):
        """Test Route53PermissionError exception."""
        error = Route53PermissionError("Access denied")
        assert str(error) == "Access denied"
        assert isinstance(error, Route53Error)

    def test_route53_throttle_error(self):
        """Test Route53ThrottleError exception."""
        error = Route53ThrottleError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, Route53Error)


class TestHandleAwsErrors:
    """Test handle_aws_errors decorator."""

    def test_handle_aws_errors_decorator_success(self):
        """Test decorator with successful function execution."""

        @handle_aws_errors()
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_handle_aws_errors_client_error_not_found(self):
        """Test decorator with NoSuchHostedZone error."""

        @handle_aws_errors()
        def failing_function():
            raise ClientError(
                {"Error": {"Code": "NoSuchHostedZone", "Message": "Zone not found"}},
                "ListResourceRecordSets",
            )

        with pytest.raises(Route53NotFoundError, match="Zone not found"):
            failing_function()

    def test_handle_aws_errors_client_error_invalid_input(self):
        """Test decorator with InvalidInput error."""

        @handle_aws_errors()
        def failing_function():
            raise ClientError(
                {"Error": {"Code": "InvalidInput", "Message": "Invalid parameter"}},
                "ChangeResourceRecordSets",
            )

        with pytest.raises(Route53ValidationError, match="Invalid parameter"):
            failing_function()

    def test_handle_aws_errors_client_error_access_denied(self):
        """Test decorator with AccessDenied error."""

        @handle_aws_errors()
        def failing_function():
            raise ClientError(
                {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
                "CreateHostedZone",
            )

        with pytest.raises(Route53PermissionError, match="Access denied"):
            failing_function()

    def test_handle_aws_errors_client_error_throttling(self):
        """Test decorator with Throttling error."""

        @handle_aws_errors()
        def failing_function():
            raise ClientError(
                {"Error": {"Code": "Throttling", "Message": "Rate exceeded"}},
                "ChangeResourceRecordSets",
            )

        with pytest.raises(Route53ThrottleError, match="Rate exceeded"):
            failing_function()


class TestValidationFunctions:
    """Test validation utility functions."""

    def test_validate_hosted_zone_id_valid(self):
        """Test validation of valid hosted zone IDs."""
        valid_ids = [
            "Z1234567890123",
            "Z1A2B3C4D5E6F7",
            "ZABCDEFGHIJKLMN",
        ]

        for zone_id in valid_ids:
            validate_hosted_zone_id(zone_id)  # Should not raise

    def test_validate_hosted_zone_id_invalid(self):
        """Test validation of invalid hosted zone IDs."""
        invalid_ids = [
            "",  # Empty
            "1234567",  # Too short
            "Z123456$",  # Invalid character
            "a" * 33,  # Too long
        ]

        for zone_id in invalid_ids:
            with pytest.raises(Route53ValidationError):
                validate_hosted_zone_id(zone_id)

    def test_validate_hosted_zone_id_prefix_removal(self):
        """Test removal of /hostedzone/ prefix."""
        zone_id_with_prefix = "/hostedzone/Z1234567890123"
        result = validate_hosted_zone_id(zone_id_with_prefix)
        assert result == "Z1234567890123"

    def test_validate_domain_name_valid(self):
        """Test validation of valid domain names."""
        valid_domains = [
            "example.com",
            "subdomain.example.com",
            "test-domain.org",
            "a.b.c.d.com",
            "123.example.com",
        ]

        for domain in valid_domains:
            validate_domain_name(domain)  # Should not raise

    def test_validate_domain_name_invalid(self):
        """Test validation of invalid domain names."""
        invalid_domains = [
            "",  # Empty
            "a" * 254,  # Too long
        ]

        for domain in invalid_domains:
            with pytest.raises(Route53ValidationError):
                validate_domain_name(domain)

    def test_validate_domain_name_normalization(self):
        """Test domain name normalization (adding trailing dot)."""
        test_cases = [
            ("example.com", "example.com."),
            ("sub.example.org", "sub.example.org."),
            ("test.co.uk", "test.co.uk."),
        ]

        for input_domain, expected in test_cases:
            result = validate_domain_name(input_domain)
            assert result == expected
