import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.containers import container
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
def test_data(db_session):
    # Create some test data
    from app.models.employee import Department, Position, Location, Employee

    # Clear existing data
    db_session.query(Employee).delete()
    db_session.query(Department).delete()
    db_session.query(Position).delete()
    db_session.query(Location).delete()

    # Create test departments
    dept1 = Department(name="Engineering", description="Tech department")
    dept2 = Department(name="HR", description="Human Resources")
    db_session.add(dept1)
    db_session.add(dept2)
    db_session.flush()

    # Create test positions
    pos1 = Position(name="Software Engineer", description="Developer role")
    pos2 = Position(name="HR Manager", description="HR leadership")
    db_session.add(pos1)
    db_session.add(pos2)
    db_session.flush()

    # Create test locations
    loc1 = Location(
        name="Hanoi", address="123 Main St", city="Hanoi", country="Vietnam"
    )
    loc2 = Location(
        name="Ho Chi Minh City", address="456 Tech St", city="HCMC", country="Vietnam"
    )
    db_session.add(loc1)
    db_session.add(loc2)
    db_session.flush()

    # Create test employees
    emp1 = Employee(
        name="Test Employee 1",
        email="test1@example.com",
        phone="+84123456789",
        status="active",
        department_id=dept1.id,
        position_id=pos1.id,
        location_id=loc1.id,
    )
    emp2 = Employee(
        name="Test Employee 2",
        email="test2@example.com",
        phone="+84987654321",
        status="active",
        department_id=dept2.id,
        position_id=pos2.id,
        location_id=loc2.id,
    )
    db_session.add(emp1)
    db_session.add(emp2)
    db_session.commit()

    return {
        "departments": [dept1, dept2],
        "positions": [pos1, pos2],
        "locations": [loc1, loc2],
        "employees": [emp1, emp2],
    }
