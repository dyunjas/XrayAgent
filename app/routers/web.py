from __future__ import annotations

import os
from pathlib import Path
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import settings
from app.deps import get_db
from app.models import Key, KeyStatus
from app.schemas.web import WebCreateKeyReq, WebLoginReq, WebResetTrafficReq, WebUpdateXrayConfigReq
from app.services.stats_service import StatsService
from app.services.xray_config_service import XrayConfigService
from app.services.sync_service import SyncService
from app.services.traffic_service import TrafficService
from app.services.xray_service import XrayService
from app.utils.email import email_for_key, email_for_user_id
from app.utils.web_auth import create_session_token, get_nick_from_session, verify_credentials
from app.utils.xray_uri import build_vless_uri

router = APIRouter(tags=["web"])

SESSION_COOKIE = "xray_web_session"
stats_service = StatsService()
traffic_service = TrafficService()
xray_service = XrayService()
sync_service = SyncService(xray=xray_service)
xray_cfg_service = XrayConfigService()

WEB_DIR = Path(__file__).resolve().parents[1] / "web"
PAGES_DIR = WEB_DIR / "pages"


def _api_auth_nick(request: Request) -> str:
    nick = get_nick_from_session(request.cookies.get(SESSION_COOKIE))
    if not nick:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return nick


def _page_or_login(request: Request, page: str):
    nick = get_nick_from_session(request.cookies.get(SESSION_COOKIE))
    if not nick:
        return RedirectResponse(url="/web/login", status_code=302)
    return FileResponse(path=PAGES_DIR / page)


def _active_keys(db: Session) -> list[Key]:
    return db.execute(
        select(Key).where(
            Key.status == KeyStatus.active,
            Key.server_id == settings.sync_server_id,
        )
    ).scalars().all()


def _management_endpoints() -> list[dict]:
    return [
        {"method": "POST", "path": "/add_user", "auth": "Bearer", "description": "Add user to Xray inbound"},
        {"method": "POST", "path": "/remove_user", "auth": "Bearer", "description": "Remove user by email"},
        {"method": "POST", "path": "/resync", "auth": "Bearer", "description": "Resync active keys from DB to Xray"},
        {"method": "GET", "path": "/web/api/dashboard", "auth": "Cookie", "description": "Dashboard data including online users"},
        {"method": "POST", "path": "/web/api/keys", "auth": "Cookie", "description": "Create user key + add user in Xray"},
        {"method": "GET", "path": "/web/api/xray/settings", "auth": "Cookie", "description": "Xray and dependency status"},
        {"method": "GET", "path": "/web/api/xray/config", "auth": "Cookie", "description": "Read Xray config file"},
        {"method": "PUT", "path": "/web/api/xray/config", "auth": "Cookie", "description": "Update Xray config file"},
        {"method": "POST", "path": "/web/api/xray/restart", "auth": "Cookie", "description": "Restart Xray service command"},
        {"method": "POST", "path": "/web/api/xray/resync", "auth": "Cookie", "description": "Run sync process"},
        {"method": "POST", "path": "/web/api/resets/traffic", "auth": "Cookie", "description": "Reset traffic counters"},
        {"method": "GET", "path": "/web/api/graphs/live", "auth": "Cookie", "description": "Live stats for charts"},
    ]


def _extract_xray_keypair(cfg: dict) -> dict:
    """Try to extract Reality/X25519 key material from xray config."""
    private_key = ""
    public_key = ""
    short_id = ""

    def walk(node):
        nonlocal private_key, public_key, short_id
        if isinstance(node, dict):
            if not private_key and isinstance(node.get("privateKey"), str):
                private_key = node.get("privateKey", "").strip()
            if not public_key and isinstance(node.get("publicKey"), str):
                public_key = node.get("publicKey", "").strip()
            short_ids = node.get("shortIds")
            if not short_id and isinstance(short_ids, list):
                for value in short_ids:
                    if isinstance(value, str) and value.strip():
                        short_id = value.strip()
                        break
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(cfg if isinstance(cfg, dict) else {})
    return {
        "private_key": private_key,
        "public_key": public_key,
        "short_id": short_id,
        "has_keys": bool(private_key or public_key or short_id),
    }


@router.get("/web/login", include_in_schema=False)
def web_login_page(request: Request):
    nick = get_nick_from_session(request.cookies.get(SESSION_COOKIE))
    if nick:
        return RedirectResponse(url="/web", status_code=302)
    return FileResponse(path=PAGES_DIR / "login.html")


@router.post("/web/login", include_in_schema=False)
def web_login(req: WebLoginReq):
    if not verify_credentials(req.nick, req.password):
        raise HTTPException(status_code=401, detail="Wrong nick or password")

    token = create_session_token(req.nick)
    response = JSONResponse({"ok": True})
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=settings.web_session_ttl_sec,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
    )
    return response


@router.post("/web/logout", include_in_schema=False)
def web_logout():
    response = JSONResponse({"ok": True})
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response


@router.get("/web", include_in_schema=False)
def web_dashboard_page(request: Request):
    return _page_or_login(request, "dashboard.html")


@router.get("/web/xray", include_in_schema=False)
def web_xray_page(request: Request):
    return _page_or_login(request, "xray_settings.html")


@router.get("/web/resets", include_in_schema=False)
def web_resets_page(request: Request):
    return _page_or_login(request, "resets.html")


@router.get("/web/graphs", include_in_schema=False)
def web_graphs_page(request: Request):
    return _page_or_login(request, "graphs.html")


@router.get("/web/settings", include_in_schema=False)
def web_panel_settings_page(request: Request):
    return _page_or_login(request, "panel_settings.html")


@router.get("/web/api/dashboard", include_in_schema=False)
def web_dashboard_api(
    request: Request,
    db: Session = Depends(get_db),
):
    nick = _api_auth_nick(request)
    keys = _active_keys(db)

    emails = [email_for_key(k) for k in keys]
    user_traffic = traffic_service.get_users_traffic(emails)
    user_online = traffic_service.get_users_online(emails, user_traffic)
    inbound = traffic_service.get_inbound_traffic()

    users = []
    total_user_up = 0
    total_user_down = 0
    online_now = 0
    online_supported_users = 0
    stats_available = inbound["available"]

    for k in keys:
        email = email_for_key(k)
        traffic = user_traffic.get(email, {"available": False, "uplink": 0, "downlink": 0, "total": 0})
        stats_available = stats_available or traffic["available"]
        total_user_up += int(traffic["uplink"])
        total_user_down += int(traffic["downlink"])
        online_data = user_online.get(email, {"supported": False, "online": False, "value": 0})
        if bool(online_data["supported"]):
            online_supported_users += 1
        if bool(online_data["online"]):
            online_now += 1
        users.append(
            {
                "user_id": int(k.user_id),
                "uuid": k.uuid,
                "email": email,
                "uri": k.uri,
                "uplink": int(traffic["uplink"]),
                "downlink": int(traffic["downlink"]),
                "total": int(traffic["total"]),
                "stats_available": bool(traffic["available"]),
                "online": bool(online_data["online"]),
                "online_supported": bool(online_data["supported"]),
                "online_value": int(online_data["value"]),
            }
        )

    users_sorted = sorted(users, key=lambda u: (not u["online"], -u["total"], u["user_id"]))
    top_users = sorted(users, key=lambda u: u["total"], reverse=True)[:5]

    return {
        "ok": True,
        "nick": nick,
        "server_id": settings.sync_server_id,
        "stats_available": stats_available,
        "server": stats_service.get_stats().__dict__,
        "summary": {
            "active_keys": len(keys),
            "online_now": online_now,
            "offline_now": max(len(keys) - online_now, 0),
            "online_supported_users": online_supported_users,
            "online_ratio_percent": round((online_now / len(keys) * 100.0), 1) if keys else 0.0,
            "inbound_uplink": int(inbound["uplink"]),
            "inbound_downlink": int(inbound["downlink"]),
            "inbound_total": int(inbound["total"]),
            "users_uplink": total_user_up,
            "users_downlink": total_user_down,
            "users_total": total_user_up + total_user_down,
            "avg_user_total": int((total_user_up + total_user_down) / len(keys)) if keys else 0,
        },
        "users": users_sorted,
        "top_users": top_users,
    }


@router.post("/web/api/dashboard/resync", include_in_schema=False)
def web_dashboard_resync(request: Request, db: Session = Depends(get_db)):
    _api_auth_nick(request)
    return sync_service.resync(db)


@router.post("/web/api/dashboard/reset_users_traffic", include_in_schema=False)
def web_dashboard_reset_users_traffic(request: Request, db: Session = Depends(get_db)):
    _api_auth_nick(request)
    keys = _active_keys(db)
    emails = [email_for_key(k) for k in keys]
    return {
        "ok": True,
        "users": traffic_service.reset_users_traffic(emails),
    }


@router.post("/web/api/keys", include_in_schema=False)
def web_create_key(
    payload: WebCreateKeyReq,
    request: Request,
    db: Session = Depends(get_db),
):
    _api_auth_nick(request)

    exists = db.execute(
        select(Key).where(
            Key.user_id == payload.user_id,
            Key.server_id == settings.sync_server_id,
            Key.status == KeyStatus.active,
        )
    ).scalars().first()
    if exists:
        raise HTTPException(status_code=409, detail=f"Active key already exists for user_id={payload.user_id}")

    key_uuid = str(uuid.uuid4())
    email = email_for_user_id(payload.user_id)
    grpc_note = None

    try:
        xray_service.add_user(email=email, level=payload.level, uid=key_uuid)
    except HTTPException as exc:
        detail = str(exc.detail)
        if not xray_service.is_already_exists_error(detail):
            raise
        grpc_note = "xray user already exists"

    key = Key(
        user_id=payload.user_id,
        server_id=settings.sync_server_id,
        uuid=key_uuid,
        uri=build_vless_uri(uid=key_uuid, email=email),
        status=KeyStatus.active,
    )
    db.add(key)
    db.commit()
    db.refresh(key)

    return {
        "ok": True,
        "id": int(key.id),
        "user_id": int(key.user_id),
        "server_id": int(key.server_id),
        "uuid": key.uuid,
        "email": email,
        "uri": key.uri,
        "status": key.status.value,
        "note": grpc_note,
    }


@router.get("/web/api/xray/settings", include_in_schema=False)
def web_xray_settings_api(request: Request, db: Session = Depends(get_db)):
    _api_auth_nick(request)
    missing: list[str] = []
    for p, name in ((settings.protoc_bin, "protoc"), (settings.grpcurl_bin, "grpcurl")):
        if not os.path.exists(p):
            missing.append(name)
    if not os.path.isdir(settings.proto_root):
        missing.append(f"dir:{settings.proto_root}")

    db_ok = True
    db_error = None
    try:
        db.execute(text("SELECT 1")).scalar_one()
    except Exception as exc:
        db_ok = False
        db_error = str(exc)

    inbound = traffic_service.get_inbound_traffic()
    cfg_error = None
    try:
        cfg = xray_cfg_service.read_config()
    except Exception as exc:
        cfg = {}
        cfg_error = str(exc)
    cfg_summary = xray_cfg_service.summarize(cfg)
    keypair = _extract_xray_keypair(cfg)
    return {
        "ok": True,
        "ts": int(time.time()),
        "xray_addr": settings.xray_addr,
        "inbound_tag": settings.inbound_tag,
        "sync_server_id": settings.sync_server_id,
        "protoset": settings.protoset,
        "proto_root": settings.proto_root,
        "grpcurl_bin": settings.grpcurl_bin,
        "protoc_bin": settings.protoc_bin,
        "dependencies_missing": missing,
        "db_ok": db_ok,
        "db_error": db_error,
        "stats_available": inbound["available"],
        "config_path": str(xray_cfg_service.config_path),
        "config_error": cfg_error,
        "config_summary": cfg_summary,
        "xray_keys": keypair,
        "api_endpoints": _management_endpoints(),
    }


@router.get("/web/api/panel/settings", include_in_schema=False)
def web_panel_settings_api(request: Request, db: Session = Depends(get_db)):
    return web_xray_settings_api(request=request, db=db)


@router.get("/web/api/xray/config", include_in_schema=False)
def web_xray_get_config(request: Request):
    _api_auth_nick(request)
    try:
        cfg = xray_cfg_service.read_config()
        err = None
    except Exception as exc:
        cfg = {}
        err = str(exc)
    return {
        "ok": True,
        "path": str(xray_cfg_service.config_path),
        "error": err,
        "config": cfg,
        "summary": xray_cfg_service.summarize(cfg),
    }


@router.put("/web/api/xray/config", include_in_schema=False)
def web_xray_update_config(payload: WebUpdateXrayConfigReq, request: Request):
    _api_auth_nick(request)
    cfg = payload.config
    saved = xray_cfg_service.write_config(cfg)
    return {
        **saved,
        "summary": xray_cfg_service.summarize(cfg),
    }


@router.post("/web/api/xray/restart", include_in_schema=False)
def web_xray_restart(request: Request):
    _api_auth_nick(request)
    return xray_cfg_service.restart_xray()


@router.get("/web/api/dev/endpoints", include_in_schema=False)
def web_dev_endpoints(request: Request):
    _api_auth_nick(request)
    return {
        "ok": True,
        "title": "Lunet Panel API (Xray Management)",
        "endpoints": _management_endpoints(),
    }


@router.post("/web/api/xray/resync", include_in_schema=False)
def web_xray_resync(request: Request, db: Session = Depends(get_db)):
    _api_auth_nick(request)
    return sync_service.resync(db)


@router.post("/web/api/resets/traffic", include_in_schema=False)
def web_reset_traffic(
    payload: WebResetTrafficReq,
    request: Request,
    db: Session = Depends(get_db),
):
    _api_auth_nick(request)
    keys = _active_keys(db)
    emails = [email_for_key(k) for k in keys]

    inbound = {"ok": True, "available": True, "reset_total": 0, "reset_uplink": 0, "reset_downlink": 0}
    users = {"ok": True, "available": True, "reset_total": 0, "reset_uplink": 0, "reset_downlink": 0}

    if payload.scope in ("all", "inbound"):
        inbound = traffic_service.reset_inbound_traffic()
    if payload.scope in ("all", "users"):
        users = traffic_service.reset_users_traffic(emails)

    return {
        "ok": True,
        "scope": payload.scope,
        "inbound": inbound,
        "users": users,
    }


@router.get("/web/api/graphs/live", include_in_schema=False)
def web_graphs_live(request: Request, db: Session = Depends(get_db)):
    _api_auth_nick(request)
    keys = _active_keys(db)
    emails = [email_for_key(k) for k in keys]

    server = stats_service.get_stats()
    inbound = traffic_service.get_inbound_traffic()
    users_map = traffic_service.get_users_traffic(emails)
    users_total = sum(int(v["total"]) for v in users_map.values())
    users_online_map = traffic_service.get_users_online(emails, users_map)
    online_now = sum(1 for v in users_online_map.values() if bool(v.get("online")))

    return {
        "ok": True,
        "ts": int(time.time()),
        "cpu_percent": float(server.cpu_percent),
        "mem_percent": float(server.mem_percent),
        "inbound_total": int(inbound["total"]),
        "users_total": int(users_total),
        "active_keys": len(keys),
        "online_now": int(online_now),
        "stats_available": bool(inbound["available"]),
    }
