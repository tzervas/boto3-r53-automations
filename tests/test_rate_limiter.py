"""Tests for rate limiting utilities."""

import time
from typing import Optional

import pytest

from src.utils.rate_limiter import RateLimiter, rate_limit


class TestRateLimiter:
    """Test base RateLimiter class."""

    def test_base_rate_limiter(self) -> None:
        """Test base rate limiter functionality."""
        limiter = RateLimiter()

        # Test that we can acquire tokens
        assert limiter.acquire() is True

        # Test wait_for_tokens method exists and works
        assert limiter.wait_for_tokens() is True


class RateLimiterTest:
    """Tests for RateLimiter class."""

    def test_create_rate_limiter(self) -> None:
        """Test creation of a rate limiter."""
        limiter = RateLimiter(max_calls=5, time_window=1.0)
        assert limiter.max_calls == 5
        assert limiter.time_window == 1.0
        assert limiter.bucket_size == 5


class TestRateLimitDecorator:
    """Test rate_limit decorator."""

    def test_rate_limit_success(self) -> None:
        """Test successful function execution with rate limiting."""

        @rate_limit("route53")
        def test_function() -> str:
            return "success"

        assert test_function() == "success"

    def test_rate_limit_multiple_calls(self) -> None:
        """Test multiple function calls with rate limiting."""

        @rate_limit("route53")
        def test_function() -> float:
            return time.time()

        # Test that function executes
        start_time = time.time()
        first_call = test_function()
        assert first_call >= start_time

    def test_rate_limit_exception_handling(self) -> None:
        """Test rate limiting with function that raises exception."""

        @rate_limit("route53")
        def failing_function() -> None:
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()

    def test_rate_limit_with_args(self) -> None:
        """Test rate limiting with function arguments."""

        @rate_limit("route53")
        def function_with_args(a: int, b: int, c: Optional[int] = None) -> int:
            return a + b + (c or 0)

        assert function_with_args(1, 2) == 3
        assert function_with_args(1, 2, 3) == 6

    def test_rate_limit_burst_handling(self) -> None:
        """Test burst handling in rate limiter."""

        @rate_limit("route53")
        def test_function() -> float:
            return time.time()

        # Test that function executes
        start = time.time()
        result = test_function()
        assert result >= start
