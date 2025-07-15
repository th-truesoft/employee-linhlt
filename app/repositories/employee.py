from typing import List, Optional, Dict, Any
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session, joinedload

from app.models.employee import Employee, Department, Position, Location
from app.repositories.base import BaseRepository
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeSearchFilters,
    DepartmentCreate,
    DepartmentUpdate,
    PositionCreate,
    PositionUpdate,
    LocationCreate,
    LocationUpdate,
)


class EmployeeRepository(BaseRepository[Employee, EmployeeCreate, EmployeeUpdate]):
    def get_by_org(
        self, db: Session, *, id: int, organization_id: str
    ) -> Optional[Employee]:
        """Get employee by ID within organization"""
        return (
            db.query(Employee)
            .filter(Employee.id == id, Employee.organization_id == organization_id)
            .first()
        )

    def search_by_org(
        self, db: Session, *, filters: EmployeeSearchFilters, organization_id: str
    ) -> List[Employee]:
        """
        Search employees with filters and pagination within organization
        """
        query = db.query(Employee).filter(Employee.organization_id == organization_id)

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
            joinedload(Employee.location),
        )

        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        return query.all()

    def count_by_org(
        self, db: Session, *, filters: EmployeeSearchFilters, organization_id: str
    ) -> int:
        """
        Count total employees matching the filters within organization
        """
        query = db.query(Employee).filter(Employee.organization_id == organization_id)

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

    def create_with_org(
        self, db: Session, *, obj_in: EmployeeCreate, organization_id: str
    ) -> Employee:
        """Create employee with organization_id"""
        obj_data = obj_in.dict()
        obj_data["organization_id"] = organization_id
        db_obj = Employee(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_by_org(self, db: Session, *, id: int, organization_id: str) -> Employee:
        """Remove employee by ID within organization"""
        obj = (
            db.query(Employee)
            .filter(Employee.id == id, Employee.organization_id == organization_id)
            .first()
        )
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    # Keep original methods for backward compatibility
    def search(self, db: Session, *, filters: EmployeeSearchFilters) -> List[Employee]:
        """
        Search employees with filters and pagination (backward compatibility)
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
            joinedload(Employee.location),
        )

        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        return query.all()

    def count(self, db: Session, *, filters: EmployeeSearchFilters) -> int:
        """
        Count total employees matching the filters (backward compatibility)
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


class DepartmentRepository(
    BaseRepository[Department, DepartmentCreate, DepartmentUpdate]
):
    def get_by_org(
        self, db: Session, *, id: int, organization_id: str
    ) -> Optional[Department]:
        """Get department by ID within organization"""
        return (
            db.query(Department)
            .filter(Department.id == id, Department.organization_id == organization_id)
            .first()
        )

    def get_by_name_and_org(
        self, db: Session, *, name: str, organization_id: str
    ) -> Optional[Department]:
        """Get department by name within organization"""
        return (
            db.query(Department)
            .filter(
                Department.name == name, Department.organization_id == organization_id
            )
            .first()
        )

    def get_multi_by_org(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: str
    ) -> List[Department]:
        """Get multiple departments within organization"""
        return (
            db.query(Department)
            .filter(Department.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_org(
        self, db: Session, *, obj_in: DepartmentCreate, organization_id: str
    ) -> Department:
        """Create department with organization_id"""
        obj_data = obj_in.dict()
        obj_data["organization_id"] = organization_id
        db_obj = Department(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_by_org(
        self, db: Session, *, id: int, organization_id: str
    ) -> Department:
        """Remove department by ID within organization"""
        obj = (
            db.query(Department)
            .filter(Department.id == id, Department.organization_id == organization_id)
            .first()
        )
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    # Keep original method for backward compatibility
    def get_by_name(self, db: Session, *, name: str) -> Optional[Department]:
        return db.query(Department).filter(Department.name == name).first()


class PositionRepository(BaseRepository[Position, PositionCreate, PositionUpdate]):
    def get_by_org(
        self, db: Session, *, id: int, organization_id: str
    ) -> Optional[Position]:
        """Get position by ID within organization"""
        return (
            db.query(Position)
            .filter(Position.id == id, Position.organization_id == organization_id)
            .first()
        )

    def get_by_name_and_org(
        self, db: Session, *, name: str, organization_id: str
    ) -> Optional[Position]:
        """Get position by name within organization"""
        return (
            db.query(Position)
            .filter(Position.name == name, Position.organization_id == organization_id)
            .first()
        )

    def get_multi_by_org(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: str
    ) -> List[Position]:
        """Get multiple positions within organization"""
        return (
            db.query(Position)
            .filter(Position.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_org(
        self, db: Session, *, obj_in: PositionCreate, organization_id: str
    ) -> Position:
        """Create position with organization_id"""
        obj_data = obj_in.dict()
        obj_data["organization_id"] = organization_id
        db_obj = Position(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_by_org(self, db: Session, *, id: int, organization_id: str) -> Position:
        """Remove position by ID within organization"""
        obj = (
            db.query(Position)
            .filter(Position.id == id, Position.organization_id == organization_id)
            .first()
        )
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    # Keep original method for backward compatibility
    def get_by_name(self, db: Session, *, name: str) -> Optional[Position]:
        return db.query(Position).filter(Position.name == name).first()


class LocationRepository(BaseRepository[Location, LocationCreate, LocationUpdate]):
    def get_by_org(
        self, db: Session, *, id: int, organization_id: str
    ) -> Optional[Location]:
        """Get location by ID within organization"""
        return (
            db.query(Location)
            .filter(Location.id == id, Location.organization_id == organization_id)
            .first()
        )

    def get_by_name_and_org(
        self, db: Session, *, name: str, organization_id: str
    ) -> Optional[Location]:
        """Get location by name within organization"""
        return (
            db.query(Location)
            .filter(Location.name == name, Location.organization_id == organization_id)
            .first()
        )

    def get_multi_by_org(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: str
    ) -> List[Location]:
        """Get multiple locations within organization"""
        return (
            db.query(Location)
            .filter(Location.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_org(
        self, db: Session, *, obj_in: LocationCreate, organization_id: str
    ) -> Location:
        """Create location with organization_id"""
        obj_data = obj_in.dict()
        obj_data["organization_id"] = organization_id
        db_obj = Location(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_by_org(self, db: Session, *, id: int, organization_id: str) -> Location:
        """Remove location by ID within organization"""
        obj = (
            db.query(Location)
            .filter(Location.id == id, Location.organization_id == organization_id)
            .first()
        )
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    # Keep original method for backward compatibility
    def get_by_name(self, db: Session, *, name: str) -> Optional[Location]:
        return db.query(Location).filter(Location.name == name).first()


employee_repository = EmployeeRepository(Employee)
department_repository = DepartmentRepository(Department)
position_repository = PositionRepository(Position)
location_repository = LocationRepository(Location)
