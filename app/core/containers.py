"""Dependency injection container for the application."""

from dependency_injector import containers, providers
from dependency_injector.ext import aiohttp

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.employee import (
    EmployeeRepository,
    DepartmentRepository, 
    PositionRepository,
    LocationRepository
)
from app.services.employee import (
    EmployeeService,
    DepartmentService,
    PositionService,
    LocationService
)
from app.models.employee import Employee, Department, Position, Location


class Container(containers.DeclarativeContainer):
    """Application dependency injection container."""
    
    # Configuration
    config = providers.Configuration()
    
    # Database
    db_session_factory = providers.Singleton(
        SessionLocal
    )
    
    # Repositories
    employee_repository = providers.Factory(
        EmployeeRepository,
        model=Employee
    )
    
    department_repository = providers.Factory(
        DepartmentRepository,
        model=Department
    )
    
    position_repository = providers.Factory(
        PositionRepository,
        model=Position
    )
    
    location_repository = providers.Factory(
        LocationRepository,
        model=Location
    )
    
    # Services
    employee_service = providers.Factory(
        EmployeeService,
        repository=employee_repository
    )
    
    department_service = providers.Factory(
        DepartmentService,
        repository=department_repository
    )
    
    position_service = providers.Factory(
        PositionService,
        repository=position_repository
    )
    
    location_service = providers.Factory(
        LocationService,
        repository=location_repository
    )


# Global container instance
container = Container()

# Configure the container
container.config.from_dict({
    "database_url": settings.SQLALCHEMY_DATABASE_URI,
    "secret_key": settings.SECRET_KEY,
    "api_token": settings.DEFAULT_API_TOKEN
}) 