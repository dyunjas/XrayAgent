from __future__ import annotations

from pydantic import BaseModel


class DBHealthOK(BaseModel):
    ok: bool
    result: int


class DBHealthFail(BaseModel):
    ok: bool
    error: str
