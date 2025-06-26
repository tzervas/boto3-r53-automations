#!/usr/bin/env python3
"""
Command Line Interface for boto3-r53-automations.

This provides a user-friendly CLI for Route 53 DNS management operations.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from src.route53_client import Route53Client
from src.route53_operations import Route53Operations
from src.session_manager import SessionManager
from src.utils.error_handling import Route53Error
from src.utils.logging import setup_logger


def setup_cli_logging(verbose: bool = False) -> None:
    """Set up logging for CLI operations."""
    level = "DEBUG" if verbose else "INFO"
    log_file = Path("logs/route53-cli.log")
    setup_logger("cli", level=level, log_file=log_file)


def create_operations(
    profile: Optional[str] = None, region: str = "us-east-1"
) -> Route53Operations:
    """Create and return a Route53Operations instance."""
    session_manager = SessionManager(profile_name=profile, region_name=region)
    session = session_manager.get_session()

    route53_client = Route53Client(session)
    client = route53_client.get_client()

    return Route53Operations(client)


def cmd_list_records(args: argparse.Namespace) -> None:
    """List records in a hosted zone."""
    try:
        operations = create_operations(args.profile, args.region)
        records = operations.list_records(args.zone_id)

        print(f"Found {len(records)} records in zone {args.zone_id}:")
        for record in records:
            record_type = record.get("Type", "Unknown")
            name = record.get("Name", "Unknown")

            if "ResourceRecords" in record:
                values = [rr["Value"] for rr in record["ResourceRecords"]]
                value_str = ", ".join(values)
            elif "AliasTarget" in record:
                value_str = (
                    f"ALIAS -> {record['AliasTarget'].get('DNSName', 'Unknown')}"
                )
            else:
                value_str = "No value found"

            print(f"  {record_type:<6} {name:<40} {value_str}")

    except Route53Error as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_create_record(args: argparse.Namespace) -> None:
    """Create DNS records."""
    try:
        operations = create_operations(args.profile, args.region)
        change_id = operations.create_dns_record(
            hosted_zone_id=args.zone_id,
            domain=args.domain,
            load_balancer_ip=args.ip,
            services=args.services,
        )

        print("Created DNS records successfully!")
        print(f"   Zone ID: {args.zone_id}")
        print(f"   Domain: {args.domain}")
        print(f"   IP: {args.ip}")
        print(f"   Services: {', '.join(args.services)}")
        print(f"   Change ID: {change_id}")

    except Route53Error as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_delete_records(args: argparse.Namespace) -> None:
    """Delete DNS records."""
    try:
        operations = create_operations(args.profile, args.region)
        change_id = operations.delete_dns_records(
            hosted_zone_id=args.zone_id,
            domain=args.domain,
            services=args.services,
        )

        print("✅ Deleted DNS records successfully!")
        print(f"   Zone ID: {args.zone_id}")
        print(f"   Domain: {args.domain}")
        print(f"   Services: {', '.join(args.services)}")
        print(f"   Change ID: {change_id}")

    except Route53Error as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_check_change(args: argparse.Namespace) -> None:
    """Check the status of a change."""
    try:
        operations = create_operations(args.profile, args.region)
        status = operations.get_change_status(args.change_id)

        print(f"Change {args.change_id} status: {status}")

        if status == "INSYNC":
            print("✅ Change has been propagated successfully!")
        elif status == "PENDING":
            print("⏳ Change is still propagating...")
        else:
            print(f"❓ Unknown status: {status}")

    except Route53Error as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Route 53 DNS automation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list-records Z1234567890
  %(prog)s create-record Z1234567890 example.com 10.0.0.100 api web
  %(prog)s delete-records Z1234567890 example.com api web
  %(prog)s check-change /change/C123456789
        """,
    )

    parser.add_argument("--profile", help="AWS profile to use", default=None)
    parser.add_argument("--region", help="AWS region", default="us-east-1")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List records command
    list_parser = subparsers.add_parser(
        "list-records", help="List records in a hosted zone"
    )
    list_parser.add_argument("zone_id", help="Hosted zone ID")
    list_parser.set_defaults(func=cmd_list_records)

    # Create record command
    create_parser = subparsers.add_parser("create-record", help="Create DNS records")
    create_parser.add_argument("zone_id", help="Hosted zone ID")
    create_parser.add_argument("domain", help="Domain name (e.g., example.com)")
    create_parser.add_argument("ip", help="IP address for the records")
    create_parser.add_argument(
        "services", nargs="+", help="Service names (e.g., api web)"
    )
    create_parser.set_defaults(func=cmd_create_record)

    # Delete records command
    delete_parser = subparsers.add_parser("delete-records", help="Delete DNS records")
    delete_parser.add_argument("zone_id", help="Hosted zone ID")
    delete_parser.add_argument("domain", help="Domain name (e.g., example.com)")
    delete_parser.add_argument(
        "services", nargs="+", help="Service names (e.g., api web)"
    )
    delete_parser.set_defaults(func=cmd_delete_records)

    # Check change command
    check_parser = subparsers.add_parser("check-change", help="Check change status")
    check_parser.add_argument("change_id", help="Change ID to check")
    check_parser.set_defaults(func=cmd_check_change)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Set up logging
    setup_cli_logging(args.verbose)

    # Execute the command
    args.func(args)


if __name__ == "__main__":
    main()
