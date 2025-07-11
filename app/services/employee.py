from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session

from app.models.employee import Employee, Department, Position, Location
from app.repositories.employee import (
    EmployeeRepository, DepartmentRepository, PositionRepository, LocationRepository
)
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeSearchFilters,
    DepartmentCreate, DepartmentUpdate,
    PositionCreate, PositionUpdate,
    LocationCreate, LocationUpdate
)


class EmployeeService:
    def __init__(self, repository: EmployeeRepository):
        self._repository = repository

    def get(self, db: Session, employee_id: int) -> Optional[Employee]:
        return self._repository.get(db=db, id=employee_id)

    def search(
        self, db: Session, *, filters: EmployeeSearchFilters
    ) -> List[Employee]:
        return self._repository.search(db=db, filters=filters)
    
    def count(
        self, db: Session, *, filters: EmployeeSearchFilters
    ) -> int:
        return self._repository.count(db=db, filters=filters)
    
    def create(self, db: Session, *, obj_in: EmployeeCreate) -> Employee:
        return self._repository.create(db=db, obj_in=obj_in)

    def update(
        self, db: Session, *, db_obj: Employee, obj_in: Union[EmployeeUpdate, Dict[str, Any]]
    ) -> Employee:
        return self._repository.update(db=db, db_obj=db_obj, obj_in=obj_in)

    def delete(self, db: Session, *, employee_id: int) -> Employee:
        return self._repository.remove(db=db, id=employee_id)


class DepartmentService:
    def __init__(self, repository: DepartmentRepository):
        self._repository = repository

    def get(self, db: Session, department_id: int) -> Optional[Department]:
        return self._repository.get(db=db, id=department_id)

    def get_by_name(self, db: Session, *, name: str) -> Optional[Department]:
        return self._repository.get_by_name(db=db, name=name)

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Department]:
        return self._repository.get_multi(db=db, skip=skip, limit=limit)

    def create(self, db: Session, *, obj_in: DepartmentCreate) -> Department:
        return self._repository.create(db=db, obj_in=obj_in)

    def update(
        self, db: Session, *, db_obj: Department, obj_in: Union[DepartmentUpdate, Dict[str, Any]]
    ) -> Department:
        return self._repository.update(db=db, db_obj=db_obj, obj_in=obj_in)

    def delete(self, db: Session, *, department_id: int) -> Department:
        return self._repository.remove(db=db, id=department_id)


class PositionService:
    def __init__(self, repository: PositionRepository):
        self._repository = repository

    def get(self, db: Session, position_id: int) -> Optional[Position]:
        return self._repository.get(db=db, id=position_id)

    def get_by_name(self, db: Session, *, name: str) -> Optional[Position]:
        return self._repository.get_by_name(db=db, name=name)

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Position]:
        return self._repository.get_multi(db=db, skip=skip, limit=limit)

    def create(self, db: Session, *, obj_in: PositionCreate) -> Position:
        return self._repository.create(db=db, obj_in=obj_in)

    def update(
        self, db: Session, *, db_obj: Position, obj_in: Union[PositionUpdate, Dict[str, Any]]
    ) -> Position:
        return self._repository.update(db=db, db_obj=db_obj, obj_in=obj_in)

    def delete(self, db: Session, *, position_id: int) -> Position:
        return self._repository.remove(db=db, id=position_id)


class LocationService:
    def __init__(self, repository: LocationRepository):
        self._repository = repository

    def get(self, db: Session, location_id: int) -> Optional[Location]:
        return self._repository.get(db=db, id=location_id)

    def get_by_name(self, db: Session, *, name: str) -> Optional[Location]:
        return self._repository.get_by_name(db=db, name=name)

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Location]:
        return self._repository.get_multi(db=db, skip=skip, limit=limit)

    def create(self, db: Session, *, obj_in: LocationCreate) -> Location:
        return self._repository.create(db=db, obj_in=obj_in)

    def update(
        self, db: Session, *, db_obj: Location, obj_in: Union[LocationUpdate, Dict[str, Any]]
    ) -> Location:
        return self._repository.update(db=db, db_obj=db_obj, obj_in=obj_in)

    def delete(self, db: Session, *, location_id: int) -> Location:
        return self._repository.remove(db=db, id=location_id)
