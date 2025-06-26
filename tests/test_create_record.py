# tests/test_route53_operations.py
import boto3
import pytest
from moto import mock_aws

from src.route53_operations import Route53Operations


@pytest.fixture
def route53_client():
    with mock_aws():
        session = boto3.Session(region_name="us-east-1")
        yield session.client("route53")


def test_create_dns_records(route53_client):
    operations = Route53Operations(route53_client)
    hosted_zone = route53_client.create_hosted_zone(
        Name="example.com", CallerReference="test"
    )
    zone_id = hosted_zone["HostedZone"]["Id"].split("/")[-1]

    operations.create_dns_record(
        hosted_zone_id=zone_id,
        domain="example.com",
        load_balancer_ip="192.168.1.100",
        services=["api"],
    )

    records = route53_client.list_resource_record_sets(HostedZoneId=zone_id)
    assert any(
        r["Name"] == "api.example.com." and r["Type"] == "A"
        for r in records["ResourceRecordSets"]
    )
