import boto3
from botocore.exceptions import ClientError

from src.route53_client import Route53Client
from src.route53_operations import Route53Operations
from src.session_manager import SessionManager


def create_hosted_zone(domain: str) -> None:
    """Create a new Route 53 hosted zone."""
    session = boto3.Session()
    client = session.client("route53")

    try:
        response = client.create_hosted_zone(
            Name=domain,
            CallerReference=str(hash(domain)),  # Unique reference for idempotency
            HostedZoneConfig={
                "Comment": f"Hosted zone for {domain}",
                "PrivateZone": False,  # Set to True if it's a private hosted zone
            },
        )
        hosted_zone_id = response["HostedZone"]["Id"]
        print(f"✅ Created hosted zone: {domain} (ID: {hosted_zone_id})")

    except ClientError as e:
        print(f"❌ Error creating hosted zone: {e}")
        print("⚠️  You may need to create the hosted zone manually")
