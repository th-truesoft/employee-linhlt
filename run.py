import uvicorn
import os
import argparse
import logging

from app.db.init_db import init_db
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run the Employee Directory API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", default=8000, type=int, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--init-db", action="store_true", help="Initialize the database with sample data")
    
    args = parser.parse_args()
    
    if args.init_db:
        logger.info("Initializing database with sample data...")
        db = SessionLocal()
        try:
            init_db(db)
            logger.info("Database initialization completed!")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
        finally:
            db.close()
    
    print(f"Starting Employee Directory API server at http://{args.host}:{args.port}")
    print("API documentation available at:")
    print(f"  - Swagger UI: http://{args.host}:{args.port}/docs")
    print(f"  - ReDoc: http://{args.host}:{args.port}/redoc")
    
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
