from __future__ import annotations

from pydantic import BaseModel


class StatsResponse(BaseModel):
    ts: int
    uptime_sec: int

    cpu_percent: float
    load_1: float | None
    load_5: float | None
    load_15: float | None

    mem_total: int
    mem_used: int
    mem_percent: float

    disk_total: int
    disk_used: int
    disk_percent: float

    net_rx: int
    net_tx: int
