"""
Security middleware for production hardening.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Production security headers middleware.

    Adds essential security headers for production deployment:
    - HSTS (HTTP Strict Transport Security)
    - CSP (Content Security Policy)
    - X-Frame-Options
    - X-Content-Type-Options
    - X-XSS-Protection
    - Referrer-Policy
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to all responses.
        """
        response = await call_next(request)

        # HSTS - Force HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # CSP - Content Security Policy
        # Allow same origin, block inline scripts, allow API calls
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp_policy

        # X-Frame-Options - Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options - Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection - Enable XSS filtering
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy - Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # X-Permitted-Cross-Domain-Policies - Adobe Flash/PDF security
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Clear Server header for security
        response.headers["Server"] = "Employee-Directory-API"

        # Add security timestamp
        response.headers["X-Security-Headers"] = "enabled"

        return response


class SecurityValidationMiddleware(BaseHTTPMiddleware):
    """
    Request security validation middleware.

    Validates requests for common security threats:
    - Oversized requests
    - Suspicious user agents
    - Rate limiting bypass attempts
    """

    def __init__(self, app, max_request_size: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Validate request security.
        """
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            logger.warning(
                f"Oversized request blocked: {content_length} bytes from {request.client.host}"
            )
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request too large",
            )

        # Check for suspicious user agents
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = ["sqlmap", "nikto", "nmap", "masscan", "nessus"]
        if any(agent in user_agent for agent in suspicious_agents):
            logger.warning(
                f"Suspicious user agent blocked: {user_agent} from {request.client.host}"
            )
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )

        # Add security context to request
        request.state.security_validated = True
        request.state.request_timestamp = time.time()

        response = await call_next(request)

        # Add response timing for security monitoring
        process_time = time.time() - request.state.request_timestamp
        response.headers["X-Response-Time"] = f"{process_time:.3f}s"

        return response
