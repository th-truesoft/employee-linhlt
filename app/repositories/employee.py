from typing import List, Optional, Dict, Any
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session, joinedload

from app.models.employee import Employee, Department, Position, Location
from app.repositories.base import BaseRepository
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeSearchFilters,
    DepartmentCreate, DepartmentUpdate,
    PositionCreate, PositionUpdate,
    LocationCreate, LocationUpdate
)


class EmployeeRepository(BaseRepository[Employee, EmployeeCreate, EmployeeUpdate]):
    def search(
        self, db: Session, *, filters: EmployeeSearchFilters
    ) -> List[Employee]:
        """
        Search employees with filters and pagination
        """
        query = db.query(Employee)
        
        # Apply filters
        if filters.status:
            query = query.filter(Employee.status.in_(filters.status))
        
        if filters.location_ids:
            query = query.filter(Employee.location_id.in_(filters.location_ids))
            
        if filters.department_ids:
            query = query.filter(Employee.department_id.in_(filters.department_ids))
            
        if filters.position_ids:
            query = query.filter(Employee.position_id.in_(filters.position_ids))
            
        if filters.name:
            query = query.filter(Employee.name.ilike(f"%{filters.name}%"))
        
        # Always load relationships for better performance
        query = query.options(
            joinedload(Employee.department),
            joinedload(Employee.position),
            joinedload(Employee.location)
        )
        
        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)
        
        return query.all()
    
    def count(
        self, db: Session, *, filters: EmployeeSearchFilters
    ) -> int:
        """
        Count total employees matching the filters
        """
        query = db.query(Employee)
        
        # Apply filters
        if filters.status:
            query = query.filter(Employee.status.in_(filters.status))
        
        if filters.location_ids:
            query = query.filter(Employee.location_id.in_(filters.location_ids))
            
        if filters.department_ids:
            query = query.filter(Employee.department_id.in_(filters.department_ids))
            
        if filters.position_ids:
            query = query.filter(Employee.position_id.in_(filters.position_ids))
            
        if filters.name:
            query = query.filter(Employee.name.ilike(f"%{filters.name}%"))
        
        return query.count()


class DepartmentRepository(BaseRepository[Department, DepartmentCreate, DepartmentUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Department]:
        return db.query(Department).filter(Department.name == name).first()


class PositionRepository(BaseRepository[Position, PositionCreate, PositionUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Position]:
        return db.query(Position).filter(Position.name == name).first()


class LocationRepository(BaseRepository[Location, LocationCreate, LocationUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Location]:
        return db.query(Location).filter(Location.name == name).first()


employee_repository = EmployeeRepository(Employee)
department_repository = DepartmentRepository(Department)
position_repository = PositionRepository(Position)
location_repository = LocationRepository(Location)
