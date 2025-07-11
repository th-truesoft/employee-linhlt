from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.rate_limiter import rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for certain paths
        if not request.url.path.startswith("/api/v1/employees/search"):
            return await call_next(request)
        
        # Check rate limit
        rate_limiter.check_rate_limit(request)
        
        # Continue processing the request
        response = await call_next(request)
        return response
