from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, Body, HTTPException, Path, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core import deps
from app.core.containers import container
from app.core.config import settings
from app.services.employee import EmployeeService
from app.services.advanced_search import AdvancedSearchService
from app.schemas.employee import (
    EmployeeSearchFilters,
    EmployeeAdvancedSearchResponse,
    SearchSuggestionsResponse,
)

security = HTTPBearer()
router = APIRouter()


def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Dict[str, Any]:
    """Verify the Bearer token and return token payload"""
    return deps.validate_token(authorization=f"Bearer {credentials.credentials}")


def get_employee_service() -> EmployeeService:
    """Get employee service from container."""
    return container.employee_service()


def get_advanced_search_service() -> AdvancedSearchService:
    """Get advanced search service"""
    return AdvancedSearchService()


@router.post(
    "/search", response_model=Dict[str, Any], dependencies=[Depends(verify_token)]
)
def search_employees(
    *,
    db: Session = Depends(deps.get_db),
    filters: EmployeeSearchFilters,
    token_data: Dict[str, Any] = Depends(verify_token),
    employee_service: EmployeeService = Depends(get_employee_service),
) -> Any:
    from app.core.organization_config import get_organization_columns

    # Extract organization_id from JWT token
    organization_id = token_data.get("organization_id", "default")

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

    # Search employees using multi-tenant service methods
    employees = employee_service.search_by_org(
        db=db, filters=filters, organization_id=organization_id
    )
    total_count = employee_service.count_by_org(
        db=db, filters=filters, organization_id=organization_id
    )

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
        if "position" in columns and emp.position:
            employee_dict["position"] = emp.position.name
        if "location" in columns and emp.location:
            employee_dict["location"] = emp.location.name

        result.append(employee_dict)

    # Calculate pagination info
    total_pages = (total_count + filters.page_size - 1) // filters.page_size

    return {
        "items": result,
        "total": total_count,
        "page": filters.page,
        "page_size": filters.page_size,
        "pages": total_pages,
        "columns": columns,
        "organization_id": organization_id,
    }


@router.post(
    "/advanced-search",
    response_model=EmployeeAdvancedSearchResponse,
    dependencies=[Depends(verify_token)],
)
def advanced_search_employees(
    *,
    db: Session = Depends(deps.get_db),
    filters: EmployeeSearchFilters,
    token_data: Dict[str, Any] = Depends(verify_token),
    search_service: AdvancedSearchService = Depends(get_advanced_search_service),
) -> Any:
    """
    Advanced employee search with full-text search, fuzzy matching, and relevance scoring

    Features:
    - Full-text search across multiple fields
    - Fuzzy matching for names
    - Relevance scoring
    - Advanced filters (email domain, phone prefix, date ranges)
    - Sorting and ranking
    """

    # Extract organization_id from JWT token
    organization_id = token_data.get("organization_id", "default")

    # Validate columns if specified
    if filters.columns:
        valid_columns = {
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
            "relevance_score",
        }
        invalid_columns = [col for col in filters.columns if col not in valid_columns]
        if invalid_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid columns: {', '.join(invalid_columns)}",
            )

    # Perform advanced search
    search_results, total_count, search_metadata = search_service.search_employees(
        db=db, filters=filters, organization_id=organization_id
    )

    # Calculate pagination info
    total_pages = (total_count + filters.page_size - 1) // filters.page_size

    # Set default columns if not specified
    columns = filters.columns or [
        "id",
        "name",
        "email",
        "department",
        "position",
        "status",
    ]
    if filters.include_relevance_score and "relevance_score" not in columns:
        columns.append("relevance_score")

    return EmployeeAdvancedSearchResponse(
        items=search_results,
        total=total_count,
        page=filters.page,
        page_size=filters.page_size,
        pages=total_pages,
        search_metadata=search_metadata,
        columns=columns,
        organization_id=organization_id,
    )


@router.get(
    "/search-suggestions",
    response_model=SearchSuggestionsResponse,
    dependencies=[Depends(verify_token)],
)
def get_search_suggestions(
    *,
    db: Session = Depends(deps.get_db),
    q: str = Query(..., description="Search term for suggestions"),
    limit: int = Query(10, description="Maximum number of suggestions"),
    token_data: Dict[str, Any] = Depends(verify_token),
    search_service: AdvancedSearchService = Depends(get_advanced_search_service),
) -> Any:
    """
    Get search suggestions based on partial search term

    Returns suggestions for:
    - Employee names
    - Department names
    - Position names
    - Location names
    """

    organization_id = token_data.get("organization_id", "default")

    if len(q.strip()) < 2:
        raise HTTPException(
            status_code=400, detail="Search term must be at least 2 characters long"
        )

    suggestions = search_service.get_search_suggestions(
        db=db, search_term=q, organization_id=organization_id, limit=limit
    )

    return SearchSuggestionsResponse(suggestions=suggestions, search_term=q)
