from typing import Any, cast

import boto3
from botocore.exceptions import ClientError


def update_record(
    hosted_zone_id: str, record_name: str, new_value: str, record_type: str = "A"
) -> None:
    """Update a DNS record in a specified hosted zone."""
    session = boto3.Session()
    client = session.client("route53")

    try:
        response = client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": cast(
                            Any,
                            {
                                "Name": record_name,
                                "Type": record_type,
                                "TTL": 300,  # Set to 300 seconds
                                "ResourceRecords": [{"Value": new_value}],
                            },
                        ),
                    }
                ]
            },
        )
        change_id = response["ChangeInfo"]["Id"]
        print(f"✅ Updated DNS record (Change ID: {change_id})")

    except ClientError as e:
        print(f"❌ Error updating DNS record: {e}")
        print("⚠️  You may need to update the DNS record manually")
