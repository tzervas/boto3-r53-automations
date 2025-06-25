from botocore.exceptions import ClientError
from typing import List, Optional

import records


class Route53Operations:
    """Manages Route 53 operations like creating or updating DNS records."""

    from botocore.client import BaseClient

    def __init__(self, route53_client: BaseClient):
        """
        Initialize Route 53 operations.

        Args:
            route53_client: A boto3 Route 53 client.
        """
        self.client = route53_client

    def create_dns_record(
        self,
        hosted_zone_id: str,
        domain: str,
        load_balancer_ip: str,
        services: List[str],
    ) -> None:
        """
        Create DNS A records pointing to an internal load balancer IP.

        Args:
            hosted_zone_id: ID of the Route 53 hosted zone.
            domain: Domain name (e.g., 'example.com').
            load_balancer_ip: IP address of the load balancer.
            services: List of service names (e.g., ['api', 'web']).
        """
        changes = []
        for service in services:
            hostname = f"{service}.{domain}"
            changes.append(
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": hostname,
                        "Type": "A",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": load_balancer_ip}],
                    },
                }
            )
            print(f"📝 Configuring DNS: {hostname} → {load_balancer_ip}")

        try:
            response = self.client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id, ChangeBatch={"Changes": changes}
            )
            change_id = response["ChangeInfo"]["Id"]
            print(f"✅ Created DNS records (Change ID: {change_id})")

        except ClientError as e:
            print(f"❌ Error creating DNS records: {e}")
            print("⚠️  You may need to create DNS records manually")

    def list_records(self, hosted_zone_id: str) -> List[dict]:
        """
        List all records in a hosted zone.

        Args:
            hosted_zone_id: ID of the Route 53 hosted zone.

        Returns:
            List of resource record sets.
        """
        try:
            response = self.client.list_resource_record_sets(
                HostedZoneId=hosted_zone_id
            )
            records = response.get("ResourceRecordSets", [])
            print(f"Found {len(records)} records")
            return records
        except ClientError as e:
            print(f"❌ Error listing records: {e}")
            return []

    def delete_dns_records(
        self, hosted_zone_id: str, domain: str, services: List[str]
    ) -> None:
        """
        Delete DNS A records for the given services.

        Args:
            hosted_zone_id: ID of the Route 53 hosted zone.
            domain: Domain name (e.g., 'example.com').
            services: List of service names (e.g., ['api', 'web']).
        """
        changes = []
        for service in services:
            hostname = f"{service}.{domain}"
            changes.append(
                {
                    "Action": "DELETE",
                    "ResourceRecordSet": {"Name": hostname, "Type": "A"},
                }
            )
            print(f"🗑️ Deleting DNS: {hostname}")

        try:
            response = self.client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id, ChangeBatch={"Changes": changes}
            )
            change_id = response["ChangeInfo"]["Id"]
            print(f"✅ Deleted DNS records (Change ID: {change_id})")

        except ClientError as e:
            print(f"❌ Error deleting DNS records: {e}")
            print("⚠️  You may need to delete DNS records manually")

    def get_change_status(self, change_id: str) -> Optional[str]:
        """
        Get the status of a Route 53 change.

        Args:
            change_id: ID of the change to check.

        Returns:
            Status of the change (e.g., 'PENDING', 'INSYNC') or None if an error occurs.
        """
        try:
            response = self.client.get_change(Id=change_id)
            status = response["ChangeInfo"]["Status"]
            print(f"Change status: {status}")
            return status
        except ClientError as e:
            print(f"❌ Error getting change status: {e}")
            return None
