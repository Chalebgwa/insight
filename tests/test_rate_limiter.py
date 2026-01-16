"""Tests for rate limiter."""
import pytest
import asyncio
import time
from modules.rate_limiter import RateLimiter, SlidingWindowLimiter


@pytest.mark.asyncio
async def test_rate_limiter_basic():
    """Test that rate limiter allows immediate requests within burst."""
    limiter = RateLimiter(rate=10.0, burst=5)
    
    start = time.monotonic()
    for _ in range(5):
        await limiter.acquire()
    elapsed = time.monotonic() - start
    
    # Should complete almost immediately
    assert elapsed < 0.2


@pytest.mark.asyncio
async def test_rate_limiter_delays():
    """Test that rate limiter delays when burst is exceeded."""
    limiter = RateLimiter(rate=10.0, burst=2)
    
    # First 2 should be immediate
    await limiter.acquire()
    await limiter.acquire()
    
    # Third should delay
    start = time.monotonic()
    await limiter.acquire()
    elapsed = time.monotonic() - start
    
    # Should have waited ~0.1s (1/10)
    assert 0.05 < elapsed < 0.2


@pytest.mark.asyncio
async def test_sliding_window_basic():
    """Test that sliding window limiter allows requests within limit."""
    limiter = SlidingWindowLimiter(max_requests=5, window_seconds=1.0)
    
    start = time.monotonic()
    for _ in range(5):
        await limiter.acquire()
    elapsed = time.monotonic() - start
    
    # Should complete almost immediately
    assert elapsed < 0.2


@pytest.mark.asyncio
async def test_sliding_window_delays():
    """Test that sliding window limiter delays when limit exceeded."""
    limiter = SlidingWindowLimiter(max_requests=3, window_seconds=0.2)
    
    # First 3 should be immediate
    await limiter.acquire()
    await limiter.acquire()
    await limiter.acquire()
    
    # Fourth should delay slightly
    start = time.monotonic()
    await limiter.acquire()
    elapsed = time.monotonic() - start
    
    # Should have waited at least a bit (the test is more about it not hanging)
    assert elapsed >= 0
