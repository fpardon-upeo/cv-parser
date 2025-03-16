"""
API routes package.

This package contains all the API routes for the application.
"""
from fastapi import APIRouter

from app.api.routes import health, models

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(models.router)

__all__ = ["api_router"] 