from __future__ import annotations

import time
from fastapi import APIRouter, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

router = APIRouter(tags=["metrics"])

REQUESTS = Counter("xray_agent_requests_total", "Total HTTP requests", ["path", "method", "status"])
LATENCY = Histogram("xray_agent_request_latency_seconds", "Request latency", ["path", "method"])
UP = Gauge("xray_agent_up", "Agent is up")
START_TIME = Gauge("xray_agent_start_time", "Agent start time (unix seconds)")

UP.set(1)
START_TIME.set(int(time.time()))


@router.get("/metrics", include_in_schema=False)
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
