from __future__ import annotations

from pydantic import BaseModel, Field


class AddUserReq(BaseModel):
    email: str | None = Field(default=None, examples=["user-5@lunet"])
    db_user_id: int | None = Field(default=None, examples=[5], description="ID из vpn_users (если email не передан)")
    user_id: str | None = Field(default=None, examples=["9c7a3d2f-2b31-4f93-9d8f-3a9cb6a0c8f1"])
    level: int = Field(default=0, examples=[0])


class AddUserOK(BaseModel):
    ok: bool
    uuid: str
    email: str
    grpc: str | None = None
    note: str | None = Field(default=None, examples=["already exists"])


class RemoveUserReq(BaseModel):
    email: str = Field(..., examples=["user-5@lunet"])


class RemoveUserOK(BaseModel):
    ok: bool
    grpc: str


class ResyncItem(BaseModel):
    uuid: str
    email: str
    result: str = Field(..., examples=["ok", "already", "error"])
    error: str | None = None


class ResyncOK(BaseModel):
    ok: bool
    synced: int
    failed: list[ResyncItem]
    details: list[ResyncItem]
