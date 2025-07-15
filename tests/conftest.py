import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.containers import container
from app.core.deps import create_access_token
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.employee import Department, Position, Location, Employee


@pytest.fixture(scope="session")
def test_db_url():
    """Use test database URL"""
    return "sqlite:///test_employee_directory.db"


@pytest.fixture(scope="session")
def engine(test_db_url):
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    session.begin_nested()

    yield session

    session.rollback()
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers():
    """Generate JWT token for default organization"""
    token = create_access_token(data={"sub": "test_user", "organization_id": "default"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def org1_auth_headers():
    """Generate JWT token for org1"""
    token = create_access_token(
        data={"sub": "test_user_org1", "organization_id": "org1"}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def org2_auth_headers():
    """Generate JWT token for org2"""
    token = create_access_token(
        data={"sub": "test_user_org2", "organization_id": "org2"}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def simple_auth_headers():
    """Generate simple token for backward compatibility testing"""
    return {"Authorization": f"Bearer {settings.DEFAULT_API_TOKEN}"}


@pytest.fixture(scope="function")
def test_data(db_session):
    """Create multi-tenant test data"""
    from app.models.employee import Department, Position, Location, Employee

    # Clear existing data
    db_session.query(Employee).delete()
    db_session.query(Department).delete()
    db_session.query(Position).delete()
    db_session.query(Location).delete()

    # Create test data for default organization
    dept1_default = Department(
        name="Engineering", description="Tech department", organization_id="default"
    )
    dept2_default = Department(
        name="HR", description="Human Resources", organization_id="default"
    )
    db_session.add(dept1_default)
    db_session.add(dept2_default)

    pos1_default = Position(
        name="Software Engineer",
        description="Developer role",
        organization_id="default",
    )
    pos2_default = Position(
        name="HR Manager", description="HR leadership", organization_id="default"
    )
    db_session.add(pos1_default)
    db_session.add(pos2_default)

    loc1_default = Location(
        name="Hanoi",
        address="123 Main St",
        city="Hanoi",
        country="Vietnam",
        organization_id="default",
    )
    loc2_default = Location(
        name="Ho Chi Minh City",
        address="456 Tech St",
        city="HCMC",
        country="Vietnam",
        organization_id="default",
    )
    db_session.add(loc1_default)
    db_session.add(loc2_default)
    db_session.flush()

    emp1_default = Employee(
        name="Test Employee 1",
        email="test1@example.com",
        phone="+84123456789",
        status="active",
        organization_id="default",
        department_id=dept1_default.id,
        position_id=pos1_default.id,
        location_id=loc1_default.id,
    )
    emp2_default = Employee(
        name="Test Employee 2",
        email="test2@example.com",
        phone="+84987654321",
        status="active",
        organization_id="default",
        department_id=dept2_default.id,
        position_id=pos2_default.id,
        location_id=loc2_default.id,
    )
    db_session.add(emp1_default)
    db_session.add(emp2_default)

    # Create test data for org1
    dept1_org1 = Department(
        name="Engineering", description="Tech department", organization_id="org1"
    )
    pos1_org1 = Position(
        name="Software Engineer", description="Developer role", organization_id="org1"
    )
    loc1_org1 = Location(
        name="Hanoi",
        address="123 Main St",
        city="Hanoi",
        country="Vietnam",
        organization_id="org1",
    )
    db_session.add(dept1_org1)
    db_session.add(pos1_org1)
    db_session.add(loc1_org1)
    db_session.flush()

    emp1_org1 = Employee(
        name="Org1 Employee 1",
        email="org1_test1@example.com",
        phone="+84111111111",
        status="active",
        organization_id="org1",
        department_id=dept1_org1.id,
        position_id=pos1_org1.id,
        location_id=loc1_org1.id,
    )
    db_session.add(emp1_org1)

    # Create test data for org2
    dept1_org2 = Department(
        name="Marketing", description="Marketing department", organization_id="org2"
    )
    pos1_org2 = Position(
        name="Marketing Manager", description="Marketing role", organization_id="org2"
    )
    loc1_org2 = Location(
        name="Da Nang",
        address="789 Beach St",
        city="Da Nang",
        country="Vietnam",
        organization_id="org2",
    )
    db_session.add(dept1_org2)
    db_session.add(pos1_org2)
    db_session.add(loc1_org2)
    db_session.flush()

    emp1_org2 = Employee(
        name="Org2 Employee 1",
        email="org2_test1@example.com",
        phone="+84222222222",
        status="active",
        organization_id="org2",
        department_id=dept1_org2.id,
        position_id=pos1_org2.id,
        location_id=loc1_org2.id,
    )
    db_session.add(emp1_org2)

    db_session.commit()

    return {
        "default": {
            "departments": [dept1_default, dept2_default],
            "positions": [pos1_default, pos2_default],
            "locations": [loc1_default, loc2_default],
            "employees": [emp1_default, emp2_default],
        },
        "org1": {
            "departments": [dept1_org1],
            "positions": [pos1_org1],
            "locations": [loc1_org1],
            "employees": [emp1_org1],
        },
        "org2": {
            "departments": [dept1_org2],
            "positions": [pos1_org2],
            "locations": [loc1_org2],
            "employees": [emp1_org2],
        },
    }
