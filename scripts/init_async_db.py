#!/usr/bin/env python3
"""Initialize async database for testing."""

import asyncio
import os
import sys

# Add parent directory to path to find app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.async_session import init_async_db, AsyncSessionLocal
from app.models.employee import Employee, Department, Position, Location


async def main():
    print("🔧 Initializing async database...")

    # Initialize database tables
    await init_async_db()
    print("✅ Async database tables created")

    # Create sample data
    async with AsyncSessionLocal() as session:
        try:
            # Check if data already exists
            from sqlalchemy import select, func

            result = await session.execute(select(func.count(Employee.id)))
            count = result.scalar()

            if count > 0:
                print(f"✅ Database already has {count} employees")
                return

            # Create departments
            departments_data = [
                {
                    "name": "Engineering",
                    "description": "Software development",
                    "organization_id": "default",
                },
                {
                    "name": "Marketing",
                    "description": "Marketing department",
                    "organization_id": "default",
                },
                {
                    "name": "Sales",
                    "description": "Sales department",
                    "organization_id": "default",
                },
                {
                    "name": "HR",
                    "description": "Human resources",
                    "organization_id": "default",
                },
            ]

            departments = []
            for dept_data in departments_data:
                dept = Department(**dept_data)
                session.add(dept)
                departments.append(dept)

            await session.flush()  # Get IDs

            # Create positions
            positions_data = [
                {
                    "name": "Developer",
                    "description": "Software developer",
                    "organization_id": "default",
                },
                {
                    "name": "Manager",
                    "description": "Team manager",
                    "organization_id": "default",
                },
                {
                    "name": "Designer",
                    "description": "UI/UX designer",
                    "organization_id": "default",
                },
                {
                    "name": "Analyst",
                    "description": "Business analyst",
                    "organization_id": "default",
                },
            ]

            positions = []
            for pos_data in positions_data:
                pos = Position(**pos_data)
                session.add(pos)
                positions.append(pos)

            await session.flush()  # Get IDs

            # Create locations
            locations_data = [
                {
                    "name": "Hanoi",
                    "address": "Ha Noi",
                    "city": "Hanoi",
                    "country": "Vietnam",
                    "organization_id": "default",
                },
                {
                    "name": "Ho Chi Minh",
                    "address": "Ho Chi Minh City",
                    "city": "HCMC",
                    "country": "Vietnam",
                    "organization_id": "default",
                },
            ]

            locations = []
            for loc_data in locations_data:
                loc = Location(**loc_data)
                session.add(loc)
                locations.append(loc)

            await session.flush()  # Get IDs

            # Create employees
            print("📝 Creating sample employees...")
            for i in range(50):  # Smaller dataset for testing
                employee = Employee(
                    name=f"Employee {i+1}",
                    email=f"employee{i+1}@example.com",
                    phone=f"+84-123-456-{i+1:03d}",
                    status="active" if i % 10 != 0 else "inactive",
                    organization_id="default",
                    department_id=departments[i % len(departments)].id,
                    position_id=positions[i % len(positions)].id,
                    location_id=locations[i % len(locations)].id,
                )
                session.add(employee)

            await session.commit()
            print("✅ Created 50 sample employees with async database")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
