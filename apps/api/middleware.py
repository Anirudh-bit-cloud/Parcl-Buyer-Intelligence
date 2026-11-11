"""FastAPI custom middleware for Request IDs, Structured Logging, ETags, Rate Limiting, and Performance Timing."""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from apps.api.config import api_settings

logger = logging.getLogger("parcl.api")


def record_audit(
    user_id: str,
    role: str,
    action: str,
    resource: str,
    details: str | None = None,
    ip_address: str | None = None,
) -> None:
    """Safely record an audit log entry in the relational database with SHA-256 hash chaining."""
    try:
        from datetime import UTC, datetime

        from apps.api.db import AuditLogEntity, SessionLocal, compute_audit_entry_hash

        with SessionLocal() as session:
            last_entry = session.query(AuditLogEntity).order_by(AuditLogEntity.id.desc()).first()
            prev_hash = str(last_entry.entry_hash) if last_entry and last_entry.entry_hash else "GENESIS"
            now_dt = datetime.now(UTC)

            entry_hash = compute_audit_entry_hash(
                prev_hash=prev_hash,
                timestamp=now_dt,
                user_id=user_id,
                role=role,
                action=action,
                resource=resource,
                details=details,
            )

            entry = AuditLogEntity(
                timestamp=now_dt,
                user_id=user_id,
                role=role,
                action=action,
                resource=resource,
                details=details,
                ip_address=ip_address,
                prev_hash=prev_hash,
                entry_hash=entry_hash,
            )
            session.add(entry)
            session.commit()
    except Exception as exc:
        logger.warning("Failed to record audit log: %s", exc)


class RequestIdAndLoggingMiddleware(BaseHTTPMiddleware):
    """Assigns X-Request-ID and outputs structured JSON logs for requests."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id

        start_time = time.perf_counter()
        client_ip = request.client.host if request.client else "unknown"

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        response.headers["X-Request-ID"] = req_id

        # Skip high-frequency poll log spam for health checks in production
        if request.url.path not in ["/health/live", "/health/ready", "/metrics"]:
            log_payload = {
                "timestamp": time.time(),
                "request_id": req_id,
                "client_ip": client_ip,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
            logger.info(json.dumps(log_payload))

        return response


class PerformanceTimingMiddleware(BaseHTTPMiddleware):
    """Measures and adds processing time header to all responses."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
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

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
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
    """Sliding-window rate limiter per client IP with Redis integration and in-memory fallback."""

    client_records: dict[str, list[float]] = defaultdict(list)
    _redis_client: Any = None
    _redis_failed: bool = False

    def __init__(self, app: Any, max_requests_per_minute: int = 120) -> None:
        super().__init__(app)
        self.max_requests = max_requests_per_minute

    @classmethod
    def reset(cls) -> None:
        """Reset rate limiter buckets (used in test suite)."""
        cls.client_records.clear()
        cls._redis_client = None
        cls._redis_failed = False

    @classmethod
    def _get_redis(cls) -> Any:
        if not api_settings.redis_enabled or cls._redis_failed:
            return None
        if cls._redis_client is None:
            try:
                import redis
                cls._redis_client = redis.from_url(api_settings.redis_url, socket_timeout=0.5)
                cls._redis_client.ping()
            except Exception as e:
                logger.warning("Redis rate limiter unavailable (%s); falling back to in-memory sliding window.", e)
                cls._redis_failed = True
                cls._redis_client = None
        return cls._redis_client

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        # Exempt health checks, metrics, and docs from rate limiting
        if request.url.path in [
            "/api/v1/health",
            "/api/health",
            "/health/live",
            "/health/ready",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60.0

        r_client = self._get_redis()
        if r_client is not None:
            try:
                key = f"ratelimit:{client_ip}"
                pipe = r_client.pipeline()
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zadd(key, {str(now): now})
                pipe.zcard(key)
                pipe.expire(key, 65)
                results = pipe.execute()
                current_count = results[2]
                if current_count > self.max_requests:
                    return StarletteResponse(
                        content='{"detail": "Rate limit exceeded. Maximum 120 requests per minute."}',
                        status_code=429,
                        media_type="application/json",
                        headers={"Retry-After": "60"},
                    )
                return await call_next(request)
            except Exception as exc:
                logger.debug("Redis rate limit check failed (%s); using in-memory fallback.", exc)

        # In-memory sliding window fallback
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
