<<<<<<< feature/production-ready-improvements
from typing import Any, Dict, List

from botocore.exceptions import ClientError


def list_hosted_zones(client: Any) -> List[Dict[str, Any]]:
    """List all hosted zones."""
    try:
        response = client.list_hosted_zones()
=======
import boto3
from botocore.exceptions import ClientError
from typing import List
from src.session_manager import SessionManager
from src.route53_client import Route53Client
from src.route53_operations import Route53Operations


def list_hosted_zones(self) -> List[dict]:
    """List all hosted zones."""
    try:
        response = self.client.list_hosted_zones()
>>>>>>> main
        zones = response.get("HostedZones", [])
        print(f"Found {len(zones)} hosted zones")
        return zones
    except ClientError as e:
        print(f"❌ Error listing hosted zones: {e}")
        return []
