from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, Body, HTTPException, Path
from sqlalchemy.orm import Session

from app.core import deps
from app.core.containers import container
from app.services.employee import EmployeeService
from app.schemas.employee import EmployeeSearchFilters

router = APIRouter()


def get_employee_service() -> EmployeeService:
    """Get employee service from container."""
    return container.employee_service()


@router.post("/search", response_model=Dict[str, Any])
def search_employees(
    *,
    db: Session = Depends(deps.get_db),
    filters: EmployeeSearchFilters,
    organization_id: str = Query(
        "default", description="Organization ID for column configuration"
    ),
    _: bool = Depends(deps.validate_token),
    employee_service: EmployeeService = Depends(get_employee_service),
) -> Any:
    from app.core.organization_config import get_organization_columns

    org_columns = get_organization_columns(organization_id)

    columns = filters.columns or org_columns

    # Validate columns
    valid_columns = set(
        [
            "id",
            "name",
            "email",
            "phone",
            "status",
            "department",
            "position",
            "location",
            "created_at",
            "updated_at",
        ]
    )
    invalid_columns = [col for col in columns if col not in valid_columns]
    if invalid_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid columns: {', '.join(invalid_columns)}",
        )

    # Search employees using injected service
    employees = employee_service.search(db=db, filters=filters)
    total_count = employee_service.count(db=db, filters=filters)

    # Format the response with only the requested columns
    result = []
    for emp in employees:
        employee_dict = {}

        # Add basic fields
        if "id" in columns:
            employee_dict["id"] = emp.id
        if "name" in columns:
            employee_dict["name"] = emp.name
        if "email" in columns:
            employee_dict["email"] = emp.email
        if "phone" in columns:
            employee_dict["phone"] = emp.phone
        if "status" in columns:
            employee_dict["status"] = emp.status
        if "created_at" in columns:
            employee_dict["created_at"] = emp.created_at
        if "updated_at" in columns:
            employee_dict["updated_at"] = emp.updated_at

        # Add related fields
        if "department" in columns and emp.department:
            employee_dict["department"] = emp.department.name
        elif "department" in columns:
            employee_dict["department"] = None

        if "position" in columns and emp.position:
            employee_dict["position"] = emp.position.name
        elif "position" in columns:
            employee_dict["position"] = None

        if "location" in columns and emp.location:
            employee_dict["location"] = emp.location.name
        elif "location" in columns:
            employee_dict["location"] = None

        result.append(employee_dict)

    # Return paginated results with metadata
    return {
        "items": result,
        "total": total_count,
        "page": filters.page,
        "page_size": filters.page_size,
        "pages": (total_count + filters.page_size - 1) // filters.page_size,
        "columns": columns,
    }
