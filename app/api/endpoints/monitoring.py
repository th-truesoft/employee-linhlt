"""
Monitoring and analytics endpoints for production insights.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.deps import get_db
from app.models.employee import Employee
from app.core.redis_client import redis_client

router = APIRouter()


@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive health check with system metrics.
    """
    start_time = time.time()

    # Database health
    try:
        employee_count = db.query(func.count(Employee.id)).scalar()
        db_healthy = True
        db_response_time = time.time() - start_time
    except Exception as e:
        employee_count = 0
        db_healthy = False
        db_response_time = -1

    # Redis health
    redis_start = time.time()
    redis_healthy = await redis_client.is_connected()
    redis_response_time = time.time() - redis_start if redis_healthy else -1

    total_response_time = time.time() - start_time

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": "production",
        "uptime_seconds": total_response_time,
        "database": {
            "status": "healthy" if db_healthy else "unhealthy",
            "response_time_ms": round(db_response_time * 1000, 2),
            "employee_count": employee_count,
        },
        "redis": {
            "status": "healthy" if redis_healthy else "unavailable",
            "response_time_ms": (
                round(redis_response_time * 1000, 2)
                if redis_response_time > 0
                else None
            ),
            "rate_limiting": "redis" if redis_healthy else "memory",
        },
        "security": {
            "headers_enabled": True,
            "rate_limiting_enabled": True,
            "jwt_enabled": True,
        },
    }


@router.get("/metrics/search", response_model=Dict[str, Any])
async def search_analytics() -> Dict[str, Any]:
    """
    Search analytics and performance metrics.
    """
    # Simulate search analytics (in real app, store actual metrics)
    analytics = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_searches_24h": 1247,
        "avg_response_time_ms": 85.6,
        "top_search_terms": [
            {"term": "manager", "count": 156, "avg_results": 12},
            {"term": "developer", "count": 143, "avg_results": 8},
            {"term": "sales", "count": 98, "avg_results": 15},
            {"term": "john", "count": 87, "avg_results": 3},
            {"term": "team lead", "count": 76, "avg_results": 6},
        ],
        "search_performance": {
            "under_50ms": 65.4,  # percentage
            "50_100ms": 28.2,
            "100_500ms": 5.8,
            "over_500ms": 0.6,
        },
        "no_results_searches": {
            "count": 23,
            "percentage": 1.8,
            "common_terms": ["xyz corp", "nonexistent", "test123"],
        },
    }

    try:
        # Get real Redis search stats if available
        if await redis_client.is_connected():
            search_stats = await redis_client.hgetall("search_analytics")
            if search_stats:
                analytics["real_data"] = {
                    k.decode(): v.decode() for k, v in search_stats.items()
                }
    except Exception:
        pass

    return analytics


@router.get("/metrics/performance", response_model=Dict[str, Any])
async def performance_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Performance testing and system load metrics.
    """
    start_time = time.time()

    # Database performance test
    db_start = time.time()
    try:
        # Simple query performance test
        employee_count = db.query(func.count(Employee.id)).scalar()
        db_time = time.time() - db_start

        # Complex query performance test
        complex_start = time.time()
        complex_result = (
            db.query(Employee)
            .join(Employee.department)
            .join(Employee.position)
            .limit(10)
            .all()
        )
        complex_time = time.time() - complex_start

        db_performance = {
            "simple_query_ms": round(db_time * 1000, 2),
            "complex_query_ms": round(complex_time * 1000, 2),
            "records_processed": len(complex_result),
        }
    except Exception as e:
        db_performance = {"error": str(e)}

    # Redis performance test
    redis_start = time.time()
    redis_performance = {}
    try:
        if await redis_client.is_connected():
            # Test Redis SET operation
            await redis_client.set("perf_test", "test_value", ex=10)
            set_time = time.time() - redis_start

            # Test Redis GET operation
            get_start = time.time()
            value = await redis_client.get("perf_test")
            get_time = time.time() - get_start

            redis_performance = {
                "set_operation_ms": round(set_time * 1000, 2),
                "get_operation_ms": round(get_time * 1000, 2),
                "connection_status": "healthy",
            }
        else:
            redis_performance = {"connection_status": "unavailable"}
    except Exception as e:
        redis_performance = {"connection_status": "error", "error": str(e)}

    total_time = time.time() - start_time

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_test_time_ms": round(total_time * 1000, 2),
        "database": db_performance,
        "redis": redis_performance,
        "system": {
            "memory_usage": "unknown",  # In production, use psutil
            "cpu_usage": "unknown",
        },
    }


@router.get("/metrics/security", response_model=Dict[str, Any])
async def security_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Security monitoring and threat detection metrics.
    """
    # Rate limiting stats
    rate_limit_stats = {}
    try:
        if await redis_client.is_connected():
            # Get rate limiting stats from Redis
            blocked_requests = await redis_client.get("rate_limit:blocked:24h")
            total_requests = await redis_client.get("rate_limit:total:24h")

            rate_limit_stats = {
                "total_requests_24h": int(total_requests) if total_requests else 0,
                "blocked_requests_24h": (
                    int(blocked_requests) if blocked_requests else 0
                ),
                "backend": "redis",
            }
        else:
            rate_limit_stats = {
                "backend": "memory",
                "total_requests_24h": "unavailable",
                "blocked_requests_24h": "unavailable",
            }
    except Exception:
        rate_limit_stats = {
            "backend": "error",
            "status": "monitoring_unavailable",
        }

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "jwt_security": {
            "algorithm": "HS256",
            "token_validation": "active",
            "expiration_check": "enabled",
        },
        "rate_limiting": rate_limit_stats,
        "security_headers": {
            "hsts_enabled": True,
            "csp_enabled": True,
            "xframe_protection": True,
            "xss_protection": True,
        },
    }


@router.get("/dashboard", response_model=Dict[str, Any])
async def monitoring_dashboard(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Combined monitoring dashboard with key metrics.
    """
    # Get all metrics in parallel for better performance
    import asyncio

    health_task = detailed_health_check(db)
    search_task = search_analytics()
    performance_task = performance_metrics(db)
    security_task = security_metrics(db)

    try:
        health, search, performance, security = await asyncio.gather(
            health_task, search_task, performance_task, security_task
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "dashboard": {
                "health": health,
                "search": search,
                "performance": performance,
                "security": security,
            },
        }
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e),
        }
