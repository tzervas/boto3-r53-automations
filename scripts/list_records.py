import boto3
from botocore.exceptions import ClientError

from src.route53_client import Route53Client
from src.route53_operations import Route53Operations
from src.session_manager import SessionManager


def list_records(hosted_zone_id: str) -> None:
    """List all DNS records in a specified hosted zone."""
    session = boto3.Session()
    client = session.client("route53")

    try:
        response = client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
        records = response.get("ResourceRecordSets", [])

        if not records:
            print("No DNS records found.")
            return

        print(f"Found {len(records)} DNS records:")
        for record in records:
            print(f" - {record['Name']} ({record['Type']})")

    except ClientError as e:
        print(f"❌ Error listing DNS records: {e}")
