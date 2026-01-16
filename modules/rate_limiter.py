"""Rate limiting utilities for Insight."""
import asyncio
import time
from collections import deque


class RateLimiter:
    """
    Token bucket rate limiter for controlling request rates.
    
    Args:
        rate: Maximum number of requests per second
        burst: Maximum burst size (tokens that can accumulate)
    """
    
    def __init__(self, rate: float = 10.0, burst: int = 20):
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1):
        """
        Acquire tokens from the bucket, blocking until available.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
        """
        async with self.lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_update
                
                # Refill tokens based on elapsed time
                self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
                self.last_update = now
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Wait for enough tokens to accumulate
                sleep_time = (tokens - self.tokens) / self.rate
                await asyncio.sleep(sleep_time)


class SlidingWindowLimiter:
    """
    Sliding window rate limiter for tracking requests over time.
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request, blocking if rate limit exceeded."""
        async with self.lock:
            while True:
                now = time.monotonic()
                
                # Remove old requests outside the window
                while self.requests and self.requests[0] < now - self.window_seconds:
                    self.requests.popleft()
                
                # Check if we can make a request
                if len(self.requests) < self.max_requests:
                    self.requests.append(now)
                    return
                
                # Wait until the oldest request falls outside the window
                sleep_time = self.requests[0] + self.window_seconds - now + 0.001
                await asyncio.sleep(sleep_time)
