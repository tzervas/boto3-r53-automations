<<<<<<< feature/production-ready-improvements
from src.route53_client import Route53Client
from src.route53_operations import Route53Operations
from src.session_manager import SessionManager
=======
from src.session_manager import SessionManager
from src.route53_client import Route53Client
from src.route53_operations import Route53Operations
>>>>>>> main


def create_dns_record(
    profile_name: str,
    hosted_zone_id: str,
    domain: str,
    record_type: str,
    record_value: str,
    ttl: int = 300,
) -> None:
    """Create a DNS record in a specified hosted zone with dynamic record type and value."""
    session_manager = SessionManager(profile_name=profile_name)
    session = session_manager.get_session()

    route53_client = Route53Client(session=session).get_client()
    operations = Route53Operations(route53_client)

    operations.create_dns_record(
        hosted_zone_id=hosted_zone_id,
        domain=domain,
        load_balancer_ip=record_value,
        services=[],
    )
    print(f"✅ Created DNS record: {domain} ({record_type}) → {record_value}")
