import pytest
from fastapi import status

from app.core.config import settings


def test_search_employees_no_filters(client, test_data, auth_headers):
    """Test search employees with JWT token"""
    response = client.post("/api/v1/employees/search", json={}, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "organization_id" in data
    assert data["organization_id"] == "default"
    assert data["total"] == 2  # Should only see default org employees
    assert len(data["items"]) == 2


def test_search_employees_backward_compatibility(
    client, test_data, simple_auth_headers
):
    """Test backward compatibility with simple token"""
    response = client.post(
        "/api/v1/employees/search", json={}, headers=simple_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "organization_id" in data
    assert data["organization_id"] == "default"


def test_search_employees_multi_tenant_isolation(
    client, test_data, org1_auth_headers, org2_auth_headers, auth_headers
):
    """Test that organizations can only see their own data"""
    # Test default org
    response_default = client.post(
        "/api/v1/employees/search", json={}, headers=auth_headers
    )
    data_default = response_default.json()
    assert data_default["total"] == 2
    assert data_default["organization_id"] == "default"

    # Test org1
    response_org1 = client.post(
        "/api/v1/employees/search", json={}, headers=org1_auth_headers
    )
    data_org1 = response_org1.json()
    assert data_org1["total"] == 1
    assert data_org1["organization_id"] == "org1"
    assert data_org1["items"][0]["name"] == "Org1 Employee 1"

    # Test org2
    response_org2 = client.post(
        "/api/v1/employees/search", json={}, headers=org2_auth_headers
    )
    data_org2 = response_org2.json()
    assert data_org2["total"] == 1
    assert data_org2["organization_id"] == "org2"
    assert data_org2["items"][0]["name"] == "Org2 Employee 1"


def test_search_employees_with_name_filter(client, test_data, auth_headers):
    response = client.post(
        "/api/v1/employees/search", json={"name": "Test"}, headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 2  # Both test employees in default org
    assert all("Test" in emp["name"] for emp in data["items"])


def test_search_employees_with_department_filter(client, test_data, auth_headers):
    """Test department filtering within organization"""
    response = client.post("/api/v1/employees/search", json={}, headers=auth_headers)

    data = response.json()
    employees = data["items"]

    if len(employees) == 0:
        pytest.skip("No employees in database")

    # Find an employee with department
    employee_with_dept = None
    for emp in employees:
        if "department" in emp and emp["department"]:
            employee_with_dept = emp
            break

    if not employee_with_dept:
        pytest.skip("No employee with department found")

    department_name = employee_with_dept["department"]

    response = client.post(
        "/api/v1/employees/search",
        json={"department": department_name},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] > 0
    assert all(emp["department"] == department_name for emp in data["items"])


def test_search_employees_with_status_filter(client, test_data, auth_headers):
    response = client.post(
        "/api/v1/employees/search", json={"status": ["active"]}, headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 2  # Both employees are active
    assert all(emp["status"] == "active" for emp in data["items"])


def test_search_employees_with_pagination(client, test_data, auth_headers):
    response = client.post(
        "/api/v1/employees/search",
        json={"page": 1, "page_size": 1},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["total"] == 2
    assert len(data["items"]) == 1
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert data["pages"] == 2


def test_search_employees_with_custom_columns(client, test_data, auth_headers):
    response = client.post(
        "/api/v1/employees/search",
        json={"columns": ["name", "email"]},
        headers=auth_headers,
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
    """Test request without authorization header"""
    response = client.post("/api/v1/employees/search", json={})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_search_employees_invalid_token(client):
    """Test request with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post("/api/v1/employees/search", json={}, headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_search_employees_malformed_jwt(client):
    """Test request with malformed JWT token"""
    headers = {"Authorization": "Bearer not.a.jwt"}
    response = client.post("/api/v1/employees/search", json={}, headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_search_employees_jwt_without_organization(client):
    """Test JWT token without organization_id claim"""
    from app.core.deps import create_access_token

    # Create token without organization_id
    token = create_access_token(data={"sub": "test_user"})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/v1/employees/search", json={}, headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "organization_id" in response.json()["detail"]


def test_search_employees_invalid_columns(client, test_data, auth_headers):
    """Test request with invalid column names"""
    response = client.post(
        "/api/v1/employees/search",
        json={"columns": ["name", "invalid_column"]},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid columns" in response.json()["detail"]


def test_org_data_isolation_detailed(
    client, test_data, org1_auth_headers, org2_auth_headers
):
    """Detailed test of organization data isolation"""
    # Org1 should only see Engineering department
    response_org1 = client.post(
        "/api/v1/employees/search", json={}, headers=org1_auth_headers
    )
    data_org1 = response_org1.json()

    assert len(data_org1["items"]) == 1
    emp_org1 = data_org1["items"][0]
    assert emp_org1["name"] == "Org1 Employee 1"
    assert emp_org1["department"] == "Engineering"
    assert emp_org1["email"] == "org1_test1@example.com"

    # Org2 should only see Marketing department
    response_org2 = client.post(
        "/api/v1/employees/search", json={}, headers=org2_auth_headers
    )
    data_org2 = response_org2.json()

    assert len(data_org2["items"]) == 1
    emp_org2 = data_org2["items"][0]
    assert emp_org2["name"] == "Org2 Employee 1"
    assert emp_org2["department"] == "Marketing"
    assert emp_org2["email"] == "org2_test1@example.com"

    # Verify no cross-contamination
    assert emp_org1["email"] != emp_org2["email"]
    assert emp_org1["department"] != emp_org2["department"]
