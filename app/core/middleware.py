"""
Middleware for the Employee Directory API.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.hybrid_rate_limiter import hybrid_rate_limiter

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with Redis support and graceful fallback.

    Features:
    - Uses hybrid rate limiter (Redis + in-memory fallback)
    - Organization-aware rate limiting
    - Performance monitoring
    - Graceful error handling
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Apply rate limiting to incoming requests.
        """
        start_time = time.time()

        try:
            # Skip rate limiting for health checks and docs
            if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
                response = await call_next(request)
                return response

            # Apply rate limiting using hybrid rate limiter
            await hybrid_rate_limiter.check_rate_limit(request)

            # Process request
            response = await call_next(request)

            # Add performance headers
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)

            # Add rate limiting info to response headers
            rate_info = await hybrid_rate_limiter.get_rate_limit_info(request)
            response.headers["X-RateLimit-Limit"] = str(rate_info["rate_limit"])
            response.headers["X-RateLimit-Window"] = str(rate_info["window_size"])
            response.headers["X-RateLimit-Backend"] = rate_info["backend"]

            if rate_info["backend"] == "redis" and "remaining_requests" in rate_info:
                response.headers["X-RateLimit-Remaining"] = str(
                    rate_info["remaining_requests"]
                )
            elif rate_info["backend"] == "memory" and "current_tokens" in rate_info:
                response.headers["X-RateLimit-Remaining"] = str(
                    rate_info["current_tokens"]
                )

            return response

        except Exception as e:
            # Rate limit exceeded or other errors are handled by the rate limiter
            # This catch is for unexpected middleware errors
            if hasattr(e, "status_code") and e.status_code == 429:
                # Re-raise rate limit exceptions
                raise e

            logger.error(f"Rate limit middleware error: {e}")

            # Continue processing if middleware fails (graceful degradation)
            response = await call_next(request)
            return response


class OrganizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and set organization context.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Extract organization ID from request and set in request state.
        """
        try:
            # Extract organization ID from header or default
            organization_id = request.headers.get("organization-id", "default")

            # Set in request state for use by other components
            request.state.organization_id = organization_id

            # Process request
            response = await call_next(request)

            # Add organization info to response headers
            response.headers["X-Organization-ID"] = organization_id

            return response

        except Exception as e:
            logger.error(f"Organization middleware error: {e}")

            # Set default organization and continue
            request.state.organization_id = "default"
            response = await call_next(request)
            return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Request/response logging middleware.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response information.
        """
        start_time = time.time()

        # Log request
        client_ip = request.client.host if request.client else "unknown"
        organization_id = getattr(request.state, "organization_id", "unknown")

        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} (org: {organization_id})"
        )

        try:
            # Process request
            response = await call_next(request)

            # Log response
            process_time = time.time() - start_time
            logger.info(
                f"Response: {response.status_code} "
                f"in {process_time:.3f}s "
                f"for {request.method} {request.url.path}"
            )

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {str(e)} "
                f"in {process_time:.3f}s "
                f"for {request.method} {request.url.path}"
            )
            raise
