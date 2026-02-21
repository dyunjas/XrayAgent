from __future__ import annotations

from pydantic import BaseModel


class ActiveKeysCountOK(BaseModel):
    ok: bool
    active_keys: int
    server_id: int


class ActiveKeysCountFail(BaseModel):
    ok: bool
    error: str
