import os
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.employee import Department, Position, Location, Employee
from app.models.base import Base

def create_tables():
    print("Creating database tables...")
    
    database_uri = settings.SQLALCHEMY_DATABASE_URI
    if database_uri is None:
        database_uri = f"sqlite:///{settings.SQLITE_DB}"
    
    print(f"Connecting to database: {database_uri}")
    
    engine = create_engine(
        str(database_uri),
        connect_args={"check_same_thread": False},
        echo=True
    )
    
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
