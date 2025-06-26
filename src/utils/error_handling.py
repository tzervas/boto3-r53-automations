import logging
from functools import wraps
from typing import Any, Callable, Optional, Type

from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
)


class Route53Error(Exception):
    """Base exception for Route 53 operations."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code


class Route53NotFoundError(Route53Error):
    """Raised when a Route 53 resource is not found."""

    pass


class Route53ValidationError(Route53Error):
    """Raised when Route 53 operation validation fails."""

    pass


class Route53PermissionError(Route53Error):
    """Raised when Route 53 operation lacks permissions."""

    pass


class Route53ThrottleError(Route53Error):
    """Raised when Route 53 operations are being throttled."""

    pass


def handle_aws_errors(
    logger: Optional[logging.Logger] = None,
    reraise_as: Optional[Type[Route53Error]] = None,
) -> Callable:
    """
    Decorator to handle AWS/boto3 errors consistently.

    Args:
        logger: Logger instance for error logging
        reraise_as: Exception type to reraise as (defaults to Route53Error)

    Returns:
        Decorated function with error handling
    """
    if reraise_as is None:
        reraise_as = Route53Error

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "Unknown")
                error_message = e.response.get("Error", {}).get("Message", str(e))

                if logger:
                    logger.error(f"AWS ClientError [{error_code}]: {error_message}")

                # Map specific AWS errors to custom exceptions
                if error_code == "NoSuchHostedZone":
                    raise Route53NotFoundError(
                        f"Hosted zone not found: {error_message}", error_code
                    )
                elif error_code == "InvalidInput":
                    raise Route53ValidationError(
                        f"Invalid input: {error_message}", error_code
                    )
                elif error_code == "AccessDenied":
                    raise Route53PermissionError(
                        f"Access denied: {error_message}", error_code
                    )
                elif error_code == "Throttling":
                    raise Route53ThrottleError(
                        f"Request throttled: {error_message}", error_code
                    )
                else:
                    raise reraise_as(
                        f"AWS Error [{error_code}]: {error_message}", error_code
                    )

            except NoCredentialsError as e:
                if logger:
                    logger.error(f"AWS credentials not found: {e}")
                raise Route53Error(f"AWS credentials not configured: {e}")

            except PartialCredentialsError as e:
                if logger:
                    logger.error(f"Partial AWS credentials: {e}")
                raise Route53Error(f"Incomplete AWS credentials: {e}")

            except BotoCoreError as e:
                if logger:
                    logger.error(f"BotoCore error: {e}")
                raise Route53Error(f"AWS SDK error: {e}")

            except Route53Error:
                # Re-raise our custom exceptions as-is
                raise

            except Exception as e:
                if logger:
                    logger.exception(f"Unexpected error in {func.__name__}: {e}")
                raise reraise_as(f"Unexpected error: {e}")

        return wrapper

    return decorator


def safe_execute(
    func: Callable[..., Any],
    *args: Any,
    logger: Optional[logging.Logger] = None,
    default_return: Any = None,
    **kwargs: Any,
) -> Any:
    """
    Execute a function safely with error handling.

    Args:
        func: Function to execute
        *args: Positional arguments for the function
        logger: Logger instance for error logging
        default_return: Value to return on error
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if logger:
            logger.exception(f"Error executing {func.__name__}: {e}")
        return default_return


def validate_hosted_zone_id(zone_id: str) -> str:
    """
    Validate and normalize a hosted zone ID.

    Args:
        zone_id: Raw zone ID (may include '/hostedzone/' prefix)

    Returns:
        Normalized zone ID without prefix

    Raises:
        Route53ValidationError: If zone ID format is invalid
    """
    if not zone_id:
        raise Route53ValidationError("Hosted zone ID cannot be empty")

    # Remove common prefixes
    if zone_id.startswith("/hostedzone/"):
        zone_id = zone_id[12:]

    # Basic format validation (Route 53 zone IDs are alphanumeric)
    # Real AWS zone IDs are ~13-14 chars, but moto may generate different lengths
    if not zone_id.isalnum() or len(zone_id) < 8 or len(zone_id) > 32:
        raise Route53ValidationError(f"Invalid hosted zone ID format: {zone_id}")

    return zone_id


def validate_domain_name(domain: str) -> str:
    """
    Validate and normalize a domain name.

    Args:
        domain: Domain name to validate

    Returns:
        Normalized domain name

    Raises:
        Route53ValidationError: If domain name is invalid
    """
    if not domain:
        raise Route53ValidationError("Domain name cannot be empty")

    # Basic domain validation
    if len(domain) > 253:
        raise Route53ValidationError("Domain name too long (max 253 characters)")

    # Ensure domain ends with a dot for Route 53
    if not domain.endswith("."):
        domain = f"{domain}."

    return domain
