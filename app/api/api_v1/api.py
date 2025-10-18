"""Main API router."""

from fastapi import APIRouter

# Import route modules
from app.api.api_v1.endpoints import auth, quizzes
# from app.api.api_v1.endpoints import admin, sessions, users

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["Quizzes"])
# api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Placeholder endpoint
@api_router.get("/")
async def api_info():
    """API information endpoint."""
    return {
        "message": "Quiz API v1",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth",
            "quizzes": "/quizzes",
            "sessions": "/sessions",
            "users": "/users",
            "admin": "/admin"
        }
    }