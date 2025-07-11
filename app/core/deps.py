from typing import Generator, Optional

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide

from app.core.config import settings
from app.core.containers import Container
from app.db.session import SessionLocal


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def validate_token(authorization: Optional[str] = Header(None)) -> bool:
    """
    Simple token validation function that checks if the provided token matches the default API token
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if token != settings.DEFAULT_API_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return True
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Dependency injection functions using container
@inject
def get_employee_service(
    service = Provide[Container.employee_service]
):
    return service


@inject
def get_department_service(
    service = Provide[Container.department_service]
):
    return service


@inject
def get_position_service(
    service = Provide[Container.position_service]
):
    return service


@inject
def get_location_service(
    service = Provide[Container.location_service]
):
    return service
