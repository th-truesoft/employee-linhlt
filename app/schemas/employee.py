from typing import Optional, List
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


# Schema for search filters
class EmployeeSearchFilters(BaseModel):
    status: Optional[List[str]] = None
    location_ids: Optional[List[int]] = None
    department_ids: Optional[List[int]] = None
    position_ids: Optional[List[int]] = None
    name: Optional[str] = None
    page: int = 1
    page_size: int = 20
    columns: Optional[List[str]] = None  # Dynamic columns to return
