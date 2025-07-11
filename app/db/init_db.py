import logging
from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.models.employee import Employee, Department, Position, Location

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create departments if they don't exist
    departments = [
        {"name": "Engineering", "description": "Software development department"},
        {"name": "HR", "description": "Human resources department"},
        {"name": "Marketing", "description": "Marketing department"},
        {"name": "Sales", "description": "Sales department"},
        {"name": "Finance", "description": "Finance department"},
    ]
    
    for dept_data in departments:
        dept = db.query(Department).filter(Department.name == dept_data["name"]).first()
        if not dept:
            dept = Department(**dept_data)
            db.add(dept)
    
    db.commit()
    logger.info("Departments created")
    
    # Create positions if they don't exist
    positions = [
        {"name": "Software Engineer", "description": "Develops software applications"},
        {"name": "HR Manager", "description": "Manages HR operations"},
        {"name": "Marketing Specialist", "description": "Handles marketing campaigns"},
        {"name": "Sales Representative", "description": "Manages client relationships"},
        {"name": "Financial Analyst", "description": "Analyzes financial data"},
    ]
    
    for pos_data in positions:
        pos = db.query(Position).filter(Position.name == pos_data["name"]).first()
        if not pos:
            pos = Position(**pos_data)
            db.add(pos)
    
    db.commit()
    logger.info("Positions created")
    
    # Create locations if they don't exist
    locations = [
        {"name": "Hanoi", "city": "Hanoi", "country": "Vietnam"},
        {"name": "Ho Chi Minh City", "city": "Ho Chi Minh City", "country": "Vietnam"},
        {"name": "Da Nang", "city": "Da Nang", "country": "Vietnam"},
        {"name": "Singapore", "city": "Singapore", "country": "Singapore"},
        {"name": "Bangkok", "city": "Bangkok", "country": "Thailand"},
    ]
    
    for loc_data in locations:
        loc = db.query(Location).filter(Location.name == loc_data["name"]).first()
        if not loc:
            loc = Location(**loc_data)
            db.add(loc)
    
    db.commit()
    logger.info("Locations created")
    
    # Create sample employees if there are none
    if db.query(Employee).count() == 0:
        # Get references to created entities
        eng_dept = db.query(Department).filter(Department.name == "Engineering").first()
        hr_dept = db.query(Department).filter(Department.name == "HR").first()
        marketing_dept = db.query(Department).filter(Department.name == "Marketing").first()
        
        sw_eng_pos = db.query(Position).filter(Position.name == "Software Engineer").first()
        hr_mgr_pos = db.query(Position).filter(Position.name == "HR Manager").first()
        marketing_pos = db.query(Position).filter(Position.name == "Marketing Specialist").first()
        
        hanoi_loc = db.query(Location).filter(Location.name == "Hanoi").first()
        hcmc_loc = db.query(Location).filter(Location.name == "Ho Chi Minh City").first()
        danang_loc = db.query(Location).filter(Location.name == "Da Nang").first()
        
        # Create sample employees
        employees = [
            {
                "name": "Nguyen Van A",
                "email": "nguyenvana@example.com",
                "phone": "+84123456789",
                "status": "active",
                "department_id": eng_dept.id,
                "position_id": sw_eng_pos.id,
                "location_id": hanoi_loc.id,
            },
            {
                "name": "Tran Thi B",
                "email": "tranthib@example.com",
                "phone": "+84987654321",
                "status": "active",
                "department_id": hr_dept.id,
                "position_id": hr_mgr_pos.id,
                "location_id": hcmc_loc.id,
            },
            {
                "name": "Le Van C",
                "email": "levanc@example.com",
                "phone": "+84555666777",
                "status": "inactive",
                "department_id": marketing_dept.id,
                "position_id": marketing_pos.id,
                "location_id": danang_loc.id,
            },
        ]
        
        # Add more sample data to demonstrate performance with larger datasets
        for i in range(1, 1000):
            status = "active" if i % 3 != 0 else "inactive"
            dept_id = eng_dept.id if i % 3 == 0 else (hr_dept.id if i % 3 == 1 else marketing_dept.id)
            pos_id = sw_eng_pos.id if i % 3 == 0 else (hr_mgr_pos.id if i % 3 == 1 else marketing_pos.id)
            loc_id = hanoi_loc.id if i % 3 == 0 else (hcmc_loc.id if i % 3 == 1 else danang_loc.id)
            
            employees.append({
                "name": f"Employee {i}",
                "email": f"employee{i}@example.com",
                "phone": f"+84{1000000+i}",
                "status": status,
                "department_id": dept_id,
                "position_id": pos_id,
                "location_id": loc_id,
            })
        
        for emp_data in employees:
            emp = Employee(**emp_data)
            db.add(emp)
        
        db.commit()
        logger.info(f"{len(employees)} employees created")
    
    logger.info("Database initialization completed")
