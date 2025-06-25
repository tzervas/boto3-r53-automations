import boto3
from typing import Optional


class SessionManager:
    """Manages a boto3 session for AWS interactions."""

    def __init__(
        self, profile_name: Optional[str] = None, region_name: str = "us-east-1"
    ):
        """
        Initialize a boto3 session.

        Args:
            profile_name: AWS profile name to use, if specified.
            region_name: AWS region to use (default: 'us-east-1').
        """
        self.session = boto3.Session(profile_name=profile_name, region_name=region_name)

    def get_session(self) -> boto3.Session:
        """Return the boto3 session object."""
        return self.session
