from __future__ import annotations

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.routers.metrics import REQUESTS, LATENCY


class PromMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response: Response = await call_next(request)
        dur = time.perf_counter() - start

        path = request.url.path
        method = request.method
        status = str(response.status_code)

        REQUESTS.labels(path=path, method=method, status=status).inc()
        LATENCY.labels(path=path, method=method).observe(dur)
        return response
