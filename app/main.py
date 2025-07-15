"""
FastAPI application with Redis rate limiting and graceful fallback.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.core.config import settings
from app.core.middleware import (
    RateLimitMiddleware,
    OrganizationMiddleware,
    LoggingMiddleware,
)
from app.core.security_middleware import (
    SecurityHeadersMiddleware,
    SecurityValidationMiddleware,
)
from app.core.redis_client import redis_client
from app.core.hybrid_rate_limiter import hybrid_rate_limiter
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting Employee Directory API...")

    # Try to connect to Redis (graceful fallback if not available)
    if settings.REDIS_RATE_LIMITING:
        redis_connected = await redis_client.connect()
        if redis_connected:
            logger.info("✅ Redis connected - using distributed rate limiting")
        else:
            logger.info("📊 Using in-memory rate limiting (Redis not available)")
    else:
        logger.info("📊 Redis rate limiting disabled - using in-memory")

    # Initialize rate limiter
    logger.info(
        f"⚡ Rate limiting: {settings.RATE_LIMIT} requests per {settings.RATE_LIMIT_WINDOW_SIZE}s"
    )

    logger.info("✅ Application startup complete")

    yield  # Application runs here

    # Shutdown
    logger.info("🛑 Shutting down Employee Directory API...")

    # Disconnect Redis gracefully
    await redis_client.disconnect()

    logger.info("✅ Application shutdown complete")


# Create FastAPI app with enhanced configuration
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Employee Directory API with multi-tenant support and Redis rate limiting",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add middleware in the correct order (last added = first executed)
# 1. Logging middleware (for all requests)
app.add_middleware(LoggingMiddleware)

# 2. Organization middleware (extract org context)
app.add_middleware(OrganizationMiddleware)

# 3. Rate limiting middleware (after org context is set)
app.add_middleware(RateLimitMiddleware)

# 4. Security validation middleware (validate request security)
app.add_middleware(
    SecurityValidationMiddleware, max_request_size=settings.MAX_REQUEST_SIZE
)

# 5. Security headers middleware (add security headers to responses)
if settings.ENABLE_SECURITY_HEADERS:
    app.add_middleware(SecurityHeadersMiddleware)

# 4. CORS middleware (last, handles preflight requests)
if settings.BACKEND_CORS_ORIGINS:
    # Parse CORS origins from string
    import json

    try:
        cors_origins = json.loads(settings.BACKEND_CORS_ORIGINS)
    except (json.JSONDecodeError, TypeError):
        cors_origins = ["http://localhost", "http://localhost:8000"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Employee Directory API. Visit /docs for documentation.",
        "version": settings.VERSION,
        "api_version": settings.API_V1_STR,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    """
    # Check Redis connection status
    redis_status = "connected" if await redis_client.is_connected() else "disconnected"

    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "version": settings.VERSION,
            "redis": {
                "status": redis_status,
                "rate_limiting": settings.REDIS_RATE_LIMITING,
            },
            "rate_limiting": {
                "backend": (
                    "redis"
                    if redis_status == "connected" and settings.REDIS_RATE_LIMITING
                    else "memory"
                ),
                "limit": settings.RATE_LIMIT,
                "window": settings.RATE_LIMIT_WINDOW_SIZE,
            },
        },
    )


@app.get("/api/v1/rate-limit-info")
async def rate_limit_info(request: Request):
    """
    Debug endpoint to check current rate limit status.
    """
    info = await hybrid_rate_limiter.get_rate_limit_info(request)
    return JSONResponse(content=info)
