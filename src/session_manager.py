<<<<<<< feature/production-ready-improvements
from typing import Optional

import boto3

from .utils.error_handling import Route53Error, handle_aws_errors
from .utils.logging import get_logger
=======
import boto3
from typing import Optional
>>>>>>> main


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
<<<<<<< feature/production-ready-improvements
        self.logger = get_logger(__name__)
        self.profile_name = profile_name
        self.region_name = region_name

        try:
            self.session = boto3.Session(
                profile_name=profile_name, region_name=region_name
            )
            self.logger.info(
                f"Initialized AWS session with profile='{profile_name}' "
                f"region='{region_name}'"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize AWS session: {e}")
            raise Route53Error(f"Failed to create AWS session: {e}")

    @handle_aws_errors(logger=get_logger(__name__))
    def get_session(self) -> boto3.Session:
        """Return the boto3 session object."""
        return self.session

    def get_credentials(self) -> dict:
        """
        Get current session credentials (for debugging/validation).

        Returns:
            Dictionary with credential information (without secrets)
        """
        try:
            credentials = self.session.get_credentials()
            if credentials:
                return {
                    "access_key_id": credentials.access_key[:8] + "...",
                    "region": self.region_name,
                    "profile": self.profile_name,
                }
            else:
                return {"status": "No credentials found"}
        except Exception as e:
            self.logger.warning(f"Could not retrieve credential info: {e}")
            return {"status": "Error retrieving credentials"}
=======
        self.session = boto3.Session(profile_name=profile_name, region_name=region_name)

    def get_session(self) -> boto3.Session:
        """Return the boto3 session object."""
        return self.session
>>>>>>> main
