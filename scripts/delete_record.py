from typing import Any, cast

import boto3
from botocore.exceptions import ClientError


def delete_record(hosted_zone_id: str, record_name: str, record_type: str) -> None:
    """Delete a DNS record from a specified hosted zone."""
    session = boto3.Session()
    client = session.client("route53")

    try:
        response = client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "DELETE",
                        "ResourceRecordSet": cast(
                            Any,
                            {
                                "Name": record_name,
                                "Type": record_type,
                                "TTL": 300,  # Set to 300 seconds
                            },
                        ),
                    }
                ]
            },
        )
        change_id = response["ChangeInfo"]["Id"]
        print(f"✅ Deleted DNS record (Change ID: {change_id})")

    except ClientError as e:
        print(f"❌ Error deleting DNS record: {e}")
        print("⚠️  You may need to delete the DNS record manually")
