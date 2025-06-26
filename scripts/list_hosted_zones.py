from typing import Any, Dict, List

from botocore.exceptions import ClientError


def list_hosted_zones(client: Any) -> List[Dict[str, Any]]:
    """List all hosted zones."""
    try:
        response = client.list_hosted_zones()
        zones: List[Dict[str, Any]] = response.get("HostedZones", [])
        print(f"Found {len(zones)} hosted zones")
        return zones
    except ClientError as e:
        print(f"❌ Error listing hosted zones: {e}")
        return []
