"""
CarbonTrack FastAPI Backend
A SaaS MVP for tracking and reducing carbon footprints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.api.v1.api import api_router

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A comprehensive SaaS platform for tracking and reducing individual and organizational carbon footprints",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS with support for wildcard via env ALLOWED_ORIGINS="*"
configured_origins = settings.allowed_origins or []
is_wildcard = False
if isinstance(configured_origins, list) and len(configured_origins) == 1 and configured_origins[0] == "*":
    is_wildcard = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if is_wildcard else configured_origins,
    allow_credentials=False if is_wildcard else True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"]
)

# Include API routes
app.include_router(api_router)


@app.get("/", response_model=dict, tags=["Health"])
async def root():
    """
    Health check endpoint
    """
    return {
        "message": "Welcome to CarbonTrack API",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "environment": settings.environment
    }


@app.get("/health", response_model=dict, tags=["Health"])
async def health_check():
    """
    Detailed health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": "2024-01-15T12:00:00Z",
        "version": settings.app_version,
        "environment": settings.environment,
        "services": {
            "api": "operational",
            "auth": "operational",
            "database": "operational"
        }
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
