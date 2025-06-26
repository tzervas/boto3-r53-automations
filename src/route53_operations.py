from typing import Any, Dict, List, cast

from mypy_boto3_route53.client import Route53Client

from .utils.error_handling import (
    Route53Error,
    handle_aws_errors,
    validate_domain_name,
    validate_hosted_zone_id,
)
from .utils.logging import get_logger
from .utils.rate_limiter import rate_limit


class Route53Operations:
    """Manages Route 53 operations like creating or updating DNS records."""

    def __init__(self, route53_client: Route53Client):
        """
        Initialize Route 53 operations.

        Args:
            route53_client: A boto3 Route 53 client.
        """
        self.client = route53_client
        self.logger = get_logger(__name__)

    @rate_limit(adaptive=True)
    @handle_aws_errors(logger=get_logger(__name__))
    def create_dns_record(
        self,
        hosted_zone_id: str,
        domain: str,
        load_balancer_ip: str,
        services: List[str],
    ) -> str:
        """
        Create DNS A records pointing to an internal load balancer IP.

        Args:
            hosted_zone_id: ID of the Route 53 hosted zone.
            domain: Domain name (e.g., 'example.com').
            load_balancer_ip: IP address of the load balancer.
            services: List of service names (e.g., ['api', 'web']).

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
            self.logger.debug(f"Configuring DNS: {hostname} → {load_balancer_ip}")

        response = self.client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id, ChangeBatch={"Changes": cast(Any, changes)}
        )
        change_id = str(response["ChangeInfo"]["Id"])
        self.logger.info(f"Created DNS records successfully (Change ID: {change_id})")

        return change_id

    @rate_limit()
    @handle_aws_errors(logger=get_logger(__name__))
    def list_records(self, hosted_zone_id: str) -> List[Dict[str, Any]]:
        """
        List all records in a hosted zone.

        Args:
            hosted_zone_id: ID of the Route 53 hosted zone.

        Returns:
            List of resource record sets.

        Raises:
            Route53Error: If the operation fails.
        """
        hosted_zone_id = validate_hosted_zone_id(hosted_zone_id)
        self.logger.info(f"Listing records for hosted zone {hosted_zone_id}")

        response = self.client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
        records = response.get("ResourceRecordSets", [])
        self.logger.info(f"Found {len(records)} records in zone {hosted_zone_id}")
        return cast(List[Dict[str, Any]], records)

    @rate_limit(adaptive=True)
    @handle_aws_errors(logger=get_logger(__name__))
    def delete_dns_records(
        self, hosted_zone_id: str, domain: str, services: List[str]
    ) -> str:
        """
        Delete DNS A records for the given services.

        Args:
            hosted_zone_id: ID of the Route 53 hosted zone.
            domain: Domain name (e.g., 'example.com').
            services: List of service names (e.g., ['api', 'web']).

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

        changes = []
        for service in services:
            hostname = f"{service}.{domain}"
            changes.append(
                {
                    "Action": "DELETE",
                    "ResourceRecordSet": {"Name": hostname, "Type": "A"},
                }
            )
            self.logger.debug(f"Deleting DNS: {hostname}")

        response = self.client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id, ChangeBatch={"Changes": cast(Any, changes)}
        )
        change_id = str(response["ChangeInfo"]["Id"])
        self.logger.info(f"Deleted DNS records successfully (Change ID: {change_id})")

        return change_id

    @rate_limit()
    @handle_aws_errors(logger=get_logger(__name__))
    def get_change_status(self, change_id: str) -> str:
        """
        Get the status of a Route 53 change.

        Args:
            change_id: ID of the change to check.

        Returns:
            Status of the change (e.g., 'PENDING', 'INSYNC').

        Raises:
            Route53Error: If the operation fails.
        """
        if not change_id:
            raise Route53Error("Change ID cannot be empty")

        self.logger.debug(f"Checking status for change ID: {change_id}")

        response = self.client.get_change(Id=change_id)
        status: str = response["ChangeInfo"]["Status"]
        self.logger.debug(f"Change {change_id} status: {status}")
        return status
