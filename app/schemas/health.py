from __future__ import annotations

from pydantic import BaseModel, Field


class PingResponse(BaseModel):
    ok: bool = Field(True, examples=[True])


class HealthResponse(BaseModel):
    ok: bool
    missing: list[str]
    xray_addr: str
    inbound_tag: str
    sync_server_id: int
    db_dsn: str
    protoset: str
    service: str
    version: str
