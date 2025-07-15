from fastapi import APIRouter

from app.api.endpoints import employees, monitoring

api_router = APIRouter()
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
