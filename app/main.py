from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.middleware import RateLimitMiddleware
from app.core.containers import container
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Employee Directory API",
    description="Employee Directory Search API with FastAPI using clean architecture",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Employee Directory API. Visit /docs for documentation."
    }
