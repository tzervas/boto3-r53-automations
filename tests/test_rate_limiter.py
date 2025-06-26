"""Tests for rate limiting utilities."""

import time
from unittest.mock import MagicMock, patch

import pytest

from src.utils.rate_limiter import RateLimiter, rate_limit


class TestRateLimiter:
    """Test base RateLimiter class."""

    def test_base_rate_limiter(self):
        """Test base rate limiter interface."""
        limiter = RateLimiter()

        # Abstract methods should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            limiter.wait_for_token()

        with pytest.raises(NotImplementedError):
            limiter.reset()


class RateLimiterTest:
    """Tests for RateLimiter class."""

    def test_create_rate_limiter(self):
        """Test creation of a rate limiter."""
        limiter = RateLimiter(max_calls=5, time_window=1.0)
        assert limiter.max_calls == 5
        assert limiter.time_window == 1.0
        assert limiter.bucket_size == 5


class TestRateLimitDecorator:
    """Test rate_limit decorator."""

    def test_rate_limit_success(self):
        """Test successful function execution with rate limiting."""
        limiter = RateLimiter(max_calls=100)  # High rate for testing

        @rate_limit(limiter)
        def test_function():
            return "success"

        assert test_function() == "success"

    def test_rate_limit_multiple_calls(self):
        """Test multiple function calls with rate limiting."""
        limiter = RateLimiter(max_calls=5)

        @rate_limit(limiter)
        def test_function():
            return time.time()

        # First call should be immediate
        start_time = time.time()
        first_call = test_function()
        assert first_call - start_time < 0.1

        # Second call should be rate limited
        second_call = test_function()
        assert second_call - first_call >= 0.15  # Should wait ~0.2s (1/rate)

    def test_rate_limit_exception_handling(self):
        """Test rate limiting with function that raises exception."""
        limiter = RateLimiter(max_calls=1)

        @rate_limit(limiter)
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()

    def test_rate_limit_with_args(self):
        """Test rate limiting with function arguments."""
        limiter = RateLimiter(max_calls=1)

        @rate_limit(limiter)
        def function_with_args(a, b, c=None):
            return a + b + (c or 0)

        assert function_with_args(1, 2) == 3
        assert function_with_args(1, 2, 3) == 6

    def test_rate_limit_burst_handling(self):
        """Test burst handling in rate limiter."""
        limiter = RateLimiter(
            max_calls=2, time_window=1.0
        )  # Simulate burst with high rate

        @rate_limit(limiter)
        def test_function():
            return time.time()

        # First three calls should be immediate (within burst)
        times = []
        start = time.time()

        for _ in range(3):
            times.append(test_function())

        # All three should complete quickly
        assert times[-1] - start < 0.1

        # Fourth call should be rate limited
        last_time = test_function()
        assert last_time - times[-1] >= 0.45  # Should wait ~0.5s (1/rate)
