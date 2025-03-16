from typing import Optional

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger()

api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)


async def get_api_key(
    request: Request,
    api_key_header: Optional[str] = Security(api_key_header),
) -> str:
    """Validate API key from header."""
    if api_key_header == settings.API_KEY_SECRET:
        return api_key_header
    
    logger.warning(f"Invalid API key attempt from {request.client.host}")
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate API key"
    )


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self._requests = {}
        from time import time
        self._time = time
    
    async def check_rate_limit(self, api_key: str) -> None:
        """Check if the request is within rate limits."""
        now = int(self._time())
        
        if api_key not in self._requests:
            self._requests[api_key] = {"count": 1, "start_time": now}
            return
        
        request_info = self._requests[api_key]
        time_passed = now - request_info["start_time"]
        
        if time_passed >= settings.RATE_LIMIT_PERIOD:
            self._requests[api_key] = {"count": 1, "start_time": now}
            return
        
        if request_info["count"] >= settings.RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for API key ending in ...{api_key[-4:]}")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {settings.RATE_LIMIT_PERIOD - time_passed} seconds"
            )
        
        request_info["count"] += 1


rate_limiter = RateLimiter() 