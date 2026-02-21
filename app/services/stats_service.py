from __future__ import annotations

import time
import psutil
from dataclasses import dataclass


@dataclass
class ServerStats:
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


class StatsService:
    def __init__(self):
        self._boot_ts = int(time.time())

    def get_stats(self) -> ServerStats:
        now = int(time.time())
        uptime = now - self._boot_ts

        cpu = psutil.cpu_percent(interval=0.1)

        try:
            l1, l5, l15 = psutil.getloadavg()
        except OSError:
            l1 = l5 = l15 = None

        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        return ServerStats(
            ts=now,
            uptime_sec=uptime,
            cpu_percent=float(cpu),
            load_1=None if l1 is None else float(l1),
            load_5=None if l5 is None else float(l5),
            load_15=None if l15 is None else float(l15),
            mem_total=int(mem.total),
            mem_used=int(mem.used),
            mem_percent=float(mem.percent),
            disk_total=int(disk.total),
            disk_used=int(disk.used),
            disk_percent=float(disk.percent),
            net_rx=int(net.bytes_recv),
            net_tx=int(net.bytes_sent),
        )
