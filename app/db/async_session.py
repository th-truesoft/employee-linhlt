"""Async database session configuration for enterprise performance."""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create async engine with optimized settings
database_uri = str(settings.ASYNC_SQLALCHEMY_DATABASE_URI)

if "sqlite" in database_uri:
    # SQLite async configuration
    async_engine = create_async_engine(
        database_uri,
        poolclass=NullPool,  # Disable pooling for SQLite
        echo=False,  # Set to True for SQL debugging
        future=True,
        connect_args={"check_same_thread": False},  # Allow multithreaded access
    )
else:
    # PostgreSQL async configuration
    async_engine = create_async_engine(
        database_uri,
        pool_size=20,  # Max persistent connections
        max_overflow=30,  # Max overflow connections
        pool_pre_ping=True,  # Health check connections
        pool_recycle=3600,  # Recycle connections every hour
        echo=False,  # Set to True for SQL debugging
        future=True,
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autoflush=False,  # Manual control over flushing
    autocommit=False,  # Manual transaction control
)

# Import shared Base for model compatibility
from app.models.base import Base as AsyncBase


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency for FastAPI.

    Yields:
        AsyncSession: Database session for async operations
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Auto-commit successful transactions
        except Exception:
            await session.rollback()  # Rollback on errors
            raise
        finally:
            await session.close()


async def init_async_db() -> None:
    """Initialize async database tables."""
    async with async_engine.begin() as conn:
        # Import models to ensure they're registered
        from app.models.employee import Employee, Department, Position, Location

        # Create all tables
        await conn.run_sync(AsyncBase.metadata.create_all)


async def close_async_db() -> None:
    """Close async database connections."""
    await async_engine.dispose()
