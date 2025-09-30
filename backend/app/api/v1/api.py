"""
API v1 router - combines all v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1 import auth, carbon, users, goals, achievements, recommendations

# Create main v1 router
api_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(carbon.router)
api_router.include_router(users.router)
api_router.include_router(goals.router)
api_router.include_router(achievements.router)
api_router.include_router(recommendations.router)
