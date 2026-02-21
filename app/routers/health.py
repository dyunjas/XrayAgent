import os
from fastapi import APIRouter

from app.config import settings
from app.schemas.health import PingResponse, HealthResponse
from app.utils.mask import mask_dsn

router = APIRouter(tags=["health"])


@router.get("/ping", response_model=PingResponse)
def ping():
    return {"ok": True}


@router.get("/health", response_model=HealthResponse)
def health():
    missing: list[str] = []
    for p, name in [(settings.protoc_bin, "protoc"), (settings.grpcurl_bin, "grpcurl")]:
        if not os.path.exists(p):
            missing.append(name)
    if not os.path.isdir(settings.proto_root):
        missing.append(f"dir:{settings.proto_root}")

    return {
        "ok": len(missing) == 0,
        "missing": missing,
        "xray_addr": settings.xray_addr,
        "inbound_tag": settings.inbound_tag,
        "sync_server_id": settings.sync_server_id,
        "db_dsn": mask_dsn(settings.db_dsn),
        "protoset": settings.protoset,
        "service": settings.service_name,
        "version": settings.version,
    }
