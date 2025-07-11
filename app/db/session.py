from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from app.core.config import settings

# Default to SQLite if SQLALCHEMY_DATABASE_URI is None
database_uri = settings.SQLALCHEMY_DATABASE_URI
if database_uri is None:
    database_uri = f"sqlite:///{settings.SQLITE_DB}"

# Ensure the SQLite database directory exists
db_path = str(database_uri).replace('sqlite:///', '')
db_dir = os.path.dirname(db_path)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir)

# Configure SQLite for better concurrency
engine = create_engine(
    str(database_uri),
    connect_args={"check_same_thread": False},  # Allow multithreaded access
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600  # Recycle connections after 1 hour
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
