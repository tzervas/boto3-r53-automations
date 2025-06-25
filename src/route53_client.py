import boto3
from typing import Any


class Route53Client:
    """Manages a boto3 Route 53 client."""

    def __init__(self, session: boto3.Session):
        """
        Initialize a Route 53 client.

        Args:
            session: A boto3 session object.
        """
        self.client = session.client("route53")

    def get_client(self) -> Any:
        """Return the Route 53 client."""
        return self.client
