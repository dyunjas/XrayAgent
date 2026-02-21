from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str = Field(..., examples=["Unauthorized"])
    detail: str | None = Field(default=None, examples=["Bearer token mismatch"])
    code: str | None = Field(default=None, examples=["UNAUTHORIZED"])


class OKResponse(BaseModel):
    ok: bool = Field(True, examples=[True])
