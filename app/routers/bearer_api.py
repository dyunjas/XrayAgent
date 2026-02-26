from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.deps import auth_dep, get_db
from app.models import Key, KeyStatus
from app.services.persistent_traffic_service import PersistentTrafficService
from app.services.stats_service import StatsService
from app.services.traffic_service import TrafficService
from app.utils.email import email_for_key, email_for_user_id

router = APIRouter(tags=["bearer-api"], dependencies=[Depends(auth_dep)])

traffic_service = TrafficService()
stats_service = StatsService()
persistent_traffic_service = PersistentTrafficService()


def _active_keys(db: Session) -> list[Key]:
    return db.execute(
        select(Key).where(
            Key.status == KeyStatus.active,
            Key.server_id == settings.sync_server_id,
        )
    ).scalars().all()


@router.get("/user_traffic")
def user_traffic(
    user_id: int | None = Query(default=None, gt=0),
    email: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if not user_id and not email:
        return {"ok": False, "detail": "Provide user_id or email"}

    persistent_traffic_service.ensure_table(db)

    active_key: Key | None = None
    if user_id:
        active_key = db.execute(
            select(Key).where(
                Key.user_id == user_id,
                Key.status == KeyStatus.active,
                Key.server_id == settings.sync_server_id,
            )
        ).scalars().first()

    resolved_email = (email or (email_for_key(active_key) if active_key else "")).strip()
    if not resolved_email and user_id:
        resolved_email = email_for_user_id(user_id)
    if not resolved_email:
        return {"ok": False, "detail": "Could not resolve user email"}

    current = traffic_service.get_users_traffic([resolved_email]).get(
        resolved_email,
        {"available": False, "uplink": 0, "downlink": 0, "total": 0},
    )

    resolved_user_id = int(active_key.user_id) if active_key else (int(user_id) if user_id else None)
    if resolved_user_id is not None and bool(current.get("available")):
        persisted = persistent_traffic_service.apply_snapshot(
            db,
            server_id=settings.sync_server_id,
            user_id=resolved_user_id,
            email=resolved_email,
            current_uplink=int(current["uplink"]),
            current_downlink=int(current["downlink"]),
        )
        db.commit()
    elif resolved_user_id is not None:
        persisted = persistent_traffic_service.get_totals(
            db,
            server_id=settings.sync_server_id,
            user_id=resolved_user_id,
        )
    else:
        persisted = {"uplink": 0, "downlink": 0, "total": 0}

    return {
        "ok": True,
        "server_id": settings.sync_server_id,
        "user_id": resolved_user_id,
        "email": resolved_email,
        "current": {
            "available": bool(current.get("available")),
            "uplink": int(current["uplink"]),
            "downlink": int(current["downlink"]),
            "total": int(current["total"]),
        },
        "persisted": persisted,
    }


@router.get("/server_load")
def server_load():
    return {
        "ok": True,
        "server": stats_service.get_stats().__dict__,
    }


@router.get("/xray_stats")
def xray_stats(db: Session = Depends(get_db)):
    keys = _active_keys(db)
    emails = [email_for_key(k) for k in keys]
    inbound = traffic_service.get_inbound_traffic()
    users_map = traffic_service.get_users_traffic(emails)
    users_total = sum(int(v.get("total", 0)) for v in users_map.values())
    users_online_map = traffic_service.get_users_online(emails, users_map)
    online_now = sum(1 for v in users_online_map.values() if bool(v.get("online")))

    return {
        "ok": True,
        "server_id": settings.sync_server_id,
        "stats_available": bool(inbound["available"]),
        "summary": {
            "active_keys": len(keys),
            "online_now": int(online_now),
            "inbound_uplink": int(inbound["uplink"]),
            "inbound_downlink": int(inbound["downlink"]),
            "inbound_total": int(inbound["total"]),
            "users_total": int(users_total),
        },
    }
