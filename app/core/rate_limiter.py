import time
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException, status

from app.core.config import settings


class RateLimiter:
    """
    A simple in-memory rate limiter that uses a token bucket algorithm.
    
    For production use, consider using Redis or another distributed cache
    to handle rate limiting across multiple instances.
    """
    
    def __init__(self, rate_limit: int = 100, window_size: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            rate_limit: Maximum number of requests allowed in the window
            window_size: Time window in seconds
        """
        self.rate_limit = rate_limit
        self.window_size = window_size
        self.tokens: Dict[str, Tuple[int, float]] = {}  # {client_id: (tokens, last_refill_time)}
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get a unique identifier for the client.
        
        In production, you might want to use a combination of IP address,
        user agent, and other factors to identify clients more accurately.
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Include user ID if authenticated
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"{client_ip}:{user_id}"
        
        return client_ip
    
    def _refill_tokens(self, client_id: str) -> None:
        """
        Refill tokens based on time elapsed since last refill.
        """
        if client_id not in self.tokens:
            self.tokens[client_id] = (self.rate_limit, time.time())
            return
        
        tokens, last_refill_time = self.tokens[client_id]
        now = time.time()
        time_passed = now - last_refill_time
        
        # Calculate how many tokens to add based on time passed
        new_tokens = int(time_passed * (self.rate_limit / self.window_size))
        
        if new_tokens > 0:
            tokens = min(tokens + new_tokens, self.rate_limit)
            self.tokens[client_id] = (tokens, now)
    
    def check_rate_limit(self, request: Request) -> None:
        """
        Check if the request exceeds the rate limit.
        
        Raises:
            HTTPException: If the rate limit is exceeded
        """
        client_id = self._get_client_id(request)
        self._refill_tokens(client_id)
        
        tokens, _ = self.tokens[client_id]
        
        if tokens <= 0:
            # Calculate retry-after time
            retry_after = int(self.window_size / self.rate_limit)
            headers = {"Retry-After": str(retry_after)}
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers=headers,
            )
        
        # Consume one token
        self.tokens[client_id] = (tokens - 1, self.tokens[client_id][1])


# Create a global rate limiter instance
rate_limiter = RateLimiter(
    rate_limit=getattr(settings, "RATE_LIMIT", 100),  # Default to 100 if not set
    window_size=getattr(settings, "RATE_LIMIT_WINDOW_SIZE", 60)  # Default to 60 seconds if not set
)
