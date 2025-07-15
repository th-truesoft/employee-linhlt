"""Async repository layer for enterprise performance."""

from typing import List, Optional, Dict, Any, Sequence
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.employee import Employee, Department, Position, Location
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


class AsyncBaseRepository:
    """Base async repository with common CRUD operations."""

    def __init__(self, model):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[Any]:
        """Get by ID."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: Any) -> Any:
        """Create new object."""
        obj_data = obj_in.dict() if hasattr(obj_in, "dict") else obj_in
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


class AsyncEmployeeRepository(AsyncBaseRepository):
    """Async Employee repository with organization isolation."""

    def __init__(self):
        super().__init__(Employee)

    async def get_by_org(
        self, db: AsyncSession, *, id: int, organization_id: str
    ) -> Optional[Employee]:
        """Get employee by ID within organization."""
        result = await db.execute(
            select(Employee)
            .filter(Employee.id == id, Employee.organization_id == organization_id)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.position),
                selectinload(Employee.location),
            )
        )
        return result.scalar_one_or_none()

    async def search_by_org(
        self, db: AsyncSession, *, filters: EmployeeSearchFilters, organization_id: str
    ) -> List[Employee]:
        """Search employees with filters and pagination within organization."""
        query = select(Employee).filter(Employee.organization_id == organization_id)

        # Apply filters
        if filters.status:
            query = query.filter(Employee.status.in_(filters.status))

        if filters.location_ids:
            query = query.filter(Employee.location_id.in_(filters.location_ids))

        if filters.department_ids:
            query = query.filter(Employee.department_id.in_(filters.department_ids))

        if filters.position_ids:
            query = query.filter(Employee.position_id.in_(filters.position_ids))

        # Search by name
        if filters.name:
            search_term = f"%{filters.name}%"
            query = query.filter(
                or_(Employee.name.ilike(search_term), Employee.email.ilike(search_term))
            )

        # Add eager loading for related objects
        query = query.options(
            selectinload(Employee.department),
            selectinload(Employee.position),
            selectinload(Employee.location),
        )

        # Pagination
        if filters.page and filters.page_size:
            offset = (filters.page - 1) * filters.page_size
            query = query.offset(offset).limit(filters.page_size)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def count_by_org(
        self, db: AsyncSession, *, filters: EmployeeSearchFilters, organization_id: str
    ) -> int:
        """Count employees matching filters within organization."""
        query = select(func.count(Employee.id)).filter(
            Employee.organization_id == organization_id
        )

        # Apply same filters as search
        if filters.status:
            query = query.filter(Employee.status.in_(filters.status))

        if filters.location_ids:
            query = query.filter(Employee.location_id.in_(filters.location_ids))

        if filters.department_ids:
            query = query.filter(Employee.department_id.in_(filters.department_ids))

        if filters.position_ids:
            query = query.filter(Employee.position_id.in_(filters.position_ids))

        if filters.name:
            search_term = f"%{filters.name}%"
            query = query.filter(
                or_(Employee.name.ilike(search_term), Employee.email.ilike(search_term))
            )

        result = await db.execute(query)
        return result.scalar()

    async def create_with_org(
        self, db: AsyncSession, *, obj_in: EmployeeCreate, organization_id: str
    ) -> Employee:
        """Create employee with organization."""
        obj_data = obj_in.dict()
        obj_data["organization_id"] = organization_id

        db_obj = Employee(**obj_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get_all_by_org(
        self, db: AsyncSession, *, organization_id: str, skip: int = 0, limit: int = 100
    ) -> List[Employee]:
        """Get all employees by organization with pagination."""
        result = await db.execute(
            select(Employee)
            .filter(Employee.organization_id == organization_id)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.position),
                selectinload(Employee.location),
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


class AsyncDepartmentRepository(AsyncBaseRepository):
    """Async Department repository with organization isolation."""

    def __init__(self):
        super().__init__(Department)

    async def get_by_org(
        self, db: AsyncSession, *, id: int, organization_id: str
    ) -> Optional[Department]:
        """Get department by ID within organization."""
        result = await db.execute(
            select(Department).filter(
                Department.id == id, Department.organization_id == organization_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_org(
        self, db: AsyncSession, *, organization_id: str
    ) -> List[Department]:
        """Get all departments by organization."""
        result = await db.execute(
            select(Department).filter(Department.organization_id == organization_id)
        )
        return list(result.scalars().all())

    async def create_with_org(
        self, db: AsyncSession, *, obj_in: DepartmentCreate, organization_id: str
    ) -> Department:
        """Create department with organization."""
        obj_data = obj_in.dict()
        obj_data["organization_id"] = organization_id

        db_obj = Department(**obj_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


class AsyncPositionRepository(AsyncBaseRepository):
    """Async Position repository with organization isolation."""

    def __init__(self):
        super().__init__(Position)

    async def get_by_org(
        self, db: AsyncSession, *, id: int, organization_id: str
    ) -> Optional[Position]:
        """Get position by ID within organization."""
        result = await db.execute(
            select(Position).filter(
                Position.id == id, Position.organization_id == organization_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_org(
        self, db: AsyncSession, *, organization_id: str
    ) -> List[Position]:
        """Get all positions by organization."""
        result = await db.execute(
            select(Position).filter(Position.organization_id == organization_id)
        )
        return list(result.scalars().all())

    async def create_with_org(
        self, db: AsyncSession, *, obj_in: PositionCreate, organization_id: str
    ) -> Position:
        """Create position with organization."""
        obj_data = obj_in.dict()
        obj_data["organization_id"] = organization_id

        db_obj = Position(**obj_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


class AsyncLocationRepository(AsyncBaseRepository):
    """Async Location repository with organization isolation."""

    def __init__(self):
        super().__init__(Location)

    async def get_by_org(
        self, db: AsyncSession, *, id: int, organization_id: str
    ) -> Optional[Location]:
        """Get location by ID within organization."""
        result = await db.execute(
            select(Location).filter(
                Location.id == id, Location.organization_id == organization_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_org(
        self, db: AsyncSession, *, organization_id: str
    ) -> List[Location]:
        """Get all locations by organization."""
        result = await db.execute(
            select(Location).filter(Location.organization_id == organization_id)
        )
        return list(result.scalars().all())

    async def create_with_org(
        self, db: AsyncSession, *, obj_in: LocationCreate, organization_id: str
    ) -> Location:
        """Create location with organization."""
        obj_data = obj_in.dict()
        obj_data["organization_id"] = organization_id

        db_obj = Location(**obj_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
