"""Tests for Route53Operations delete functionality."""
import boto3
import pytest
from moto import mock_aws
from botocore.exceptions import ClientError

from src.route53_operations import Route53Operations
from src.utils.error_handling import Route53ValidationError, Route53NotFoundError


@pytest.fixture
def route53_client():
    """Provide a mocked Route53 client."""
    with mock_aws():
        session = boto3.Session(region_name="us-east-1")
        yield session.client("route53")


@pytest.fixture
def hosted_zone(route53_client):
    """Create a test hosted zone."""
    hosted_zone = route53_client.create_hosted_zone(
        Name="example.com", CallerReference="test-delete"
    )
    return hosted_zone["HostedZone"]["Id"].split("/")[-1]


class TestRoute53OperationsDelete:
    """Test cases for Route53Operations delete functionality."""

    def test_delete_dns_records_success(self, route53_client, hosted_zone):
        """Test successful deletion of DNS records."""
        operations = Route53Operations(route53_client)
        
        # First create some records
        operations.create_dns_record(
            hosted_zone_id=hosted_zone,
            domain="example.com",
            load_balancer_ip="192.168.1.100",
            services=["api", "web"]
        )
        
        # Verify records exist
        records = route53_client.list_resource_record_sets(HostedZoneId=hosted_zone)
        api_record_exists = any(
            r["Name"] == "api.example.com." and r["Type"] == "A"
            for r in records["ResourceRecordSets"]
        )
        web_record_exists = any(
            r["Name"] == "web.example.com." and r["Type"] == "A"
            for r in records["ResourceRecordSets"]
        )
        assert api_record_exists
        assert web_record_exists
        
        # Delete the records
        change_id = operations.delete_dns_records(
            hosted_zone_id=hosted_zone,
            domain="example.com",
            services=["api", "web"]
        )
        
        assert change_id.startswith("/change/")
        
        # Verify records are deleted
        records_after = route53_client.list_resource_record_sets(HostedZoneId=hosted_zone)
        api_record_exists_after = any(
            r["Name"] == "api.example.com." and r["Type"] == "A"
            for r in records_after["ResourceRecordSets"]
        )
        web_record_exists_after = any(
            r["Name"] == "web.example.com." and r["Type"] == "A"
            for r in records_after["ResourceRecordSets"]
        )
        assert not api_record_exists_after
        assert not web_record_exists_after

    def test_delete_dns_records_partial_success(self, route53_client, hosted_zone):
        """Test deletion when only some records exist."""
        operations = Route53Operations(route53_client)
        
        # Create only one record
        operations.create_dns_record(
            hosted_zone_id=hosted_zone,
            domain="example.com",
            load_balancer_ip="192.168.1.100",
            services=["api"]
        )
        
        # Try to delete both existing and non-existing records
        change_id = operations.delete_dns_records(
            hosted_zone_id=hosted_zone,
            domain="example.com",
            services=["api", "nonexistent"]
        )
        
        assert change_id.startswith("/change/")

    def test_delete_dns_records_invalid_zone_id(self, route53_client):
        """Test deletion with invalid hosted zone ID."""
        operations = Route53Operations(route53_client)
        
        with pytest.raises(Route53ValidationError, match="Invalid hosted zone ID"):
            operations.delete_dns_records(
                hosted_zone_id="invalid-zone",
                domain="example.com",
                services=["api"]
            )

    def test_delete_dns_records_invalid_domain(self, route53_client, hosted_zone):
        """Test deletion with invalid domain."""
        operations = Route53Operations(route53_client)
        
        with pytest.raises(Route53ValidationError, match="Invalid domain name"):
            operations.delete_dns_records(
                hosted_zone_id=hosted_zone,
                domain="",
                services=["api"]
            )

    def test_delete_dns_records_empty_services(self, route53_client, hosted_zone):
        """Test deletion with empty services list."""
        operations = Route53Operations(route53_client)
        
        with pytest.raises(Route53ValidationError, match="Services list cannot be empty"):
            operations.delete_dns_records(
                hosted_zone_id=hosted_zone,
                domain="example.com",
                services=[]
            )

    def test_delete_dns_records_nonexistent_zone(self, route53_client):
        """Test deletion with non-existent hosted zone."""
        operations = Route53Operations(route53_client)
        
        with pytest.raises(Route53NotFoundError):
            operations.delete_dns_records(
                hosted_zone_id="Z1234567890123",  # Valid format but doesn't exist
                domain="example.com",
                services=["api"]
            )
