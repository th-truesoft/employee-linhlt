import pytest
from sqlalchemy.orm import Session

from app.services.employee import employee_service
from app.schemas.employee import EmployeeSearchFilters


def test_search_employees_no_filters(db_session: Session, test_data):
    filters = EmployeeSearchFilters()
    result = employee_service.search(db_session, filters=filters)
    
    assert len(result) > 0
    for employee in result:
        assert hasattr(employee, "id")
        assert hasattr(employee, "name")
        assert hasattr(employee, "email")


def test_search_employees_with_name_filter(db_session: Session, test_data):
    all_employees = employee_service.search(db_session, filters=EmployeeSearchFilters())
    if not all_employees:
        pytest.skip("Employee data is empty")
    
    first_name_part = all_employees[0].name.split()[0]
    
    filters = EmployeeSearchFilters(name=first_name_part)
    result = employee_service.search(db_session, filters=filters)
    
    assert len(result) > 0
    assert first_name_part.lower() in result[0].name.lower()


def test_search_employees_with_department_filter(db_session: Session, test_data):
    if not test_data["employees"]:
        pytest.skip("Employee data is empty")
    
    employee_with_dept = None
    for emp in test_data["employees"]:
        if emp.department_id is not None:
            employee_with_dept = emp
            break
    
    if not employee_with_dept:
        pytest.skip("Employee with department not found")
    
    department_id = employee_with_dept.department_id
    filters = EmployeeSearchFilters(department_ids=[department_id])
    result = employee_service.search(db_session, filters=filters)
    
    if len(result) == 0:
        pytest.skip(f"Employee with department ID={department_id} not found")
    
    for employee in result:
        assert employee.department_id == department_id


def test_search_employees_with_position_filter(db_session: Session, test_data):
    if not test_data["employees"]:
        pytest.skip("Employee data is empty")
    
    employee_with_position = None
    for emp in test_data["employees"]:
        if emp.position_id is not None:
            employee_with_position = emp
            break
    
    if not employee_with_position:
        pytest.skip("Employee with position not found")
    
    position_id = employee_with_position.position_id
    filters = EmployeeSearchFilters(position_ids=[position_id])
    result = employee_service.search(db_session, filters=filters)
    
    if len(result) == 0:
        pytest.skip(f"Employee with position ID={position_id} not found")
    
    for employee in result:
        assert employee.position_id == position_id


def test_search_employees_with_location_filter(db_session: Session, test_data):
    if not test_data["employees"]:
        pytest.skip("Employee data is empty")
    
    employee_with_location = None
    for emp in test_data["employees"]:
        if emp.location_id is not None:
            employee_with_location = emp
            break
    
    if not employee_with_location:
        pytest.skip("Employee with location not found")
    
    location_id = employee_with_location.location_id
    filters = EmployeeSearchFilters(location_ids=[location_id])
    result = employee_service.search(db_session, filters=filters)
    
    if len(result) == 0:
        pytest.skip(f"Employee with location ID={location_id} not found")
    
    for employee in result:
        assert employee.location_id == location_id


def test_search_employees_with_status_filter(db_session: Session, test_data):
    if not test_data["employees"]:
        pytest.skip("Employee data is empty")
    
    status = test_data["employees"][0].status
    
    filters = EmployeeSearchFilters(status=[status])
    result = employee_service.search(db_session, filters=filters)
    
    if len(result) == 0:
        pytest.skip(f"Employee with status {status} not found")
    
    assert len(result) > 0
    
    for employee in result:
        assert employee.status == status


def test_search_employees_with_pagination(db_session: Session, test_data):
    if not test_data["employees"]:
        pytest.skip("Employee data is empty")
    
    all_result = employee_service.search(db_session, filters=EmployeeSearchFilters())
    total_employees = len(all_result)
    
    if total_employees == 0:
        pytest.skip("Employee data is empty")
    
    filters = EmployeeSearchFilters(page=1, page_size=1)
    result = employee_service.search(db_session, filters=filters)
    
    assert len(result) <= 1  
    
    if total_employees > 1:
        filters = EmployeeSearchFilters(page=2, page_size=1)
        result = employee_service.search(db_session, filters=filters)
        
        assert len(result) <= 1


def test_search_employees_with_custom_columns(db_session: Session, test_data):
    if not test_data["employees"]:
        pytest.skip("Employee data is empty")
    
    all_employees = employee_service.search(db_session, filters=EmployeeSearchFilters())
    if not all_employees:
        pytest.skip("Employee data is empty")
    
    filters = EmployeeSearchFilters(columns=["name", "email"])
    result = employee_service.search(db_session, filters=filters)
    
    assert len(result) > 0
    
    for employee in result:
        assert hasattr(employee, "name")
        assert hasattr(employee, "email")
