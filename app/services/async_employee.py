"""Async service layer for enterprise performance."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.async_employee import (
    AsyncEmployeeRepository,
    AsyncDepartmentRepository,
    AsyncPositionRepository,
    AsyncLocationRepository,
)
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    Employee,
    EmployeeSearchFilters,
    EmployeeSearchResponse,
    DepartmentCreate,
    DepartmentUpdate,
    PositionCreate,
    PositionUpdate,
    LocationCreate,
    LocationUpdate,
)
from app.models.employee import Employee, Department, Position, Location


class AsyncEmployeeService:
    """Async Employee service with organization isolation."""

    def __init__(self):
        self.repository = AsyncEmployeeRepository()
        self.department_repository = AsyncDepartmentRepository()
        self.position_repository = AsyncPositionRepository()
        self.location_repository = AsyncLocationRepository()

    async def search_by_org(
        self,
        db: AsyncSession,
        *,
        filters: EmployeeSearchFilters,
        organization_id: str,
        columns: List[str],
    ) -> EmployeeSearchResponse:
        """Search employees with enhanced performance."""

        # Get employees and count in parallel for better performance
        import asyncio

        employees_task = self.repository.search_by_org(
            db, filters=filters, organization_id=organization_id
        )
        count_task = self.repository.count_by_org(
            db, filters=filters, organization_id=organization_id
        )

        employees, total = await asyncio.gather(employees_task, count_task)

        # Transform to response format with selected columns
        items = []
        for employee in employees:
            item = {}
            for column in columns:
                if hasattr(employee, column):
                    item[column] = getattr(employee, column)
                elif column == "department" and employee.department:
                    item[column] = employee.department.name
                elif column == "position" and employee.position:
                    item[column] = employee.position.name
                elif column == "location" and employee.location:
                    item[column] = employee.location.name
            items.append(item)

        # Calculate pagination info
        pages = (
            (total + filters.page_size - 1) // filters.page_size
            if filters.page_size
            else 1
        )

        # Generate summary statistics
        summary = await self._generate_summary(db, organization_id)

        return EmployeeSearchResponse(
            items=items,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            pages=pages,
            columns=columns,
            organization_id=organization_id,
            summary=summary,
        )

    async def get_by_org(
        self, db: AsyncSession, *, id: int, organization_id: str
    ) -> Optional[Employee]:
        """Get employee by ID within organization."""
        return await self.repository.get_by_org(
            db, id=id, organization_id=organization_id
        )

    async def create_with_org(
        self, db: AsyncSession, *, obj_in: EmployeeCreate, organization_id: str
    ) -> Employee:
        """Create employee with organization."""
        return await self.repository.create_with_org(
            db, obj_in=obj_in, organization_id=organization_id
        )

    async def get_all_by_org(
        self,
        db: AsyncSession,
        *,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Employee]:
        """Get all employees by organization with pagination."""
        return await self.repository.get_all_by_org(
            db, organization_id=organization_id, skip=skip, limit=limit
        )

    async def _generate_summary(
        self, db: AsyncSession, organization_id: str
    ) -> Dict[str, Any]:
        """Generate summary statistics for organization."""

        # Get all data in parallel
        import asyncio

        employees_task = self.repository.get_all_by_org(
            db, organization_id=organization_id, skip=0, limit=10000
        )
        departments_task = self.department_repository.get_all_by_org(
            db, organization_id=organization_id
        )
        positions_task = self.position_repository.get_all_by_org(
            db, organization_id=organization_id
        )
        locations_task = self.location_repository.get_all_by_org(
            db, organization_id=organization_id
        )

        employees, departments, positions, locations = await asyncio.gather(
            employees_task, departments_task, positions_task, locations_task
        )

        return {
            "total_employees": len(employees),
            "departments": [dept.name for dept in departments],
            "positions": [pos.name for pos in positions],
            "locations": [loc.name for loc in locations],
            "active_employees": len(
                [emp for emp in employees if emp.status == "active"]
            ),
            "inactive_employees": len(
                [emp for emp in employees if emp.status == "inactive"]
            ),
        }


class AsyncDepartmentService:
    """Async Department service with organization isolation."""

    def __init__(self):
        self.repository = AsyncDepartmentRepository()

    async def get_by_org(
        self, db: AsyncSession, *, id: int, organization_id: str
    ) -> Optional[Department]:
        """Get department by ID within organization."""
        return await self.repository.get_by_org(
            db, id=id, organization_id=organization_id
        )

    async def get_all_by_org(
        self, db: AsyncSession, *, organization_id: str
    ) -> List[Department]:
        """Get all departments by organization."""
        return await self.repository.get_all_by_org(db, organization_id=organization_id)

    async def create_with_org(
        self, db: AsyncSession, *, obj_in: DepartmentCreate, organization_id: str
    ) -> Department:
        """Create department with organization."""
        return await self.repository.create_with_org(
            db, obj_in=obj_in, organization_id=organization_id
        )


class AsyncPositionService:
    """Async Position service with organization isolation."""

    def __init__(self):
        self.repository = AsyncPositionRepository()

    async def get_by_org(
        self, db: AsyncSession, *, id: int, organization_id: str
    ) -> Optional[Position]:
        """Get position by ID within organization."""
        return await self.repository.get_by_org(
            db, id=id, organization_id=organization_id
        )

    async def get_all_by_org(
        self, db: AsyncSession, *, organization_id: str
    ) -> List[Position]:
        """Get all positions by organization."""
        return await self.repository.get_all_by_org(db, organization_id=organization_id)

    async def create_with_org(
        self, db: AsyncSession, *, obj_in: PositionCreate, organization_id: str
    ) -> Position:
        """Create position with organization."""
        return await self.repository.create_with_org(
            db, obj_in=obj_in, organization_id=organization_id
        )


class AsyncLocationService:
    """Async Location service with organization isolation."""

    def __init__(self):
        self.repository = AsyncLocationRepository()

    async def get_by_org(
        self, db: AsyncSession, *, id: int, organization_id: str
    ) -> Optional[Location]:
        """Get location by ID within organization."""
        return await self.repository.get_by_org(
            db, id=id, organization_id=organization_id
        )

    async def get_all_by_org(
        self, db: AsyncSession, *, organization_id: str
    ) -> List[Location]:
        """Get all locations by organization."""
        return await self.repository.get_all_by_org(db, organization_id=organization_id)

    async def create_with_org(
        self, db: AsyncSession, *, obj_in: LocationCreate, organization_id: str
    ) -> Location:
        """Create location with organization."""
        return await self.repository.create_with_org(
            db, obj_in=obj_in, organization_id=organization_id
        )
