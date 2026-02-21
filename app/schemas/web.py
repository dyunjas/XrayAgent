from pydantic import BaseModel, Field


class WebLoginReq(BaseModel):
    nick: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=256)


class WebCreateKeyReq(BaseModel):
    user_id: int = Field(..., gt=0)
    level: int = Field(default=0, ge=0, le=255)


class WebResetTrafficReq(BaseModel):
    scope: str = Field(default="all", pattern="^(all|inbound|users)$")


class WebUpdateXrayConfigReq(BaseModel):
    config: dict
