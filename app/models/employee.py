from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class Department(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationship
    employees = relationship("Employee", back_populates="department")


class Position(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationship
    employees = relationship("Employee", back_populates="position")


class Location(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    
    # Relationship
    employees = relationship("Employee", back_populates="location")


class Employee(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    phone = Column(String, nullable=True)
    status = Column(String, nullable=False, index=True)  # active, inactive, on_leave, etc.
    
    # Foreign keys
    department_id = Column(Integer, ForeignKey("department.id"), nullable=True, index=True)
    position_id = Column(Integer, ForeignKey("position.id"), nullable=True, index=True)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=True, index=True)
    
    # Relationships
    department = relationship("Department", back_populates="employees")
    position = relationship("Position", back_populates="employees")
    location = relationship("Location", back_populates="employees")
    
    # Audit fields are already in Base model (created_at, updated_at)
