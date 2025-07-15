"""Async API endpoints for enhanced performance."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import validate_token
from app.db.async_session import get_async_db
from app.services.async_employee import AsyncEmployeeService
from app.schemas.employee import (
    EmployeeSearchFilters,
    EmployeeSearchResponse,
    EmployeeCreate,
    Employee,
)
from app.core.organization_config import get_organization_columns

router = APIRouter()

# Service instances
employee_service = AsyncEmployeeService()


@router.post("/search", response_model=EmployeeSearchResponse)
async def search_employees_async(
    *,
    db: AsyncSession = Depends(get_async_db),
    filters: EmployeeSearchFilters,
    token_data: Dict[str, Any] = Depends(validate_token),
) -> Any:
    """
    Advanced async employee search with enhanced performance.

    Features:
    - Async database operations for better concurrency
    - Parallel query execution
    - Connection pooling support
    - Enhanced eager loading
    """
    try:
        organization_id = token_data.get("organization_id", "default")

        # Get allowed columns for organization
        allowed_columns = get_organization_columns(organization_id)

        # Validate requested columns
        if filters.columns:
            invalid_columns = [
                col for col in filters.columns if col not in allowed_columns
            ]
            if invalid_columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid columns for organization {organization_id}: {invalid_columns}",
                )
            columns = filters.columns
        else:
            columns = allowed_columns

        # Perform async search with enhanced performance
        result = await employee_service.search_by_org(
            db=db,
            filters=filters,
            organization_id=organization_id,
            columns=columns,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/{employee_id}", response_model=Employee)
async def get_employee_async(
    employee_id: int,
    *,
    db: AsyncSession = Depends(get_async_db),
    token_data: Dict[str, Any] = Depends(validate_token),
) -> Any:
    """
    Get employee by ID with async database operations.
    """
    try:
        organization_id = token_data.get("organization_id", "default")

        employee = await employee_service.get_by_org(
            db=db, id=employee_id, organization_id=organization_id
        )

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found in organization {organization_id}",
            )

        return employee

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post("/", response_model=Employee)
async def create_employee_async(
    *,
    db: AsyncSession = Depends(get_async_db),
    employee_in: EmployeeCreate,
    token_data: Dict[str, Any] = Depends(validate_token),
) -> Any:
    """
    Create new employee with async database operations.
    """
    try:
        organization_id = token_data.get("organization_id", "default")

        employee = await employee_service.create_with_org(
            db=db, obj_in=employee_in, organization_id=organization_id
        )

        return employee

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/", response_model=List[Employee])
async def list_employees_async(
    *,
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100,
    token_data: Dict[str, Any] = Depends(validate_token),
) -> Any:
    """
    List employees with async database operations and pagination.
    """
    try:
        organization_id = token_data.get("organization_id", "default")

        employees = await employee_service.get_all_by_org(
            db=db, organization_id=organization_id, skip=skip, limit=limit
        )

        return employees

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
