"""
Health check API routes.

This module provides API endpoints for health checks.
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=Dict[str, Any])
async def health_check():
    """Check the health of the application.
    
    Returns:
        Dictionary with health status
    """
    return {
        "status": "ok",
        "version": "1.0.0"
    } 