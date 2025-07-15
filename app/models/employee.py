from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class Department(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    organization_id = Column(String, nullable=False, index=True)

    # Relationship
    employees = relationship("Employee", back_populates="department")

    # Composite unique constraint: name unique per organization
    __table_args__ = (
        Index("idx_department_org_name", "organization_id", "name", unique=True),
    )


class Position(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    organization_id = Column(String, nullable=False, index=True)

    # Relationship
    employees = relationship("Employee", back_populates="position")

    # Composite unique constraint: name unique per organization
    __table_args__ = (
        Index("idx_position_org_name", "organization_id", "name", unique=True),
    )


class Location(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    organization_id = Column(String, nullable=False, index=True)

    # Relationship
    employees = relationship("Employee", back_populates="location")

    # Composite unique constraint: name unique per organization
    __table_args__ = (
        Index("idx_location_org_name", "organization_id", "name", unique=True),
    )


class Employee(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    status = Column(
        String, nullable=False, index=True
    )  # active, inactive, on_leave, etc.
    organization_id = Column(String, nullable=False, index=True)

    # Foreign keys
    department_id = Column(
        Integer, ForeignKey("department.id"), nullable=True, index=True
    )
    position_id = Column(Integer, ForeignKey("position.id"), nullable=True, index=True)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=True, index=True)

    # Relationships
    department = relationship("Department", back_populates="employees")
    position = relationship("Position", back_populates="employees")
    location = relationship("Location", back_populates="employees")

    # Composite unique constraint: email unique per organization
    __table_args__ = (
        Index("idx_employee_org_email", "organization_id", "email", unique=True),
    )

    # Audit fields are already in Base model (created_at, updated_at)
