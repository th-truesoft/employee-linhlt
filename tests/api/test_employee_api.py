import pytest
from fastapi import status

from app.core.config import settings


def test_search_employees_no_filters(client, test_data):
    headers = {"Authorization": f"Bearer {settings.DEFAULT_API_TOKEN}"}
    response = client.post("/api/v1/employees/search", json={}, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] > 0
    assert len(data["items"]) > 0


def test_search_employees_with_name_filter(client, test_data):
    headers = {"Authorization": f"Bearer {settings.DEFAULT_API_TOKEN}"}
    first_employee = client.post("/api/v1/employees/search", json={"page": 1, "page_size": 1}, headers=headers).json()["items"][0]
    name_part = first_employee["name"].split()[0]
    
    response = client.post(
        "/api/v1/employees/search", 
        json={"name": name_part}, 
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] > 0
    assert name_part.lower() in data["items"][0]["name"].lower()


def test_search_employees_with_department_filter(client, test_data):
    headers = {"Authorization": f"Bearer {settings.DEFAULT_API_TOKEN}"}
    employees = client.post("/api/v1/employees/search", json={"page": 1, "page_size": 10}, headers=headers).json()["items"]
    if len(employees) == 0:
        pytest.skip("Không có nhân viên trong database")
    
    employee_with_dept = None
    for emp in employees:
        if "department" in emp and emp["department"]:
            employee_with_dept = emp
            break
    
    if not employee_with_dept:
        pytest.skip("Không tìm thấy nhân viên có phòng ban")
    
    department_name = employee_with_dept["department"]
    
    response = client.post(
        "/api/v1/employees/search", 
        json={"department": department_name}, 
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] > 0
    assert any(emp["department"] == department_name for emp in data["items"])


def test_search_employees_with_status_filter(client, test_data):
    headers = {"Authorization": f"Bearer {settings.DEFAULT_API_TOKEN}"}
    
    employees = client.post("/api/v1/employees/search", json={"page": 1, "page_size": 10}, headers=headers).json()["items"]
    if len(employees) == 0:
        pytest.skip("Không có nhân viên trong database")
    
    status_count = {}
    for emp in employees:
        if "status" in emp and emp["status"]:
            emp_status = emp["status"]
            status_count[emp_status] = status_count.get(emp_status, 0) + 1
    
    if not status_count:
        pytest.skip("Không tìm thấy nhân viên có trạng thái")
    
    common_status = max(status_count.items(), key=lambda x: x[1])[0]
    
    response = client.post(
        "/api/v1/employees/search", 
        json={"status": [common_status]}, 
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] > 0
    for employee in data["items"]:
        assert employee["status"] == common_status


def test_search_employees_with_pagination(client, test_data):
    headers = {"Authorization": f"Bearer {settings.DEFAULT_API_TOKEN}"}
    
    total_response = client.post("/api/v1/employees/search", json={}, headers=headers)
    total_data = total_response.json()
    total_employees = total_data["total"]
    
    if total_employees == 0:
        pytest.skip("Không có nhân viên trong database")
    
    response = client.post(
        "/api/v1/employees/search", 
        json={"page": 1, "page_size": 1}, 
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["total"] == total_employees
    assert len(data["items"]) <= 1
    assert data["page"] == 1
    assert data["page_size"] == 1
    
    expected_pages = (total_employees + data["page_size"] - 1) // data["page_size"]
    expected_pages = (total_employees + data["page_size"] - 1) // data["page_size"]
    assert data["pages"] == expected_pages


def test_search_employees_with_custom_columns(client, test_data):
    headers = {"Authorization": f"Bearer {settings.DEFAULT_API_TOKEN}"}
    
    employees = client.post("/api/v1/employees/search", json={"page": 1, "page_size": 1}, headers=headers).json()["items"]
    if len(employees) == 0:
        pytest.skip("Không có nhân viên trong database")
    
    response = client.post(
        "/api/v1/employees/search", 
        json={"columns": ["name", "email"]}, 
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "columns" in data
    assert set(data["columns"]) == {"name", "email"}
    
    for employee in data["items"]:
        assert set(employee.keys()) == {"name", "email"}
        assert "department" not in employee
        assert "position" not in employee


def test_search_employees_unauthorized(client):
    response = client.post("/api/v1/employees/search", json={})
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_search_employees_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post("/api/v1/employees/search", json={}, headers=headers)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
