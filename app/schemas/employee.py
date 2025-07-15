from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr


# Department schemas
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = None


class Department(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Position schemas
class PositionBase(BaseModel):
    name: str
    description: Optional[str] = None


class PositionCreate(PositionBase):
    pass


class PositionUpdate(PositionBase):
    name: Optional[str] = None


class Position(PositionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Location schemas
class LocationBase(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(LocationBase):
    name: Optional[str] = None


class Location(LocationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Employee schemas
class EmployeeBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    location_id: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    name: Optional[str] = None
    status: Optional[str] = None


class Employee(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeDetail(Employee):
    department: Optional[Department] = None
    position: Optional[Position] = None
    location: Optional[Location] = None


# Enhanced schema for advanced search filters
class EmployeeSearchFilters(BaseModel):
    # Basic filters (existing)
    status: Optional[List[str]] = None
    location_ids: Optional[List[int]] = None
    department_ids: Optional[List[int]] = None
    position_ids: Optional[List[int]] = None
    name: Optional[str] = None

    # Advanced search features
    search_term: Optional[str] = None  # Full-text search across multiple fields
    fuzzy_match: bool = False  # Enable fuzzy matching for names
    email_domain: Optional[str] = None  # Filter by email domain
    phone_prefix: Optional[str] = None  # Filter by phone prefix

    # Date range filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None

    # Advanced filters
    has_email: Optional[bool] = None  # Filter employees with/without email
    has_phone: Optional[bool] = None  # Filter employees with/without phone

    # Search configuration
    search_fields: Optional[List[str]] = None  # Fields to search in for search_term
    exact_match: bool = False  # Require exact match for search_term
    case_sensitive: bool = False  # Case sensitive search

    # Sorting and ranking
    sort_by: Optional[str] = None  # Field to sort by
    sort_order: str = "asc"  # asc or desc
    include_relevance_score: bool = False  # Include search relevance score

    # Pagination (existing)
    page: int = 1
    page_size: int = 20
    columns: Optional[List[str]] = None  # Dynamic columns to return

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "search_term": "john",
                    "page": 1,
                    "page_size": 10,
                    "columns": ["name", "email", "department", "position", "status"],
                },
                {
                    "status": ["active"],
                    "department_ids": [1, 2],
                    "page": 1,
                    "page_size": 20,
                    "columns": [
                        "id",
                        "name",
                        "email",
                        "phone",
                        "department",
                        "position",
                    ],
                },
                {
                    "search_term": "manager",
                    "fuzzy_match": True,
                    "include_relevance_score": True,
                    "sort_by": "name",
                    "sort_order": "asc",
                    "columns": [
                        "name",
                        "email",
                        "department",
                        "position",
                        "relevance_score",
                    ],
                },
            ]
        }
    }


# Enhanced search response with relevance scoring
class EmployeeSearchResult(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    department: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    relevance_score: Optional[float] = None  # Search relevance score (0-1)


class EmployeeAdvancedSearchResponse(BaseModel):
    items: List[EmployeeSearchResult]
    total: int
    page: int
    page_size: int
    pages: int
    search_metadata: Dict[str, Any]  # Search statistics and metadata
    columns: List[str]
    organization_id: str


# Search suggestions
class SearchSuggestion(BaseModel):
    suggestion: str
    type: str  # 'name', 'department', 'position', 'location'
    count: int  # Number of matching results


class SearchSuggestionsResponse(BaseModel):
    suggestions: List[SearchSuggestion]
    search_term: str
