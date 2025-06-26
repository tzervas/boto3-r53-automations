import logging
import threading
import time
from functools import wraps
from typing import Callable, Optional


class RateLimiter:
    """
    Token bucket rate limiter for API calls.

    This implements a token bucket algorithm that allows bursts up to the bucket size
    while maintaining a steady rate over time.
    """

    def __init__(
        self,
        max_calls: int = 5,
        time_window: float = 1.0,
        bucket_size: Optional[int] = None,
    ):
        """
        Initialize the rate limiter.

        Args:
            max_calls: Maximum number of calls allowed per time window
            time_window: Time window in seconds
            bucket_size: Maximum tokens in bucket (defaults to max_calls)
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.bucket_size = bucket_size or max_calls
        self.tokens = self.bucket_size
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens from the bucket.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens were acquired, False otherwise
        """
        with self.lock:
            now = time.time()

            # Refill tokens based on elapsed time
            elapsed = now - self.last_refill
            tokens_to_add = elapsed * (self.max_calls / self.time_window)
            self.tokens = min(self.bucket_size, self.tokens + tokens_to_add)
            self.last_refill = now

            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_for_tokens(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Wait until tokens are available or timeout is reached.

        Args:
            tokens: Number of tokens needed
            timeout: Maximum time to wait in seconds

        Returns:
            True if tokens were acquired, False if timeout
        """
        start_time = time.time()

        while True:
            if self.acquire(tokens):
                return True

            if timeout and (time.time() - start_time) >= timeout:
                return False

            # Calculate sleep time until next token is available
            with self.lock:
                time_per_token = self.time_window / self.max_calls
                tokens_needed = tokens - self.tokens
                sleep_time = min(0.1, tokens_needed * time_per_token)

            time.sleep(sleep_time)


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts based on response patterns.

    This limiter starts with conservative limits and adapts based on
    success/failure patterns and response times.
    """

    def __init__(
        self,
        initial_rate: float = 2.0,
        min_rate: float = 0.5,
        max_rate: float = 10.0,
        backoff_factor: float = 0.5,
        recovery_factor: float = 1.1,
    ):
        """
        Initialize adaptive rate limiter.

        Args:
            initial_rate: Initial requests per second
            min_rate: Minimum requests per second
            max_rate: Maximum requests per second
            backoff_factor: Factor to reduce rate on errors
            recovery_factor: Factor to increase rate on success
        """
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.backoff_factor = backoff_factor
        self.recovery_factor = recovery_factor
        self.last_call = 0.0
        self.lock = threading.Lock()
        self.success_count = 0
        self.error_count = 0

    def wait_and_acquire(self) -> None:
        """Wait for the appropriate interval before allowing the next call."""
        with self.lock:
            now = time.time()
            time_since_last = now - self.last_call
            required_interval = 1.0 / self.current_rate

            if time_since_last < required_interval:
                sleep_time = required_interval - time_since_last
                time.sleep(sleep_time)

            self.last_call = time.time()

    def report_success(self) -> None:
        """Report a successful operation to potentially increase rate."""
        with self.lock:
            self.success_count += 1

            # Increase rate after consecutive successes
            if self.success_count % 5 == 0:  # Every 5 successes
                self.current_rate = min(
                    self.max_rate, self.current_rate * self.recovery_factor
                )
                self.error_count = 0  # Reset error count

    def report_error(self, is_throttle_error: bool = False) -> None:
        """Report an error to potentially decrease rate."""
        with self.lock:
            self.error_count += 1
            self.success_count = 0  # Reset success count

            # More aggressive backoff for throttle errors
            factor = 0.25 if is_throttle_error else self.backoff_factor
            self.current_rate = max(self.min_rate, self.current_rate * factor)


# Global rate limiters for different AWS services
_rate_limiters = {
    "route53": RateLimiter(max_calls=5, time_window=1.0),  # AWS Route53 default limits
    "route53_adaptive": AdaptiveRateLimiter(initial_rate=2.0),
}


def rate_limit(
    limiter_name: str = "route53",
    adaptive: bool = False,
    logger: Optional[logging.Logger] = None,
) -> Callable:
    """
    Decorator to apply rate limiting to functions.

    Args:
        limiter_name: Name of the rate limiter to use
        adaptive: Whether to use adaptive rate limiting
        logger: Logger for rate limiting events

    Returns:
        Decorated function with rate limiting
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter_key = f"{limiter_name}_adaptive" if adaptive else limiter_name
            limiter = _rate_limiters.get(limiter_key)

            if not limiter:
                if logger:
                    logger.warning(
                        f"Rate limiter '{limiter_key}' not found, "
                        "proceeding without rate limiting"
                    )
                return func(*args, **kwargs)

            # Apply rate limiting
            if isinstance(limiter, AdaptiveRateLimiter):
                limiter.wait_and_acquire()

                try:
                    result = func(*args, **kwargs)
                    limiter.report_success()
                    return result
                except Exception as e:
                    # Check if it's a throttle error
                    is_throttle = (
                        hasattr(e, "error_code") and e.error_code == "Throttling"
                    ) or "throttle" in str(e).lower()

                    limiter.report_error(is_throttle_error=is_throttle)

                    if logger and is_throttle:
                        logger.warning(
                            f"Throttling detected, reducing rate to "
                            f"{limiter.current_rate:.2f} req/s"
                        )

                    raise

            else:  # Regular RateLimiter
                if not limiter.wait_for_tokens(timeout=30.0):
                    if logger:
                        logger.error("Rate limiter timeout - request rejected")
                    raise TimeoutError("Rate limiter timeout")

                return func(*args, **kwargs)

        return wrapper

    return decorator


def get_rate_limiter(name: str) -> Optional[RateLimiter]:
    """
    Get a rate limiter by name.

    Args:
        name: Name of the rate limiter

    Returns:
        Rate limiter instance or None if not found
    """
    return _rate_limiters.get(name)


def set_rate_limiter(name: str, limiter: RateLimiter) -> None:
    """
    Set or update a rate limiter.

    Args:
        name: Name of the rate limiter
        limiter: Rate limiter instance
    """
    _rate_limiters[name] = limiter
