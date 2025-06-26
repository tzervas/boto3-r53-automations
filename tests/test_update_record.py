"""Tests for Route53Operations update functionality."""

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from src.route53_operations import Route53Operations
from src.utils.error_handling import Route53NotFoundError, Route53ValidationError


@pytest.fixture
def route53_client():
    """Provide a mocked Route53 client."""
    with mock_aws():
        session = boto3.Session(region_name="us-east-1")
        yield session.client("route53")


@pytest.fixture
def hosted_zone_with_records(route53_client):
    """Create a test hosted zone with existing records."""
    hosted_zone = route53_client.create_hosted_zone(
        Name="example.com", CallerReference="test-update"
    )
    zone_id = hosted_zone["HostedZone"]["Id"].split("/")[-1]

    # Create initial records
    operations = Route53Operations(route53_client)
    operations.create_dns_record(
        hosted_zone_id=zone_id,
        domain="example.com",
        load_balancer_ip="192.168.1.100",
        services=["api", "web"],
    )

    return zone_id


class TestRoute53OperationsUpdate:
    """Test cases for Route53Operations update functionality."""

    def test_list_records_success(self, route53_client, hosted_zone_with_records):
        """Test successful listing of DNS records."""
        operations = Route53Operations(route53_client)

        records = operations.list_records(hosted_zone_with_records)

        # Should have at least NS, SOA, and our A records
        assert len(records) >= 4

        # Check our created A records exist
        a_records = [r for r in records if r["Type"] == "A"]
        assert len(a_records) == 2

        record_names = [r["Name"] for r in a_records]
        assert "api.example.com." in record_names
        assert "web.example.com." in record_names

    def test_list_records_empty_zone(self, route53_client):
        """Test listing records in empty hosted zone."""
        hosted_zone = route53_client.create_hosted_zone(
            Name="empty.com", CallerReference="test-empty"
        )
        zone_id = hosted_zone["HostedZone"]["Id"].split("/")[-1]

        operations = Route53Operations(route53_client)
        records = operations.list_records(zone_id)

        # Should have default NS and SOA records
        assert len(records) >= 2
        record_types = [r["Type"] for r in records]
        assert "NS" in record_types
        assert "SOA" in record_types

    def test_list_records_invalid_zone_id(self, route53_client):
        """Test listing records with invalid zone ID."""
        operations = Route53Operations(route53_client)

        with pytest.raises(Route53ValidationError, match="Invalid hosted zone ID"):
            operations.list_records("invalid-zone")

    def test_list_records_nonexistent_zone(self, route53_client):
        """Test listing records for non-existent zone."""
        operations = Route53Operations(route53_client)

        with pytest.raises(Route53NotFoundError):
            operations.list_records("Z1234567890123")

    def test_get_change_status_success(self, route53_client, hosted_zone_with_records):
        """Test successful change status retrieval."""
        operations = Route53Operations(route53_client)

        # Create a change to get a change ID
        change_id = operations.create_dns_record(
            hosted_zone_id=hosted_zone_with_records,
            domain="example.com",
            load_balancer_ip="192.168.1.200",
            services=["test"],
        )

        # Get the status
        status = operations.get_change_status(change_id)

        # In moto, changes are typically INSYNC immediately
        assert status in ["PENDING", "INSYNC"]

    def test_get_change_status_invalid_format(self, route53_client):
        """Test change status with invalid change ID format."""
        operations = Route53Operations(route53_client)

        with pytest.raises(Route53ValidationError, match="Invalid change ID format"):
            operations.get_change_status("invalid-change-id")

    def test_get_change_status_nonexistent_change(self, route53_client):
        """Test change status for non-existent change."""
        operations = Route53Operations(route53_client)

        with pytest.raises(Route53NotFoundError):
            operations.get_change_status("/change/C1234567890123")

    def test_create_dns_record_multiple_services(self, route53_client):
        """Test creating DNS records for multiple services."""
        hosted_zone = route53_client.create_hosted_zone(
            Name="multi.com", CallerReference="test-multi"
        )
        zone_id = hosted_zone["HostedZone"]["Id"].split("/")[-1]

        operations = Route53Operations(route53_client)
        change_id = operations.create_dns_record(
            hosted_zone_id=zone_id,
            domain="multi.com",
            load_balancer_ip="10.0.0.1",
            services=["api", "web", "admin"],
        )

        assert change_id.startswith("/change/")

        # Verify all records were created
        records = route53_client.list_resource_record_sets(HostedZoneId=zone_id)
        a_records = [r for r in records["ResourceRecordSets"] if r["Type"] == "A"]

        assert len(a_records) == 3
        record_names = [r["Name"] for r in a_records]
        assert "api.multi.com." in record_names
        assert "web.multi.com." in record_names
        assert "admin.multi.com." in record_names

        # Verify IP addresses
        for record in a_records:
            assert record["ResourceRecords"][0]["Value"] == "10.0.0.1"

    def test_create_dns_record_duplicate_services(self, route53_client):
        """Test creating DNS records with duplicate service names."""
        hosted_zone = route53_client.create_hosted_zone(
            Name="dup.com", CallerReference="test-dup"
        )
        zone_id = hosted_zone["HostedZone"]["Id"].split("/")[-1]

        operations = Route53Operations(route53_client)
        change_id = operations.create_dns_record(
            hosted_zone_id=zone_id,
            domain="dup.com",
            load_balancer_ip="10.0.0.1",
            services=["api", "api", "web", "api"],  # Duplicates
        )

        assert change_id.startswith("/change/")

        # Verify only unique records were created
        records = route53_client.list_resource_record_sets(HostedZoneId=zone_id)
        a_records = [r for r in records["ResourceRecordSets"] if r["Type"] == "A"]

        assert len(a_records) == 2  # Only api and web
        record_names = [r["Name"] for r in a_records]
        assert "api.dup.com." in record_names
        assert "web.dup.com." in record_names
