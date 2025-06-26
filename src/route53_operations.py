<<<<<<< feature/production-ready-improvements
from typing import List

from botocore.client import BaseClient

from .utils.error_handling import (
    Route53Error,
    handle_aws_errors,
    validate_domain_name,
    validate_hosted_zone_id,
)
from .utils.logging import get_logger
from .utils.rate_limiter import rate_limit
=======
from botocore.exceptions import ClientError
from typing import List, Optional

import records
>>>>>>> main


class Route53Operations:
    """Manages Route 53 operations like creating or updating DNS records."""

<<<<<<< feature/production-ready-improvements
=======
    from botocore.client import BaseClient

>>>>>>> main
    def __init__(self, route53_client: BaseClient):
        """
        Initialize Route 53 operations.

        Args:
            route53_client: A boto3 Route 53 client.
        """
        self.client = route53_client
<<<<<<< feature/production-ready-improvements
        self.logger = get_logger(__name__)

    @rate_limit(adaptive=True)
    @handle_aws_errors(logger=get_logger(__name__))
=======

>>>>>>> main
    def create_dns_record(
        self,
        hosted_zone_id: str,
        domain: str,
        load_balancer_ip: str,
        services: List[str],
<<<<<<< feature/production-ready-improvements
    ) -> str:
=======
    ) -> None:
>>>>>>> main
        """
        Create DNS A records pointing to an internal load balancer IP.

        Args:
            hosted_zone_id: ID of the Route 53 hosted zone.
            domain: Domain name (e.g., 'example.com').
            load_balancer_ip: IP address of the load balancer.
            services: List of service names (e.g., ['api', 'web']).
<<<<<<< feature/production-ready-improvements

        Returns:
            Change ID for tracking the operation status.

        Raises:
            Route53Error: If the operation fails.
        """
        # Validate inputs
        hosted_zone_id = validate_hosted_zone_id(hosted_zone_id)
        domain = validate_domain_name(domain)

        if not services:
            raise Route53Error("At least one service must be specified")

        self.logger.info(
            f"Creating DNS records for services {services} in zone {hosted_zone_id}"
        )

=======
        """
>>>>>>> main
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
<<<<<<< feature/production-ready-improvements
            self.logger.debug(f"Configuring DNS: {hostname} → {load_balancer_ip}")

        response = self.client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id, ChangeBatch={"Changes": changes}
        )
        change_id = response["ChangeInfo"]["Id"]
        self.logger.info(f"Created DNS records successfully (Change ID: {change_id})")

        return change_id

    @rate_limit()
    @handle_aws_errors(logger=get_logger(__name__))
=======
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

>>>>>>> main
    def list_records(self, hosted_zone_id: str) -> List[dict]:
        """
        List all records in a hosted zone.

        Args:
            hosted_zone_id: ID of the Route 53 hosted zone.

        Returns:
            List of resource record sets.
<<<<<<< feature/production-ready-improvements

        Raises:
            Route53Error: If the operation fails.
        """
        hosted_zone_id = validate_hosted_zone_id(hosted_zone_id)
        self.logger.info(f"Listing records for hosted zone {hosted_zone_id}")

        response = self.client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
        records = response.get("ResourceRecordSets", [])
        self.logger.info(f"Found {len(records)} records in zone {hosted_zone_id}")
        return records

    @rate_limit(adaptive=True)
    @handle_aws_errors(logger=get_logger(__name__))
    def delete_dns_records(
        self, hosted_zone_id: str, domain: str, services: List[str]
    ) -> str:
=======
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
>>>>>>> main
        """
        Delete DNS A records for the given services.

        Args:
            hosted_zone_id: ID of the Route 53 hosted zone.
            domain: Domain name (e.g., 'example.com').
            services: List of service names (e.g., ['api', 'web']).
<<<<<<< feature/production-ready-improvements

        Returns:
            Change ID for tracking the operation status.

        Raises:
            Route53Error: If the operation fails.
        """
        # Validate inputs
        hosted_zone_id = validate_hosted_zone_id(hosted_zone_id)
        domain = validate_domain_name(domain)

        if not services:
            raise Route53Error("At least one service must be specified")

        self.logger.info(
            f"Deleting DNS records for services {services} in zone {hosted_zone_id}"
        )

=======
        """
>>>>>>> main
        changes = []
        for service in services:
            hostname = f"{service}.{domain}"
            changes.append(
                {
                    "Action": "DELETE",
                    "ResourceRecordSet": {"Name": hostname, "Type": "A"},
                }
            )
<<<<<<< feature/production-ready-improvements
            self.logger.debug(f"Deleting DNS: {hostname}")

        response = self.client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id, ChangeBatch={"Changes": changes}
        )
        change_id = response["ChangeInfo"]["Id"]
        self.logger.info(f"Deleted DNS records successfully (Change ID: {change_id})")

        return change_id

    @rate_limit()
    @handle_aws_errors(logger=get_logger(__name__))
    def get_change_status(self, change_id: str) -> str:
=======
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
>>>>>>> main
        """
        Get the status of a Route 53 change.

        Args:
            change_id: ID of the change to check.

        Returns:
<<<<<<< feature/production-ready-improvements
            Status of the change (e.g., 'PENDING', 'INSYNC').

        Raises:
            Route53Error: If the operation fails.
        """
        if not change_id:
            raise Route53Error("Change ID cannot be empty")

        self.logger.debug(f"Checking status for change ID: {change_id}")

        response = self.client.get_change(Id=change_id)
        status = response["ChangeInfo"]["Status"]
        self.logger.debug(f"Change {change_id} status: {status}")
        return status
=======
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
>>>>>>> main
