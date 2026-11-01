"""FastAPI custom middleware for ETags, Rate Limiting, and Performance Timing."""

import hashlib
import time
from collections import defaultdict
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse


class PerformanceTimingMiddleware(BaseHTTPMiddleware):
    """Measures and adds processing time header to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        response.headers["X-Process-Time-Ms"] = str(process_time_ms)
        return response


class ETagMiddleware(BaseHTTPMiddleware):
    """Calculates role-aware SHA-256 ETag for idempotent GET requests and handles 304 Not Modified.

    ROLE-AWARE CACHING GUARANTEE:
    Incorporates the Authorization header hash into the ETag so that masked responses
    are never served as 304 Not Modified to privileged admin callers, and vice-versa.
    Adds 'Vary: Authorization' and 'Cache-Control: private' on all cacheable GET responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Only apply ETags to successful GET requests
        if request.method != "GET" or response.status_code != 200:
            return response

        # Add mandatory caching privacy headers
        response.headers["Vary"] = "Authorization"
        response.headers["Cache-Control"] = "private, max-age=60"

        # Consume streaming body for hashing
        body = [chunk async for chunk in response.body_iterator]
        full_body = b"".join(body)

        # Derive role identity salt from authorization header
        auth_header = request.headers.get("authorization", "anonymous")
        auth_salt = hashlib.sha256(auth_header.encode()).hexdigest()[:16]

        etag = f'"{hashlib.sha256(full_body + auth_salt.encode()).hexdigest()}"'
        if_none_match = request.headers.get("if-none-match")

        if if_none_match and if_none_match.strip() == etag:
            return StarletteResponse(
                status_code=304,
                headers={
                    "ETag": etag,
                    "Vary": "Authorization",
                    "Cache-Control": "private, max-age=60",
                },
            )

        # Return new response with body restored and ETag header
        new_response = Response(
            content=full_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
        new_response.headers["ETag"] = etag
        new_response.headers["Vary"] = "Authorization"
        new_response.headers["Cache-Control"] = "private, max-age=60"
        return new_response


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window in-memory rate limiter per client IP."""

    client_records: dict[str, list[float]] = defaultdict(list)

    def __init__(self, app, max_requests_per_minute: int = 120) -> None:
        super().__init__(app)
        self.max_requests = max_requests_per_minute

    @classmethod
    def reset(cls) -> None:
        """Reset rate limiter buckets (used in test suite)."""
        cls.client_records.clear()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Exempt health check and docs from rate limiting
        if request.url.path in [
            "/api/v1/health",
            "/api/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60.0

        # Purge timestamps older than 60 seconds
        timestamps = [t for t in self.client_records[client_ip] if t > window_start]
        self.client_records[client_ip] = timestamps

        if len(timestamps) >= self.max_requests:
            return StarletteResponse(
                content='{"detail": "Rate limit exceeded. Maximum 120 requests per minute."}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"},
            )

        self.client_records[client_ip].append(now)
        return await call_next(request)
