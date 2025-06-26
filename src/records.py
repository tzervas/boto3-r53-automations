from abc import ABC, abstractmethod
<<<<<<< feature/production-ready-improvements
from typing import Any, Dict, List, Optional, Type, TypedDict
=======
from typing import Optional, List, Dict, Type, TypedDict, Any
>>>>>>> main


# AliasTarget TypedDict for Route 53 alias records
class AliasTarget(TypedDict):
    HostedZoneId: str
    DNSName: str
    EvaluateTargetHealth: bool


# Base class for all DNS records
class DnsRecord(ABC):
    """Abstract base class for all DNS record types."""

    def __init__(self, name: str, ttl: int = 300):
        """
        Initialize a DNS record.

        Args:
            name: The name of the record (e.g., 'example.com.').
            ttl: Time to live in seconds (default: 300).
        """
        self.name = name
        self.ttl = ttl

    @abstractmethod
    def get_record_set(self) -> dict:
        """
        Return the record in Route 53 API format.

        Returns:
            A dictionary representing the resource record set.
        """
        pass


# A Record class
class ARecord(DnsRecord):
    """Class for A records, supporting both standard and alias records."""

    def __init__(
        self,
        name: str,
        ttl: int = 300,
        values: Optional[List[str]] = None,
        alias_target: Optional[AliasTarget] = None,
    ):
        """
        Initialize an A record.

        Args:
            name: The name of the record.
            ttl: Time to live in seconds (default: 300).
            values: List of IPv4 addresses (for standard A records).
            alias_target: Dictionary with alias details (for alias A records).
        """
        super().__init__(name, ttl)
        if values and alias_target:
            raise ValueError(
                "Cannot specify both values and alias_target for A record."
            )
        if not values and not alias_target:
            raise ValueError("Must specify either values or alias_target for A record.")
        self.values = values
        self.alias_target = alias_target

    def get_record_set(self) -> dict[str, Any]:
        """Return the A record in Route 53 API format."""
        record_set: dict[str, Any] = {
            "Name": self.name,
            "Type": "A",
        }
        if self.alias_target:
            record_set["AliasTarget"] = dict(self.alias_target)
        else:
            record_set["TTL"] = self.ttl
            record_set["ResourceRecords"] = [
                {"Value": ip.strip()} for ip in (self.values or [])
            ]
        return record_set


# CNAME Record class
class CNAMERecord(DnsRecord):
    """Class for CNAME records."""

    def __init__(self, name: str, ttl: int = 300, values: Optional[List[str]] = None):
        """
        Initialize a CNAME record.

        Args:
            name: The name of the record.
            ttl: Time to live in seconds (default: 300).
            values: List containing a single canonical name.
        """
        super().__init__(name, ttl)
        if not values:
            raise ValueError("CNAME record requires a value.")
        if len(values) != 1:
            raise ValueError("CNAME record can only have one value.")
        self.values = values

    def get_record_set(self) -> dict:
        """Return the CNAME record in Route 53 API format."""
        return {
            "Name": self.name,
            "Type": "CNAME",
            "TTL": self.ttl,
            "ResourceRecords": [{"Value": self.values[0].strip()}],
        }


# MX Record class
class MXRecord(DnsRecord):
    """Class for MX records."""

    def __init__(self, name: str, ttl: int = 300, values: Optional[List[str]] = None):
        """
        Initialize an MX record.

        Args:
            name: The name of the record.
            ttl: Time to live in seconds (default: 300).
<<<<<<< feature/production-ready-improvements
            values: List of strings in the format 'preference mail_server'
                   (e.g., '10 mail.example.com').
=======
            values: List of strings in the format 'preference mail_server' (e.g., '10 mail.example.com').
>>>>>>> main
        """
        super().__init__(name, ttl)
        if not values:
            raise ValueError("MX record requires at least one value.")
        self.values = values

    def get_record_set(self) -> dict:
        """Return the MX record in Route 53 API format."""
        resource_records = [{"Value": value.strip()} for value in self.values]
        return {
            "Name": self.name,
            "Type": "MX",
            "TTL": self.ttl,
            "ResourceRecords": resource_records,
        }


# TXT Record class
class TXTRecord(DnsRecord):
    """Class for TXT records."""

    def __init__(self, name: str, ttl: int = 300, values: Optional[List[str]] = None):
        """
        Initialize a TXT record.

        Args:
            name: The name of the record.
            ttl: Time to live in seconds (default: 300).
            values: List of text strings.
        """
        super().__init__(name, ttl)
        if not values:
            raise ValueError("TXT record requires at least one value.")
        self.values = values

    def get_record_set(self) -> dict:
        """Return the TXT record in Route 53 API format."""
        resource_records = [
            (
                {"Value": f'"{value.strip()}"'}
                if not (value.startswith('"') and value.endswith('"'))
                else {"Value": value.strip()}
            )
            for value in self.values
        ]
        return {
            "Name": self.name,
            "Type": "TXT",
            "TTL": self.ttl,
            "ResourceRecords": resource_records,
        }


# AAAA Record class
class AAAARecord(DnsRecord):
    """Class for AAAA records, supporting both standard and alias records."""

    def __init__(
        self,
        name: str,
        ttl: int = 300,
        values: Optional[List[str]] = None,
        alias_target: Optional[AliasTarget] = None,
    ):
        """
        Initialize an AAAA record.

        Args:
            name: The name of the record.
            ttl: Time to live in seconds (default: 300).
            values: List of IPv6 addresses (for standard AAAA records).
            alias_target: Dictionary with alias details (for alias AAAA records).
        """
        super().__init__(name, ttl)
        if values and alias_target:
            raise ValueError(
                "Cannot specify both values and alias_target for AAAA record."
            )
        if not values and not alias_target:
            raise ValueError(
                "Must specify either values or alias_target for AAAA record."
            )
        self.values = values
        self.alias_target = alias_target

    def get_record_set(self) -> dict[str, Any]:
        """Return the AAAA record in Route 53 API format."""
        record_set: dict[str, Any] = {
            "Name": self.name,
            "Type": "AAAA",
        }
        if self.alias_target:
            record_set["AliasTarget"] = dict(self.alias_target)
        else:
            record_set["TTL"] = self.ttl
            record_set["ResourceRecords"] = [
                {"Value": ip.strip()} for ip in (self.values or [])
            ]
        return record_set


# Mapping of record types to their classes
RECORD_TYPES: Dict[str, Type[DnsRecord]] = {
    "A": ARecord,
    "CNAME": CNAMERecord,
    "MX": MXRecord,
    "TXT": TXTRecord,
    "AAAA": AAAARecord,
}


# Factory function to create record instances
def create_record(record_type: str, **kwargs) -> DnsRecord:
    """
    Create a DNS record instance based on the record type.

    Args:
        record_type: The type of DNS record (e.g., 'A', 'CNAME').
        **kwargs: Additional arguments specific to the record type.

    Returns:
        An instance of the appropriate DnsRecord subclass.

    Raises:
        ValueError: If the record type is unknown.
    """
    record_type = record_type.upper()
    if record_type not in RECORD_TYPES:
        raise ValueError(f"Unknown record type: {record_type}")
    record_class = RECORD_TYPES[record_type]
    return record_class(**kwargs)
