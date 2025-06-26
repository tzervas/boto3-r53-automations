from typing import Any

import boto3

from .utils.error_handling import Route53Error, handle_aws_errors
from .utils.logging import get_logger


class Route53Client:
    """Manages a boto3 Route 53 client."""

    def __init__(self, session: boto3.Session):
        """
        Initialize a Route 53 client.

        Args:
            session: A boto3 session object.
        """
        self.logger = get_logger(__name__)

        try:
            self.client = session.client("route53")
            self.logger.info("Initialized Route 53 client")
        except Exception as e:
            self.logger.error(f"Failed to initialize Route 53 client: {e}")
            raise Route53Error(f"Failed to create Route 53 client: {e}")

    @handle_aws_errors(logger=get_logger(__name__))
    def get_client(self) -> Any:
        """Return the Route 53 client."""
        return self.client

    def get_client_info(self) -> dict:
        """
        Get client information for debugging.

        Returns:
            Dictionary with client information
        """
        try:
            return {
                "service": "route53",
                "region": self.client.meta.region_name,
                "endpoint_url": self.client.meta.endpoint_url,
            }
        except Exception as e:
            self.logger.warning(f"Could not retrieve client info: {e}")
            return {"status": "Error retrieving client info"}
