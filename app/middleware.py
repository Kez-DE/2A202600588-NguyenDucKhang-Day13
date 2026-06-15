from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        clear_contextvars()

        header_id = request.headers.get("x-request-id", "").strip()
        correlation_id = header_id or f"req-{uuid.uuid4().hex[:8]}"

        bind_contextvars(correlation_id=correlation_id)
        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        try:
            response = await call_next(request)
            return response
        finally:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            if "response" in locals():
                response.headers["x-request-id"] = correlation_id
                response.headers["x-response-time-ms"] = str(elapsed_ms)
            clear_contextvars()
